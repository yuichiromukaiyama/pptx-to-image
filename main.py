from fastapi import Depends, FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import subprocess
from pdf2image import convert_from_path
import os
import tempfile
import zipfile

BASE_DIR = os.path.join(os.path.dirname(__file__), "temp")

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

app = FastAPI()


@app.post("/convert/")
async def convert_pptx_to_images(file: UploadFile = File(...)):
    temp_dir = tempfile.mkdtemp(dir=BASE_DIR)

    # ファイル名を設定（nullの場合はデフォルト値を使用）
    filename: str = file.filename if file.filename is not None else "unknown.pptx"
    # アップロードされたファイルを保存
    pptx_path = os.path.join(temp_dir, filename)
    with open(pptx_path, "wb") as f:
        f.write(file.file.read())

    # PPTXファイルをPDFに変換
    pdf_path = pptx_path.replace(".pptx", ".pdf")
    subprocess.run(
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
    images = convert_from_path(pdf_path, dpi=300)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(temp_dir, f"slide_{i + 1}.jpg")
        print(image_path)
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
