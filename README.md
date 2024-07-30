# PPTX to Images Converter API

このプロジェクトは、アップロードされたPPTXファイルを画像に変換し、ZIPファイルとして返すAPIです。FastAPIを使用して構築されており、非同期処理を活用して効率的にファイル変換を行います。

## 機能

- PPTXファイルをPDFに変換
- PDFを画像に変換
- 変換された画像をZIPファイルにまとめて返す

## 使用技術

- Python 3.8+
- FastAPI
- asyncio
- LibreOffice
- pdf2image
- zipfile

## インストール

1. リポジトリをクローンします。

```bash
git clone https://github.com/yuichiromukaiyama/pptx-to-image
cd pptx-to-images-api
```

2. 仮想環境を作成し、アクティベートします。

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. 必要なパッケージをインストールします。

```bash
pip install -r requirements.txt
```

4. LibreOfficeをインストールします。以下のコマンドでインストールできます。

```bash
sudo apt-get install libreoffice  # Ubuntu
brew install --cask libreoffice  # macOS
```

## 使用方法

1. サーバーを起動します。

```bash
uvicorn main:app --reload
```

2. ブラウザで以下のURLにアクセスして、APIのドキュメントを確認します。

```
http://127.0.0.1:8000/docs
```

3. `/convert/` エンドポイントにPOSTリクエストを送信して、PPTXファイルをアップロードします。例えば、`curl`を使用して以下のようにリクエストを送信できます。

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/convert/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path_to_your_pptx_file.pptx'
```

## エンドポイント

### `POST /convert/`

アップロードされたPPTXファイルを画像に変換し、ZIPファイルとして返します。

- **リクエストパラメータ**:
- `file` (UploadFile): アップロードされたPPTXファイル。

- **レスポンス**:
- `FileResponse`: 変換された画像を含むZIPファイルを返します。

