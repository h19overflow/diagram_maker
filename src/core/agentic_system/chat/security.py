"""
Security validation for chat agent.

Protects against:
- Prompt injection attacks
- Code-based attacks
- System prompt exposure attempts
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


# Prompt injection patterns
PROMPT_INJECTION_PATTERNS = [
    # Direct instruction override
    r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|rules|directions)",
    r"disregard\s+(all\s+)?(previous|above|prior)?\s*(instructions|prompts|rules|directions)",
    r"forget\s+(all\s+)?(your\s+)?(previous|above|prior)?\s*(instructions|prompts|rules|guidelines)",
    r"override\s+(all\s+)?(previous|system|prior)\s+(instructions|prompts|rules)",
    # Role-playing attacks
    r"you\s+are\s+now\s+(a\s+)?(?!a\s+helpful)",
    r"pretend\s+(you\s+are|to\s+be)",
    r"act\s+as\s+(if\s+)?(?:you\s+)?",
    r"roleplay\s+as",
    r"simulate\s+(being\s+)?(?:a\s+)?",
    # Delimiter injection
    r"---\s*end\s+(of\s+)?(instructions|prompt|system)",
    r"<\s*/\s*system\s*>",
    r"\[END\s+SYSTEM\]",
    r"```\s*system",
    # DAN (Do Anything Now) variants
    r"DAN\s+mode",
    r"developer\s+mode",
    r"jailbreak",
    r"you\s+can\s+do\s+anything\s+now",
    # Instruction reveal attempts
    r"repeat\s+(your\s+)?(system\s+)?(instructions|prompt|rules)",
    r"what\s+(are|were)\s+your\s+(initial\s+)?(instructions|prompts|rules)",
    r"show\s+me\s+your\s+(system\s+)?(prompt|instructions|rules)",
    r"tell\s+me\s+your\s+(system\s+)?(prompt|instructions|rules)",
    r"print\s+(your\s+)?(system\s+)?(prompt|instructions|rules)",
    r"output\s+(your\s+)?(system\s+)?(prompt|instructions|rules)",
]

# Code injection patterns
CODE_INJECTION_PATTERNS = [
    # SQL injection
    r"(?:union\s+select|select\s+.+\s+from|insert\s+into|update\s+.+\s+set|delete\s+from|drop\s+table|create\s+table|alter\s+table)",
    r"';?\s*(?:drop|delete|truncate)\s+table",
    r"(?:or|and)\s+['\"]?1['\"]?\s*=\s*['\"]?1",
    # Command injection
    r"(?:;|\||&|`|\$\()\s*(?:ls|cat|rm|chmod|curl|wget|bash|sh|python|eval|exec)",
    r"(?:ls|cat|rm|grep|chmod|curl|wget)\s+[\-/]",
    r"(?:system|shell_exec|passthru|exec|popen)\s*\(",
    # XSS
    r"<\s*script[^>]*>",
    r"javascript\s*:",
    r"on(?:load|error|click|mouse)\s*=",
    # Path traversal
    r"\.\./",
    r"\.\.\\",
    # Code execution
    r"__import__\s*\(",
    r"eval\s*\(",
    r"exec\s*\(",
    r"compile\s*\(",
]

# System prompt exposure patterns
SYSTEM_PROMPT_EXPOSURE_PATTERNS = [
    r"what\s+(is|are)\s+your\s+(base|core|system|initial)\s+(prompt|instruction)",
    r"show\s+(me\s+)?(?:your\s+)?(?:system\s+)?(?:prompt|instruction|rule)",
    r"reveal\s+(?:your\s+)?(?:system\s+)?(?:core\s+)?(?:prompt|instruction|rule)",
    r"describe\s+your\s+(?:system\s+)?(?:prompt|instruction|rule|guideline)",
    r"copy\s+(?:and\s+)?paste\s+your\s+(?:system\s+)?(?:prompt|instruction)",
    r"verbatim\s+(?:of\s+)?your\s+(?:system\s+)?(?:prompt|instruction)",
    r"(?:exact|actual)\s+(?:text|words|wording)\s+(?:of\s+)?(?:your\s+)?(?:base\s+)?(?:prompt|instruction)",
    r"tell\s+me\s+the\s+(?:exact|actual)\s+(?:text|words)",
]


def check_patterns(text: str, patterns: List[str]) -> Tuple[bool, List[str]]:
    """Check text against a list of regex patterns.

    Args:
        text: The text to check
        patterns: List of regex patterns

    Returns:
        Tuple of (is_detected, list_of_matched_patterns)
    """
    text_lower = text.lower()
    matches = []

    for pattern in patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            matches.append(pattern)

    return len(matches) > 0, matches


def validate_security(query: str) -> Dict[str, any]:
    """Validate query for security threats.

    Args:
        query: The user query to validate

    Returns:
        dict with validation results
    """
    if not query or len(query.strip()) == 0:
        return {"is_safe": True, "threat_type": None, "details": None}

    # Check for prompt injection
    is_injection, injection_matches = check_patterns(
        query, PROMPT_INJECTION_PATTERNS
    )
    if is_injection:
        logger.warning(
            f"Prompt injection detected. Matches: {len(injection_matches)}"
        )
        return {
            "is_safe": False,
            "threat_type": "prompt_injection",
            "details": f"Detected {len(injection_matches)} injection pattern(s)",
        }

    # Check for code injection
    is_code_attack, code_matches = check_patterns(query, CODE_INJECTION_PATTERNS)
    if is_code_attack:
        logger.warning(f"Code injection detected. Matches: {len(code_matches)}")
        return {
            "is_safe": False,
            "threat_type": "code_injection",
            "details": f"Detected {len(code_matches)} code attack pattern(s)",
        }

    # Check for system prompt exposure attempts
    is_exposure, exposure_matches = check_patterns(
        query, SYSTEM_PROMPT_EXPOSURE_PATTERNS
    )
    if is_exposure:
        logger.warning(
            f"System prompt exposure attempt detected. Matches: {len(exposure_matches)}"
        )
        return {
            "is_safe": False,
            "threat_type": "system_prompt_exposure",
            "details": f"Detected {len(exposure_matches)} exposure attempt(s)",
        }

    # Additional heuristics
    # Check for excessive special characters (potential obfuscation)
    special_char_ratio = sum(
        1 for c in query if not c.isalnum() and not c.isspace()
    ) / len(query)
    if special_char_ratio > 0.3:
        logger.warning(f"High special character ratio: {special_char_ratio:.2f}")
        return {
            "is_safe": False,
            "threat_type": "obfuscation_attempt",
            "details": f"High special character ratio: {special_char_ratio:.2f}",
        }

    # Check for suspicious encoding attempts
    suspicious_encodings = [
        r"&#\d+;",  # HTML entities
        r"%[0-9a-f]{2}",  # URL encoding
        r"\\x[0-9a-f]{2}",  # Hex encoding
        r"\\u[0-9a-f]{4}",  # Unicode escapes
    ]
    is_encoded, _ = check_patterns(query, suspicious_encodings)
    if is_encoded:
        logger.warning("Suspicious encoding detected")
        return {
            "is_safe": False,
            "threat_type": "encoding_attack",
            "details": "Suspicious encoding patterns detected",
        }

    return {"is_safe": True, "threat_type": None, "details": None}


def get_security_error_message(threat_type: str) -> str:
    """Get user-friendly error message for security threat.

    Args:
        threat_type: The type of security threat detected

    Returns:
        str: User-friendly error message
    """
    messages = {
        "prompt_injection": "I cannot process this request as it appears to contain instructions that conflict with my operation guidelines. Please rephrase your question about the documentation.",
        "code_injection": "I detected potentially unsafe code patterns in your query. Please ask questions in plain language about the documentation.",
        "system_prompt_exposure": "I cannot share internal instructions or system prompts. I'm here to answer questions about the documentation. How can I help you with that?",
        "obfuscation_attempt": "Your query contains unusual patterns. Please ask your question in plain language.",
        "encoding_attack": "I detected encoded content in your query. Please ask your question in plain text.",
    }

    return messages.get(
        threat_type,
        "I cannot process this request due to security concerns. Please rephrase your question about the documentation.",
    )
