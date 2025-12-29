import subprocess
import os
from pathlib import Path

class VoiceShell:
    def __init__(self):
        self.current_dir = Path.cwd()
        
    def execute_command(self, command):
        """Execute a shell command safely"""
        try:
            # Change to current directory context
            os.chdir(self.current_dir)
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Update current directory (in case cd was used)
            self.current_dir = Path.cwd()
            
            # Return output
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
            'rm -rf',
            'sudo rm',
            'mkfs',
            '> /dev/',
            'dd if=',
            'chmod -R 777',
            ':(){:|:&};:'  # Fork bomb
        ]
        return any(pattern in command.lower() for pattern in dangerous_patterns)
    
    def run(self):
        """Main application loop"""
        print("🚀 VoiceShell - Terminal Voice Agent")
        print("=" * 50)
        print("Current directory:", self.current_dir)
        print("\nType 'exit' to quit\n")
        
        while True:
            # Get user input
            user_input = input("🎤 You: ").strip()
            
            if user_input.lower() == 'exit':
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # For now, treat input as direct command
            # We'll add pattern matching next
            command = user_input
            
            # Safety check
            if self.is_dangerous_command(command):
                confirm = input(f"⚠️  Dangerous command detected: '{command}'\nContinue? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("❌ Command cancelled")
                    continue
            
            # Execute
            print(f"⚙️  Executing: {command}")
            result = self.execute_command(command)
            
            if result['success']:
                if result['output']:
                    print(result['output'])
                print("✅ Done")
            else:
                print(f"❌ Error: {result['error']}")
            
            print()

if __name__ == "__main__":
    agent = VoiceShell()
    agent.run()
