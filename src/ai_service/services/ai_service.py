import logging


class AIService:
    """Application service containing the Week 04 demo logic."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def classify(self, text: str) -> dict[str, str]:
        """Classify input text using simple keyword rules."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty.")

        normalized_text = text.lower()
        self.logger.info("Classifying text")

        if "password" in normalized_text:
            category = "account"
        elif "fee" in normalized_text or "payment" in normalized_text:
            category = "finance"
        elif (
            "server" in normalized_text
            or "api" in normalized_text
            or "error" in normalized_text
        ):
            category = "technical"
        elif "admission" in normalized_text:
            category = "admission"
        elif "lab" in normalized_text or "classroom" in normalized_text:
            category = "facilities"
        else:
            category = "other"

        self.logger.info("Classification completed: %s", category)
        return {"text": text, "category": category}
