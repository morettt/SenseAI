import aiohttp
import asyncio
import json
import argparse
from typing import List, Tuple
import keyboard

stop_flag = False


def interrupt_response():
    global stop_flag
    stop_flag = True


keyboard.add_hotkey('tab', interrupt_response)


async def stream_response(session: aiohttp.ClientSession, url: str, prompt: str, history: List[Tuple[str, str]]):
    headers = {'Content-Type': 'application/json'}
    data = {
        "prompt": prompt,
        "history": history,
        "max_length": 2048,
        "top_p": 0.8,
        "temperature": 0.6
    }
    async with session.post(url, headers=headers, json=data) as response:
        response.raise_for_status()
        async for line in response.content:
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    yield json.loads(line[5:])


async def chat_with_ai(session: aiohttp.ClientSession, url: str, prompt: str, history: List[Tuple[str, str]]) -> str:
    global stop_flag
    full_response = ""
    print("AI: ", end="", flush=True)

    try:
        async for chunk in stream_response(session, url, prompt, history):
            if stop_flag:
                break
            if 'response' in chunk:
                content = chunk['response']
                print(content, end="", flush=True)
                full_response += content
            elif 'end_of_stream' in chunk:
                break
    except aiohttp.ClientError as e:
        print(f"\nError: {e}")

    print()
    return full_response


async def main(url: str):
    history = []
    print(f"Async text chat system started, using server address: {url}")
    print("Start chatting... (Press Tab to interrupt AI's response)")

    async with aiohttp.ClientSession() as session:
        while True:
            user_input = await asyncio.get_event_loop().run_in_executor(None, lambda: input("You: ").strip())

            if user_input.lower() == 'exit':
                print("AI: Goodbye!")
                break

            global stop_flag
            stop_flag = False

            full_response = await chat_with_ai(session, url, user_input, history)

            if full_response:
                history.append((user_input, full_response))
            elif not stop_flag:
                print("Warning: No response received from the AI.")

    keyboard.remove_hotkey('tab')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Async Text Chat System")
    parser.add_argument("--url", type=str, default="https://u456499-b362-14f1ece3.nma1.seetacloud.com:8448",
                        help="Server address")
    args = parser.parse_args()

    asyncio.run(main(args.url))