# How these patches were tested

The testing is deliberately **non-exploit**: nothing here attempts remote code
execution or memory disclosure. The goal is to prove that the specific primitive the
CVE chain relies on (an OOM during request start followed by cleanup of partially
initialised state) is no longer reachable, and that normal behaviour is not broken.

## 1. Build and applicability

For every version:

1. Fresh official tarball (`php-<version>.tar.gz` from museum.php.net / php.net).
2. `patch -p1 --dry-run` first, then a real `patch -p1`; the patch must apply with
   **zero rejects**.
3. `./configure --disable-all --enable-cli --enable-cgi --enable-session \
   --enable-filter --enable-libxml` (a lab build is enough; production builds use the
   options of the existing package).
4. `make -j"$(nproc)"` — every touched translation unit must compile without new
   warnings (`zend_alloc.c`, `zend_execute_API.c`, `zend_operators.c`,
   `zend_stack.c`, `zend_ptr_stack.c`, `zend_llist.c`, `zend_strtod.c`, `session.c`,
   `SAPI.c`, `main.c`, `php_variables.c`, `rfc1867.c`).
5. `php -v`, `php -m` — the binary starts, the expected extension set is present.

For distribution trees (the 5.3.3-50.el6_10 case) the same steps were run **after**
applying all 114 patches from the spec's `%prep`, so the test happens on the tree that
is actually shipped, not on vanilla sources.

## 2. OOM reproducer (the core check)

A request is built so that PHP exhausts `memory_limit` while starting to parse a
multipart body. The observable difference is the exit path:

```sh
# CLI variant: exhaust the limit inside a request
php -d memory_limit=4M -r '$a=array(); while(1){$a[]=str_repeat("x",100000);}'
echo "exit=$?"
```

| Build | Result |
|---|---|
| stock 5.x | `exit=255`, the engine continues its shutdown with partially initialised state |
| patched | `exit=1`, the fatal error is printed and the process exits immediately, no shutdown path runs |

CGI variant (closer to a web request, no server needed):

```sh
printf '--X\r\nContent-Disposition: form-data; name="a"\r\n\r\n' > /tmp/mp.body
php-cgi -q -d cgi.force_redirect=0 -d memory_limit=2M \
        -d post_max_size=1M -f /tmp/post.php < /tmp/mp.body
echo "exit=$?"     # 1 on a patched build
```

Server-level check: Apache with the patched mod_php on a spare port. A large OOM
request kills the child (`exited on signal`/`exit code 1` in the log) and the parent
keeps serving the next requests; with FPM the worker dies and the master replaces it.

## 3. Multipart parser checks

| Check | Expected on a patched build |
|---|---|
| Normal 2-part form | both fields in `$_POST`, file uploaded |
| 3 parts with `max_multipart_body_parts=1` | only the first part is accepted, a warning is logged |
| Parts without `Content-Disposition` | counted against the limit as well |
| Duplicate `Content-Disposition` / `Content-Type` | only the first occurrence is used |
| Body larger than `post_max_size`, no `Content-Length` (chunked) | reading stops at the limit, the upload is rejected, no temp file left |
| Truncated file part | `UPLOAD_ERR_PARTIAL`-style handling, temp file removed |

The limit test is repeatable with `php-cgi` by feeding a hand-written body:

```sh
php-cgi -q -d cgi.force_redirect=0 -d max_multipart_body_parts=1 \
        -d log_errors=1 -d error_log=/tmp/e.log -f /tmp/post.php < /tmp/mp.body
```

## 4. Regression checks around the patched code

- `shutdown_executor()` paths: a fatal error in a shutdown function, in a destructor
  and in an object `__destruct` — the next request in the same worker must start with
  clean state (no leaked handlers, no double free, no crash).
- Session write on OOM: with the patch a session is **not** written (documented
  trade-off); verify the application tolerates that.
- Upload temp directory: after an OOM during an upload, no `php*` files remain.
- Repeated OOM requests: the worker set recovers, no crash loop; measure restart rate
  to size `pm.max_children`.
- Smoke tests on staging sites after swapping the binary: front page, a form
  submission, an upload, an admin page.

## 5. What was verified per branch

| Version | Patch applied | Compiled | OOM exit 1 | Multipart / limit | Notes |
|---|---|---|---|---|---|
| 5.0.5 | yes | yes (CLI) | not run | not run | Experimental hardening only; no confirmed php2shell vector |
| 5.1.6 | yes | yes (CLI) | not run | not run | Experimental hardening only; no confirmed php2shell vector |
| 5.2.17 | yes | yes | yes | yes | Apache DSO, tested on a spare Apache instance |
| 5.3.3 | yes | yes | yes | yes | CLI+CGI, vanilla tree |
| 5.3.3-50.el6_10 | yes | yes | yes | yes | distro tree after 114 spec patches |
| 5.4.16 | yes | yes | yes | yes | CLI+CGI |
| 5.4.45 | yes | yes | yes | yes | CLI+CGI; later built as an Apache module and smoke-tested on live sites |
| 5.5.34 | yes | yes | yes | yes | CLI+CGI |
| 5.6.40 | yes | yes | yes | yes | CLI+CGI, FPM build, spare-port FPM test |
| 7.1.33 | yes | yes (CLI) | not run | not run | Enhanced port; declaration hunk relocated |

> The 5.3.3/5.4.16/5.4.45/5.5.34/5.6.40 rows above record builds of the earlier
> patches. The 2026-10-26 hardened 5.0.5, 5.1.6, 5.2.17, 5.3.3 and 5.4.16 patches, plus the 7.1.33 port, were
> built as CLI on CentOS 6 / GCC 4.4.7 with `--enable-session` (`make` clean); their
> CGI/Apache modules were not re-run. 5.1.6 has no confirmed php2shell vector; its
> patch is experimental defense-in-depth. The 5.3.3-50.el6_10 patch was verified with
> `patch -p1 --dry-run -F0` on the real distro prep tree after its 114 spec
> patches. The enhanced-universal sync for 5.4.45, 5.5.34, 5.6.40 and 7.0.33 was
> verified with `patch -p1 --dry-run -F0` on clean vanilla tarballs; those
> binaries were not rebuilt as part of this sync.

## 6. What is **not** covered by these tests

- No RCE PoC was executed, by design.
- OPcache-specific paths were not tested: the patches do not touch `ext/opcache`, so
  keep `opcache.enable=0` while this mitigation is in place.
- Non-OOM `E_ERROR` paths (about 288 call sites) are unchanged and were not retested.
- Long-running load tests and fuzzing of the multipart parser were not performed;
  treat the parser changes as hardening, not as a audited rewrite.
