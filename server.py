import asyncio

from fastapi import FastAPI, Request, Response, status
from typing import Union
from typing import List, Dict, Tuple
import uuid
from pydantic import BaseModel
import aiohttp


app = FastAPI()

class Data(BaseModel):
    urls: List[str]


class Task(BaseModel):
    uuid: str = uuid.uuid4()
    status: str
    urls: List[str]
    result: List[Tuple[str, str]]
    comment: str = ""


class Tasker(object):
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    async def addtask(self, task: Task):
        print(f"ADDING - {task}")
        task.status = "running"
        task.result = []
        self.tasks[str(task.uuid)] = task
        try:
            results = await runtask(task)
            task.status = 'ready'
        except Exception as e:
            print(e)
            results = ["BAD URL(s)"]
            task.comment = 'error happened'
            task.status = 'error'

        task.result = results
        self.tasks[str(task.uuid)] = task
        print("DONE")

    def get_task(self, task_uuid):
        print(task_uuid)
        print(self.tasks)
        task = self.tasks.get(task_uuid)
        if not task:
            return "No such task"
        return task


async def runtask(task):
    results = []
    print("crawling", task.urls)
    async with aiohttp.ClientSession(trust_env=True, connector=aiohttp.TCPConnector(verify_ssl=False)) as httpcli:
        print("cli success ...")
        for url in task.urls:
            print("getting --- ", url)
            async with httpcli.get(url) as resp:
                results.append((str(resp.status), url))
    print(results)
    return results



tasker = Tasker()


@app.get('/api/v1/tasks/{task_id}')
async def send_task(task_id: str):
    task = tasker.get_task(task_id)
    print(task)
    return {'task': task}

@app.post('/api/v1/tasks/')
async def get_urls(data: Data, response: Response):
    task = Task(
        urls=data.urls,
        status="running",
        result=[]
    )
    loop = asyncio.get_event_loop()
    loop.create_task(tasker.addtask(task))
    response.status_code = status.HTTP_201_CREATED
    return {"task": task}



