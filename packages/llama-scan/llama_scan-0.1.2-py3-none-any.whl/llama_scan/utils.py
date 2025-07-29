from pathlib import Path
from PIL import Image


def setup_output_dirs(output_base: Path) -> tuple[Path, Path]:
    """
    Create and return paths for image and text output directories.

    Args:
        output_base (Path): The base directory for output.
    """
    image_dir = output_base / "images"
    text_dir = output_base / "text"

    image_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    return image_dir, text_dir


def resize_image(image_path: str, output_path: str, width: int) -> None:
    """
    Resize an image to the specified width while maintaining aspect ratio.

    Args:
        image_path (str): Path to the input image file
        output_path (str): Path where the resized image will be saved
        width (int): Desired width of the image
    """
    if width == 0:
        return
    else:
        img = Image.open(image_path)
        w_percent = width / float(img.size[0])
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((width, h_size), Image.Resampling.LANCZOS)
        img.save(output_path)


def merge_text_files(text_dir: Path) -> Path:
    """
    Merge all individual text files into a single merged file.

    Args:
        text_dir (Path): Directory containing individual text files.

    Returns:
        Path: Path to the created merged file.
    """
    text_files = sorted(text_dir.glob("page_*.txt"))
    merged_file = text_dir / "merged.txt"

    if text_files:
        with open(merged_file, "w", encoding="utf-8") as merged_f:
            for text_file in text_files:
                with open(text_file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read().strip()
                    if content:  # Only add non-empty content
                        merged_f.write(content + "\n\n")

    return merged_file
