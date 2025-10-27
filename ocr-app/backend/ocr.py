from typing import List, Tuple
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import pytesseract
from pdf2image import convert_from_bytes
import io

def _preprocess(img: Image.Image) -> Image.Image:
    # Gris + légère amélioration de contraste + léger sharpen
    g = ImageOps.grayscale(img)
    g = ImageEnhance.Contrast(g).enhance(1.4)
    g = g.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
    # Option: upscale léger si trop petite
    if min(g.size) < 800:
        ratio = 800 / min(g.size)
        g = g.resize((int(g.width*ratio), int(g.height*ratio)), Image.LANCZOS)
    return g

def images_from_file(file_bytes: bytes, filename: str, dpi: int = 300) -> List[Image.Image]:
    name = filename.lower()
    if name.endswith(".pdf"):
        # PDF -> liste d'images
        pages = convert_from_bytes(file_bytes, dpi=dpi)
        return pages
    # Image -> 1 image
    img = Image.open(io.BytesIO(file_bytes))
    return [img.convert("RGB")]

def ocr_images(images: List[Image.Image], lang: str = "eng+fra") -> Tuple[str, List[str]]:
    page_texts: List[str] = []
    for page in images:
        pimg = _preprocess(page)
        text = pytesseract.image_to_string(
            pimg,
            lang=lang,
            config="--oem 3 --psm 6"
        )
        page_texts.append(text.strip())
    full_text = "\n\n==== PAGE BREAK ====\n\n".join(page_texts)
    return full_text, page_texts
