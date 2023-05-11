import requests
import json


gpt_3_models = ("text-curie-001", "text-babbage-001", "text-ada-001")
gpt_3_5_models = ("gpt-3.5-turbo",)
#"text-davinci-003", 


class GPT:
    
    def __init__(self, model):
        
        bearer = "put your token here"
        self.headers = {"authorization": "Bearer "+bearer}
        
        self.model = model
        self.temperature = 1
        self.max_tokens = 256
        self.top_p = 1
        self.frequency_penalty = 0.5
        self.presence_penalty = 0
        self.memory = 1
        
        self.conversation = []

        
        
class GPT3(GPT):
    
    def __init__(self, model="text-curie-001"):
        super().__init__(model)
        self.url = "https://api.openai.com/v1/completions"
        
    
    def ask(self, message):
        
        prompt = f"Me:{message}\nYou: "
        
        if self.conversation:
            prompt = f"Me:{self.conversation[-1][0]}\nYou:{self.conversation[-1][1]}\n"+prompt
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop": None
            }
            
        r = requests.post(self.url, json=payload, headers=self.headers)
        data = r.json()
        
        if data.get("error"):
            raise Exception(data["error"]["message"])
        
        response = data["choices"][0]["text"].strip()
        self.conversation.append((message, response))
        
        return response
        
        
class GPT3_5(GPT):
    
    def __init__(self, model="gpt-3.5-turbo"):
        super().__init__(model)
        self.url = "https://api.openai.com/v1/chat/completions"
        
    
    def ask(self, message):

        self.conversation.append({"role":"user","content":message})
        
        payload = {
            "model": self.model,
            "messages": self.conversation[-10:],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop": None
            }
            
        r = requests.post(self.url, json=payload, headers=self.headers)
        data = r.json()

        if data.get("error"):
            raise Exception(data["error"]["message"])
        
        response = data["choices"][0]["message"]["content"].strip()
        self.conversation.append({"role":"assistant","content":response})
        
        return response
        
        
def get_gpt(model=""):
    model = model.lower()
    if not model:
        model = "text-curie-001"
    if model in gpt_3_models:
        return GPT3(model)
    elif model in gpt_3_5_models:
        return GPT3_5(model)
        

if __name__ == "__main__":
        
    a = GPT3_5()

    while True:
        print(a.ask(input(">> ")))
            
