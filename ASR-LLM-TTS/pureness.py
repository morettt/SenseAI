import io
import os
import re
import ffmpeg
import ast
import requests
import logging
import time
import sys

logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为INFO
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[

        logging.StreamHandler()  # 输出到控制台
    ]
)
limit = 2000
sys.setrecursionlimit(limit)


def role2id(role):
    speaker = m1.get_speaker()
    for s in range(len(speaker)):
        if role == speaker[s]:
            return s


def id2role(id):
    import re
    speaker = m1.get_speaker()
    for e in range(len(speaker)):
        pattern = r"\（.*?\）"
        speaker[e] = re.sub(pattern, "", speaker[e], re.S)
    return speaker[int(id)]


class CUT200:
    def __init__(self):
        self.new = []
        self.newnew = []

    def slice_string(self, text):

        if len(text) < 100:
            return text

        mid_index = len(text) // 2
        left_part = ''
        right_part = ''

        for i in range(mid_index, -1, -1):
            if text[i] in ['，', '。', '！', '？', '!', '.', '?', '~', '～', ',', '.']:  # '、', '」', '」', '“', '，', '。'
                left_part = text[:i + 1]
                right_part = text[i + 1:]
                break

        return left_part, right_part

    def str2list(self, content):
        if isinstance(content, str):
            content_list = ['']
            content_list[0] = content

            return self.main_cutting(content_list)

    def main_cutting(self, content):

        self.newnew = content
        start = time.time()
        for i in range(50):
            self.new = []

            for l in self.newnew:

                if len(l) > 100:

                    left, right = self.slice_string(l)

                    self.new.append(left)
                    self.new.append(right)

                else:
                    selfless = self.slice_string(l)
                    self.new.append(selfless)
            # self.new = [item for item in content_list if item != '' and item is not None]
            string_list = []
            for item in self.new:
                string_list.append(str(item))
            self.new = [item for item in self.new if item != '' and item is not None]
            self.new = string_list
            self.newnew = self.new

        end = time.time()
        print(f'切片完成，耗时{end - start}')
        return [item for item in self.new if item != '' and item is not None]


class conbined_wavs:

    def __init__(self):
        self.detail_name = None
        self.name = None

    def make_valid_filename(self, filename):
        import re
        import os
        # 去除非法字符
        valid_filename = re.sub(r'[<>:"/\\|?*\s]', '', filename)

        # # 删除连续的空格
        # valid_filename = re.sub(r'\s+', ' ', valid_filename)

        return valid_filename

    def add_name(self, name):
        self.name = self.make_valid_filename(str(name))

    def conbine(self, wavs):
        import ffmpeg
        content_list = wavs
        ffmpeg_path = r'./ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe'

        # 设置输入文件和输出文件路径
        input_files = content_list  # 假设content_list是包含待拼接语音文件的列表
        # output_file = '路径/输出文件.wav'

        input_streams = [ffmpeg.input(filename) for filename in input_files]
        output = ffmpeg.concat(*input_streams, v=0, a=1)

        out_filename = f'{self.name}.wav'
        output = ffmpeg.output(output, out_filename)

        ffmpeg.run(output, cmd=ffmpeg_path)

        # inputs = []
        # for file in input_files:
        #     inputs.append(ffmpeg.input(file))
        #
        # # 合并输入流到一个输出流中
        # output = ffmpeg.concat(*inputs, v=0, a=1).output(f'{self.name}.wav')
        # ffmpeg.run(output, cmd=ffmpeg_path)
        # for file_name in content_list:
        #     if os.path.exists(file_name):
        #         os.remove(file_name)
        #         print(f"已删除临时文件: {file_name}")
        #     else:
        #         print(f"临时文件不存在: {file_name}")




