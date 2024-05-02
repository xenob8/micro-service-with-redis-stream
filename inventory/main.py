import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from fastapi.background import BackgroundTasks


app = FastAPI()

redis_stream = get_redis_connection(
    host=os.getenv("REDIS_STREAM_HOST") or "127.0.0.1",
    port=os.getenv("REDIS_STREAM_PORT") or 8005,
    decode_responses=True
)

redis_host = os.getenv('REDIS_INVENTORY_HOST')
redis_port = os.getenv("REDIS_INVENTORY_PORT")

redis = get_redis_connection(
    host=redis_host or "127.0.0.1",
    port=redis_port or 8081,
    # password="pRdcpRkKPFn6UnEFskrDGxrmFbf5T9ER",
    decode_responses=True
)






class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get('/products')
def all():
    print(123)
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    product = Product.get(pk)

    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }


@app.post('/products')
def create(product: Product):
    return product.save()


@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)


@app.delete('/products/{pk}')
def delete(pk: str):
    return Product.delete(pk)





