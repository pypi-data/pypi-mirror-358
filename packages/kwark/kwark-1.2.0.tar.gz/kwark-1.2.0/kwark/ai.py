from anthropic import Anthropic

DEFAULT_MODEL = 'claude-3-5-sonnet-20241022'


class AI:  # pragma: nocover

    def __init__(self, api_key=None):
        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = Anthropic()

        # Fetch available models once during initialization
        self.available_models = self._fetch_available_models()

    def _fetch_available_models(self):
        """Fetch list of available Anthropic models"""
        try:
            response = self.client.models.list()
            models = []
            for model in response:
                models.append({
                    'id': model.id,
                    'display_name': getattr(model, 'display_name', model.id),
                    'created_at': getattr(model, 'created_at', None),
                })
            return models
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    def query(self, text, model=DEFAULT_MODEL):
        """Send a one-time query, no tools"""
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }

        ]
        message = self.client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=0,
            messages=messages)
        response = message.content[0].text
        return response
