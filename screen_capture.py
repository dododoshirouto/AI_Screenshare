# screen_capture.py

import mss
import mss.tools
from PIL import Image
from enum import Enum

from func import Logger

logger = Logger("ScreenCapture", enable=False)

class ImageFormat(Enum):
    WEBP = "WEBP"
    PNG = "PNG"
    JPEG = "JPEG"

class ScreenCapture:
    def __init__(self, scale=0.5, format=ImageFormat.WEBP, quality=80, filename="captures/latest"):
        self.scale = scale
        self.format = format
        self.quality = quality
        self.filename = filename
    
    """
    :return: 保存したファイルパス
    """
    def capture_and_resize_and_save(self, filename=None) -> str:
        if filename is None:
            filename = self.filename
        with mss.mss() as sct:
            # 全画面キャプチャ
            logger.print(f'start capture.')
            screenshot = sct.grab(sct.monitors[1])
            logger.print(f'end capture.')

            # キャプチャした画像データをPillowで扱えるようにする
            logger.print(f'start convert to Pillow.')
            img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
            logger.print(f'end convert to Pillow.')

            # 元画像の幅・高さを取得
            w, h = img.size
            
            # リサイズ倍率を適用
            new_w = int(w * self.scale)
            new_h = int(h * self.scale)
            
            logger.print(f'start resize.')
            img_resized = img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)
            logger.print(f'end resize.')

            # ファイルパスを生成
            file_path = f"{filename}.{self.format.value.lower()}"

            # 画像を保存
            logger.print(f'start save.')
            import os
            # フォルダが存在しなかったら作成する
            folder = os.path.dirname(file_path)
            if not os.path.exists(folder):
                os.makedirs(folder)
            img_resized.save(file_path, format=self.format.value, quality=self.quality)
            logger.print(f'end save.')
            
            return file_path

# 使い方の例
if __name__ == '__main__':
    cap = ScreenCapture(0.4, ImageFormat.WEBP, 80, "capture")
    img_path = cap.capture_and_resize_and_save()
    import os

    # 保存された画像をデフォルトアプリで表示
    os.system(f"start {img_path}")