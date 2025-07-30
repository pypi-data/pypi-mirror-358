"""
Welcome to Youtube Autonomous Image Base module.

TODO: Try to apply the same 'with_' and 'apply_'
logic that in the 'yta_audio_editor' project to
keep the original image as it was or to transform
it in the instance.
"""
from yta_image_base.parser import ImageParser
from yta_image_base.converter import ImageConverter
from yta_image_base.size import ImageResizer
from yta_image_base.background import ImageBackgroundRemover
from yta_image_base.region.finder import ImageRegionFinder
# TODO: This 'ImageEditor' maybe should be not
# a class but methods inside the 'Image' class
from yta_image_base.edition.editor import ImageEditor
from PIL import Image as PillowImage
from typing import Union


class _Color:
    """
    Class to simplify the access to our image
    color changes for our custom Image class.
    This class must be used in our custom Image
    class.
    """

    image: any
    """
    Instance of our custom Image class to simplify
    the way we applicate color changes.
    """

    def __init__(
        self,
        image: 'Image'
    ):
        # TODO: Maybe receive the Pillow image instead (?)
        self.image = image.image

    # TODO: Talk about limits (yta_image\edition\settings.py)
    def set_temperature(
        self,
        factor: int = 0
    ):
        return ImageEditor.modify_color_temperature(self.image, factor)

    def set_contrast(
        self,
        factor: int = 0
    ):
        return ImageEditor.modify_contrast(self.image, factor)
    
    def set_brightness(
        self,
        factor: int = 0
    ):
        return ImageEditor.modify_brightness(self.image, factor)
    
    def set_sharpness(
        self,
        factor: int = 0
    ):
        return ImageEditor.modify_sharpness(self.image, factor)

    def set_white_balance(
        self,
        factor: int = 0
    ):
        return ImageEditor.modify_white_balance(self.image, factor)
    
    def set_color_hue(
        self,
        factor: int = 0
    ):
        return ImageEditor.modify_color_hue(self.image, factor)

class Image:
    """
    Class to wrap images and make easier the way we
    work with them.
    """

    image: PillowImage.Image
    """
    The image but stored as a Pillow image.
    """
    color: _Color
    """
    A shortcut to the available color changes. The
    color changes, once they are applied, return a new
    image. The original image remains unchanged.
    """
    # TODO: Rethink this variable and move to the
    # 'advanced' or 'filters' module
    _description: str
    """
    A description of the image, given by an engine that
    has been trained to describe images.
    """
    _green_regions: any
    """
    The green regions that have been found in the image.
    """
    _alpha_regions: any
    """
    The alpha (transparent) regions that have been found
    in the image.
    """

    @property
    def as_pillow(
        self
    ) -> PillowImage.Image:
        return self.image
    
    @property
    def as_numpy(
        self
    ) -> 'np.ndarray':
        return ImageConverter.pil_image_to_numpy(self.image)
    
    @property
    def as_opencv(
        self
    ) -> 'np.ndarray':
        return ImageConverter.pil_image_to_opencv(self.image)
    
    @property
    def as_base64(
        self
    ) -> str:
        return ImageConverter.pil_image_to_base64(self.image)
    
    @property
    def green_regions(
        self
    ):
        """
        The green regions that have been found in the image.
        This method will make a search the fist time it is
        accessed.
        """
        if not hasattr(self, '_green_regions'):
            self._green_regions = ImageRegionFinder.find_green_regions(self.image)

        return self._green_regions
    
    @property
    def alpha_regions(
        self
    ):
        """
        The alpha (transparent) regions that have been found
        in the image. This method will make a search the
        first time it is accessed.
        """
        if not hasattr(self, '_alpha_regions'):
            self._alpha_regions = ImageRegionFinder.find_transparent_regions(self.image)

        return self._alpha_regions

    def __init__(
        self,
        image: Union[
            str,
            'np.ndarray',
            PillowImage.Image
        ]
    ):
        self.image = ImageParser.to_pillow(image)
        self.color = _Color(self)

    def resize(
        self,
        size: tuple,
        output_filename: Union[str, None] = None
    ):
        """
        This method returns the image modified but
        does not modify the original image.
        """
        return ImageResizer.resize(self.image, size, output_filename).file_converted
    
    def remove_background(
        self,
        output_filename: Union[str, None] = None
    ):
        return ImageBackgroundRemover.remove_background(self.image, output_filename).file_converted

# TODO: Maybe I want to update the self.image when
# I modify something so I return a new Image
# instance with that modified image, so if you do
# image = image.filters.pixelate(10) you will update
# your image instance, but if you do
# n_image = image.filters.pixelate(10) you will get
# a new instance in n_image