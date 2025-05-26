import os
import json
from aiohttp import ClientSession


api_token = os.getenv('SERVERSPACE_API_KEY')
model = os.getenv('SERVERSPACE_MODEL')


class LLMapi:
    def __init__(self):
        self.api_completions_url = "https://gpt.serverspace.ru/v1/chat/completions"
        self.api_token = api_token
        self.model = model

    async def prompt_answer(
        self, messages: list, temperature: float, top_p: float, max_tokens: int
    ):
        payload = {
          "model": self.model,
          "max_tokens": max_tokens,
          "top_p": top_p,
          "temperature": temperature,
          "messages": messages
        }
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        async with ClientSession() as session:
            async with session.post(
                f"{self.api_completions_url}",
                headers=headers,
                data=json.dumps(payload)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    text = await response.text()
                    raise Exception(f"Request failed: {text}")


def main():
    api_use = LLMapi()
    # resp = api_use.health_check()
    # print(resp)


if __name__ == '__main__':
    main()
