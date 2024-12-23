# main.py
from screen_capture import ScreenCapture
from image_diff_analyzer import ImageDiffAnalyzer
from image_send_gpt import ImageSendGPT
from voicevox_yomiage import VoicevoxYomiage, VV_Speaker

from dotenv import load_dotenv
import os
import queue
import time
import asyncio

from func import Logger

load_dotenv()

# ユーザー設定
#TODO: GUIで設定できるようにする

THRESHOLD_DIFF_RATE = 0.35
THRESHOLD_DIFF_RATE_MIN = 0.75
CAPTURE_INTERVAL = 10
CAPTURE_MIN_INTERVAL = 45
AI_MODE_ZUNDAMON = True
VOICEVOX_SPEAKER: VV_Speaker = VV_Speaker.ずんだもん
VOICEVOX_SPEED = 1.2
VOICEVOX_VOLUME = 1.0
ENABLE_VOICEVOX = True
ENABLE_NOTIFICATION = True

logger = Logger("main")
# TODO: 最初期化に必要なものをinit関数にまとめる
capture = ScreenCapture()
analyzer = ImageDiffAnalyzer()
vv = VoicevoxYomiage(speaker_id=VOICEVOX_SPEAKER.value, speed=VOICEVOX_SPEED)


API_KEY = os.getenv("OPENAI_API_KEY") or "your-openai-api-key-here"
gpt = ImageSendGPT(api_key=API_KEY, zundamon=AI_MODE_ZUNDAMON)
imgs_queue = queue.Queue()
ai_capture_interval: float = 0
last_capture_time: float = 0

from tasktray import TaskTray
tasktray = TaskTray()


def main():
    # TODO: 前回起動までに残っている画像を削除
    tasktray.start()
    while tasktray.active:
        asyncio.run(loop())
        time.sleep(CAPTURE_INTERVAL)
    pass

async def loop():
    global ai_capture_interval
    global last_capture_time

    img = capture.capture_and_resize_and_save("captures/image-"+time.strftime("%Y%m%d%H%M%S"))
    imgs_queue.put(img)

    if imgs_queue.qsize() >= 2:
        last_img = imgs_queue.get()
        analyzer.analyze(last_img, img)
        diff_rate = analyzer.get_diff_rate()
        diff_area_rate = analyzer.get_diff_area_rate()

        # TODO: 無視するアプリをユーザーが設定できるようにする

        # 前回のキャプチャからの経過時間が最小間隔を超えていない場合は閾値を0.75にする
        threshold = THRESHOLD_DIFF_RATE if (time.time() - last_capture_time > CAPTURE_MIN_INTERVAL) else THRESHOLD_DIFF_RATE_MIN
        logger.print(f"diff rate: {diff_rate}")
        logger.print(f"diff area rate: {diff_area_rate}")
        logger.print(f"calced rate: {diff_rate * diff_area_rate}")
        logger.print(f"threshold: {threshold} {diff_rate * diff_area_rate > threshold}")
        logger.print(f"next count: {(last_capture_time + ai_capture_interval) - time.time()}")

        if diff_rate * diff_area_rate > threshold or (time.time() - last_capture_time > ai_capture_interval):
            last_capture_time = time.time()

            # ChatGPTに画像を送信
            gpt.active_app_name = get_active_app_name()
            gpt_response = await gpt.send_image(img)

            # print(f"[ImageSendGPT] result: {gpt_result}")
            if gpt_response["content"].strip() != "":
                gpt_message = gpt_response["content"] # type: ignore
                
                ai_capture_interval = gpt_response["interval_seconds"] # type: ignore

                if ENABLE_NOTIFICATION:
                    await windows_notification(f"{gpt_message}")
                if ENABLE_VOICEVOX:
                    await vv.speak_and_play(gpt_message)
            else:
                if ENABLE_NOTIFICATION:
                    await windows_notification("<Skip message.>")
            pass
        
        try:
            # last_imgを削除
            # os.remove(last_img)
            pass
        except Exception as e:
            # 失敗したら諦める
            logger.print(f"error: {e}")
    pass






async def windows_notification(message):
    from plyer import notification
    notification.notify(
        title="DODO Screen AI",
        message=message,
        app_name="DODO Screen AI",
        timeout=5  # 通知が表示される秒数
    ) # type: ignore
    pass

def get_active_app_name()->str:
    import win32gui
    import win32process
    import psutil
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    process = psutil.Process(pid)
    title = win32gui.GetWindowText(hwnd)
    return f"{process.name()}:{title}"

if __name__ == "__main__":
    main()
    pass