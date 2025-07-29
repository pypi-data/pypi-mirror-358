from openai import OpenAI
import os
from dotenv import load_dotenv
import re
import json
from ollama import Client


class LLMClient:
    initiated = False

    def __init__(self, openai_api_key=None, openai_model=None, openai_api_base=None, ollama_host=None, ollama_model=None):
        load_dotenv()
        openai_key = os.getenv('PYHURL_OPENAI_API') if openai_api_key is None else openai_api_key
        self.openai_model = os.getenv('PYHURL_OPENAI_MODEL') if openai_model is None else openai_model
        openai_api_base = os.getenv('PYHURL_OPENAI_API_BASE') if openai_api_base is None else openai_api_base
        self.openai_client = OpenAI(api_key=openai_key, base_url=openai_api_base)

        ollama_host = os.getenv('PYHURL_OLLAMA_HOST', 'http://localhost:11434') if ollama_host is None else ollama_host
        self.ollama_model = os.getenv('PYHURL_OLLAMA_MODEL', 'llama2') if ollama_model is None else ollama_model
        self.ollama_client = Client(host=ollama_host)

    def call_openai(self, messages: list[dict], model=None, temperature=0.1, max_tokens=None, timeout=None):
        response = self.openai_client.chat.completions.create(
            model=self.openai_model if model is None else model,
            messages=messages,
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            tool_choice='auto',
            top_p=1)
        return response.choices[0].message.content

    def call_ollama(self, messages: list[dict], model=None, options=None):
        return self.ollama_client.chat(model=model if model else self.ollama_model, messages=messages, options=options)['message']['content']

    @classmethod
    def find_all_json_datas(cls, text):
        if not text:
            return []
        try:
            return [json.loads(text)]
        except:
            matches = re.findall(r'```(?:.*?)\s*([\[\{])(.*?)```', text, re.DOTALL)
            if matches:
                try:
                    return [json.loads(''.join(match)) for match in matches]
                except:
                    return []
            else:
                return []

    @classmethod
    def find_first_json_data(cls, text):
        datas = cls.find_all_json_datas(text)
        return datas[0] if len(datas) > 0 else None