from ..image_metadata.interface.image_linker_interface import IImageLinker
from ..image_metadata import Plot as BasePlot
from .mspec_image import MSpecImage


class Plot(BasePlot, IImageLinker):
    def link_images(self, images):
        """
        Links a (list of) images to the current instance.

        Expands the list of linked images.

        :param images: (list of) images to link
        :type images: MSpecImage or list[MSpecImage]
        """
        super().link_images(images)

    def link_image(self, image):
        """
        Links an image to the current instance.

        Expands the list of linked images.

        :param image: image to link
        :type image: MSpecImage
        """
        super().link_image(image)

    def has_images(self):
        """
        Returns True if at least one image is linked to the current instance.

        :return: True if at least one image is linked to the current instance
        :rtype: bool
        """
        return super().has_images()

    def get_images(self):
        """
        Returns the list of images linked to the current instance (empty list if none linked).

        :return: list of images linked to the current instance (empty list if none linked)
        :rtype: List[MSpecImage]
        """
        return super().get_images()
