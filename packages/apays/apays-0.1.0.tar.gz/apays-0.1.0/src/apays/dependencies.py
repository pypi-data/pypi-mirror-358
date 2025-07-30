from contextlib import asynccontextmanager
from .apays_client import APaysClient

@asynccontextmanager
async def get_apays_client(client_id: int, secret_key: str):
    client = APaysClient(client_id, secret_key)
    try:
        yield client
    finally:
        await client.close()