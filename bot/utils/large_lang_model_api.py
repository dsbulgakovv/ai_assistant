from aiohttp import ClientSession


class LLMapi:
    def __init__(self):
        self.base_url = "http://large_lang_model:8001"

    async def health_check(self):
        async with ClientSession() as session:
            async with session.get(
                f"{self.base_url}"
            ) as resp:
                response = await resp.json()
        return response

    async def answer(self, inp_text):
        async with ClientSession() as session:
            async with session.get(
                f"{self.base_url}/answer_me_llm", params={"inp_text": inp_text}
            ) as resp:
                response = await resp.json()
        return response


def main():
    api_use = LLMapi()
    resp = api_use.health_check()
    print(resp)


if __name__ == '__main__':
    main()
