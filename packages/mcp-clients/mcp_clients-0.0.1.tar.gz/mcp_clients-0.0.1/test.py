# from mcp_clients import Gemini
# import asyncio

# async def custom_chat(self):
#     """Run an interactive chat loop"""
#     print("\nMCP Client Started! Custom Chat Loop")
#     print("Type your queries or 'q' to exit.")

#     while True:
#         try:
#             query = input("\nQuery: ").strip()

#             if query.lower() == 'q':
#                 break

#             response = await self.process_query(query)
#             print("\n" + response)

#         except Exception as e:
#             print(f"\nError: {str(e)}")

# async def main():
#     client = await Gemini.init(
#         api_key='AIzaSyAiCVmfQrdMO-MG4IUX1EC02s0u1lX_cZs',
#         server_script_path='/home/faizraza/Personal/Projects/mcp_clients/weather.py',
#         custom_chat_loop = custom_chat
#     )
#     try:
#         await client.chat_loop()
#     finally:
#         await client.cleanup()

# if __name__ == "__main__":
#     asyncio.run(main())

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