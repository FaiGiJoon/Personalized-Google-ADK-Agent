import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger("CasperC2.Security")

def validate_snort_rule(rule: str) -> Dict[str, Any]:
    """
    Validates a Snort 3 rule for syntax and basic security issues.
    """
    issues = []

    # Basic syntax checks for Snort 3
    if not rule.startswith(("alert", "log", "pass", "drop", "reject", "rewrite")):
        issues.append("Rule must start with a valid action (e.g., 'alert').")

    if "(" not in rule or ")" not in rule:
        issues.append("Rule options must be enclosed in parentheses.")

    # Check for insecure or poorly performing patterns
    if "any any -> any any" in rule:
        issues.append("Broad rule detected ('any any -> any any'). Consider narrowing down IP/ports for performance and security.")

    if "content:\"" in rule:
        # Check for very short content matches
        contents = re.findall(r'content:"([^"]+)"', rule)
        for content in contents:
            if len(content) < 3:
                issues.append(f"Short content match found: '{content}'. This might lead to high false positive rates.")

    # Check for GID/SID
    if "sid:" not in rule:
        issues.append("Rule is missing an 'sid' (Signature ID).")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "rule": rule
    }

def check_quishing_threats(content: str) -> Dict[str, Any]:
    """
    Analyzes content for 'quishing' (QR code phishing) or linguistic threats.
    """
    threats = []

    # Linguistic triggers for quishing/phishing
    quishing_keywords = ["qr code", "scan to", "scan the code", "authenticate via qr"]
    phishing_keywords = ["urgent", "action required", "password reset", "verify your account"]

    content_lower = content.lower()

    for kw in quishing_keywords:
        if kw in content_lower:
            threats.append(f"Potential quishing trigger found: '{kw}'")

    for kw in phishing_keywords:
        if kw in content_lower:
            threats.append(f"Potential phishing linguistic trigger: '{kw}'")

    # Check for suspicious URLs or redirections (simplified)
    if re.search(r'https?://[^\s]+', content_lower):
        if "bit.ly" in content_lower or "tinyurl.com" in content_lower:
            threats.append("Shortened URL detected, which is common in quishing/phishing.")

    return {
        "threat_detected": len(threats) > 0,
        "threats": threats,
        "severity": "High" if "quishing" in str(threats).lower() else "Medium"
    }

# Export functions for tool wrapping in core/agent.py if needed
