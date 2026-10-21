import io, os, sys

root = sys.argv[1] if len(sys.argv) > 1 else "."

def read(p):
    with io.open(p, "r", encoding="utf-8", errors="surrogateescape") as f:
        return f.read()

def write(p, s):
    with io.open(p, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write(s)

# 1) noreturn attribute on zend_mm_safe_error_ex declaration
p = os.path.join(root, "Zend/zend_alloc.h")
s = read(p)
old = "ZEND_API void zend_mm_safe_error_ex(const char *format, ...);"
new = (
    "#if defined(__GNUC__)\n"
    "# define ZEND_ATTRIBUTE_NORETURN __attribute__((__noreturn__))\n"
    "#else\n"
    "# define ZEND_ATTRIBUTE_NORETURN\n"
    "#endif\n"
    "ZEND_API ZEND_ATTRIBUTE_NORETURN void zend_mm_safe_error_ex(const char *format, ...);"
)
assert s.count(old) == 1, "zend_alloc.h anchor not found"
s = s.replace(old, new)
write(p, s)

# 2) emergency upload cleanup: extern + call before _exit
p = os.path.join(root, "Zend/zend_alloc.c")
s = read(p)
anchor = '#include "zend_execute.h"\n'
assert s.count(anchor) >= 1, "include anchor"
decl = anchor + (
    "\n/* Implemented in main/SAPI.c. Must not allocate memory. */\n"
    "extern void php_emergency_cleanup_uploaded_files(TSRMLS_D);\n"
)
s = s.replace(anchor, decl, 1)
old_exit = (
    "\tfprintf(stderr, \"\\nFatal error: %s in %s on line %d\\n\", buf, error_filename, error_lineno);\n"
    "/* See http://support.microsoft.com/kb/190351 */\n"
    "#ifdef PHP_WIN32\n"
    "\tfflush(stderr);\n"
    "#endif\n"
    "\t_exit(1);\n"
)
new_exit = (
    "\tfprintf(stderr, \"\\nFatal error: %s in %s on line %d\\n\", buf, error_filename, error_lineno);\n"
    "/* See http://support.microsoft.com/kb/190351 */\n"
    "#ifdef PHP_WIN32\n"
    "\tfflush(stderr);\n"
    "#endif\n"
    "\t/* Do not leak uploaded temp files when the process dies here. */\n"
    "\tphp_emergency_cleanup_uploaded_files(TSRMLS_C);\n"
    "\t_exit(1);\n"
)
assert s.count(old_exit) == 1, "exit anchor not found"
s = s.replace(old_exit, new_exit)
write(p, s)

# 3) emergency cleanup implementation in main/SAPI.c
p = os.path.join(root, "main/SAPI.c")
s = read(p)
anchor = "SAPI_API void sapi_terminate_process(TSRMLS_D) {"
assert s.count(anchor) == 1, "SAPI anchor"
func = (
    "/* Unlink temporary upload files without using the allocator.\n"
    " * Called right before _exit(1) on OOM, where normal request shutdown\n"
    " * (and destroy_uploaded_files_hash) never runs. */\n"
    "void php_emergency_cleanup_uploaded_files(TSRMLS_D) /* {{{ */\n"
    "{\n"
    "\tBucket *p;\n"
    "\n"
    "\tif (!SG(rfc1867_uploaded_files)) {\n"
    "\t\treturn;\n"
    "\t}\n"
    "\tfor (p = SG(rfc1867_uploaded_files)->pListHead; p; p = p->pListNext) {\n"
    "\t\tif (p->nKeyLength) {\n"
    "\t\t\tVCWD_UNLINK(p->arKey);\n"
    "\t\t}\n"
    "\t}\n"
    "}\n"
    "/* }}} */\n"
    "\n"
)
s = s.replace(anchor, func + anchor, 1)
write(p, s)

# 4) count every multipart part, not only parts with Content-Disposition
p = os.path.join(root, "main/rfc1867.c")
s = read(p)
old = (
    "\t\tif ((cd = php_mime_get_hdr_value(header, \"Content-Disposition\"))) {\n"
    "\t\t\tchar *pair = NULL;\n"
    "\t\t\tint end = 0;\n"
    "\n"
    "\t\t\tif (--body_parts_cnt < 0) {\n"
    "\t\t\t\tsapi_module.sapi_error(E_WARNING, \"Multipart body parts limit exceeded %d. To increase the limit change max_multipart_body_parts in php.ini.\", body_parts_limit);\n"
    "\t\t\t\tgoto fileupload_done;\n"
    "\t\t\t}\n"
)
new = (
    "\t\tif (--body_parts_cnt < 0) {\n"
    "\t\t\tsapi_module.sapi_error(E_WARNING, \"Multipart body parts limit exceeded %d. To increase the limit change max_multipart_body_parts in php.ini.\", body_parts_limit);\n"
    "\t\t\tgoto fileupload_done;\n"
    "\t\t}\n"
    "\n"
    "\t\tif ((cd = php_mime_get_hdr_value(header, \"Content-Disposition\"))) {\n"
    "\t\t\tchar *pair = NULL;\n"
    "\t\t\tint end = 0;\n"
)
assert s.count(old) == 1, "rfc1867 counter anchor not found"
s = s.replace(old, new)
write(p, s)

print("v2 edits applied to", root)
