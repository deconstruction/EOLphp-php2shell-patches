# EOLphp-php2shell-patches

Unofficial mitigation patches for **CVE-2026-109618 / CVE-2026-109619** ("php2shell")
covering selected end-of-life PHP branches: 5.2, 5.3, 5.4, 5.5, 5.6, 7.0,
7.2–7.4 and 8.0–8.1. **PHP 7.1 is not covered.** PHP 5.1.6 has a separate
experimental hardening patch (not a confirmed CVE fix).

> ⚠️ This is **not** a vendor fix and **not** a replacement for upgrading. PHP 5.2–7.0
> and 7.1/7.2/7.3/7.4/8.0/8.1 are end-of-life. The 5.4.45/5.5.34/5.6.40/7.0/7.2/7.3/7.4/8.0/8.1
> patches follow the enhanced backports (root-cause fix, 8.2.35 parity); the
> 5.2/5.3/5.4.16 ones are minimal mitigations. None of them makes an EOL branch safe.
> The only complete fix is a supported branch: **8.2.35+ / 8.3.36+ / 8.4.27+ / 8.5.12+**.
> Apply only after testing; the authors accept no liability.

## Patches

| File | Version | Target | SHA-256 |
|---|---|---|---|
| `php-5.1.6-hardening.patch` | 5.1.6 | vanilla tarball (experimental hardening; no confirmed php2shell vector) | `bf2c2c828909124a53630b87ed6d685ea59786d4e33c4e5bf113abf0ed5aacc9` |
| `php-5.2.17-CVE-2026-109618-109619.patch` | 5.2.17 | mod_php (Apache DSO), vanilla tarball; no upload_progress in 5.2 | `1294094deffa8bd046b1a1ff0d783df1149152f61afb41ad6216eb2feb944dde` |
| `php-5.3.3-CVE-2026-109618-109619.patch` | 5.3.3 | vanilla tarball (minimal; no upload_progress in 5.3) | `7f3216cd6d306cf44795588a278795fbaffbce72051515472898ba4f9377018f` |
| `php-5.3.3-50.el6_10-CVE-2026-109618-109619.patch` | 5.3.3-50.el6_10 | CentOS/OL 6.10 distro tree (minimal; after the 114 patches from the spec) | `ac0f8bf2da36b811c1c2d57d1faab923e24094557ef9e4eb9ef09e8df108df39` |
| `php-5.4.16-CVE-2026-109618-109619.patch` | 5.4.16 | vanilla tarball (minimal; upload_progress disabled) | `3744e693b203b1618940f01a90515ad0b5a5096041d3d1048abaf5fd51e0b088` |
| `php-5.4.45-CVE-2026-109618-109619.patch` | 5.4.45 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `1e446a1562fd7040223e9551dba7f81aeff6eb8caa138fe98254128acd786c8c` |
| `php-5.5.34-CVE-2026-109618-109619.patch` | 5.5.34 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `8084e5514995bea5d635cc6637159168478d020403e685a1cd5b2af780a1e547` |
| `php-5.6.40-CVE-2026-109618-109619.patch` | 5.6.40 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `35c8fb03fb6503d0182fa9964dad6c701a7797cb654593fcf7bd5183e8cee1ba` |
| `php-7.0.33-CVE-2026-109618-109619.patch` | 7.0.33 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `28ce9a75054c86a1425cbfb81897d671c2ae85f8635c62ae0ece506dea2015fa` |
| `php-7.2.34-CVE-2026-109618-109619.patch` | 7.2.34 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `cd2e30e705e9b0fdd9c6e51b8e7791985482050d78b9e8eb70c8e66dfb4bce2e` |
| `php-7.3.33-CVE-2026-109618-109619.patch` | 7.3.33 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `1fb0116da44bab2c63803c53e6a3d6b183684153e5e3a45daece36121cf9c236` |
| `php-7.4.33-CVE-2026-109618-109619.patch` | 7.4.33 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `fd0a3f874b15ab8e018fde34831a1116baa0523d35f66a73164d5c2dfb57e4ca` |
| `php-8.0.30-CVE-2026-109618-109619.patch` | 8.0.30 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `4b70292bb7a4a8f23ced14e29f0e109fb8920da05ec39054ef2fec2db83d6325` |
| `php-8.1.34-CVE-2026-109618-109619.patch` | 8.1.34 | vanilla tarball (enhanced universal backport, 8.2.35 parity) | `1bb15cc59aff2d3f8b2e7378443e5f0ec72357a5ca3b2b801c4881cbb7bfab08` |

