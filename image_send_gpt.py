# image_send_gpt.py

# OpenAI Assistant Manager Page
# https://platform.openai.com/assistants

import json
import time
import openai
import asyncio

from func import Logger

logger = Logger("ImageSendGPT", enable=False)

class ImageSendGPT:
    def __init__(self, api_key, zundamon=False):
        self.api_key = api_key

        self.client = openai.OpenAI(api_key=self.api_key)
        self.thread: Thread = None # type: ignore
        self.file_ids = []
        self.zundamon = zundamon
        self.active_app_name:str|None = None
        self.create_assistant()

        self.compressed_history = None

        asyncio.run(self.create_thread())

    def create_assistant(self):
        assistant_name = "dodo_image_send_gpt"
        if self.zundamon:
            assistant_name += "_zundamon"
        existing_assistant = next(
            (
                assistant
                for assistant in self.client.beta.assistants.list().data
                if assistant.name == assistant_name
            ),
            None,
        )

        if existing_assistant is None:
            logger.print(f"start create assistant.")
            if self.zundamon:
                self.assistant = self.client.beta.assistants.create(
                    name=assistant_name,
                    instructions="あなたは僕っ子ボーイッシュ幼馴染です。ため口で、語尾は「のだ」や「なのだ」です。幼馴染になりきって、なるべく短い文章の日本語で回答してほしいのだ。以下の画像から今の作業に対してアドバイスしてほしいのだ！",
                    model="gpt-4o",
                    tools=[
                        {"type": "file_search"},
                        {
                            "type": "function",
                            "function": {
                                "name": "analyze_image_for_advice",
                                "description": "アドバイスするかどうかを決定し、画像から現在の作業に対するアドバイスを行い、次にキャプチャするまでの秒数を設定するのだ。",
                                "strict": True,
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "content": {
                                            "type": "string",
                                            "description": "アドバイス内容なのだ。画面から操作者がどんな作業をしてるかを具体的に予想して、僕っ子ボーイッシュ幼馴染の「のだ口調」でなるべく短い文章で回答するのだ。長くても2文くらい。キャプチャとかのメタ部分には触れないでくれなのだ。",
                                        },
                                        "interval_seconds": {
                                            "type": "integer",
                                            "description": "次にキャプチャするまでの秒数なのだ。画像の内容から、アドバイスを頻繁に生成したほうがいい場合は小さく、アドバイスを生成しなくていい場合は大きくするのだ。標準は180秒くらいなのだ。",
                                        },
                                    },
                                    "required": [
                                        "content",
                                        "interval_seconds",
                                    ],
                                    "additionalProperties": False,
                                },
                            },
                        },
                    ],
                )
            else:
                self.assistant = self.client.beta.assistants.create(
                    name=assistant_name,
                    instructions="あなたはボーイッシュ幼馴染メイド女子高生です。ぼくの幼馴染になりきって、なるべく短い文章の日本語で回答してね。以下の画像から今の作業に対してアドバイスして！",
                    model="gpt-4o",
                    tools=[
                        {"type": "file_search"},
                        {
                            "type": "function",
                            "function": {
                                "name": "analyze_image_for_advice",
                                "description": "アドバイスするかどうかを決定し、画像から現在の作業に対するアドバイスを行い、次にキャプチャするまでの秒数を設定します。",
                                "strict": True,
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "content": {
                                            "type": "string",
                                            "description": "アドバイス内容。画面から操作者がどんな作業をしてるかを具体的に予想して、ボーイッシュ幼馴染の口調でなるべく短い文章で回答してね。長くても2文くらい。キャプチャとかのメタ部分には触れないでね。",
                                        },
                                        "interval_seconds": {
                                            "type": "integer",
                                            "description": "次にキャプチャするまでの秒数。画像の内容から、アドバイスを頻繁に生成したほうがいい場合は小さく、アドバイスを生成しなくていい場合は大きく。標準は180秒くらい。",
                                        },
                                    },
                                    "required": [
                                        "content",
                                        "interval_seconds",
                                    ],
                                    "additionalProperties": False,
                                },
                            },
                        },
                    ],
                )
            print(
                f"[ImageSendGPT] create assistant.\nassistant ID: {self.assistant.id}"
            )
        else:
            self.assistant = existing_assistant
            print(
                f"[ImageSendGPT] assistant already exists.\nassistant ID: {self.assistant.id}"
            )

    async def create_thread(self):
        self.thread = self.client.beta.threads.create()

    def clear_thread(self):
        logger.print(f"start clear thread.")
        messages = self.client.beta.threads.messages
        for message in messages.list(self.thread.id):
            self.client.beta.threads.messages.delete(
                message_id=message.id,
                thread_id=self.thread.id,
            )
        logger.print(f"clear thread.")

    def clear_files(self):
        # TODO: ストレージにあるファイルを全部削除する
        # TODO: ファイルのプロジェクト判別のためにファイル名にプレフィックスを付ける(どの段階でつけるかは要検討)
        logger.print(f"start clear files.")
        for file_id in self.file_ids:
            self.client.files.delete(file_id=file_id)
        self.file_ids = []
        logger.print(f"clear files.")

    async def send_image(self, image_path):
        try:
            # self.thread = self.client.beta.threads.create()
            if self.thread is None:
                asyncio.run(self.create_thread())

            # 画像ファイルをバイナリとして読み込む
            logger.print(f"start create file.")
            file = self.client.files.create(
                file=open(image_path, "rb"),
                purpose="vision",
            )
            file_id = file.id
            self.file_ids.append(file_id)
            print(f"create client file.\nfile ID: {file_id}")

            # メッセージの内容を作成
            # TODO: テキスト情報も送信する: 今の作業内容(ユーザに入力させる)とか
            logger.print(f"start create message.")
            content = []
            content.append({"type": "image_file", "image_file": {"file_id": file_id}})
            # self.compressed_historyがあれば、メッセージに追加する
            if self.compressed_history is not None:
                content.append({"type": "text", "text": "過去の履歴: "+self.compressed_history})
                self.compressed_history = None
            if self.active_app_name is not None:
                content.append({"type": "text", "text": "現在アクティブなウィンドウ: "+self.active_app_name})
                self.active_app_name = None
                
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=content,
            )

            # ランを作成
            logger.print(f"start create run.")
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
            )
            logger.print(f"end create run.")

            tool_outputs = []

            logger.print(f"run")
            for tool in run.required_action.submit_tool_outputs.tool_calls: # type: ignore
                logger.print(f"tool: {tool.function.name}")
                tool_outputs.append(
                    {
                        "tool_call_id": tool.id,
                        "output": tool.function.arguments,
                    }
                )

            logger.print(f"start submit tool outputs.")
            run = self.client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=self.thread.id, run_id=run.id, tool_outputs=tool_outputs
            )

            # 既存のランが終了していない場合は明示的に終了する
            logger.print(f"start check run status.")
            if run.status in ["queued", "in_progress"]:
                logger.print(f"wait run end...\nrun status: {run.status}")
                while run.status in ["queued", "in_progress"]:
                    run = self.client.beta.threads.runs.retrieve(
                        thread_id=self.thread.id, run_id=run.id
                    )
                    time.sleep(0.5)
                logger.print(f"run end.\nrun status: {run.status}")
                
            self.clear_files()
            await self.create_thread()

            if tool_outputs[0]["output"] != "":
                tool_output_obj = self.json_dumps(tool_outputs[0]["output"])

            # compressed_history_promptがあれば、保存する
            if tool_output_obj is not None and "compressed_history_prompt" in tool_output_obj:
                if tool_output_obj["compressed_history_prompt"].strip() != "":
                    self.compressed_history = tool_output_obj["compressed_history_prompt"]
            else:
                self.compressed_history = None

            print(f"tool outputs: {tool_outputs}")
            return tool_output_obj

        except Exception as e:
            logger.print(f"error: {e}")
            return f"[ImageSendGPT] error: {e}"

        finally:
            pass

    def send_chat(self, message):
        # TODO: チャットを送信する
        pass

    # Json形式かをチェックして、できるならobjectに変換する
    @staticmethod
    def json_dumps(json_str):
        try:
            return json.loads(json_str)
        except:
            return None


# 使い方の例
if __name__ == "__main__":
    from screen_capture import ScreenCapture
    from dotenv import load_dotenv
    import os
    # OpenAI APIキー設定
    load_dotenv()
    API_KEY = os.getenv("OPENAI_API_KEY")

    # 画像キャプチャ
    cap = ScreenCapture()
    img_path = cap.capture_and_resize_and_save()
    print(f"画像を保存しました: {img_path}")

    # GPTに画像を送信
    gpt = ImageSendGPT(API_KEY)
    response = asyncio.run(gpt.send_image(img_path))
    print("ChatGPTの応答:", response)

