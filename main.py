import torch
import torchaudio
import numpy as np
import pyaudio
from queue import Queue
from time import sleep, time
from transformers import pipeline
from ActionSelector import Action, LLMActionSelector
from VietnameseTextToSpeech import VietnameseTextToSpeech

class VoiceAssistant:
    def __init__(self, sample_rate=16000, chunk_size=512, speech_threshold=0.5, silence_timeout=1.0, pre_buffer_max=16):
        self.debug = False
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.speech_threshold = speech_threshold
        self.silence_timeout = silence_timeout 
        self.pre_buffer_max = pre_buffer_max 
        self.audio_queue = Queue()
        self.is_running = False
        self.recording = False
        self.audio_buffer = []  
        self.pre_buffer = []   
        self.last_speech_time = 0

        # Load Silero VAD model
        self.vad_model, utils = torch.hub.load('snakers4/silero-vad', 'silero_vad')
        self.get_speech_timestamps = utils[0]

        # Load PhoWhisper ASR model
        self.transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-medium")

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self.callback
        )

        # Initialize action selector
        self.action_lst = [
            Action("turn_on_light", "Turn on the light", "bật đèn", "bật đèn lên giúp tôi", "bật đèn"),
            Action("turn_off_light", "Turn off the light", "tắt đèn", "tắt đèn đi", "tắt đèn"),
            Action("turn_on_fan", "Turn on the fan", "bật quạt", "làm ơn mở quạt", "bật quạt"),
            Action("turn_off_fan", "Turn off the fan", "tắt quạt", "hãy tắt quạt ngay", "tắt quạt"),
        ]
        self.action_selector = LLMActionSelector(self.action_lst)

        self.tts = VietnameseTextToSpeech()

    def callback(self, in_data, frame_count, time_info, status):
        """Reads audio stream into a queue."""
        self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)

    def process_audio(self):
        """Processes audio and performs speech recognition when speech is detected."""
        while self.is_running:
            if not self.audio_queue.empty():
                audio_chunk = self.audio_queue.get()
                # Convert to normalized numpy array
                audio_np = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
                audio_tensor = torch.from_numpy(audio_np)

                # Compute speech probability
                speech_prob = self.vad_model(audio_tensor, self.sample_rate).item()

                if speech_prob > self.speech_threshold:
                    self.last_speech_time = time()  
                    if not self.recording:
                        print("Speech detected! Recording started...")
                        self.recording = True
                        self.audio_buffer = self.pre_buffer.copy()
                        self.pre_buffer = [] 
                elif (time() - self.last_speech_time) > self.silence_timeout:
                    self.recording = False

                if self.recording:
                    self.audio_buffer.append(audio_np)
                elif len(self.audio_buffer) >= 1:
                    print("Silence detected! Transcribing...")
                    self.transcribe_audio()
                    self.audio_buffer = []
                    self.recording = False

                if not self.recording:
                    self.pre_buffer.append(audio_np)
                    if len(self.pre_buffer) > self.pre_buffer_max:
                        self.pre_buffer.pop(0)

    def transcribe_audio(self):
        """Concatenates buffered audio segments and transcribes using PhoWhisper."""
        if not self.audio_buffer:
            return

        full_audio = np.concatenate(self.audio_buffer)
        
        # Save to a file if debugging is enabled
        if self.debug:
            audio_tensor = torch.from_numpy(full_audio)
            torchaudio.save("temp.wav", audio_tensor.unsqueeze(0), self.sample_rate)

        result = self.transcriber(full_audio)
        print("Transcription:", result["text"])

        # Generate action
        action = self.action_selector.generate_action(result["text"])
        print("Action:", action)
        flag = False
        for act in self.action_lst:
            if act.name in action:
                self.tts.speak("Đã thực hiện hành động " + act.vietnamese_description)
                flag = True
                break
        if not flag:
            self.tts.speak("Không thể thực hiện hành động")

    def start(self):
        """Starts the microphone stream."""
        self.is_running = True
        self.stream.start_stream()
        print("Speech Recognition started...")

    def stop(self):
        """Stops the microphone stream."""
        self.is_running = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        print("Speech Recognition stopped.")

if __name__ == "__main__":
    voice_assistant = VoiceAssistant()
    
    try:
        voice_assistant.start()
        voice_assistant.process_audio()
    except KeyboardInterrupt:
        voice_assistant.stop()
