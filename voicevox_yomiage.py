# voicevox_yomiage.py
# Reference: https://qiita.com/taka7n/items/1dc61e507274b93ee868

from enum import Enum

class VV_Speaker(Enum):
    四国めたん = 2
    ずんだもん = 3
    春日部つむぎ = 8

# https://note.com/closer0502/n/ncd5745ef43ca

from pathlib import Path
from voicevox_core import VoicevoxCore, METAS
import pyaudio
import asyncio

import re



class VoicevoxYomiage:
    def __init__(self, speaker_id: int, speed:float = 1.2, jtalk_path: str="open_jtalk_dic_utf_8-1.11"):
        self.speaker_id = speaker_id
        self.speed_scale = speed

        self.jtalk_path = Path(jtalk_path)
        self.core = VoicevoxCore(open_jtalk_dict_dir=self.jtalk_path)
        self.core.load_model(self.speaker_id)  # 指定したidのモデルを読み込む
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

        self.eng_to_kana_init()

    # TODO: 再生デバイスを設定できるようにする
    # TODO: 音量を設定できるようにする
    async def speak_and_play(self, text: str):
        # wave_bytes = self.core.tts(text, self.speaker_id)  # 音声合成を行う
        # https://voicevox.github.io/voicevox_core/apis/python_api/autoapi/voicevox_core/index.html
        aq = self.core.audio_query(self.eng_to_kana(text), self.speaker_id)
        aq.speed_scale = self.speed_scale
        wave_bytes = self.core.synthesis(aq, self.speaker_id)
        self.stream.write(wave_bytes)
        # self.stream.stop_stream()
        # self.stream.close()
        # self.pa.terminate()

    def set_speaker(self, speaker_id: int):
        self.speaker_id = speaker_id
        self.core.load_model(self.speaker_id)  # 指定したidのモデルを読み込む

    def set_speed(self, speed: float):
        self.speed_scale = speed
    



    def eng_to_kana_init(self):

        dic_file = 'bep-eng.dic.txt'
        self.kana_dict = {}
        with open(dic_file, mode='r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                line_list = line.replace(r'\n', '').split(' ')
                self.kana_dict[line_list[0]] = line_list[1]

        self.reduction=[["It\'s","イッツ"],["I\'m","アイム"],["You\'re","ユーァ"],["He\'s","ヒーィズ"],["She\'s","シーィズ"],["We\'re","ウィーアー"],["They\'re","ゼァー"],["That\'s","ザッツ"],["Who\'s","フーズ"],["Where\'s","フェアーズ"],["I\'d","アイドゥ"],["You\'d","ユードゥ"],["I\'ve","アイブ"],["I\'ll","アイル"],["You\'ll","ユール"],["He\'ll","ヒール"],["She\'ll","シール"],["We\'ll","ウィール"]]



    # TODO: TransferNoda から発掘してくる
    def eng_to_kana(self, text:str) -> str:
        # 読みたい記号。他の単語と混ざらないように、前後に半角スペースを挟む
        text = text.replace("+"," プラス ").replace("＋"," プラス ").replace("-"," マイナス ").replace("="," イコール ").replace("＝"," イコール ")

        # No.2、No6みたいに、No.の後に数字が続く場合はノーではなくナンバーと読む
        text = re.sub(r'No\.([0-9])',"ナンバー\\1",text)
        text = re.sub(r'No([0-9])',"ナンバー\\1",text)

        # 短縮形の処理
        for red in self.reduction: text = text.replace(red[0]," "+red[1]+" ")

        # this is a pen.のように、aの後に半角スペース、続いてアルファベットの場合、エーではなくアッと呼ぶ
        text = re.sub(r'a ([a-zA-Z])',"アッ \\1",text)

        # 文を区切る文字は消してはダメなので、前後に半角スペースを挟む
        text = text.replace("."," . ").replace("。"," 。 ").replace("!"," ! ").replace("！"," ！ ")

        # アルファベットとアルファベット以外が近接している時、その間に半角スペースを挟む（この後、英単語を単語ごとに区切るための前準備）
        text_l=list(text)
        for i in range(len(text))[::-1][:-1]:
            if re.compile("[a-zA-Z]").search(text_l[i]) and re.compile("[^a-zA-Z]").search(text_l[i-1]): text_l.insert(i," ")
            elif re.compile("[^a-zA-Z]").search(text_l[i]) and re.compile("[a-zA-Z]").search(text_l[i+-1]): text_l.insert(i," ")

        text = "".join(text_l)

        # 半角スペースや読まなくて良い文字で区切り、各単語の英語をカタカナに変換
        text_split = re.split(r'[ \,\*\-\_\=\(\)\[\]\'\"\&\$　]',text)
        for i in range(len(text_split)):
            if str.upper(text_split[i]) in self.kana_dict:
                text_split[i] = self.kana_dict[str.upper(text_split[i])]

        return ("".join(text_split))


if __name__ == "__main__":
    async def main():
        vv = VoicevoxYomiage(speaker_id=VV_Speaker.四国めたん.value)
        await vv.speak_and_play("こんにちは、これはTestです。EDGE WISE")
        print("終了")

    asyncio.run(main())
