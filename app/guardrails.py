import re
import logging

logger = logging.getLogger(__name__)

# Questions shorter than this are probably not real questions
MIN_QUESTION_LENGTH = 5

# Questions longer than this are suspicious (possible prompt injection)
MAX_QUESTION_LENGTH = 500

# Keywords that signal prompt injection attempts
INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "you are now",
    "forget your instructions",
    "disregard your",
    "act as",
    "pretend you are",
    "system prompt",
    "jailbreak",
]

def validate_question(question: str) -> tuple[bool, str]:
    """
    Validates a question before sending it to the LLM.
    Returns (is_valid, error_message).
    If is_valid is True, error_message is empty.
    """

    # Check 1 — empty or whitespace only
    if not question or question.strip() == "":
        logger.warning("Guardrail triggered | reason=empty_question")
        return False, "Please enter a question."

    question = question.strip()

    # Check 2 — too short
    if len(question) < MIN_QUESTION_LENGTH:
        logger.warning(f"Guardrail triggered | reason=too_short | length={len(question)}")
        return False, "Your question is too short. Please be more specific."

    # Check 3 — too long
    if len(question) > MAX_QUESTION_LENGTH:
        logger.warning(f"Guardrail triggered | reason=too_long | length={len(question)}")
        return False, f"Your question is too long. Please keep it under {MAX_QUESTION_LENGTH} characters."

    # Check 4 — prompt injection detection
    question_lower = question.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in question_lower:
            logger.warning(f"Guardrail triggered | reason=injection_attempt | pattern={pattern}")
            return False, "Your question contains invalid content."

    # All checks passed
    return True, ""