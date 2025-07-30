import base64
from io import BytesIO
from PIL import Image


def convert_image_to_base64(
    pillow_image: Image.Image = None, image_path: str = None
) -> str:
    """
    Convert an image to a base64-encoded string.

    This function accepts either a Pillow Image object or a file path to an image.
    It returns the base64 representation of the image in PNG format.

    Parameters:
    - pillow_image (Image.Image, optional): A Pillow Image object. Default is None.
    - image_path (str, optional): A file path to the image. Default is None.

    Returns:
    - str: The base64-encoded string of the image.

    Raises:
    - ValueError: If neither pillow_image nor image_path is provided.
    """

    if pillow_image is None and image_path is None:
        raise ValueError("Either pillow_image or image_path must be provided")

    if pillow_image is None:
        pillow_image = Image.open(image_path)

    # Create a BytesIO buffer to hold the image data in memory
    buffered = BytesIO()

    # Save the image to the buffer in PNG format
    pillow_image.save(buffered, format="PNG")

    # Encode the buffer's contents as a base64 string and decode to UTF-8
    image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Return the base64-encoded string
    return image_base64