class main:
    def __init__(self):
        self.content = []
        self.wavs = []

    def read(self, speakers, tempid, _long, noise, noisew, content, filename):
        self.content = content.replace('\n ', '').replace('\n', '').replace('　　', '').replace('   ',
                                                                                              '').replace(
            'amp;', '')
        if self.content:
            self.content = c3.str2list(self.content)
            length = len(self.content)
            speaker = '123'
            files = []

            for i in range(len(self.content)):
                pattern = r'恢(.*?)皿'
                self.content[i] = re.sub(pattern, r'恢父皿', self.content[i])
            self.content = [item.replace('炸一炸', '杂一杂') for item in self.content]
            # print(self.content)
            for i in range(length):
                time.sleep(0.01)
                file = f'./temp/{time.time()}.wav'
                files.append(file)
            index = [0] * length
            print(self.content)
            for i in range(length):
                process = f'{i}/{length}'
                logging.info(f'{process}|{speaker}|{self.content[i][:1]}......')
                # url = f'https://www.纯度.site/run?text={self.content[i]}&id_speaker={tempid}&length={_long}&noise={noise}&noisew={noisew}'
                url = f'http://cn-hk-bgp-6.ofalias.net:28666/tts?text={self.content[i]}&batch_size=8'
                r = requests.get(url)
                stream = io.BytesIO(r.content)

                with open(files[i], "wb") as f:
                    f.write(stream.getvalue())
                file_size = os.path.getsize(files[i])

                if file_size < 1024:
                    index[i] = 0
                    os.remove(files[i])
                else:
                    self.wavs.append(files[i])
                    index[i] = 1

            for j in range(30):
                for i in range(len(index)):
                    if index[i] == 0:
                        process = f'合成失败音频{i}'
                        logging.info(f'{process}|{speaker}|{self.content[i][:1]}......')
                        # url = f'https://www.纯度.site/run?text={self.content[i]}&id_speaker={tempid}&length={_long}&noise={noise}&noisew={noisew}'

                        url = f'http://cn-hk-bgp-6.ofalias.net:28666/tts?text={self.content[i]}&batch_size=8'
                        print(url)
                        r = requests.get(url)
                        stream = io.BytesIO(r.content)
                        with open(files[i], "wb") as f:
                            f.write(stream.getvalue())
                        file_size = os.path.getsize(files[i])
                        if file_size < 1024:  # 1KB = 1024 bytes
                            index[i] = 0
                            os.remove(files[i])
                        else:
                            index[i] = 1
            c1.add_name(f'{filename}')
            print(files, 'wavs')
            c1.conbine(files)
            print(f'{filename}合成完成')
            m1.del_folders(files)
            self.wavs = []

    def del_folders(self, wavs):
        import os

        # 获取目标文件夹中的所有文件名

        # 遍历文件名，并删除文件
        for wav in wavs:
            os.remove(wav)
            print(f'删除{wav}')

    def get_speaker(self):
        # r=requests.get(url='https://www.baidu.com')
        # data_dict = r.json()["models"]  # 将 JSON 响应转换为字典
        # new_list = [item.split(':')[1].strip() for item in data_dict]
        data_dict=[]
        print(data_dict)

        return data_dict

if __name__ == '__main__':
    c1 = conbined_wavs()
    c3 = CUT200()
    m1 = main()
    try:
        import os

        # 指定目标文件夹的路径
        folder_path = 'vits'

        # 获取目标文件夹中的所有文件名
        file_names = os.listdir(folder_path)
        file_paths = []

        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            file_paths.append(file_path)

        speakers = m1.get_speaker()
        tempid = int(input('输入模型ID（输入数字:'))
        _long = float(input('输入长度(越长越慢,按回车选取默认值1.1)：') or 1.1)
        noise = float(input('输入控制感情起伏(按回车选取默认值0.37)：') or 0.37)
        noisew = float(input('输入控制音素发音长度(按回车选取默认值0.2)：') or 0.2)
        file_names = sorted(file_names)
        for file_path in range(len(file_paths)):
            with open(file_paths[file_path], 'r', encoding='utf-8') as file:
                content = file.read()

            m1.read(speakers, tempid, _long, noise, noisew, content, file_names[file_path])
        # raise Exception("gg")
    except Exception as e:
        print("发生错误：", str(e), '遇到问题请加群691432604')
        input("按任意键继续...")
        sys.exit(1)
        # input('出现意料之外的情况，联系qq1071718696')
    # print(m1.get_speaker())
