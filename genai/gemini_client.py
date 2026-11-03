import os
import json
import time
import re
import logging
from typing import Optional, Type, TypeVar, Tuple, Any
from pydantic import BaseModel, ValidationError
from google import genai
from google.genai import types
from google.genai.errors import APIError
import config
from genai.schemas import GeminiRecommendationBatchResponse, GeminiRecommendationItem

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger("clara.genai.gemini_client")

def sanitize_text(text: str, secret: Optional[str] = None) -> str:
    """
    Removes any sensitive tokens or secrets from logged text.
    """
    if not text:
        return ""
    if secret and len(secret) > 4:
        text = text.replace(secret, "[REDACTED_API_KEY]")
    # Redact common Gemini API key patterns
    text = re.sub(r'AIzaSy[A-Za-z0-9_-]{10,}', '[REDACTED_API_KEY]', text)
    return text

def classify_error(err: Exception) -> str:
    """
    Categorizes errors into safe, discrete failure classifications:
    - 'missing_api_key'
    - 'auth_error'
    - 'quota_exceeded'
    - 'timeout'
    - 'schema_validation_error'
    - 'api_error'
    """
    if isinstance(err, (ValidationError, json.JSONDecodeError)):
        return "schema_validation_error"

    err_str = str(err).lower()
    code = getattr(err, "code", None)

    if code in (401, 403) or any(k in err_str for k in ("unauthenticated", "permission_denied", "api_key_invalid", "api key not valid", "invalid api key")):
        return "auth_error"
    if code == 429 or any(k in err_str for k in ("resource_exhausted", "quota", "rate limit", "too many requests")):
        return "quota_exceeded"
    if any(k in err_str for k in ("timeout", "timed out", "deadline exceeded")):
        return "timeout"
    if "api key" in err_str and "not found" in err_str:
        return "missing_api_key"

    return "api_error"

class GeminiClient:
    """
    Production-ready wrapper around Google GenAI Python SDK (google-genai).
    Supports structured output enforcement, bounded retry with backoff,
    safe error categorization, and key redaction.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        raw_key = api_key if api_key is not None else os.environ.get("GEMINI_API_KEY", getattr(config, "GEMINI_API_KEY", None))
        
        if not raw_key or raw_key.strip() in ("", "your_key_here", "dummy_key", "None"):
            self.api_key = None
            self.client = None
            self.is_configured = False
        else:
            self.api_key = raw_key.strip()
            self.is_configured = True
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai Client: {sanitize_text(str(e), self.api_key)}")
                self.client = None
                self.is_configured = False

        self.model_name = model_name or os.environ.get("GEMINI_MODEL", getattr(config, "GEMINI_MODEL", "gemini-3.8-flash"))

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Type[T] = GeminiRecommendationBatchResponse,
        max_retries: int = 2,
        initial_backoff: float = 1.5,
    ) -> Tuple[Optional[T], Optional[str]]:
        """
        Invokes Gemini using google-genai structured output enforcement with bounded retries.
        
        Returns:
            Tuple[Optional[T], Optional[str]]: (parsed_pydantic_model, error_category)
            If successful, (model, None).
            If failed, (None, error_category).
        """
        if not self.is_configured or self.client is None:
            return None, "missing_api_key"

        generation_config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.2,
        )

        backoff = initial_backoff
        last_error: Optional[Exception] = None

        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=generation_config
                )

                # Attempt 1: response.parsed from google-genai
                if hasattr(response, "parsed") and response.parsed is not None:
                    if isinstance(response.parsed, response_schema):
                        return response.parsed, None
                    try:
                        # In case parsed is a dict
                        validated = response_schema.model_validate(response.parsed)
                        return validated, None
                    except Exception:
                        pass

                # Attempt 2: response.text parsed via Pydantic model_validate_json
                raw_text = getattr(response, "text", "") or ""
                if not raw_text.strip():
                    raise ValueError("Gemini returned empty text response")

                # Strip possible markdown fences if SDK returned unparsed string
                clean_text = raw_text.strip()
                if clean_text.startswith("```"):
                    lines = clean_text.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    clean_text = "\n".join(lines).strip()

                parsed = response_schema.model_validate_json(clean_text)
                return parsed, None

            except Exception as e:
                last_error = e
                category = classify_error(e)
                # Retry only on transient rate limits (quota_exceeded), timeouts, or server errors
                if attempt < max_retries and category in ("quota_exceeded", "timeout", "api_error"):
                    safe_msg = sanitize_text(str(e), self.api_key)
                    logger.warning(f"Gemini call attempt {attempt + 1} failed ({category}: {safe_msg}). Retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    break

        error_category = classify_error(last_error) if last_error else "api_error"
        logger.error(f"Gemini generation failed: {error_category}")
        return None, error_category

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_retries: int = 2,
        initial_backoff: float = 1.0,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Plain text generation for narrative summaries.
        
        Returns:
            Tuple[Optional[str], Optional[str]]: (text, error_category)
        """
        if not self.is_configured or self.client is None:
            return None, "missing_api_key"

        generation_config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
        )

        backoff = initial_backoff
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=generation_config
                )
                text = getattr(response, "text", "")
                if text:
                    return text.strip(), None
                return None, "api_error"
            except Exception as e:
                last_error = e
                category = classify_error(e)
                if attempt < max_retries and category in ("quota_exceeded", "timeout", "api_error"):
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    break

        error_category = classify_error(last_error) if last_error else "api_error"
        return None, error_category
