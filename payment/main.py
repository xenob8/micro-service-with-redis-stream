import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests, time

app = FastAPI()

redis_stream = get_redis_connection(
    host=os.getenv("REDIS_STREAM_HOST") or "127.0.0.1",
    port=os.getenv("REDIS_STREAM_PORT") or 8005,
    decode_responses=True
)

redis_host = os.getenv('REDIS_PAYMENT_HOST')
redis_port = os.getenv("REDIS_PAYMENT_PORT")

redis = get_redis_connection(
    host=redis_host or "127.0.0.1",
    port=redis_port or 8081,
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # pending, completed, refunded

    class Meta:
        database = redis



@app.get('/orders/{pk}')
def get(pk: str):
    return Order.get(pk)


@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks):  # id, quantity
    body = await request.json()
    inventory_host = os.getenv("INVENTORY_HOST")
    inventory_port = os.getenv("INVENTORY_PORT")
    url = f'http://{inventory_host}:{inventory_port}/products/{body["id"]}'
    req = requests.get(url)
    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total=1.2 * product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    order.save()

    background_tasks.add_task(order_completed, order)

    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    redis_stream.xadd('order_completed', order.dict(), '*')
