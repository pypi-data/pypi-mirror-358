from yta_image_base.parser import ImageParser
from yta_programming.output import Output
from yta_constants.file import FileExtension
from yta_general_utils.dataclasses import FileReturned
from typing import Union
from PIL import Image


def pixelate_image(
    image,
    i_size,
    output_filename: Union[str, None] = None
) -> FileReturned:
    """
    Pixelates the provided 'image' and saves it as the 'output_filename' if
    provided.
    The 'i_size' is the pixelating square. The smaller it is, the less pixelated 
    its.

    'i_size' must be a tuple such as (8, 8) or (16, 16).
    """
    img = ImageParser.to_pillow(image)

    # Convert to small image
    small_img = img.resize(i_size, Image.BILINEAR)

    # Resize to output size
    res = small_img.resize(img.size, Image.NEAREST)

    output_filename = Output.get_filename(output_filename, FileExtension.PNG)
        
    return FileReturned(
        content = res,
        filename = output_filename
    )