import pyttsx3
from threading import Thread
from time import sleep

class VietnameseTextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.voice_id = self._find_vietnamese_voice()
    
    def _find_vietnamese_voice(self):
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'vietnam' in voice.name.lower() or 'viet' in voice.name.lower():
                return voice.id
        print("Vietnamese voice not found. Please install a Vietnamese voice pack for your OS.")
        return None
    
    def speak(self, text):
        if self.voice_id:
            self.engine.setProperty('voice', self.voice_id)
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            print("Cannot synthesize speech without a Vietnamese voice.")

if __name__ == "__main__":
    tts = VietnameseTextToSpeech()
    tts.speak("Xin chào! Đây là một đoạn văn bản được chuyển thành giọng nói Tiếng Việt.")
