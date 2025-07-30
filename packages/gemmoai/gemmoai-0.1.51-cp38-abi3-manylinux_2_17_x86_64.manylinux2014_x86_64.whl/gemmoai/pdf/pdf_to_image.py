import pymupdf
from pathlib import Path
from typing import List


def convert_pdf_to_images(
    pdf_path: str, output_dir: str, zoom_x: float = 1.0, zoom_y: float = 1.0
) -> List[Path]:
    """
    Convert a PDF file to a series of images.

    Args:
        pdf_path (str): The path to the PDF file.
        output_dir (str): The directory where the images will be saved.
    """

    # Create the output directory if it doesn't exist
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Open the PDF file
    doc = pymupdf.open(pdf_path)

    # Create the zoom matrix
    mat = pymupdf.Matrix(zoom_x, zoom_y)

    # Init the path to the images
    images_paths = []

    for page in doc:
        # Get the pixmap
        pix = page.get_pixmap(matrix=mat)

        # Save the image
        image_path = (output_dir / f"{pdf_path.stem}@page-{page.number}.png").resolve()

        # Save the image
        pix.save(image_path)

        # Add the image path to the list
        images_paths.append(image_path)

    return images_paths
