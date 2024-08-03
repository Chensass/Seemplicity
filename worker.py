from celery import Celery

celery_app = Celery('tasks', broker='redis://redis/0', backend='redis://redis/0')

@celery_app.task()
def add(a, b):
    for i in range(a,b):
        print(i)
    return {"number":a+b}