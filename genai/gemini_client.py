import os
import json
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
import config

class GeminiClient:
    """
    Wrapper around the Google Gemini Generative AI Python SDK.
    """
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        if not self.api_key or self.api_key == "your_key_here":
            raise ValueError("GEMINI_API_KEY not found. Add it to your .env file.")
            
        genai.configure(api_key=self.api_key)
        self.model_name = config.GEMINI_MODEL
        print(f"GenAI [Client]: Configured Gemini Client using model {self.model_name}")

    def _call_with_retry(self, model, prompt: str, generation_config: dict) -> str:
        """
        Executes model.generate_content with rate-limit retries and exponential backoff.
        """
        retries = 2
        wait_time = 2.0
        for attempt in range(retries + 1):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                return response.text
            except (ResourceExhausted, GoogleAPIError) as e:
                if attempt < retries:
                    print(f"GenAI [Client]: Rate limit or API error ({e}). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    wait_time *= 2.0
                else:
                    raise e

    def generate_json(self, system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> dict:
        """
        Sends system and user prompt to Gemini and returns a parsed JSON dictionary.
        Implements rate-limit retries with backoff and one JSON parsing retry.

        Parameters:
            system_prompt (str): System configuration rules/role.
            user_prompt (str): Input prompt containing data payload.
            max_tokens (int): Max response length. Defaults to 1024.

        Returns:
            dict: Parsed JSON response.
        """
        # Create model instance with system instruction
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt
        )
        
        # Generation configuration forcing JSON output format
        generation_config = {
            "response_mime_type": "application/json",
            "max_output_tokens": max_tokens,
            "temperature": 0.3
        }

        # First generation attempt
        raw_text = self._call_with_retry(model, user_prompt, generation_config)
        
        try:
            return self._parse_json(raw_text)
        except (json.JSONDecodeError, ValueError) as first_err:
            print("GenAI [Client]: First JSON parse attempt failed. Retrying with explicit prompt instruction...")
            # Append correction instruction to user prompt for the retry
            retry_prompt = (
                f"{user_prompt}\n\n"
                "Your previous response was not valid JSON. "
                "Return ONLY the JSON object, no markdown, no explanation."
            )
            raw_text_retry = self._call_with_retry(model, retry_prompt, generation_config)
            try:
                return self._parse_json(raw_text_retry)
            except Exception as second_err:
                raise ValueError(
                    f"Failed to generate valid JSON after 2 attempts. "
                    f"First error: {first_err}. Second error: {second_err}. "
                    f"Raw response: {raw_text_retry}"
                )

    def _parse_json(self, text: str) -> dict:
        """
        Cleans markdown wrappers and loads json.
        """
        text_clean = text.strip()
        # Remove markdown code fences if present
        if text_clean.startswith("```"):
            lines = text_clean.split("\n")
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            text_clean = "\n".join(lines).strip()
            
        return json.loads(text_clean)

    def generate_text(self, system_prompt: str, user_prompt: str, max_tokens: int = 512) -> str:
        """
        Sends prompts to Gemini for plain text generation (e.g. executive summary).

        Parameters:
            system_prompt (str): System instruction.
            user_prompt (str): Content prompt.
            max_tokens (int): Max response length. Defaults to 512.

        Returns:
            str: Generated text.
        """
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt
        )
        
        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": 0.3
        }
        
        raw_text = self._call_with_retry(model, user_prompt, generation_config)
        return raw_text.strip()
