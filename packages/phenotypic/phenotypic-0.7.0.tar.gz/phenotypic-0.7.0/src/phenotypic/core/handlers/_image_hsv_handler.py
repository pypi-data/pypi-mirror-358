from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: from phenotypic import Image

from typing import Optional, Union
import numpy as np
from skimage.color import rgb2hsv
from os import PathLike

from ..accessors import HsvAccessor
from ._image_objects import ImageObjectsHandler
from phenotypic.util.constants_ import IMAGE_FORMATS
from phenotypic.util.exceptions_ import IllegalAssignmentError


class ImageHsvHandler(ImageObjectsHandler):
    """Adds HSV format support for the color measurement module."""

    def __init__(self, input_image: Optional[Union[np.ndarray, Image, PathLike]] = None, imformat: str = None, name: str = None):
        super().__init__(input_image=input_image, imformat=imformat, name=name)
        self._accessors.hsv = HsvAccessor(self)

    @property
    def _hsv(self) -> np.ndarray:
        """Returns the hsv array dynamically of the current _root_image.

        This can become computationally expensive, so implementation may be changed in the future.

        Returns:
            np.ndarray: The hsv array of the current _root_image.
        """
        if self.imformat.is_matrix():
            raise AttributeError('Grayscale images cannot be directly converted to hsv. Convert to RGB first')
        else:
            match self.imformat:
                case IMAGE_FORMATS.RGB:
                    return rgb2hsv(self.array[:])
                case _:
                    raise ValueError(f'Unsupported imformat {self.imformat} for HSV conversion')

    @property
    def hsv(self) -> HsvAccessor:
        """Returns the HSV accessor.

        This property returns an instance of the HsvAccessor associated with the
        current object, allowing access to HSV (hue, saturation, other_image) related
        functionalities controlled by this handler.

        Returns:
            HsvAccessor: The instance of the HSV accessor.
        """
        return self._accessors.hsv

    @hsv.setter
    def hsv(self, value):
        raise IllegalAssignmentError('hsv')
