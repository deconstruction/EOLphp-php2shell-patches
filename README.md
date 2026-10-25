# EOLphp-php2shell-patches

Unofficial mitigation patches for **CVE-2026-109618 / CVE-2026-109619** ("php2shell")
covering end-of-life PHP 5.x–8.1 branches.

> ⚠️ This is **not** a vendor fix and **not** a replacement for upgrading. PHP 5.2–7.0
> and 7.2/7.4/8.0/8.1 are end-of-life. The 5.4.45/5.5.34/5.6.40/7.0/7.2/7.3/7.4/8.0/8.1
> patches follow the enhanced backports (root-cause fix, 8.2.35 parity); the
> 5.2/5.3/5.4.16 ones are minimal mitigations. None of them makes an EOL branch safe.
> The only complete fix is a supported branch: **8.2.35+ / 8.3.36+ / 8.4.27+ / 8.5.12+**.
> Apply only after testing; the authors accept no liability.

## Patches

| File | Version | Target | SHA-256 |
|---|---|---|---|
| `php-5.2.17-CVE-2026-109618-109619.patch` | 5.2.17 | mod_php (Apache DSO), vanilla tarball; no upload_progress in 5.2 | `1294094deffa8bd046b1a1ff0d783df1149152f61afb41ad6216eb2feb944dde` |
| `php-5.3.3-CVE-2026-109618-109619.patch` | 5.3.3 | vanilla tarball | `7f3216cd6d306cf44795588a278795fbaffbce72051515472898ba4f9377018f` |
| `php-5.3.3-50.el6_10-CVE-2026-109618-109619.patch` | 5.3.3-50.el6_10 | CentOS/OL 6.10 distro tree (after the 114 patches from the spec) | `ac0f8bf2da36b811c1c2d57d1faab923e24094557ef9e4eb9ef09e8df108df39` |
| `php-5.4.16-CVE-2026-109618-109619.patch` | 5.4.16 | vanilla tarball (minimal; upload_progress disabled) | `3744e693b203b1618940f01a90515ad0b5a5096041d3d1048abaf5fd51e0b088` |
| `php-5.4.45-CVE-2026-109618-109619.patch` | 5.4.45 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `1e446a1562fd7040223e9551dba7f81aeff6eb8caa138fe98254128acd786c8c` |
| `php-5.5.34-CVE-2026-109618-109619.patch` | 5.5.34 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `8084e5514995bea5d635cc6637159168478d020403e685a1cd5b2af780a1e547` |
| `php-7.2.34-CVE-2026-109618-109619.patch` | 7.2.34 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `cd2e30e705e9b0fdd9c6e51b8e7791985482050d78b9e8eb70c8e66dfb4bce2e` |
| `php-7.4.33-CVE-2026-109618-109619.patch` | 7.4.33 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `fd0a3f874b15ab8e018fde34831a1116baa0523d35f66a73164d5c2dfb57e4ca` |
| `php-7.3.33-CVE-2026-109618-109619.patch` | 7.3.33 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `1fb0116da44bab2c63803c53e6a3d6b183684153e5e3a45daece36121cf9c236` |
| `php-8.0.30-CVE-2026-109618-109619.patch` | 8.0.30 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `4b70292bb7a4a8f23ced14e29f0e109fb8920da05ec39054ef2fec2db83d6325` |
| `php-8.1.34-CVE-2026-109618-109619.patch` | 8.1.34 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `1bb15cc59aff2d3f8b2e7378443e5f0ec72357a5ca3b2b801c4881cbb7bfab08` |
| `php-7.0.33-CVE-2026-109618-109619.patch` | 7.0.33 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `28ce9a75054c86a1425cbfb81897d671c2ae85f8635c62ae0ece506dea2015fa` |
| `php-5.6.40-CVE-2026-109618-109619.patch` | 5.6.40 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `35c8fb03fb6503d0182fa9964dad6c701a7797cb654593fcf7bd5183e8cee1ba` |

