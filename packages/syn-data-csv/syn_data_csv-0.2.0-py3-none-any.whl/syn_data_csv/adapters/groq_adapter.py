from groq import Groq, GroqError
from syn_data_csv.adapters.base import BaseChatAdapter

class GroqChatAdapter(BaseChatAdapter):

    def generate(self, prompt):
        try:

            client = Groq(api_key=self.api_key)
            messages = [{"role": "user", "content": prompt}]
            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=1,
                max_tokens=6000,
                top_p=1,
                stream=True
            )
            response = ""
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    response += chunk.choices[0].delta.content
            return response.strip()

        except GroqError as e:
            error_msg = getattr(e, 'message', str(e))

            if "Internal Server Error" in error_msg or "500" in error_msg:
                print("❌ Groq API Error: Internal Server Error encountered.")
                print("🔁 Please try again later or select a different model (e.g., 'llama3-70b-8192').")
            else:
                print(f"❌ Groq API Error: {error_msg}")

            raise
