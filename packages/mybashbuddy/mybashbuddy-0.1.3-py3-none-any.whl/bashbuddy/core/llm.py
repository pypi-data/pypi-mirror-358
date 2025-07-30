import os
import google.generativeai as genai

class GeminiLLM:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("\n" + "="*60)
            print("🚀 Welcome to BashBuddy!")
            print("="*60)
            print("❌ GEMINI_API_KEY environment variable not set.")
            print("\n📋 To get started:")
            print("1. Get your API key from: https://makersuite.google.com/app/apikey")
            print("2. Set it as an environment variable:")
            print("   • Windows CMD: set GEMINI_API_KEY=your_api_key_here")
            print("   • Windows PowerShell: $env:GEMINI_API_KEY='your_api_key_here'")
            print("   • Linux/Mac: export GEMINI_API_KEY=your_api_key_here")
            print("\n💡 For permanent setup:")
            print("   • Windows: Add to System Environment Variables")
            print("   • Linux/Mac: Add to ~/.bashrc or ~/.zshrc")
            print("\n🔗 More info: https://github.com/yourusername/mybashbuddy")
            print("="*60)
            raise EnvironmentError("GEMINI_API_KEY environment variable not set. Please follow the instructions above.")
        
        genai.configure(api_key=api_key)
        
        # Try different models in order of preference
        self.model = self._initialize_model()
    
    def _initialize_model(self):
        """Try different Gemini models and return the first working one."""
        models_to_try = [
            "gemini-2.0-flash-exp",  # Latest experimental
            "gemini-2.0-flash",      # Stable flash model
            "gemini-1.5-flash",      # Previous flash model
            "gemini-1.5-pro",        # Pro model
            "gemini-pro",            # Original pro model
        ]
        
        for model_name in models_to_try:
            try:
                print(f"🔄 Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                # Test the model with a simple prompt
                test_response = model.generate_content("Hello")
                print(f"✅ Successfully connected to model: {model_name}")
                return model
            except Exception as e:
                print(f"❌ Model {model_name} not available: {str(e)[:100]}...")
                continue
        
        # If no models work, provide helpful error message
        print("\n" + "="*60)
        print("❌ No compatible Gemini models found!")
        print("="*60)
        print("💡 This could be due to:")
        print("   • API key doesn't have access to any Gemini models")
        print("   • API key is invalid or expired")
        print("   • Network connectivity issues")
        print("   • Google AI API service is down")
        print("\n🔧 Troubleshooting:")
        print("1. Check your API key at: https://makersuite.google.com/app/apikey")
        print("2. Ensure you have access to Gemini models")
        print("3. Try regenerating your API key")
        print("4. Check your internet connection")
        print("="*60)
        raise Exception("No compatible Gemini models found. Please check your API key and model access.")

    def generate(self, prompt, **kwargs):
        response = self.model.generate_content(prompt, **kwargs)
        return response.text 