<p align="center">
  <h1 align="center">apays</h1>
</p>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python 3.8+">
  </a>
  <a href="https://www.python-httpx.org/">
    <img src="https://img.shields.io/badge/httpx-%3E%3D0.24.0-blue.svg" alt="httpx">
  </a>
  <a href="https://pydantic.dev/">
    <img src="https://img.shields.io/badge/pydantic-v2-blue.svg" alt="pydantic v2">
  </a>
</p>


**apays** is an asynchronous Python client for the APays payment API. It provides methods to create payments, check status, and (optionally) poll until completion.

> ## [GitHub Repository](https://github.com/Bezdarnost01/apays)

## Quick start

```python
import asyncio
from apays import APaysClient, APayError

async def main():
    client = APaysClient(client_id=123, secret_key="abc123")
    try:
        # Создаём платёж на сумму 45.67 (будет сконвертировано в 4567 копеек)
        resp = await client.create_order(45.67)
        print("Order ID:", resp.order_id)
        print("Payment URL:", resp.url)

        # Проверяем статус
        status = await client.get_order(resp.order_id)
        print("Current status:", status.order_status)
    except APayError as e:
        print("APays error:", e)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Polling example

```python
import asyncio
from apays import APaysClient, APayError

async def main():
    client = APaysClient(client_id=123, secret_key="abc123")
    try:
        resp = await client.create_order(10.50)
        print("Order ID:", resp.order_id)

        # Ждём завершения платежа (проверяем каждые 5 секунд, максимум 2 минуты)
        final = await client.start_order_polling(
            order_id=resp.order_id,
            interval=5.0,
            timeout=120.0
        )
        print("Final status:", final.order_status)
    except APayError as e:
        print("APays error:", e)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```


## Installation

Since **apays** isn’t on PyPI yet, you can install it directly from GitHub:

```bash
pip install git+https://github.com/Bezdarnost01/apays.git@main#egg=apays
```

## License

MIT © [Bezdarnost01](https://github.com/Bezdarnost01)
