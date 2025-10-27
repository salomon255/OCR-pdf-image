from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Optional
from ocr import images_from_file, ocr_images

app = FastAPI(title="OCR API")

# Autoriser ton front local / domaine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # mets ton domaine en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ocr")
async def ocr_endpoint(
    file: UploadFile = File(...),
    lang: str = Form("eng+fra"),
    dpi: int = Form(300),
    format: Optional[str] = Form("json")
):
    fb = await file.read()
    try:
        images = images_from_file(fb, file.filename, dpi=dpi)
        full_text, pages = ocr_images(images, lang=lang)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    if format == "text":
        return PlainTextResponse(full_text, media_type="text/plain; charset=utf-8")

    return {
        "filename": file.filename,
        "pages": len(pages),
        "lang": lang,
        "text": full_text
    }

@app.get("/")
def root():
    return {"ok": True, "service": "OCR API"}
