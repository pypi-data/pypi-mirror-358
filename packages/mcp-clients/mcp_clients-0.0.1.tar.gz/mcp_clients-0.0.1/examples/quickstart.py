from dotenv import load_dotenv
import asyncio

from mcp_clients import Gemini

load_dotenv()

async def main():
    client = await Gemini.init(
        server_script_path='/home/faizraza/Personal/Projects/mcp_clients/weather.py',
    )
    try:
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())