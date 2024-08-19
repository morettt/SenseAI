import requests
import io
import pygame
import keyboard
import pureness
import threading
import queue
import re
import time

c3 = pureness.CUT200()
BASE_URL = "http://192.168.110.68:23456"
stop_flag = threading.Event()
audio_queue = queue.Queue()
text_buffer = ""
audio_playing = threading.Event()
processing_lock = threading.Lock()

def interrupt_playback():
    global text_buffer
    stop_flag.set()
    print("\n操作被中断.")
    pygame.mixer.music.stop()
    clear_audio_queue()
    with processing_lock:
        text_buffer = ""  # 清除待处理的文本

keyboard.add_hotkey('tab', interrupt_playback)

def clear_audio_queue():
    with audio_queue.mutex:
        audio_queue.queue.clear()

def play_audio_thread():
    pygame.mixer.init()
    while True:
        try:
            audio_stream = audio_queue.get(timeout=1)
            if stop_flag.is_set():
                continue
            audio_playing.set()
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() and not stop_flag.is_set():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.stop()
            if audio_queue.empty():
                audio_playing.clear()
        except queue.Empty:
            audio_playing.clear()

def text_to_speech_stream(text, speaker_id=1):
    if stop_flag.is_set():
        return None
    params = {
        "id": speaker_id,
        "segment_size": 5,
        "streaming": True,
        "prompt_lang": "auto",
        "prompt_text": "都红到耳朵根了，现在要是用嘴亲亲你的小脸蛋？",
        "preset": "default",
        "text": text
    }
    try:
        with requests.get(f"{BASE_URL}/voice/gpt-sovits", params=params, stream=True) as response:
            response.raise_for_status()
            return io.BytesIO(response.content) if not stop_flag.is_set() else None
    except requests.RequestException as e:
        print(f"网络请求错误: {e}")
        return None

def text_to_speech(text, speaker_id=1, flush=False):
    global text_buffer
    with processing_lock:
        if stop_flag.is_set():
            return
        text_buffer += text

        segments = re.split(r'([。？！.?!])', text_buffer)
        complete_segments = [''.join(segments[i:i+2]) for i in range(0, len(segments)-1, 2) if segments[i]]

        for segment in complete_segments:
            if stop_flag.is_set():
                break
            audio_stream = text_to_speech_stream(segment, speaker_id)
            if audio_stream:
                audio_queue.put(audio_stream)

        text_buffer = segments[-1] if len(segments) % 2 == 1 else ''

        if flush and text_buffer and not stop_flag.is_set():
            audio_stream = text_to_speech_stream(text_buffer, speaker_id)
            if audio_stream:
                audio_queue.put(audio_stream)
            text_buffer = ""

def flush_tts_buffer():
    text_to_speech("", flush=True)

def wait_for_audio_complete():
    while not audio_queue.empty() or audio_playing.is_set():
        time.sleep(0.1)
        if stop_flag.is_set():
            break

def reset_stop_flag():
    stop_flag.clear()
    clear_audio_queue()

# 启动音频播放线程
playback_thread = threading.Thread(target=play_audio_thread, daemon=True)
playback_thread.start()