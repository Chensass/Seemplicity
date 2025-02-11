from fastapi import FastAPI, WebSocket
from worker import add, celery_app
from celery.result import AsyncResult
import asyncio

import time

app = FastAPI()

@app.get("/process")
async def process_endpoint(a:int, b:int):
    result = add.delay(a, b)
    return {"task_id": result.id}

@app.websocket("/ws/task/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()

    # Get the task result asynchronously
    result = AsyncResult(task_id, app=celery_app)

    while True:
        if result.ready():
            break
        await websocket.send_text(result.state)
        await asyncio.sleep(1)

    # Task is ready, send the final result
    if result.successful():
        await websocket.send_text(str(result.state))
        await websocket.send_text(str(result.result))
        await websocket.close()
    else:
        await websocket.send_text(result.state)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)