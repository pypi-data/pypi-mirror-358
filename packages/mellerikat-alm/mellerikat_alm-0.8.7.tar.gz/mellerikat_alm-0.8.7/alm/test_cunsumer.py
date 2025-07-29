import httpx
import asyncio

async def ask_chat(endpoint_url: str, topic: str):
    headers = {'Content-Type': 'application/json'}
    data = {'topic': topic}

    async with httpx.AsyncClient() as client:
        response = await client.post(endpoint_url, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()

if __name__ == "__main__":
    endpoint_url = "http://10.158.2.106:8812/api/ask_chat"
    topic = "Python의 장단점"
    try:
        response = asyncio.run(ask_chat(endpoint_url, topic))
        print(response)
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"Other error occurred: {e}")