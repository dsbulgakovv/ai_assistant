import os
import json
from aiohttp import ClientSession

project_id = os.getenv('PROJECT_ID')
api_key = os.getenv('KEY_ID')
api_secret = os.getenv('KEY_SECRET')


class LLMapi:
    def __init__(self):
        self.api_completions_url = "https://api.cloud.ru/api/gigacube/openai/v1/completions"
        self.key_id = api_key
        self.key_secret = api_secret

    async def health_check(self):
        async with ClientSession() as session:
            async with session.get(
                f"{self.base_url}"
            ) as resp:
                response = await resp.json()
        return response

    async def get_auth_token(self) -> str:
        auth_url = "https://iam.api.cloud.ru/api/v1/auth/token"
        payload = {
            "keyId": self.key_id,
            "secret": self.key_secret
        }

        async with ClientSession() as session:
            async with session.post(
                    auth_url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("access_token")  # Предполагаем, что токен возвращается в поле "access_token"
                else:
                    text = await response.text()
                    raise Exception(f"Auth failed: {text}")

    async def prompt_answer(
        self, prompt: str, model: str, temperature: float
    ):
        token = await self.get_auth_token()
        payload = {
            "model": model,
            "prompt": [prompt],
            "temperature": temperature,
            # Другие параметры по необходимости
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        async with ClientSession() as session:
            async with session.post(
                f"{self.api_completions_url}",
                headers=headers,
                data=json.dumps(payload)
            ) as resp:
                response = await resp.json()
        return response


def main():
    api_use = LLMapi()
    resp = api_use.health_check()
    print(resp)


if __name__ == '__main__':
    main()
