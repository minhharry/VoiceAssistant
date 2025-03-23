import requests
from dataclasses import dataclass
import random

@dataclass
class Action:
    name: str
    description: str
    vietnamese_description: str
    keyword: str

    def __str__(self):
        return f"Action: {self.name}, Description: {self.description}, Vietnamese Description: {self.vietnamese_description}, Keyword: {self.keyword}"

class LLMActionSelector:
    def __init__(self, actions: list[Action], model="llama3.1", api_url="http://localhost:11434/api/generate", debug=False):
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
        
    def update_actions(self, new_actions):
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
    
    def generate_action(self, user_command: str):
        prompt = self.prompt + f'User\'s command: "{user_command.lower()}"\nDesired output: '
        if self.debug:
            print("[DEBUG] prompt: " + prompt)
        data = {
            "model": self.model,
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
                    return action.name
            return "unknown"
        except requests.exceptions.RequestException as error:
            return f"Error: {error}"
        
class LLMActionSelector2:
    def __init__(self, actions: list[Action], model="llama3.1", api_url="http://localhost:11434/api/generate", debug=False):
        self.debug = debug
        self.model = model
        self.api_url = api_url
        self.actions = actions
        
        self.base_prompt_template = "Is the user's command \"{command}\" call the action \"{action}: {description}\"? Answer only with \"yes\" or \"no\", no further explanation."
    
    def generate_action(self, user_command: str):
        prompts = [self.base_prompt_template.format(command=user_command.lower(), action=action.name, description=action.description) for action in self.actions]
        if self.debug:
            print("[DEBUG] prompts: ", prompts)
        res = []
        for prompt in prompts:
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0}
            }
            try:
                response = requests.post(self.api_url, json=data)
                response.raise_for_status()
                text = response.json().get('response')
                res.append(text.lower())
            except requests.exceptions.RequestException as error:
                return f"Error: {error}"
        if self.debug:
            print("[DEBUG] responses: ", res)
        yes_count = 0
        for text in res:
            if "yes" in text:
                yes_count += 1
        if yes_count > 1 or yes_count == 0:
            return "unknown"
        for i, text in enumerate(res):
            if "yes" in text:
                return self.actions[i].name
        return "unknown"

class LLMActionSelector3:
    def __init__(self, actions: list[Action], model="llama3.1", api_url="http://localhost:11434/api/generate", debug=False):
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
        
    def update_actions(self, new_actions):
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
    
    def generate_action(self, user_command: str):
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
                    return action.name
            return "unknown"
        except requests.exceptions.RequestException as error:
            return f"Error: {error}"
        
class WordsMatchingActionSelector:
    def __init__(self, actions: list[Action]):
        self.actions = actions
    
    def generate_action(self, user_command: str):
        user_command = user_command.lower()
        for action in self.actions:
            if action.keyword in user_command:
                return action.name
        return "unknown"

