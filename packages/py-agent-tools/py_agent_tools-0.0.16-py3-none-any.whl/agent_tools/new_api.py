import asyncio
import json
from enum import Enum
from typing import Any, Dict, Optional

import httpx

from agent_tools.settings import agent_settings


class NewAPIModelName(str, Enum):
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_PRO_THINKING = "gemini-2.5-pro-thinking"


class NewAPIGenmini:
    def __init__(self, model_name: NewAPIModelName):
        self.model_name = model_name.value
        self.base_url = agent_settings.new_api.base_url
        self.api_key = agent_settings.new_api.key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_content(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate content using the NewAPI Gemini model.

        Args:
            prompt: The text prompt to send to the model
            temperature: Controls randomness in the response (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters to pass to the API

        Returns:
            Dictionary containing the API response
        """
        url = f"{self.base_url}/v1beta/models/{self.model_name}:generateContent"

        # Prepare the request payload
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "system",
                    "parts": [{"text": system_prompt}],
                },
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                },
            ]
        }

        # Add optional parameters
        if temperature is not None or max_tokens is not None or kwargs:
            payload["generationConfig"] = {}

        if temperature is not None:
            payload["generationConfig"]["temperature"] = temperature

        if max_tokens is not None:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens

        # Add any additional kwargs to generationConfig
        if kwargs:
            payload["generationConfig"].update(kwargs)

        async with httpx.AsyncClient(timeout=600) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload,
                params={"key": self.api_key} if self.api_key else {},
            )

            response.raise_for_status()
            return response.json()

    def generate_content_sync(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Synchronous version of generate_content.

        Args:
            prompt: The text prompt to send to the model
            temperature: Controls randomness in the response (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters to pass to the API

        Returns:
            Dictionary containing the API response
        """
        return asyncio.run(self.generate_content(prompt, temperature, max_tokens, **kwargs))


if __name__ == "__main__":
    print(agent_settings.new_api.key)
    print(agent_settings.new_api.base_url)

    # Example usage
    async def test_api():
        gemini = NewAPIGenmini(NewAPIModelName.GEMINI_2_5_FLASH)
        try:
            response = await gemini.generate_content("Write a story about a magic backpack.")
            print("Response:", json.dumps(response, indent=2))
        except Exception as e:
            print(f"Error: {e}")

    # Run the test if API key is available
    if agent_settings.new_api.key:
        asyncio.run(test_api())
    else:
        print("No API key found. Set NEW_API_KEY environment variable.")
