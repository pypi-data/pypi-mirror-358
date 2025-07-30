import os
from huggingface_hub import InferenceClient
from syn_data_csv.adapters.base import BaseChatAdapter

class HuggingFaceChatAdapter(BaseChatAdapter):
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
        self.client = InferenceClient(
            token=self.api_key,
        )

    def generate(self, prompt):
        # Use chat API if the model supports chat (like Mixtral)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return response.choices[0].message["content"]