Patches apply to the official `php-<version>.tar.gz` tarballs
(museum.php.net / php.net) with `patch -p1`, no rejects. The 5.4.45/5.5.34/5.6.40/
7.0/7.2/7.3/7.4/8.0/8.1 patches are the `enhanced-universal` backports from
[Anton-Barinov/php2shell-patches](https://github.com/Anton-Barinov/php2shell-patches)
(verified against the vanilla tarballs listed above); they carry the official OOM
fix plus the root-cause upload_progress fix, so upload progress bars keep working.
The 5.2/5.3/5.4.16 patches remain the minimal mitigations; their upload progress
support is intentionally disabled (see below).

## What the patches change

- **OOM no longer unwinds the request.** Instead of `zend_error_noreturn()` /
  `zend_bailout()` (longjmp), the engine prints a fatal error and calls `_exit(1)`.
  The same applies to `safe_address` overflows, string concatenation overflow,
  `zend_mm_panic()` and `Balloc()`. Upload temp files are removed before exiting, so
  no orphaned `php*` files are left behind.
- **State reset between requests:** `shutdown_executor()` clears error/exception
  handlers and `objects_store`; `main.c` clears `PG(http_globals)` and
  `modules_activated`; `SAPI.c` clears `SG(request_info)` fields; stacks and llist
  null their pointers after destroy.
- **Multipart parser:** stop reading the body beyond `post_max_size` even without
  `Content-Length`; keep only `Content-Disposition`/`Content-Type`; ignore duplicates;
  `max_multipart_body_parts` limit that counts every part; `size_t` in `substring_conf`.
- **`session.upload_progress`:** disabled in the 5.2/5.3/5.4.16 minimal patches (one of the
  demonstrated exploit paths; progress bars stop working). In the enhanced
  5.4.45/5.5.34/5.6.40/7.0/7.2/7.3/7.4/8.0/8.1 patches the root cause is fixed instead (progress counters as `zend_long`,
  no dangling `zval*`), so upload progress keeps working.
- **Extra session hardening (5.4.45/5.5.34/5.6.40/7.0/7.2/7.3/7.4/8.0/8.1 enhanced):** a session id supplied in
  the POST body is ignored when `session.use_only_cookies=1`; the upload filename is
  sanitised (`NUL`, `|`, CR/LF removed, capped at 255 chars) before it is written into
  the session file; `PS(serializer)` is reset between requests. These block the
  session-fixation, session-file injection and cross-request handler-mismatch
  chains published alongside the CVE.
- **`var_unserializer` hardening:** the enhanced patches bundle the fixed
  `ext/standard/var_unserializer.re`/`.c` pair, matching the 8.2.35 code, so the
  unserialize path used by the second CVE is patched as well.

Details: [README-CVE-2026-109618-109619.md](README-CVE-2026-109618-109619.md).
Testing methodology and per-branch results: [TESTING.md](TESTING.md).

## How to apply

```sh
tar xzf php-5.6.40.tar.gz
cd php-5.6.40
patch -p1 < ../php-5.6.40-CVE-2026-109618-109619.patch
./configure ...   # keep --enable-session, --enable-filter, --enable-libxml
make -j"$(nproc)"
```

For distribution SRPM trees the context may shift — apply with `-F3` and review
`.rej` files. Make sure the rebuilt binary ships the same extensions as your current
build, otherwise sites will lose functionality.

Recommended pool settings while running a patched binary:

```ini
; opcache is not covered by these patches
opcache.enable=0
; the OOM message goes to stderr, keep it visible in the FPM log
catch_workers_output=yes
```

## Known limitations

- **OPcache is not patched.** The official fix touches `ext/opcache`
  (`ZendAccelerator.c`, `zend_persist.c`, `zend_file_cache.c`); these patches do not.
  With `opcache.enable=1` part of CVE-2026-109619 may remain reachable.
- **Non-OOM `E_ERROR` paths are not covered.** About 288 sites in `php_error_cb` still
  go through `zend_bailout()`. The patches only change OOM and overflow paths.
- **`_exit` skips shutdown:** shutdown functions, destructors, session writes and
  output handlers do not run. Upload temp files are removed, but data that would be
  written during shutdown is lost.
- **OOM kills the worker** (FPM worker or Apache child) — that amplifies DoS and
  returns 502 for legitimately heavy requests. Monitor worker restarts.
- **`session.upload_progress`** is disabled only in the 5.2/5.3/5.4.16 minimal patches;
  the enhanced 5.4.45/5.5.34/5.6.40/7.0/7.2/7.3/7.4/8.0/8.1 patches fix it at the root and leave the feature
  working.
- The OOM message goes to stderr; with `catch_workers_output=no` (FPM default) it is
  lost.

## Repository changes

- Fixed a C error in all patches that touch it: `if (!PS(rfc1867_enabled) || true)` →
  `|| 1`. Upstream code uses `true`, which does not compile with gcc (C has no `true`
  without `<stdbool.h>`).
- 5.2/5.3 patches are unaffected (no `session.upload_progress` there).

## Credits

Session hardening ideas (POST-supplied session id handling, upload filename
sanitisation, serializer reset) follow the community patch set
`Anton-Barinov/php2shell-patches`.

## License

Patch context is PHP source, distributed under the
[PHP License 3.01](https://www.php.net/license/3_01.txt). Original changes are provided
as is, without warranty.
