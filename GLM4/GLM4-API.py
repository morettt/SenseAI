import requests
import json
import argparse
import keyboard

stop_flag = False

def interrupt_response():
    global stop_flag
    stop_flag = True

keyboard.add_hotkey('tab', interrupt_response)

def stream_response(url, prompt, history):
    headers = {'Content-Type': 'application/json'}
    data = {
        "prompt": prompt,
        "history": history,
        "max_length": 2048,
        "top_p": 0.8,
        "temperature": 0.6
    }
    with requests.post(url, headers=headers, json=data, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    yield json.loads(line[5:])

def chat_with_ai(url, prompt, history):
    global stop_flag
    full_response = ""
    print("AI: ", end="", flush=True)
    try:
        for chunk in stream_response(url, prompt, history):
            if stop_flag:
                break
            if 'response' in chunk:
                content = chunk['response']
                print(content, end="", flush=True)
                full_response += content
            elif 'end_of_stream' in chunk:
                break
    except requests.RequestException as e:
        print(f"\n错误: {e}")
    print()
    return full_response

def main(url):
    history = []
    print(f"同步文本聊天系统已启动，使用服务器地址: {url}")
    print("开始聊天... (按Tab键中断AI的回应)")
    print("输入'clear'清除聊天历史")

    while True:
        user_input = input("你: ").strip()
        if user_input.lower() == 'clear':
            history = []
            print("聊天历史已清除。开始新的对话。")
            continue

        global stop_flag
        stop_flag = False
        full_response = chat_with_ai(url, user_input, history)
        if full_response:
            history.append((user_input, full_response))
        elif not stop_flag:
            print("警告: 未收到AI的回应。")

    keyboard.remove_hotkey('tab')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="同步文本聊天系统")
    parser.add_argument("--url", type=str, default="https://u456499-b362-14f1ece3.nma1.seetacloud.com:8448",
                        help="服务器地址")
    args = parser.parse_args()
    main(args.url)
