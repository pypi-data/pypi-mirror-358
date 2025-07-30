import requests
from typing import List, Optional, Dict, Any

class TNSAClient:
    """
    Python SDK for accessing TNSA AI models via API tokens.
    Usage:
        client = TNSAClient(api_key="YOUR_API_KEY")
        models = client.list_models()
        result = client.infer(model="NGen3-7B-0625", prompt="Hello!")
    """
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "x-api-key": self.api_key
        }

    def list_models(self) -> List[str]:
        """List available models."""
        response = requests.get(f"{self.base_url}/models", headers=self.headers)
        response.raise_for_status()
        return response.json().get("models", [])

    def infer(
        self,
        model: str,
        prompt: str,
        history: Optional[List[Dict[str, Any]]] = None,
        format: str = "html",
        chat_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run inference on a model.
        Args:
            model: Model name (from list_models)
            prompt: User prompt
            history: Optional chat history (list of {role, content})
            format: 'html' or 'text'
            chat_id: Optional chat session id
        Returns:
            Dict with response, tokens, cost, etc.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "format": format
        }
        if isinstance(history, list) and all(isinstance(item, dict) for item in history):
            payload["history"] = history  # type: ignore
        if chat_id:
            payload["chat_id"] = chat_id
        response = requests.post(
            f"{self.base_url}/infer",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        try:
            return response.json()
        except Exception as e:
            print('Raw response from server:', response.text)
            raise RuntimeError(f'Failed to decode JSON response: {e}')

# Example usage
if __name__ == "__main__":
    client = TNSAClient(api_key="YOUR_API_KEY")
    print("Available models:", client.list_models())
    result = client.infer(model="NGen3-7B-0625", prompt="What is AI?")
    print("Response:", result["response"])