import aiohttp
import asyncio
import json
import sys
import math


async def main():
    if len(sys.argv) <= 1:
        print("No enough arguments. Please write URLs to query separated with a space.")
        exit(1)
    urls = [*sys.argv[1:]]
    task_id = 0
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:8888/api/v1/tasks/', json={"urls": urls}) as resp:
            res = await resp.json()
            task_id = res.get('task').get('uuid')

        if task_id:
            task_status = 'running'
            results = []
            i = 0
            while task_status == 'running':
                print("waiting " + '.' * i, end='\r')
                await asyncio.sleep(1)
                if i > 15:
                    print("Wait timeout...")
                    break
                i += 1

                async with session.get("http://127.0.0.1:8888/api/v1/tasks/" + task_id) as resp:
                    data = await resp.json()
                    results = data.get('task').get('result')
                    task_status = data.get('task').get('status')
        if results:
            for status, url in results:
                print(f"{status} -- {url}")
        else:
            print("Task had no results, somethings wrong, here is the full task \n", data)

asyncio.run(main())


