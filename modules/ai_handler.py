import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class AIHandler:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')

        if api_key:
            self.client = genai.Client(api_key=api_key)  # Should work
            self.model = 'gemini-2.0-flash-exp'
            print("✅ Gemini AI connected")
        else:
            self.client = None
            self.model = None
            print("⚠️ AI disabled")

            print("DEBUG: AIHandler initialized")

    def generate_command(self, user_input, current_dir):
    """Use Gemini to generate command from natural language"""
    if not self.client:
        return None
    
    prompt = f"""You are a Linux terminal command generator.
Convert this natural language request into a single, safe Linux terminal command.

User request: "{user_input}"
Current directory: {current_dir}

Rules:
- Return ONLY the command, no explanation
- If the request is unclear or dangerous, return "UNSAFE" or "UNCLEAR"
- Use common Linux tools (ls, cd, find, grep, etc.)
- Prefer safe, non-destructive commands

Command:"""

    try:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        
        command = response.text.strip()
        command = command.replace('```bash', '').replace('```', '').replace('`', '').strip()
        
        if command.upper() in ['UNSAFE', 'UNCLEAR']:
            return None
        
        return command
        
    except Exception as e:
        print(f"❌ AI Error: {e}")
        return None
