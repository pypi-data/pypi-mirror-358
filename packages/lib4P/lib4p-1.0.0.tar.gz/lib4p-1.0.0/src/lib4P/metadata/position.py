class Position:

    def __init__(self, x=0, y=0, z=0, yaw=0, pitch=0, roll=0):
        """
        Position is an oriented point with Cartesian coordinates (`x`,`y`,`z`) and Tait-Bryan angles (`yaw`,`pitch`,`roll`).

        :param x: `x` coordinate
        :type x: int or float
        :param y: `y` coordinate
        :type y: int or float
        :param z: `z` coordinate
        :type z: int or float
        :param yaw: `yaw` angle (rad)
        :type yaw: int or float
        :param pitch: `pitch` angle (rad)
        :type pitch: int or float
        :param roll: `roll` angle (rad)
        :type roll: int or float
        """
        self._x = None
        self.set_x(x)

        self._y = None
        self.set_y(y)

        self._z = None
        self.set_z(z)

        self._yaw = None
        self.set_yaw(yaw)

        self._pitch = None
        self.set_pitch(pitch)

        self._roll = None
        self.set_roll(roll)

    def __eq__(self, other):
        """
        Tests for equality between two `Position` objects.
        Equality is true when both objects are of type `Position`, and their `x`, `y`, `z`, `yaw`, `pitch`, and `roll` values are equal to each other.

        :param other: another `Position` object
        :type other: Position
        :return: true if the two objects are equal
        :rtype: bool
        """
        return (
            isinstance(other, Position)
            and self.get_x() == other.get_x()
            and self.get_y() == other.get_y()
            and self.get_z() == other.get_z()
            and self.get_yaw() == other.get_yaw()
            and self.get_pitch() == other.get_pitch()
            and self.get_roll() == other.get_roll()
        )

    def __add__(self, other):
        if not isinstance(other, Position):
            raise TypeError(f"Position can only be added with another instance of Position, type {type(other)} found")
        return Position(
            self.get_x() + other.get_x(),
            self.get_y() + other.get_y(),
            self.get_z() + other.get_z(),
            self.get_yaw() + other.get_yaw(),
            self.get_pitch() + other.get_pitch(),
            self.get_roll() + other.get_roll()
        )

    def __sub__(self, other):
        if not isinstance(other, Position):
            raise TypeError(f"Position can only be added with another instance of Position, type {type(other)} found")
        return Position(
            self.get_x() - other.get_x(),
            self.get_y() - other.get_y(),
            self.get_z() - other.get_z(),
            self.get_yaw() - other.get_yaw(),
            self.get_pitch() - other.get_pitch(),
            self.get_roll() - other.get_roll()
        )

    def set_x(self, x):
        """
        Set the value of the `x` coordinate.

        :param x: `x` position
        :type x: int or float
        """
        if not isinstance(x, int) and not isinstance(x, float):
            raise TypeError(f"Argument 'x' must be of type {int} or {float}, type {type(x)} found")
        self._x = x

    def get_x(self):
        """
        Returns the value of the `x` coordinate.

        :return: value of the `x` coordinate
        :rtype: int or float
        """
        return self._x

    def set_y(self, y):
        """
        Set the value of the `y` coordinate.

        :param y: `y` position
        :type y: int or float
        """
        if not isinstance(y, int) and not isinstance(y, float):
            raise TypeError(f"Argument 'y' must be of type {int} or {float}, type {type(y)} found")
        self._y = y

    def get_y(self):
        """
        Returns the value of the `y` coordinate.

        :return: value of the `y` coordinate
        :rtype: int or float
        """
        return self._y

    def set_z(self, z):
        """
        Set the value of the `z` coordinate.

        :param z: `z` position
        :type z: int or float
        """
        if not isinstance(z, int) and not isinstance(z, float):
            raise TypeError(f"Argument 'z' must be of type {int} or {float}, type {type(z)} found")
        self._z = z

    def get_z(self):
        """
        Returns the value of the `z` coordinate.

        :return: value of the `z` coordinate
        :rtype: int or float
        """
        return self._z

    def set_yaw(self, yaw):
        """
        Set the value of the `yaw` angle (deg).

        :param yaw: `yaw` angle (deg)
        :type yaw: int or float

        :note: The value is modulated in [-180°, 180°[
        """
        if not isinstance(yaw, int) and not isinstance(yaw, float):
            raise TypeError(f"Argument 'yaw' must be of type {int} or {float}, type {type(yaw)} found")
        self._yaw = ((yaw+180) % 360)-180  # [-180°, 180°[

    def get_yaw(self):
        """
        Returns the value of the `yaw` angle (deg).

        :return: value of the `yaw` angle (deg)
        :rtype: int or float
        """
        return self._yaw

    def set_pitch(self, pitch):
        """
        Set the value of the `pitch` angle (deg).

        :param pitch: `pitch` angle (deg)
        :type pitch: int or float
        :note: The value is modulated in [-90°, 90°[
        """
        if not isinstance(pitch, int) and not isinstance(pitch, float):
            raise TypeError(f"Argument 'pitch' must be of type {int} or {float}, type {type(pitch)} found")
        self._pitch = ((pitch+90) % 180)-90  # [-90°, 90°[
        # TODO : Pas valide pour le pitch : si on est à 90° et qu'on ajoute +1° ~on redescend à 89°
        #        Image : https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Geographic_coordinates_sphere.svg/1200px-Geographic_coordinates_sphere.svg.png

    def get_pitch(self):
        """
        Returns the value of the `pitch` angle (deg).

        :return: value of the `pitch` angle (deg)
        :rtype: int or float
        """
        return self._pitch

    def set_roll(self, roll):
        """
        Set the value of the `roll` angle (deg).

        :param roll: `roll` angle (deg)
        :type roll: int or float

        :note: The value is modulated in [-180°, 180°[
        """
        if not isinstance(roll, int) and not isinstance(roll, float):
            raise TypeError(f"Argument 'roll' must be of type {int} or {float}, type {type(roll)} found")
        self._roll = ((roll+180) % 360)-180  # [-180°, 180°[

    def get_roll(self):
        """
        Returns the value of the `pitch` angle (deg).

        :return: value of the `pitch` angle (deg)
        :rtype: int or float
        """
        return self._roll
