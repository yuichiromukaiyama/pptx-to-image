from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import FileResponse
from pdf2image import convert_from_path
import os
import tempfile
import zipfile
import asyncio

load_dotenv()
API_KEY = os.getenv("API_KEY")

# 起動時に一時ファイルの置き場を作成する
BASE_DIR = os.path.join(os.path.dirname(__file__), "temp")
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)


async def run_subprocess(command: list) -> str:
    """
    非同期でサブプロセスを実行し、その標準出力を返す関数。

    この関数は、指定されたコマンドを非同期で実行し、サブプロセスの標準出力を文字列として返します。
    サブプロセスがエラーを返した場合は、例外を発生させます。

    Args:
        command (list): 実行するコマンドとその引数を含むリスト。

    Returns:
        str: サブプロセスの標準出力。

    Raises:
        Exception: サブプロセスがエラーを返した場合、例外が発生します。
    """
    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise Exception(f"Subprocess failed with error: {stderr.decode()}")
    return stdout.decode()


app = FastAPI()


@app.post("/convert/")
async def convert_pptx_to_images(
    file: UploadFile = File(...),
    x_api_key: str = Header(...),
):
    """
    アップロードされたPPTXファイルを画像に変換し、ZIPファイルとして返すエンドポイント。

    このエンドポイントは、アップロードされたPPTXファイルを受け取り、一時ディレクトリに保存します。
    その後、LibreOfficeを使用してPPTXファイルをPDFに変換し、PDFを画像に変換します。
    変換された画像はZIPファイルにまとめられ、クライアントに返されます。

    Args:
        file (UploadFile): アップロードされたPPTXファイル。

    Returns:
        FileResponse: 変換された画像を含むZIPファイルを返します。

    Raises:
        Exception: サブプロセスがエラーを返した場合、例外が発生します。
    """
    # APIキーの検証
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    temp_dir = tempfile.mkdtemp(dir=BASE_DIR)

    # ファイル名を設定（nullの場合はデフォルト値を使用）し、アップロードされたファイルを保存
    filename: str = file.filename if file.filename is not None else "unknown.pptx"
    pptx_path = os.path.join(temp_dir, filename)
    with open(pptx_path, "wb") as f:
        f.write(file.file.read())

    # PPTXファイルをPDFに変換
    pdf_path = pptx_path.replace(".pptx", ".pdf")
    await run_subprocess(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            pptx_path,
            "--outdir",
            temp_dir,
        ]
    )

    # PDFファイルを画像に変換
    image_paths = []
    for i, image in enumerate(convert_from_path(pdf_path, dpi=300)):
        image_path = os.path.join(temp_dir, f"slide_{i + 1}.jpg")
        image.save(image_path, "JPEG")
        image_paths.append(image_path)

    # 画像をZIPファイルにまとめる
    zip_path = os.path.join(temp_dir, "images.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for image_path in image_paths:
            zipf.write(image_path, os.path.basename(image_path))

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="images.zip",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
