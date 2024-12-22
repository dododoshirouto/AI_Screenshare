# AI Screenshare Test 01

## 概要

- PCの画面を定期的にChatGPTに送信し、アドバイスや雑談をしてくれる

### 処理の流れ

1. PC画面を定期的にキャプチャする
2. キャプチャした画像をChatGPTに送信する
3. ChatGPTからの回答を受信する
4. 回答を表示する

## 使用するライブラリ

- python=3.12.8

モジュールは`requirments.txt`を参照してください

## Tooltop

### ChatGPT の APIキーページ

[ChatGPT の APIキーページ](https://platform.openai.com/api-keys)

`.evn`ファイルを作成し、`OPENAI_API_KEY`を設定する

```env
OPENAI_API_KEY=ここにAPIキー
```

## Installation

### 仮想環境の有効化

```bash
IF NOT EXIST venv (
    python -m venv venv
)
IF NOT EXIST activate.bat (
    echo venv/Scripts/activate > activate.bat
)
IF NOT EXIST install.bat (
    echo pip install -r requirements.txt > install.bat
)

```

### Jupyter Notebookでvenvを有効にする

```bash
activate.bat
pip install ipykernel
python -m ipykernel install --user --name ai_screenshhare_test01

```

### voicevox_coreのダウンロード

```bash
# voicevox-download-windows-x64.exe --device cuda -v 0.15.4 -o ./
voicevox-download-windows-x64.exe -v 0.15.4 -o ./
```