# Changelog

## 2026-10-26 — sync with Anton-Barinov/php2shell-patches (5.4.45, 5.5.34, 5.6.40, 7.0.33)

- Pulled the current `enhanced-universal` patches from
  [Anton-Barinov/php2shell-patches](https://github.com/Anton-Barinov/php2shell-patches)
  at `4c2438b` for the branches that were behind:
  - 5.6.40: updated to the latest enhanced universal patch (adds the Chain-C
    decode-window hardening, session-filename/`PS(serializer)` resets and the
    `post_max_size` multipart fix on top of the previous version);
  - 7.0.33: replaced the hand-ported 7.2.34 derivative with the full
    7.0 enhanced-universal patch (same root-cause/session/unserialize hardening as
    the other enhanced branches);
  - 5.4.45 and 5.5.34: switched from the minimal official mitigation to the
    enhanced-universal backport, so upload progress is fixed at the root instead of
    being disabled.
- 7.2.34, 7.3.33, 7.4.33, 8.0.30 and 8.1.34 were already byte-identical to the
  current Anton enhanced-universal files and were left unchanged.
- Each changed patch was verified with `patch -p1 --dry-run -F0` against the matching
  vanilla tarball (5.4.45, 5.5.34, 5.6.40 and 7.0.33): no rejects. Builds were not
  re-run for this sync.
- Removed the old “7.0.33 is a hand-ported 7.2.34 patch” note from the README;
  7.0.33 now uses the full enhanced-universal backport.
- Hardened the 5.2.17 patch with the applicable ideas from the newer branches:
  - corrected the request-stack cleanup (the previous hunk cleared
    `zend_ptr_stack.elements` inside `zend_ptr_stack_apply()`, which could crash
    when the stack held more than one element; cleanup now happens in
    `zend_ptr_stack_destroy()`, and `zend_stack_destroy()` also clears its pointer);
  - added `php_emergency_cleanup_uploaded_files()` and a `ZEND_ATTRIBUTE_NORETURN`
    declaration so an OOM `_exit(1)` unlinks temporary uploads without allocating;
  - reset `PS(serializer)` at request shutdown and clear `PS(id)` after closing the
    session (session state no longer leaks into the next request);
  - warn when the actual POST body exceeds `post_max_size` despite the declared
    `Content-Length` (the 8.2.35 multipart fix).
- The hardened 5.2.17 patch was built successfully as CLI with GCC 4.4.7 on
  CentOS 6 (`make` clean); the Apache module was not re-run.
- Hardened 5.3.3 (vanilla) and 5.3.3-50.el6_10 the same way: `zend_stack_destroy()`
  now clears its pointer, `php_emergency_cleanup_uploaded_files()` runs before the
  OOM `_exit(1)`, the allocation-error helper is marked `noreturn`, session
  `PS(id)`/`PS(serializer)` state is reset, and the actual-POST-length warning is
  present. The vanilla patch was built as CLI with `--enable-session` on CentOS 6 /
  GCC 4.4.7; the el6_10 patch was dry-run against the real distro prep tree after
  its 114 spec patches. CGI/Apache builds were not re-run. The earlier 5.3 pointer
  stack cleanup was already correct (unlike 5.2).
- The hardened 5.2.17 patch was built successfully as CLI with GCC 4.4.7 on
  CentOS 6 (`make` clean); the Apache module was not re-run.
- What is intentionally not applicable to 5.2: `session.upload_progress` and the
  upload-progress root-cause/session-filename/`PS(serializer)`-during-upload
  changes (the feature does not exist in 5.2), and the upload-progress Chain-C
  decode-window rewrite. The non-upload `var_destroy()` unserialize path remains
  outside the scope of these patches, as on every other branch.

## 2026-10-22 — enhanced backports (5.6.40, 7.2.34, 7.3.33, 7.4.33, 8.0.30, 8.1.34)

- Adopted the `enhanced-universal` backports from
  [Anton-Barinov/php2shell-patches](https://github.com/Anton-Barinov/php2shell-patches)
  in place of the earlier minimal 5.6.40 and 7.2.34 patches, and added 7.3.33,
  7.4.33, 8.0.30 and 8.1.34 coverage. Each one applies cleanly to the vanilla
  tarball with `patch -p1 -F0` (verified).
- What the enhanced flavour adds over the minimal patches:
  - upload_progress is fixed at the root (counters as `zend_long`, no dangling
    `zval*`) instead of being disabled, so upload progress bars keep working;
  - `ext/standard/var_unserializer.re`/`.c` brought to 8.2.35 parity;
  - the three session-hardening edits (POST-supplied session id ignored under
    `session.use_only_cookies=1`, upload filename sanitised, `PS(serializer)` reset)
    now ship for every enhanced branch, not only 5.6.40.
- The 7.0.33 patch remains a hand-ported 7.2.34 variant (no upstream counterpart).

## 2026-10-22 — PHP 7.0.33 patch

- Added a 7.0 mitigation patch derived from the 7.2.34 patch. Three hunks in the
  Zend core do not match the 7.0 tree and were ported by hand:
  - `Zend/zend_alloc.c` and `Zend/zend_hash.c`: the remaining
    `zend_error_noreturn(E_ERROR, "Possible integer overflow…")` call sites were
    switched to `zend_mm_safe_error_ex()` (same six sites the 7.2 patch converts).
  - `Zend/zend_execute_API.c`: the `shutdown_executor()` state reset
    (`user_error_handler`, `user_exception_handler`, `error_handling`, `exception`)
    was inserted at the matching location in the 7.0 tree.
- The resulting patch applies to the vanilla `php-7.0.33.tar.gz` with `patch -p1`;
  a `--dry-run` pass reports no rejects.
- Note: the 7.0.33 patch does not touch OpenSSL. PHP 7.0 cannot be built against
  OpenSSL 1.1 without a separate compatibility patch, so build with
  `--without-openssl` (or add that patch) if the platform ships OpenSSL 1.1.

## 2026-10-21 — initial release

- Mitigation patches for PHP 5.2.17, 5.3.3 (vanilla and `-50.el6_10`), 5.4.16,
  5.4.45, 5.5.34 and 5.6.40 for CVE-2026-109618 / CVE-2026-109619 ("php2shell").
- Fixed a C error in every patch that touches it:
  `if (!PS(rfc1867_enabled) || true)` → `|| 1`. Upstream code uses `true`, which does
  not compile with gcc without `<stdbool.h>`. Affected: 5.4.16, 5.4.45, 5.5.34, 5.6.40.
- Patch behaviour: OOM and allocation overflows exit the worker instead of unwinding
  the request, request globals are reset between requests, multipart parsing is
  hardened, `session.upload_progress` is disabled on 5.4+.
- 5.6.40 additionally carries three session hardening edits: POST-supplied session
  ids are ignored when `session.use_only_cookies=1`, upload filenames are sanitised
  before being stored in the session file, and `PS(serializer)` is reset between
  requests.
- Added a 7.2 mitigation patch: the official 7.4 backport adapted to the 7.2.34 tree
  (no upstream branch exists for 7.2).
- Added `tools/apply_review_edits.py`, the script used to apply the review-driven edits
  (`noreturn` attribute, upload temp cleanup, part counter covering every part).
