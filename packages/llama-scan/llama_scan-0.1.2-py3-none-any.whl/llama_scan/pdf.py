import io
import pymupdf
from PIL import Image
from pathlib import Path
from tqdm import tqdm


def pdf_to_images(
    pdf_path: str, output_dir: Path, start: int = 0, end: int = 0
) -> None:
    """
    Convert PDF pages to images and save them to the specified output directory.

    Args:
        pdf_path (str): Path to the input PDF file
        output_dir (Path): Directory where the images will be saved
        start (int): The start page number (1-based). If 0, starts from first page.
        end (int): The end page number (1-based). If 0, goes until last page.
    """
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)

    # Validate page numbers
    if start < 0 or (start > total_pages and start != 0):
        raise ValueError(
            f"Start page number {start} is out of range. Document has {total_pages} pages."
        )
    if end < 0 or (end > total_pages and end != 0):
        raise ValueError(
            f"End page number {end} is out of range. Document has {total_pages} pages."
        )

    # Set default values for start and end
    start = 1 if start == 0 else start
    end = total_pages if end == 0 else end

    # Convert specified pages
    for page_num in tqdm(
        range(start, end + 1),
        desc="Converting pages to images",
        total=end - start + 1,
    ):
        page = doc[page_num - 1]  # Convert to 0-based index
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        output_path = output_dir / f"page_{page_num}.png"
        img.save(str(output_path))
