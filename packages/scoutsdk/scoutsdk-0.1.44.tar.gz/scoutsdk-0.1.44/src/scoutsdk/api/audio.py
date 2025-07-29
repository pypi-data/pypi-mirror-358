from typing import Optional

import requests


class AudioAPI:
    def __init__(self, base_url: str, headers: dict) -> None:
        self._base_url = base_url
        self._headers = headers

    def text_to_speech(
        self,
        text: str,
        model: Optional[str] = None,
        voice: Optional[str] = None,
        api_args: Optional[dict] = None,
    ) -> bytes:
        """
        Convert input text to speech audio using a specified model and voice.

        Args:
            text (str): The text to be converted to speech.
            model (Optional[str], optional): The speech synthesis model to use. Defaults to None.
            voice (Optional[str], optional): The voice profile to use for speech. Defaults to None.
            api_args (Optional[dict], optional): Additional API arguments for customization. Defaults to None.

        Returns:
            bytes: The audio content generated from the text.
        """
        json_payload = {
            "text": text,
            **({"model": model} if model is not None else {}),
            **({"voice": voice} if voice is not None else {}),
            **({"api_args": api_args} if api_args is not None else {}),
        }

        response = requests.post(
            url=f"{self._base_url}/api/audio/speech",
            headers=self._headers,
            json=json_payload,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_message = "HTTP Error occurred"
            if e.response is not None:
                try:
                    error_details = e.response.json()
                    error_message = f"Error: {error_details}"
                except (ValueError, AttributeError):
                    # Handle cases where response is not valid JSON
                    error_message = f"Error: HTTP {e.response.status_code} - {e.response.text or 'No response text'}"
            else:
                # Handle cases where e.response is None
                error_message = f"Error: {str(e)}"

            raise Exception(error_message) from e

        return response.content
