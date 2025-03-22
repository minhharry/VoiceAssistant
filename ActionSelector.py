import requests
from dataclasses import dataclass
from typing import Optional

@dataclass
class Action:
    name: str
    description: str
    vietnamese_description: str
    example_command: str
    keyword: str

    def __str__(self):
        return f"Action: {self.name}, Description: {self.description}, Vietnamese Description: {self.vietnamese_description}, Example: {self.example_command}, Keyword: {self.keyword}"

class LLMActionSelector:
    def __init__(self, actions: list[Action], model="gemma3:1b", api_url="http://localhost:11434/api/generate"):
        self.model = model
        self.api_url = api_url
        self.actions = actions
        
        self.base_prompt_template = (
"""You are an AI model tasked with classifying user commands into one of the following actions:
{action_list}

Based on the user's input command, return the appropriate action as a single keyword from the list above. 
If the command does not match any of the defined actions, you must return \"unknown\", do not make up new keywords. 
Return only one of the above keywords, do not include further explanation.

Desired input and output examples:
User command -> Desired output:
{examples}

"""
        )
        self.prompt = self._generate_prompt()
        
    def update_actions(self, new_actions):
        self.actions = new_actions
        self.prompt = self._generate_prompt()
    
    def _generate_prompt(self):
        action_list = "\n".join(f'- "{action.name}": {action.description}' for action in self.actions)
        examples = "\n".join(f'"{action.example_command}" -> "{action.name}"' for action in self.actions)
        examples += '\n"hôm nay thời tiết thế nào?" -> "unknown"' 
        return self.base_prompt_template.format(action_list=action_list, examples=examples)
    
    def generate_action(self, user_command: str):
        prompt = self.prompt + f'User command: "{user_command.lower()}"\nDesired output: '
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
            for action in self.actions:
                if action.name in text:
                    return action.name
            return "unknown"
        except requests.exceptions.RequestException as error:
            return f"Error: {error}"

class WordsMatchingActionSelector:
    def __init__(self, actions: list[Action], model="gemma3:1b", api_url="http://localhost:11434/api/generate"):
        self.model = model
        self.api_url = api_url
        self.actions = actions
    
    def generate_action(self, user_command: str):
        user_command = user_command.lower()
        for action in self.actions:
            if action.keyword in user_command:
                return action.name
        return "unknown"

if __name__ == "__main__":
    action_lst = [
        Action("turn_on_light", "Turn on the light", "bật đèn", "bật đèn lên giúp tôi", "bật đèn"),
        Action("turn_off_light", "Turn off the light", "tắt đèn", "tắt đèn đi", "tắt đèn"),
        Action("turn_on_fan", "Turn on the fan", "bật quạt", "làm ơn mở quạt", "bật quạt"),
        Action("turn_off_fan", "Turn off the fan", "tắt quạt", "hãy tắt quạt ngay", "tắt quạt"),
    ]
    action_selector = LLMActionSelector(action_lst)
    result = action_selector.generate_action("mở đèn đi bạn ê.")
    print(result)
