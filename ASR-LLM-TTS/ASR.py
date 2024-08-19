import pyaudio
import numpy as np
import webrtcvad
from faster_whisper import WhisperModel
import time
import argparse
from typing import List, Tuple


class AudioRecorder:
    def __init__(self, chunk: int = 320, format: int = pyaudio.paInt16, channels: int = 1, rate: int = 16000):
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        self.p = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad(3)  # 使用最严格的VAD模式

    def record(self) -> np.ndarray:
        stream = self.p.open(format=self.format, channels=self.channels, rate=self.rate, input=True,
                             frames_per_buffer=self.chunk)
        frames = []
        num_silent_frames = 0
        triggered = False

        try:
            while True:
                data = stream.read(self.chunk)
                is_speech = self.vad.is_speech(data, self.rate)

                if not triggered:
                    if is_speech:
                        triggered = True
                    else:
                        continue

                frames.append(data)

                if not is_speech:
                    num_silent_frames += 1
                    if num_silent_frames > 30:  # 大约1秒的静音
                        break
                else:
                    num_silent_frames = 0
        finally:
            stream.stop_stream()
            stream.close()

        return np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0

    def __del__(self):
        self.p.terminate()


class SpeechRecognizer:
    def __init__(self, model_path: str, device: str = "cuda"):
        self.model = WhisperModel(model_path, device=device, local_files_only=True)

    def transcribe(self, audio: np.ndarray) -> str:
        segments, _ = self.model.transcribe(audio, beam_size=5, language="zh", vad_filter=True,
                                            vad_parameters=dict(min_silence_duration_ms=1000))
        return " ".join([segment.text for segment in segments]).strip()


def is_valid_input(text: str, min_chars: int = 2) -> bool:
    cleaned_text = ''.join(ch for ch in text if not (ch.isspace() or ch in '，。！？；：""''（）、'))
    return len(cleaned_text) >= min_chars


def main(model_path: str, max_retries: int = 3):
    recorder = AudioRecorder()
    recognizer = SpeechRecognizer(model_path)

    print("ASR系统已启动，请开始说话...")

    try:
        while True:
            for attempt in range(max_retries):
                print(f"请说话... (尝试 {attempt + 1}/{max_retries})")
                audio_data = recorder.record()
                transcription = recognizer.transcribe(audio_data)

                if is_valid_input(transcription):
                    print(f"识别结果: {transcription}")
                    break
                else:
                    print("未检测到有效语音输入，请重新说话...")
            else:
                print("多次尝试未检测到有效输入，请检查麦克风或环境噪音...")

            if transcription.lower() == '退出':
                print("程序退出!")
                break

            time.sleep(1)  # 防止CPU占用过高

    except KeyboardInterrupt:
        print("程序被用户中断")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASR System")
    parser.add_argument("--model_path", type=str, default=r"B:\faster-whisper\v3", help="Path to the Whisper model")
    parser.add_argument("--max_retries", type=int, default=3, help="Maximum number of retry attempts")
    args = parser.parse_args()

    main(args.model_path, args.max_retries)