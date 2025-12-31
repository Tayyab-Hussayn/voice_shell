import subprocess
from modules.voice_input import VoiceInput
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class VoiceShell:
    def __init__(self):
        self.current_dir = Path.cwd()
        self.command_patterns = self.load_patterns()
        self.voice = VoiceInput() 
        # Setup Gemini with NEW API
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            self.client = genai.Client(api_key=api_key)
            self.model = 'gemini-2.0-flash-exp'
            print("✅ Gemini AI connected")
        else:
            self.client = None
            self.model = None
            print("⚠️  Gemini API key not found - AI mode disabled")


    def load_patterns(self):
        """Load command patterns from JSON"""
        try:
            with open('command_patterns.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  command_patterns.json not found - pattern matching disabled")
            return {}
    
    def match_pattern(self, user_input):
        """Try to match user input to a known command pattern"""
        user_input = user_input.lower().strip()
        
        # Direct command match (exact)
        for category in self.command_patterns.values():
            for pattern, command in category.items():
                if user_input == pattern.lower():
                    return command
                
                # Partial match for commands with arguments
                if user_input.startswith(pattern.lower()):
                    # Extract argument (e.g., "make directory test" -> "mkdir test")
                    arg = user_input[len(pattern):].strip()
                    if arg:
                        return f"{command} {arg}"
                    return command
        
        return None
    
    def generate_command_with_ai(self, user_input):
        """Use Gemini to generate command from natural language"""
        if not self.client:
            return None
        
        prompt = f"""You are a Linux terminal command generator. 
Convert this natural language request into a single, safe Linux terminal command.

User request: "{user_input}"
Current directory: {self.current_dir}

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
            
            # Clean up common AI formatting issues
            command = command.replace('```bash', '').replace('```', '').replace('`', '').strip()
            
            if command.upper() in ['UNSAFE', 'UNCLEAR']:
                return None
            
            return command
            
        except Exception as e:
            print(f"❌ AI Error: {e}")
            return None
    
    def execute_command(self, command):
        """Execute a shell command safely"""
        try:
            os.chdir(self.current_dir)
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.current_dir = Path.cwd()
            
            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def is_dangerous_command(self, command):
        """Check if command is potentially dangerous"""
        dangerous_patterns = [
            'rm -rf /',
            'rm -rf /*',
            'sudo rm',
            'mkfs',
            '> /dev/',
            'dd if=',
            'chmod -R 777 /',
            ':(){:|:&};:',
            'sudo',
            'su ',
        ]
        
        cmd_lower = command.lower()
        return any(pattern in cmd_lower for pattern in dangerous_patterns)
    
    def process_input(self, user_input):
        """Main input processing pipeline"""
        print(f"\n🔍 Processing: '{user_input}'")
        
        # TIER 1: Pattern matching (fast)
        command = self.match_pattern(user_input)
        if command:
            print(f"⚡ Fast match: {command}")
            return command
        
        # TIER 2: AI generation (slower)
        if self.client:
            print("🤖 Asking AI...")
            command = self.generate_command_with_ai(user_input)
            if command:
                print(f"🧠 AI generated: {command}")
                return command
        
        # TIER 3: Assume it's a direct command
        print("📝 Treating as direct command")
        return user_input
    
    def run(self):
        print("\n" + "="*60)
        print("🚀 VoiceShell v0.3 - Voice Enabled")
        print("="*60)
        print(f"📁 Current directory: {self.current_dir}")
        print("\n💡 Press Enter to speak, or type 'exit' to quit\n")
    
        while True:
            # Choice: voice or text
            mode = input("Press ENTER for voice (or type command): ").strip()
            
            if mode.lower() == 'exit':
                print("👋 Goodbye!")
                break
            
            # Get input
            if mode == "":
                user_input = self.voice.listen() 
                if not user_input:
                    continue
                

            else:
                user_input = mode
        
            # Rest of code stays same
            command = self.process_input(user_input)
            
            if not command:
                print("❌ Could not understand request")
                continue
            
            if self.is_dangerous_command(command):
                print(f"⚠️  DANGEROUS: {command}")
                confirm = input("Continue? (yes): ")
                if confirm.lower() != 'yes':
                    print("❌ Cancelled")
                    continue
            
            print(f"⚙️  Executing: {command}")
            result = self.execute_command(command)
        
            print("\n" + "-"*60)
            if result['success']:
                if result['output']:
                    print(result['output'])
                print("✅ Done")
            else:
                print(f"❌ Error: {result['error']}")
            print("-"*60 + "\n")

if __name__ == "__main__":
    agent = VoiceShell()
    agent.run()
