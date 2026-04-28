import socket
import ssl
import urllib.request

import dns.resolver


def normalize_domain(email="", domain=""):
    domain = (domain or "").strip().lower()
    if domain:
        return domain.removeprefix("https://").removeprefix("http://").split("/")[0]

    email = (email or "").strip().lower()
    if "@" in email:
        return email.rsplit("@", 1)[1]

    return ""


def analyze_domain(domain):
    if not domain:
        return {
            "domain": "",
            "checks": [],
            "summary": "Add an email or domain to extract public security signals.",
        }

    checks = [
        _check_mx(domain),
        _check_spf(domain),
        _check_dmarc(domain),
        _check_https(domain),
        _check_security_headers(domain),
    ]
    passed = sum(1 for check in checks if check["status"] == "pass")

    return {
        "domain": domain,
        "checks": checks,
        "summary": f"{passed} of {len(checks)} public domain checks passed.",
    }


def analyze_email(email):
    email = (email or "").strip().lower()
    domain = normalize_domain(email=email)
    syntax_ok = _looks_like_email(email)
    domain_result = analyze_domain(domain) if domain else None

    checks = [
        {
            "key": "email_syntax",
            "label": "Email format",
            "status": "pass" if syntax_ok else "warn",
            "detail": "Email address format looks valid." if syntax_ok else "Enter a valid email address.",
        },
        {
            "key": "email_domain",
            "label": "Email domain",
            "status": "pass" if domain else "warn",
            "detail": domain or "No domain could be derived from the email.",
        },
    ]

    if domain_result:
        checks.extend(domain_result["checks"])

    passed = sum(1 for check in checks if check["status"] == "pass")

    return {
        "email": email,
        "domain": domain,
        "checks": checks,
        "summary": f"{passed} of {len(checks)} email identity checks passed.",
    }


def _looks_like_email(email):
    if not email or "@" not in email:
        return False

    local, domain = email.rsplit("@", 1)
    return bool(local and "." in domain and not domain.startswith(".") and not domain.endswith("."))


def _check_mx(domain):
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=4)
        hosts = [str(answer.exchange).rstrip(".") for answer in answers]
        return {
            "key": "mx",
            "label": "Mail servers found",
            "status": "pass",
            "detail": ", ".join(hosts[:3]),
        }
    except Exception:
        return {
            "key": "mx",
            "label": "Mail servers found",
            "status": "warn",
            "detail": "No MX records were found.",
        }


def _check_spf(domain):
    try:
        answers = dns.resolver.resolve(domain, "TXT", lifetime=4)
        records = ["".join(part.decode() for part in answer.strings) for answer in answers]
        spf = next((record for record in records if record.startswith("v=spf1")), "")
        return {
            "key": "spf",
            "label": "SPF record",
            "status": "pass" if spf else "warn",
            "detail": spf or "No SPF record was found.",
        }
    except Exception:
        return {
            "key": "spf",
            "label": "SPF record",
            "status": "warn",
            "detail": "No SPF record was found.",
        }


def _check_dmarc(domain):
    try:
        answers = dns.resolver.resolve(f"_dmarc.{domain}", "TXT", lifetime=4)
        records = ["".join(part.decode() for part in answer.strings) for answer in answers]
        dmarc = next((record for record in records if record.startswith("v=DMARC1")), "")
        return {
            "key": "dmarc",
            "label": "DMARC policy",
            "status": "pass" if dmarc else "warn",
            "detail": dmarc or "No DMARC policy was found.",
        }
    except Exception:
        return {
            "key": "dmarc",
            "label": "DMARC policy",
            "status": "warn",
            "detail": "No DMARC policy was found.",
        }


def _check_https(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=4) as sock:
            with context.wrap_socket(sock, server_hostname=domain):
                return {
                    "key": "https",
                    "label": "HTTPS reachable",
                    "status": "pass",
                    "detail": "A valid TLS connection was established.",
                }
    except Exception:
        return {
            "key": "https",
            "label": "HTTPS reachable",
            "status": "warn",
            "detail": "Could not establish a valid HTTPS connection.",
        }


def _check_security_headers(domain):
    try:
        request = urllib.request.Request(
            f"https://{domain}",
            method="HEAD",
            headers={"User-Agent": "SecureMe/0.1"},
        )

        with urllib.request.urlopen(request, timeout=6) as response:
            headers = {key.lower(): value for key, value in response.headers.items()}

        expected = {
            "strict-transport-security": "HSTS",
            "content-security-policy": "CSP",
            "x-frame-options": "X-Frame-Options",
            "x-content-type-options": "X-Content-Type-Options",
            "referrer-policy": "Referrer-Policy",
        }
        present = [label for header, label in expected.items() if header in headers]
        missing = [label for header, label in expected.items() if header not in headers]

        return {
            "key": "security_headers",
            "label": "Security headers",
            "status": "pass" if len(present) >= 3 else "warn",
            "detail": f"Present: {', '.join(present) or 'none'}. Missing: {', '.join(missing) or 'none'}.",
        }
    except Exception:
        return {
            "key": "security_headers",
            "label": "Security headers",
            "status": "warn",
            "detail": "Could not read HTTPS security headers.",
        }
