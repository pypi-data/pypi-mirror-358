from .interface.image_interface import IImage
from ... import Data
from ...interface.data_interface import IData


class Image(Data, IImage):

    def __init__(self, filename, name, date, shutter_time, height, width, size, **kwargs):
        """
        Image acquired by a given sensor during the measurement session.

        :param filename: path to the file containing the image data
        :type filename: str
        :param name: common name assigned to this image (used for saving variants)
        :type name: str
        :param date: date (including time) of image acquisition
        :type date: str or datetime
        :param shutter_time: shutter time (ms) used for image acquisition
        :type shutter_time: int
        :param height: height (px) of the image
        :type height: int
        :param width: width (px) of the image
        :type width: int
        :param size: [WARNING] currently, corresponds to the image size in bytes of the original mosaicked image
        :type size: int
        :param kwargs: additional attributes that can be linked to the object (example: 'plot_id' to which it is linked)

        :note: The scope of the `Image` class is metadata. Therefore, image data (RGB values) are not directly
               contained in this class. It contains the elements necessary for its reading, namely a `filename` variable.
        """
        super().__init__(filename=filename, name=name, date=date)

        self._shutter_time = None
        self.set_shutter_time(shutter_time)

        self._height = None
        self.set_height(height)

        self._width = None
        self.set_width(width)

        self._size = None
        self.set_size(size)

        self.set_additional_attributes(kwargs)

    def __eq__(self, other):
        """
        Tests for equality between two `Image` objects.
        Equality is true when both objects are of type `Image`, and their `filename`, `name`, `date`, `shutter_time`, `height`, `width` and `size` values are equal to each other.

        :param other: another `Image` object
        :type other: Image
        :return: true if the two objects are equal
        :rtype: bool

        :note: The scope of the `Image` class is metadata. Therefore, only metadata is tested for equality, and in no case is the concrete data tested.
        """
        return (
            isinstance(other, IImage)
            and self.get_filename() == other.get_filename()
            and self.get_name() == other.get_name()
            and self.get_date() == other.get_date()
            and self.get_shutter_time() == other.get_shutter_time()
            and self.get_height() == other.get_height()
            and self.get_width() == other.get_width()
            and self.get_size() == other.get_size()
            # and self.get_additional_attributes() == other.get_additional_attributes()
        )

    @classmethod
    def from_data(cls, data):
        """
        Image constructor from IData object.

        :param data: IData object from which to initialize Image (Data specialization)
        :type data: IData
        :return: Image
        """
        if not isinstance(data, IData):
            raise TypeError(f"Argument 'data' must be of type {IData}, type {type(data)} found")

        kwargs = data.get_additional_attributes()
        kwargs.update({"filename": data.get_filename(), "name": data.get_name(), "date": data.get_date()})

        try:
            image_instance = cls(**kwargs)
        except Exception as e:
            raise Exception("An error occurred while instantiating Image from a Data object. "
                            "This may mean that the provided Data object is not compatible with the Image class or "
                            "that some data is missing to cast the object. The following message was returned: "
                            f"{e.__repr__()}")

        return image_instance

    def set_shutter_time(self, shutter_time):
        """
        Set the shutter time (ms) used for image acquisition.

        :param shutter_time: shutter time (ms) used for image acquisition
        :type shutter_time: int
        """
        if not isinstance(shutter_time, int):
            raise TypeError(f"Argument 'shutter_time' must be of type {int}, "
                            f"type {type(shutter_time)} found")
        self._shutter_time = shutter_time

    def get_shutter_time(self):
        """
        Returns the shutter time (ms) used for image acquisition.

        :return: shutter time (ms) used for image acquisition
        :rtype: int
        """
        return self._shutter_time

    def set_height(self, height):
        """
        Set the height (px) of the image.

        :param height: height (px) of the image
        :type height: int
        """
        if not isinstance(height, int):
            raise TypeError(f"Argument 'height' must be of type {int}, "
                            f"type {type(height)} found")
        self._height = height

    def get_height(self):
        """
        Returns the height (px) of the image.

        :return: height (px) of the image
        :rtype: int
        """
        return self._height

    def set_width(self, width):
        """
        Set the width (px) of the image.

        :param width: width (px) of the image
        :type width: int
        """
        if not isinstance(width, int):
            raise TypeError(f"Argument 'width' must be of type {int}, "
                            f"type {type(width)} found")
        self._width = width

    def get_width(self):
        """
        Returns the width (px) of the image.

        :return: width (px) of the image
        :rtype: int
        """
        return self._width

    def set_size(self, size):
        """
        Set the size (bytes) of the image.

        :param size: size (bytes) of the image
        :type size: int
        """
        if not isinstance(size, int):
            raise TypeError(f"Argument 'size' must be of type {int}, "
                            f"type {type(size)} found")
        self._size = size

    def get_size(self):
        """
        Returns the size (bytes) of the image.

        :return: size (bytes) of the image
        :rtype: int

        :warning: Currently, corresponds to the image size in bytes of the original mosaicked image
        """
        return self._size
