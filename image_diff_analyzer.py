# image_diff_analyzer.py

import cv2
import numpy as np

from func import Logger

logger = Logger("ImageDiffAnalyzer", enable=True)

class ImageDiffAnalyzer:
    def __init__(self):
        self.diff:cv2.typing.MatLike
        self.threshold = 15
        pass

    def analyze(self, image_path1, image_path2):
        # 画像を読み込んでグレースケールに変換
        img1 = self.gray_scale(image_path1)
        img2 = self.gray_scale(image_path2)

        # サイズが異なる場合はリサイズ
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        # 差分画像の計算
        self.diff = cv2.absdiff(img1, img2)
        pass
    
    def get_diff_rate(self):
        # 変化度合いの割合を計算
        _, diff_thresh = cv2.threshold(self.diff, self.threshold, 255, cv2.THRESH_BINARY)
        total_diff_value = np.sum(self.diff)
        total_pixels = diff_thresh.size
        max_possible_diff = 255 * total_pixels
        rate = float(total_diff_value / max_possible_diff)
        return self.ease_out_circ(rate)

    def get_diff_area_rate(self):
        # 変化した面積の割合を計算
        _, diff_thresh = cv2.threshold(self.diff, self.threshold, 255, cv2.THRESH_BINARY)
        changed_pixels = np.sum(diff_thresh > 0)
        total_pixels = diff_thresh.size
        rate = changed_pixels / total_pixels
        return self.ease_out_circ(rate)

    @staticmethod
    def gray_scale(image_path)->cv2.typing.MatLike:
        # グレースケールに変換
        return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    @staticmethod
    def ease_out_circ(x:float)->float:
        return np.sqrt(1 - np.power(x - 1, 2))
    
    @staticmethod
    def ease_out_quad(x:float)->float:
        return 1 - (1 - x) ** 2

if __name__ == "__main__":
    from screen_capture import ScreenCapture
    import time

    capture = ScreenCapture()
    img1 = capture.capture_and_resize_and_save("captures/image-"+time.strftime("%Y%m%d%H%M%S"))
    time.sleep(10)
    img2 = capture.capture_and_resize_and_save("captures/image-"+time.strftime("%Y%m%d%H%M%S"))

    analyzer = ImageDiffAnalyzer()
    analyzer.analyze(img1, img2)
    logger.print(f"diff rate: {analyzer.get_diff_rate()}")
    logger.print(f"diff area rate: {analyzer.get_diff_area_rate()}")
