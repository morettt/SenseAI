import requests
import json
import argparse
from typing import List, Tuple
import keyboard
from ASR import AudioRecorder, SpeechRecognizer
from new_TTS import text_to_speech, flush_tts_buffer, wait_for_audio_complete, reset_stop_flag

# 全局变量
stop_flag = False


def interrupt_response():
    global stop_flag
    stop_flag = True
    print("\nAI: 已被打断.")


keyboard.add_hotkey('tab', interrupt_response)


def stream_response(url: str, prompt: str, history: List[Tuple[str, str]]):
    try:
        headers = {'Content-Type': 'application/json'}
        data = {
            "prompt": prompt,
            "history": history,
            "max_length": 2048,
            "top_p": 0.8,
            "temperature": 0.6
        }
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    yield json.loads(line[5:])
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        yield {"error": str(e)}


def chat_with_ai(url: str, prompt: str, history: List[Tuple[str, str]]) -> str:
    global stop_flag
    full_response = ""
    print("AI: ", end="", flush=True)

    for chunk in stream_response(url, prompt, history):
        if stop_flag:
            break
        if 'error' in chunk:
            print(f"\n错误: {chunk['error']}")
            break
        if 'response' in chunk:
            content = chunk['response']
            print(content, end="", flush=True)
            text_to_speech(content)
            full_response += content
        elif 'end_of_stream' in chunk:
            break

    if not stop_flag:
        flush_tts_buffer()
    print()  # 换行
    return full_response


def main(url: str, model_path: str, max_retries: int = 3):
    recorder = AudioRecorder()
    recognizer = SpeechRecognizer(model_path)
    history = []

    print(f"语音交互系统已启动，使用服务器地址: {url}")
    print("请开始说话...")

    try:
        while True:
            wait_for_audio_complete()

            for attempt in range(max_retries):
                print(f"请说话... (尝试 {attempt + 1}/{max_retries})")
                audio_data = recorder.record()
                user_input = recognizer.transcribe(audio_data)

                if user_input and len(user_input.strip()) >= 2:
                    print(f"识别结果: {user_input}")
                    break
                else:
                    print("未检测到有效语音输入，请重新说话...")
            else:
                print("多次尝试未检测到有效输入，请检查麦克风或环境噪音...")
                continue

            if user_input.lower() == '退出':
                print("AI: 再见!")
                break

            global stop_flag
            stop_flag = False
            reset_stop_flag()

            full_response = chat_with_ai(url, user_input, history)

            if full_response:
                history.append((user_input, full_response))

    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        print("AI: 会话已终止。")
        wait_for_audio_complete()
        keyboard.remove_hotkey('tab')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="语音交互系统")
    parser.add_argument("--url", type=str, default="http://localhost:6006", help="服务器地址")
    parser.add_argument("--model_path", type=str, default=r"B:\faster-whisper\v3", help="Whisper模型路径")
    parser.add_argument("--max_retries", type=int, default=3, help="最大重试次数")
    args = parser.parse_args()

    main(args.url, args.model_path, args.max_retries)