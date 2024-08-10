import openai
import keyboard

api_key = "sk-zk2c80daf6787e81e9f45971926d7372e636644470813455"
openai.api_base = "https://api.zhizengzeng.com/v1/"
stop_flag = False


def tab_key():
    global stop_flag
    stop_flag = True
    print("\nAssistant: 已被打断.")


keyboard.add_hotkey('tab', tab_key)


def chat_with_gpt3_5(messages):
    global stop_flag
    response = openai.ChatCompletion.create(
        model="gpt-4o-2024-05-13",
        messages=messages,
        api_key=api_key,
        stream=True
    )
    full_response = ""
    for chunk in response:
        if stop_flag:
            break
        content = chunk['choices'][0].get('delta', {}).get('content', '')
        if content:
            print(content, end='', flush=True)
            full_response += content
    print()  # 处理完所有流时打印新行
    return full_response


conversation = [
    {"role": "system", "content": "你是一个聪明的AI"}
]

while True:
    user_input = input("You: ")
    if user_input.lower() == '退出':
        print("Assistant: 再见!")
        break

    stop_flag = False  # 每次新的输入前重置 stop_flag
    conversation.append({"role": "user", "content": user_input})
    print("Assistant: ", end='', flush=True)
    assistant_message = chat_with_gpt3_5(conversation)

    # 即使被中断，也将部分响应添加到对话历史中
    if assistant_message:
        conversation.append({"role": "assistant", "content": assistant_message})

print("Assistant: 会话已终止。")