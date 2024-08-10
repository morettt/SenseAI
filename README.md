#!/bin/sh

# SenseAI

# SenseAI 是一个集成了 ASR（自动语音识别）、LLM（大型语言模型）、TTS（文本转语音）以及监控功能的多功能 AI 机器人。
# 它支持所有基于 OpenAI API 调用格式的模型，具有 LLM 模型流式输出的能力，并支持对话的打断功能。

# 系统要求
echo "注意：本项目目前仅支持 Windows 系统。"
echo "Linux 系统暂时不支持，可能会出现报错现象。"

# 快速开始

# 1. 构建虚拟环境
echo "创建并激活虚拟环境："
conda create -n senseai python=3.10 -y
conda activate senseai

# 2. 安装依赖
echo "安装项目依赖："
pip install -r requirements.txt

# 功能说明
echo "截至 8 月 10 日，目前仅上传了文字打断的功能演示。"
echo "未来几天内将逐步上传并集成 ASR、TTS、LLM 等完整功能。"
echo "您可以前往 demo 文件夹，使用已提供的文字打断功能进行体验。"
