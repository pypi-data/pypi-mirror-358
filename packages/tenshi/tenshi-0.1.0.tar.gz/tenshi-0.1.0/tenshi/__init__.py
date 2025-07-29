import requests
import random

class TenshiError(Exception):
    pass

class APIKeyError(TenshiError):
    def __init__(self, key, original_exception):
        self.key = key
        self.original_exception = original_exception
        super().__init__(f"API key '{key}' failed: {original_exception}")

class RateLimitError(TenshiError):
    pass

class InvalidResponseError(TenshiError):
    pass

class Tenshi:
    def __init__(self, api_keys, model="gemini-2.0-flash", temperature=0.7, top_p=1.0, timeout=10):
        if isinstance(api_keys, str):
            api_keys = [api_keys]
        if not api_keys:
            raise ValueError("At least one API key is required.")
        self.api_keys = api_keys
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        self.headers = {"Content-Type": "application/json"}
        self.system_prompt = None
        self.temperature = temperature
        self.top_p = top_p
        self.timeout = timeout

    def set_system(self, prompt: str):
        self.system_prompt = prompt

    def _build_contents(self, user_prompt: str):
        parts = []
        if self.system_prompt:
            parts.append({"text": self.system_prompt})
        parts.append({"text": user_prompt})
        return [{"parts": parts}]

    def generate(self, prompt: str) -> str:
        if not prompt:
            raise ValueError("Prompt cannot be empty.")
    
        body = {    
            "contents": self._build_contents(prompt),
            "generationConfig": {
                "temperature": self.temperature,
                "topP": self.top_p
            }
        }

        keys_to_try = self.api_keys[:]
        random.shuffle(keys_to_try)

        errors = []
        for key in keys_to_try:
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    params={"key": key},    
                    json=body,
                    timeout=self.timeout
                )
                if response.status_code == 429:
                    raise RateLimitError(f"Rate limit exceeded for API key: {key}")

                response.raise_for_status()

                data = response.json()
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError) as err:
                    raise InvalidResponseError(f"Unexpected response structure: {err}")

            except (requests.RequestException, RateLimitError, InvalidResponseError) as e:
                errors.append(APIKeyError(key, e))

        combined_errors = "; ".join(str(err) for err in errors)
        raise TenshiError(f"All API keys failed. Details: {combined_errors}")



# made for multiple api key systme so you can fix free version issue or ratelimiting issue