if __name__ == "__main__":
    from time import time
    action_lst = [ 
        Action("turn_on_light", "Turn on the light", "bật đèn", "bật đèn"),
        Action("turn_off_light", "Turn off the light", "tắt đèn", "tắt đèn"),
        Action("turn_on_fan", "Turn on the fan", "bật quạt", "bật quạt"),
        Action("turn_off_fan", "Turn off the fan", "tắt quạt", "tắt quạt"),
        Action("turn_on_tv", "Turn on the TV", "bật ti vi", "bật ti vi"),
        Action("turn_off_tv", "Turn off the TV", "tắt ti vi", "tắt ti vi"),
        Action("turn_on_air_conditioner", "Turn on the air conditioner", "bật điều hòa", "bật điều hòa"),
        Action("turn_off_air_conditioner", "Turn off the air conditioner", "tắt điều hòa", "tắt điều hòa"),
        Action("play_music", "Play music", "phát nhạc", "phát nhạc"),
        Action("stop_music", "Stop music", "dừng nhạc", "dừng nhạc"),
    ]

    tests = [
        # Tests for turn_on_light
        ("bật đèn", "turn_on_light"),
        ("bật sáng", "turn_on_light"),
        ("làm ơn bật đèn", "turn_on_light"),
        ("bật đèn lên", "turn_on_light"),
        ("cho tôi bật đèn", "turn_on_light"),
        
        # Tests for turn_off_light
        ("tắt đèn", "turn_off_light"),
        ("đi tắt đèn", "turn_off_light"),
        ("hãy tắt đèn", "turn_off_light"),
        ("làm ơn tắt đèn", "turn_off_light"),
        ("cho tôi tắt đèn", "turn_off_light"),
        
        # Tests for turn_on_fan
        ("bật quạt", "turn_on_fan"),
        ("bật quạt đi", "turn_on_fan"),
        ("mở quạt", "turn_on_fan"),
        ("bật quạt cho tôi", "turn_on_fan"),
        ("làm ơn bật quạt", "turn_on_fan"),
        
        # Tests for turn_off_fan
        ("tắt quạt", "turn_off_fan"),
        ("quạt tắt", "turn_off_fan"),
        ("hãy tắt quạt", "turn_off_fan"),
        ("làm ơn tắt quạt", "turn_off_fan"),
        ("cho tôi tắt quạt", "turn_off_fan"),
        
        # Tests for turn_on_tv
        ("bật ti vi", "turn_on_tv"),
        ("mở ti vi", "turn_on_tv"),
        ("ti vi bật", "turn_on_tv"),
        ("cho tôi bật ti vi", "turn_on_tv"),
        ("làm ơn bật ti vi", "turn_on_tv"),
        
        # Tests for turn_off_tv
        ("tắt ti vi", "turn_off_tv"),
        ("ti vi tắt", "turn_off_tv"),
        ("hãy tắt ti vi", "turn_off_tv"),
        ("cho tôi tắt ti vi", "turn_off_tv"),
        ("làm ơn tắt ti vi", "turn_off_tv"),
        
        # Tests for turn_on_air_conditioner
        ("bật máy lạnh", "turn_on_air_conditioner"),
        ("mở điều hòa", "turn_on_air_conditioner"),
        ("cho tôi bật điều hòa", "turn_on_air_conditioner"),
        ("làm ơn bật điều hòa", "turn_on_air_conditioner"),
        ("đi bật điều hòa", "turn_on_air_conditioner"),
        
        # Tests for turn_off_air_conditioner
        ("tắt máy lạnh", "turn_off_air_conditioner"),
        ("đi tắt điều hòa", "turn_off_air_conditioner"),
        ("cho tôi tắt điều hòa", "turn_off_air_conditioner"),
        ("làm ơn tắt điều hòa", "turn_off_air_conditioner"),
        ("đi tắt điều hòa đi", "turn_off_air_conditioner"),
        
        # Tests for play_music
        ("phát nhạc", "play_music"),
        ("bắt đầu phát nhạc", "play_music"),
        ("cho tôi phát nhạc", "play_music"),
        ("làm ơn phát nhạc", "play_music"),
        ("bắt đầu nhạc", "play_music"),
        
        # Tests for stop_music
        ("dừng nhạc", "stop_music"),
        ("tạm dừng nhạc", "stop_music"),
        ("cho tôi dừng nhạc", "stop_music"),
        ("làm ơn dừng nhạc", "stop_music"),
        ("nhạc dừng lại", "stop_music"),
    ]

    models = ["smollm2", "llama3.2", "phi4-mini", "qwen2.5", "llama3.1", "gemma3"]

    baseline_selector = WordsMatchingActionSelector(action_lst)
    baseline_correct = sum(
        1 for user_command, expected in tests
        if baseline_selector.generate_action(user_command) == expected
    )
    baseline_accuracy = baseline_correct / len(tests)

    model_results = []
    wrong_details = []

    for model in models:
        action_selectors = [
            LLMActionSelector(action_lst, model=model), 
            LLMActionSelector2(action_lst, model=model), 
            LLMActionSelector3(action_lst, model=model)
        ]
        
        for action_selector in action_selectors:
            accuracy = 0
            wrong_result = []
            action_selector.generate_action("bạn khoẻ không?") # Warmup
            start_time = time()
            for user_command, expected in tests:
                result = action_selector.generate_action(user_command)
                if result == expected:
                    accuracy += 1
                else:
                    wrong_result.append((user_command, result))
            time1 = time() - start_time

            model_results.append({
                "model": model,
                "selector": action_selector.__class__.__name__,
                "accuracy": accuracy / len(tests),
                "time": time1
            })
        
            wrong_details.append({
                "model": model,
                "selector": action_selector.__class__.__name__,
                "wrong_results": wrong_result
            })

    md_lines = []
    md_lines.append("# Benchmark Results\n\n")
    md_lines.append("## Baseline\n")
    md_lines.append("| Selector                    | Accuracy   |\n")
    md_lines.append("|-----------------------------|------------|\n")
    md_lines.append(f"| WordsMatchingActionSelector | {baseline_accuracy:.2%} |\n\n")

    md_lines.append("## Model Results\n")
    md_lines.append("| Model     | Selector              | Accuracy   | Time Taken (s) |\n")
    md_lines.append("|-----------|-----------------------|------------|----------------|\n")
    for result in model_results:
        md_lines.append(
            f"| {result['model']:<9} | {result['selector']:<21} | {result['accuracy']:.2%} | {result['time']:.2f} |\n"
        )

    md_lines.append("\n## Detailed Wrong Results\n")
    for detail in wrong_details:
        if detail["wrong_results"]:
            md_lines.append(f"### Model: {detail['model']} | Selector: {detail['selector']}\n")
            md_lines.append("| User Command | Generated Result |\n")
            md_lines.append("|--------------|------------------|\n")
            for user_command, generated in detail["wrong_results"]:
                md_lines.append(f"| {user_command} | {generated} |\n")
            md_lines.append("\n")

    with open("Benchmark.md", "a", encoding="utf-8") as file:
        file.writelines(md_lines)