openai_api.py 文件里展示的是一个基本的打断功能
其中，代码是以流式的方式进行输出，而不是模型说完一整个的内容才进行输出。也就是说可以通过外部操作进行输出的打断。
```bash
python openai_api.py
```
后，可在模型说话期间通过键盘tab按键进行打断。打断后，尝试询问模型打断的内容，模型依旧会记住之前打断的内容。

![image](https://github.com/user-attachments/assets/0fd63100-bff4-408f-bba2-0990e06e47b7)
