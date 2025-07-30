import os
import google.generativeai as genai

class GeminiLLM:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        
        # Use the specific model the user has access to
        try:
            self.model = genai.GenerativeModel("gemini-2.0-flash")
            # Test the model with a simple prompt
            test_response = self.model.generate_content("Hello")
            print(f"Successfully connected to model: gemini-2.0-flash")
        except Exception as e:
            raise Exception(f"Could not connect to gemini-2.0-flash model: {e}")

    def generate(self, prompt, **kwargs):
        response = self.model.generate_content(prompt, **kwargs)
        return response.text 