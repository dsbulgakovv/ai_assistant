from aiohttp import ClientSession


class VoiceToTextAPI:
    def __init__(self):
        self.base_url = "http://voice_to_text:8000"

    async def health_check(self):
        async with ClientSession() as session:
            async with session.get(
                f"{self.base_url}"
            ) as resp:
                response = await resp.json()
        return response

    async def transcript(self, path_to_file):
        async with ClientSession() as session:
            async with session.get(
                f"{self.base_url}/voice_to_text", params={"path_to_file": path_to_file}
            ) as resp:
                response = await resp.json()
        return response


def main():
    api_use = VoiceToTextAPI()
    print(api_use.health_check())
    resp = api_use.transcript('files/audio_AwACAgIAAxkBAAN4ZnslES-MBgVTaQZb4thG6WILAAH4AAIKUwACPnvZS6E9syBmndJnNQQ.mp3')
    print(resp)


if __name__ == '__main__':
    main()
