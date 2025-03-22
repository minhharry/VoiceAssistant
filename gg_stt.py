import speech_recognition as sr
from transformers import pipeline

def transcribe_vietnamese_realtime():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-medium")
    
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for Vietnamese speech...")
        
        while True:
            try:
                print("Say something...")
                audio = recognizer.listen(source)
                transcription = recognizer.recognize_google(audio, language="vi-VN")
                # transcription2 = transcriber(audio.get_wav_data())['text']
                
                print("(Google) You said:", transcription)
                # print("(Transformers) You said:", transcription2)
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError:
                print("Error with the recognition service")

if __name__ == "__main__":
    transcribe_vietnamese_realtime()