Patches apply to the official `php-<version>.tar.gz` tarballs
(museum.php.net / php.net) with `patch -p1`, no rejects, except
`php-5.3.3-50.el6_10` (requires the prepared distro tree noted below). The 5.4.45/5.5.34/5.6.40/
7.0/7.2/7.3/7.4/8.0/8.1 patches are the `enhanced-universal` backports from
[Anton-Barinov/php2shell-patches](https://github.com/Anton-Barinov/php2shell-patches)
(verified against the vanilla tarballs listed above); they carry the official OOM
fix plus the root-cause upload_progress fix, so upload progress bars keep working.
The enhanced files were taken from Anton-Barinov/php2shell-patches at commit
`4c2438b` (2026-10-25); 7.2.34/7.3.33/7.4.33/8.0.30/8.1.34 were already identical.
The 5.2/5.3/5.4.16 patches remain the minimal mitigations. 5.2/5.3 have no
`session.upload_progress` feature to disable; 5.4.16 disables it (see below).

## Compatibility and verification notes

- **PHP 5.1.6 is not a CVE fix.** The 5.1 branch predates
  `session.upload_progress` (5.4) and the raw-key `zend_hash_str_add/update`
  optimization associated with CVE-2026-109618 (7.3+). It is not in the published
  affected lists. `php-5.1.6-hardening.patch` is defense-in-depth only: OOM
  `_exit(1)`, request-state resets, multipart limits and temp-upload cleanup.
- **5.4.16 stays minimal:** the current Anton enhanced 5.4 patch targets 5.4.45 and
  does not apply cleanly to 5.4.16.
- **5.5.34** uses Anton's 5.5 enhanced-universal patch. Upstream documents it against
  5.5.38; it applies cleanly to the vanilla 5.5.34 tarball in a dry-run, but the
  5.5.34 build was not re-run for this sync.
- **5.3.3-50.el6_10** must be applied to the prepared CentOS/OL 6.10 tree *after* the
  114 patches from the spec. It was verified with `patch -p1 --dry-run -F0` on that
  tree; no build was re-run.
- **Build verification:** 5.1.6, 5.2.17, 5.3.3 and 5.4.16 were built as CLI with
  `--enable-session` on CentOS 6 / GCC 4.4.7 (`make` clean). CGI/Apache modules were
  not re-run. 5.4.45, 5.5.34, 5.6.40 and 7.0.33 were apply-verified only in this
  sync. 7.2.34/7.3.33/7.4.33/8.0.30/8.1.34 were already byte-identical to the
  current Anton enhanced-universal files.
- **PHP 7.1 is intentionally not included.** Use a 7.2+ patch or a supported branch.

## What the patches change

- **OOM no longer unwinds the request.** Instead of `zend_error_noreturn()` /
  `zend_bailout()` (longjmp), the engine prints a fatal error and calls `_exit(1)`.
  The same applies to `safe_address` overflows, string concatenation overflow,
  `zend_mm_panic()` and `Balloc()`. The hardened minimal 5.1.6/5.2/5.3/5.4.16 patches
  unlink upload temp files before `_exit`; the enhanced backports do not carry that
  emergency cleanup, so an OOM there may leave the current request's temp files.
- **State reset between requests:** `shutdown_executor()` clears error/exception
  handlers and `objects_store`; `main.c` clears `PG(http_globals)` and
  `modules_activated`; `SAPI.c` clears `SG(request_info)` fields. The minimal patches
  (including 5.1.6) also null ptr-stack/stack/llist pointers after destroy.
- **Multipart parser:** stop reading the body beyond `post_max_size` even without
  `Content-Length`; keep only `Content-Disposition`/`Content-Type`; ignore duplicates;
  `max_multipart_body_parts` limit that counts every part; `size_t` in `substring_conf`.
- **`session.upload_progress`:** 5.1, 5.2 and 5.3 do not have the feature;
  5.4.16 disables it (one of the demonstrated exploit paths; progress bars stop working).
  In the enhanced 5.4.45/5.5.34/5.6.40/7.0/7.2/7.3/7.4/8.0/8.1 patches the root
  cause is fixed instead (progress counters as `zend_long`, no dangling `zval*`),
  so upload progress keeps working.
- **Session hardening:** the hardened minimal patches reset `PS(id)` and, where present,
  `PS(serializer)` between requests (5.1.6/5.2/5.3/5.4.16). The enhanced
  5.4.45/5.5.34/5.6.40/7.0/7.2/7.3/7.4/8.0/8.1 patches add the upload-progress
  session fixes: a POST-supplied session id is ignored when
  `session.use_only_cookies=1`, the upload filename is sanitised (`NUL`, `|`, CR/LF
  removed, capped at 255 chars) before it is written into the session file, and the
  handler-mismatch chains from the advisory are closed. These upload-progress edits
  do not apply to 5.2/5.3 (no feature) or to 5.4.16 (feature disabled).
- **`var_unserializer` hardening:** the enhanced patches bundle the fixed
  `ext/standard/var_unserializer.re`/`.c` pair, matching the 8.2.35 code, so the
  upload-progress Chain-C decode path is patched as well. The minimal 5.1.6/5.2/5.3/5.4.16
  patches do not include that upload-progress rewrite. The separate `var_destroy()`
  unserialize UAF is not fixed by any of these patches.

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
  output handlers do not run. Upload temp files are removed only by the hardened
  minimal 5.1.6/5.2/5.3/5.4.16 patches; enhanced branches may leave them. Data that would
  be written during shutdown is lost on every branch.
- **OOM kills the worker** (FPM worker or Apache child) — that amplifies DoS and
  returns 502 for legitimately heavy requests. Monitor worker restarts.
- **`session.upload_progress`:** 5.2/5.3 do not have it; 5.4.16 disables it. The
  enhanced 5.4.45/5.5.34/5.6.40/7.0/7.2/7.3/7.4/8.0/8.1 patches fix it at the root
  and leave the feature working.
- The OOM message goes to stderr; with `catch_workers_output=no` (FPM default) it is
  lost.

## Repository changes

- Fixed a C error in all patches that touch it: `if (!PS(rfc1867_enabled) || true)` →
  `|| 1`. Upstream code uses `true`, which does not compile with gcc (C has no `true`
  without `<stdbool.h>`).
- The `|| 1` C fix does not apply to 5.2/5.3 because the `session.upload_progress`
  code does not exist there.

## Credits

Session hardening ideas (POST-supplied session id handling, upload filename
sanitisation, serializer reset) follow the community patch set
`Anton-Barinov/php2shell-patches`.

## License

Patch context is PHP source, distributed under the
[PHP License 3.01](https://www.php.net/license/3_01.txt). Original changes are provided
as is, without warranty.
