"""
Module to apply filters to images. As simple as
choose the filter available and apply to the
desired image.

This module includes a new 'Image' class that
has the 'filter' functionality to apply the
filters we have available in an easy way.

TODO: Refactor the methods to accept the same
type of 'image' parameter in all of them, being
able ot handle files, pillow, numpy, etc.
"""
from yta_image_advanced_filters.gameboy import image_file_to_gameboy
from yta_image_advanced_filters.sticker import image_file_to_sticker
from yta_image_advanced_filters.pixelate import pixelate_image
from yta_image_advanced_filters.motion_blur import MotionBlurDirection, apply_motion_blur
from yta_general_utils.dataclasses import FileReturned
from typing import Union


class ImageFilter:
    """
    Class to simplify and encapsulate the functionality
    related to applying filters to an image.
    """

    @staticmethod
    def to_gameboy(
        image_filename: str,
        output_filename: Union[str, None] = None
    ) -> FileReturned:
        """
        Apply the original GameBoy colors palette to the provided
        'image_filename'.
        """
        return image_file_to_gameboy(image_filename, output_filename)
    
    @staticmethod
    def pixelate(
        image: any,
        pixel_size: int = 8,
        output_filename: Union[str, None] = None
    ) -> FileReturned:
        """
        Pixelates the provided 'image_filename' and saves
        it as the 'output_filename'. The smaller the
        'pixel_size' is, the less pixelated the image
        becomes.

        We recommend you a 'pixel_size' between 8 and 16.
        """
        return pixelate_image(image, (pixel_size, pixel_size), output_filename)
    
    @staticmethod
    def to_sticker(
        image_filename: str,
        output_filename: Union[str, None] = None
    ) -> FileReturned:
        """
        Turn the provided 'image_filename' into a sticker, which
        is the same image without the background and with a new
        white and wide border.
        """
        # TODO: Check that it is a valid 'image_filename'
        # TODO: Refactor to accept other image types, not only files
        return image_file_to_sticker(image_filename, output_filename)
    
    @staticmethod
    def motion_blur(
        image: any,
        kernel_size: int = 30,
        direction: MotionBlurDirection = MotionBlurDirection.HORIZONTAL,
        output_filename: Union[str, None] = None
    ) -> FileReturned:
        """
        Apply a Motion Blur effect, in the given 'direction', to
        the provided 'image'.
        """
        if kernel_size <= 0:
            raise Exception('The "kernel_size" parameter must be a positive number.')

        return apply_motion_blur(image, kernel_size, direction, output_filename)
    
    # TODO: Add 'image_to_sketch' if working, but I
    # think it is too heavy processing for a filter
    # that is not interesting...


# TODO: Maybe move this 'Image' class to another file
class Image:
    """
    TODO: Do I need to put the description here
    instead of in the '_Image' instance I return (?)
    """

    def __new__(
        cls,
        *args,
        **kwargs
    ):
        try:
            from yta_image_advanced import Image as AdvancedImage
        except ImportError as e:
            raise ImportError(
                f'The "Image" class of this module needs the "yta_image_advanced" module installed.'
            ) from e

        class _Filter:
            """
            Class to simplify the access to our filters 
            for our custom Image class. This class must
            be used in our custom Image class.
            """

            image: any
            """
            Instance of our custom Image class to simplify
            the way we applicate filters.
            """

            def __init__(
                self,
                image: 'Image'
            ):
                # TODO: Maybe receive the Pillow image instead (?)
                self.image = image.image

            def pixelate(
                self,
                pixel_size: int,
                output_filename: Union[str, None] = None
            ):
                return ImageFilter.pixelate(self.image, pixel_size, output_filename)

            def motion_blur(
                self,
                kernel_size: int = 30,
                direction: MotionBlurDirection = MotionBlurDirection.HORIZONTAL,
                output_filename: Union[str, None] = None
            ):
                return ImageFilter.motion_blur(self.image, kernel_size, direction, output_filename)
            
            def to_gameboy(
                self,
                output_filename: Union[str, None] = None
            ):
                return ImageFilter.to_gameboy(self.image, output_filename)
            
            def to_sticker(
                self,
                output_filename: Union[str, None] = None
            ):
                return ImageFilter.to_sticker(self.image, output_filename)

        class _Image(AdvancedImage):
            """
            Advanced Image class that includes filtering
            functionality.
            """

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.filter: _Filter = _Filter(self)
                """
                A shortcut to the available filters. The filters,
                once they are applied, return a new image. The
                original image remains unchanged.
                """
        
        instance = _Image(*args, **kwargs)

        return instance