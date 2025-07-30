"""
Image edition module.

Interesting links below:
- https://www.geeksforgeeks.org/image-enhancement-techniques-using-opencv-python/
- https://www.geeksforgeeks.org/changing-the-contrast-and-brightness-of-an-image-using-python-opencv/
"""
from yta_image_base.parser import ImageParser
from yta_image_base.edition.editor import ImageEditor as BaseImageEditor
from yta_file.handler import FileHandler
from PIL import Image
from pillow_lut import load_cube_file
from typing import Union

import numpy as np

class ImageEditor(BaseImageEditor):
    """
    Class to simplify and encapsulate all the
    functionality related to image edition.
    
    This ImageEditor class includes the basic
    functionality from the basic editor.
    """

    def __init__(
        self
    ):
        super().__init__()

    @staticmethod
    def apply_3d_lut(
        image: Union[str, Image.Image, np.ndarray],
        lut_3d_filename: str
    ):
        """
        Apply a 3D Lut table, which is loaded from the
        provided 'lut_3d_filename' .cube file, to the
        also given 'image'.

        Thanks to:
        - https://stackoverflow.com/questions/73341263/apply-3d-luts-cube-files-into-an-image-using-python
        """
        if not FileHandler.is_file(lut_3d_filename):
            raise Exception('The "lut_3d_filename" provided is not a valid file.')
        # TODO: Improve the validation to check that is .cube
        
        return ImageParser.to_pillow(image).filter(load_cube_file(lut_3d_filename))