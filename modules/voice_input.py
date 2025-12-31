import speech_recognition as sr

class VoiceInput:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def listen(self):
        """Listen for voice input and convert to text"""
        with sr.Microphone() as source:
            print("🎤 Listening... (speak clearly)")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("🔄 Processing...")
                
                text = self.recognizer.recognize_google(audio, language='en-US', show_all=False)
                print(f"📝 Heard: '{text}'")
                return text.lower()
                
            except sr.WaitTimeoutError:
                print("⏱️ Timeout")
                return None
            except sr.UnknownValueError:
                print("❌ Could not understand")
                return None
            except Exception as e:
                print(f"❌ Error: {e}")
                return None
