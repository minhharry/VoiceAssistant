import torch
import torchaudio
import numpy as np
import pyaudio
from queue import Queue
from time import time
try:
    from transformers import pipeline
except ImportError:
    print("Transformers is not installed. Please set use_local_ASR=False to use Google ASR instead.")

from typing import Literal
import requests
from dataclasses import dataclass
import random
from typing import Callable
import speech_recognition as sr

@dataclass
class Action:
    name: str
    description: str
    vietnamese_description: str
    keyword: str
    func: Callable

    def __str__(self):
        return f"Action: {self.name}, Description: {self.description}, Vietnamese Description: {self.vietnamese_description}, Keyword: {self.keyword}"

class LLMActionSelector:
    def __init__(self, actions: list[Action], model="qwen2.5", api_url="http://localhost:11434/api/generate", debug=False):
        self.debug = debug
        self.model = model
        self.api_url = api_url
        self.actions = actions
        
        self.base_prompt_template = (
"""You are an AI model tasked with classifying user's command into one of the following actions:  
{action_list}
- "unknown": If the user's command does not match any of the defined actions.

Classification Rules:  
1. If the user's command clearly refers to an action, return the appropriate action.  
2. If user's command refers to any other device or topic, return only "unknown". Do not attempt to generalize.  
3. You must not guess or infer new actions beyond the listed above.  
4. Return only one of the predefined keywords without explanation.  

User's command input and desired output examples:
User's command -> Desired output:
{examples}

"""
        )
        self.prompt = self._generate_prompt()
        
    def update_actions(self, new_actions: list[Action]):
        self.actions = new_actions
        self.prompt = self._generate_prompt()
    
    def _generate_prompt(self):
        action_list = "\n".join(f'- "{action.name}": {action.description}' for action in self.actions)
        prefix = ["", "hãy ", "làm ơn ", "vui lòng "]
        postfix = ["", " đi", " ngay", " giúp", " giúp tôi", " đê"]
        examples = ""
        examples += "\n".join(f'"{random.choice(prefix)}{action.keyword}{random.choice(postfix)}" -> "{action.name}"' for action in self.actions)
        examples += '\n"bạn khoẻ không?" -> "unknown"\n' 
        examples += "\n".join(f'"{random.choice(prefix)}{action.keyword}{random.choice(postfix)}" -> "{action.name}"' for action in self.actions)
        examples += '\n"hôm nay thời tiết thế nào?" -> "unknown"' 
        return self.base_prompt_template.format(action_list=action_list, examples=examples)
    
    def generate_action(self, user_command: str) -> Action | str:
        prompt = f'User\'s command: "{user_command.lower()}"\nDesired output: '
        if self.debug:
            print("[DEBUG] prompt: " + prompt)
        data = {
            "model": self.model,
            "system": self.prompt,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0}
        }
        try:
            response = requests.post(self.api_url, json=data)
            response.raise_for_status()
            text = response.json().get('response')
            if self.debug:
                print("[DEBUG] response: " + text)
            for action in self.actions:
                if action.name in text:
                    return action
            return "unknown"
        except requests.exceptions.RequestException as error:
            return f"Error: {error}"
        
class WordsMatchingActionSelector:
    def __init__(self, actions: list[Action]):
        self.actions = actions
    
    def update_actions(self, new_actions: list[Action]):
        self.actions = new_actions

    def generate_action(self, user_command: str) -> Action | Literal['unknown']:
        user_command = user_command.lower()
        for action in self.actions:
            if action.keyword in user_command:
                return action
        return "unknown"

class VoiceAssistant:
    def __init__(self, action_lst: list[Action], use_local_llm=False, use_local_ASR=False, sample_rate=16000, chunk_size=512, speech_threshold=0.5, silence_timeout=1.0, pre_buffer_max=16):
        self.debug = False

        self.use_llm = use_local_llm
        self.use_local_ASR = use_local_ASR
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
        
        if self.use_local_ASR:
            # Load PhoWhisper ASR model
            self.transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-medium")
        else:
            # Load Google ASR model
            self.recognizer = sr.Recognizer()

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
        self.action_lst = action_lst
        if use_local_llm:
            self.action_selector = LLMActionSelector(self.action_lst)
        else:
            self.action_selector = WordsMatchingActionSelector(self.action_lst)

    def update_actions(self, new_actions: list[Action]):
        self.action_lst = new_actions
        self.action_selector.update_actions(new_actions)

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

        if self.use_local_ASR:
            result = self.transcriber(full_audio)['text']
        else:
            pcm16 = (full_audio * 32768).astype(np.int16)
            byte_data = pcm16.tobytes()
            audio_data = sr.AudioData(byte_data,
                                    sample_rate=self.sample_rate,
                                    sample_width=2) 
            try:
                result = self.recognizer.recognize_google(audio_data, language="vi-VN")
            except:
                print("Could not understand audio")
                result = "unknown"
        print("Transcription:", result)

        # Generate action
        action = self.action_selector.generate_action(result)
        if isinstance(action, str):
            print("Action: Unknown")
        else:
            print("Action: ", action.name)
            action.func()

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
    from Adafruit_IO import MQTTClient
    import sys
    AIO_USERNAME = "example"
    AIO_KEY      = "example"
    AIO_FEED_ID = ["BBC-LED", "BBC-FAN"]
    def  connected(client):
        print("Ket noi thanh cong...")
        for v in AIO_FEED_ID:
            client.subscribe(v)

    def  subscribe(client , userdata , mid , granted_qos):
        print("Subscribe thanh cong...")

    def  disconnected(client):
        print("Ngat ket noi...")
        sys.exit (1)

    def message(client, feed_id, payload):
        pass


    client = MQTTClient(AIO_USERNAME , AIO_KEY)
    client.on_connect = connected
    client.on_disconnect = disconnected
    client.on_message = message
    client.on_subscribe = subscribe
    client.connect()
    client.loop_background()


    def turn_on_light():
        # Push data lên AdaFruitIO
        print("===...Turning on the light...===")
        client.publish("BBC-LED", "1")
    
    def turn_off_light():
        # Push data lên AdaFruitIO
        print("===...Turning off the light...===")
        client.publish("BBC-LED", "0")
    
    def turn_on_fan():
        # Push data lên AdaFruitIO
        print("===...Turning on the fan...===")
        client.publish("BBC-FAN", "1")
    
    def turn_off_fan():
        # Push data lên AdaFruitIO
        print("===...Turning off the fan...===")
        client.publish("BBC-FAN", "0")

    def action_factory(name: str, description: str, vietnamese_description: str, keyword):
        def action_func():
            print(f"Action: {name}")
        return Action(name, description, vietnamese_description, keyword, action_func)

    action_lst = [
        Action("turn_on_light", "Turn on the light", "bật đèn", "bật đèn", turn_on_light),
        Action("turn_off_light", "Turn off the light", "tắt đèn", "tắt đèn", turn_off_light),
        Action("turn_on_fan", "Turn on the fan", "bật quạt", "bật quạt", turn_on_fan),
        Action("turn_off_fan", "Turn off the fan", "tắt quạt", "tắt quạt", turn_off_fan),
    ]
    
    voice_assistant = VoiceAssistant(action_lst, use_local_llm=False, use_local_ASR=False)
    try:
        voice_assistant.start()
        voice_assistant.process_audio()
    except KeyboardInterrupt:
        voice_assistant.stop()
