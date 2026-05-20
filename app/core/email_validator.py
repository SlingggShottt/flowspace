import dns.resolver
import re


def is_valid_email_format(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def check_email_domain_exists(email: str) -> tuple[bool, str]:
    if not is_valid_email_format(email):
        return False, "Invalid email format"

    domain = email.split('@')[1]

    try:
        dns.resolver.resolve(domain, 'MX')
        return True, "Email domain is valid"
    except dns.resolver.NXDOMAIN:
        return False, f"Domain {domain} does not exist"
    except dns.resolver.NoAnswer:
        try:
            dns.resolver.resolve(domain, 'A')
            return True, "Email domain is valid"
        except Exception:
            return False, f"Domain {domain} has no mail server"
    except Exception:
        return True, "Could not verify domain, proceeding anyway"