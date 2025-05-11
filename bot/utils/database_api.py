from aiohttp import ClientSession


class DatabaseAPI:
    def __init__(self):
        self.base_url = "http://database_api:8002"

    async def health_check(self):
        async with ClientSession() as session:
            async with session.get(
                f"{self.base_url}"
            ) as resp:
                response = await resp.json()
        return response

    async def get_user(self, tg_user_id):
        async with ClientSession() as session:
            async with session.get(f"{self.base_url}/users/{tg_user_id}") as resp:
                response, status = await resp.json(), resp.status
        return response, status

    async def get_tasks(self, tg_user_id, start_date, end_date):
        async with ClientSession() as session:
            async with session.get(
                    f"{self.base_url}/tasks/{tg_user_id}?start_date={start_date}&end_date={end_date}"
            ) as resp:
                response, status = await resp.json(), resp.status
        return response, status

    async def create_user(self, tg_user_id, username, full_name, timezone, lang):
        async with ClientSession() as session:
            async with session.post(
                f"{self.base_url}/users/add_new",
                json={
                    "tg_user_id": tg_user_id, "username": username, "full_name": full_name,
                    "timezone": timezone, "lang": lang
                }
            ) as resp:
                response, status = await resp.json(), resp.status
        return response, status

    async def create_task(
            self, tg_user_id, task_name, task_status,task_category,
            task_description, task_link, task_start_dtm, task_end_dtm
    ):
        async with ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tasks/add_new",
                json={
                    "tg_user_id": tg_user_id, "task_name": task_name, "task_status": task_status,
                    "task_category": task_category, "task_description": task_description,
                    "task_link": task_link, "task_start_dtm": task_start_dtm, "task_end_dtm": task_end_dtm
                }
            ) as resp:
                response, status = await resp.json(), resp.status
        return response, status

    async def update_task(
            self, business_dt, task_relative_id, tg_user_id, task_name, task_status,task_category,
            task_description, task_link, task_start_dtm, task_end_dtm
    ):
        async with ClientSession() as session:
            async with session.put(
                f"{self.base_url}/tasks/update",
                json={
                    "business_dt": business_dt, "task_relative_id": task_relative_id,
                    "tg_user_id": tg_user_id, "task_name": task_name, "task_status": task_status,
                    "task_category": task_category, "task_description": task_description,
                    "task_link": task_link, "task_start_dtm": task_start_dtm, "task_end_dtm": task_end_dtm
                }
            ) as resp:
                response, status = await resp.json(), resp.status
        return response, status

    async def delete_task(
            self, business_dt, task_relative_id, tg_user_id
    ):
        async with ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/tasks/delete",
                json={"business_dt": business_dt, "task_relative_id": task_relative_id, "tg_user_id": tg_user_id}
            ) as resp:
                response, status = await resp.json(), resp.status
        return response, status


def main():
    api_use = DatabaseAPI()
    print(api_use.health_check())


if __name__ == '__main__':
    main()
