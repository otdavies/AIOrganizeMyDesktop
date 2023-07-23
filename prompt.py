import json
import openai

# Load key from .env
openai.api_key = open(".env", "r").readline().strip()


class Prompt():
    def __init__(self, user_prompt, system_prompt=""):
        self.user_prompt = user_prompt
        self.system_prompt = system_prompt
        self.creativity = 0.7

    def __str__(self):
        return "[User]: [" + self.user_prompt + "]" + "\n\n" + "[System]: [" + self.system_prompt + "]"

    def __add__(self, other):
        return Prompt(self.user_prompt + "\n" + other.user_prompt, self.system_prompt + "\n" + other.system_prompt)

    def __sub__(self, other):
        return Prompt(self.user_prompt.replace(other.user_prompt, ""), self.system_prompt.replace(other.system_prompt, ""))

    def call(self, schema="", tokens=500):
        # return self.system_prompt + "\nRespond with a populated version of this JSON schema: " + str(schema)
        # create a chat completion
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt +
                    "\nRespond in this JSON schema, fill each field with the corresponding type: " + str(schema) + "\nRespond only in JSON."}
            ],
            max_tokens=tokens,
            temperature=self.creativity,
        )
        result = chat_completion["choices"][0]["message"]["content"]
        try:
            result_json = json.loads(result)
        except:
            print("Error: Response is not valid JSON")
            return result

        return result_json

    # Recursively inject for lists or dicts of strings
    def inject_params_recursively(self, input_dict):
        for key in input_dict:
            if type(input_dict[key]) == str:
                self.user_prompt = self.user_prompt.replace(
                    "<" + key + ">", str(input_dict[key]))
                self.system_prompt = self.system_prompt.replace(
                    "<" + key + ">", str(input_dict[key]))
            elif type(input_dict[key]) == dict:
                self.inject_params_recursively(input_dict[key])
            elif type(input_dict[key]) == list:
                for item in input_dict[key]:
                    if type(item) == dict:
                        self.inject_params_recursively(item)
                    elif type(item) == str:
                        self.user_prompt = self.user_prompt.replace(
                            "<" + key + ">", str(item))
                        self.system_prompt = self.system_prompt.replace(
                            "<" + key + ">", str(item))

    def set_creativity(self, creativity):
        self.creativity = creativity
