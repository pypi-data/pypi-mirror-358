# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterElementalStats:
    """
    The 6 elemental character stats
    """
    _byte_size: int = 0
    _light: int = None # type: ignore [assignment]
    _dark: int = None # type: ignore [assignment]
    _fire: int = None # type: ignore [assignment]
    _water: int = None # type: ignore [assignment]
    _earth: int = None # type: ignore [assignment]
    _wind: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def light(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._light

    @light.setter
    def light(self, light: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._light = light

    @property
    def dark(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._dark

    @dark.setter
    def dark(self, dark: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._dark = dark

    @property
    def fire(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._fire

    @fire.setter
    def fire(self, fire: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._fire = fire

    @property
    def water(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._water

    @water.setter
    def water(self, water: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._water = water

    @property
    def earth(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._earth

    @earth.setter
    def earth(self, earth: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._earth = earth

    @property
    def wind(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._wind

    @wind.setter
    def wind(self, wind: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._wind = wind

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterElementalStats") -> None:
        """
        Serializes an instance of `CharacterElementalStats` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterElementalStats): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._light is None:
                raise SerializationError("light must be provided.")
            writer.add_short(data._light)
            if data._dark is None:
                raise SerializationError("dark must be provided.")
            writer.add_short(data._dark)
            if data._fire is None:
                raise SerializationError("fire must be provided.")
            writer.add_short(data._fire)
            if data._water is None:
                raise SerializationError("water must be provided.")
            writer.add_short(data._water)
            if data._earth is None:
                raise SerializationError("earth must be provided.")
            writer.add_short(data._earth)
            if data._wind is None:
                raise SerializationError("wind must be provided.")
            writer.add_short(data._wind)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterElementalStats":
        """
        Deserializes an instance of `CharacterElementalStats` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterElementalStats: The data to serialize.
        """
        data: CharacterElementalStats = CharacterElementalStats()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._light = reader.get_short()
            data._dark = reader.get_short()
            data._fire = reader.get_short()
            data._water = reader.get_short()
            data._earth = reader.get_short()
            data._wind = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterElementalStats(byte_size={repr(self._byte_size)}, light={repr(self._light)}, dark={repr(self._dark)}, fire={repr(self._fire)}, water={repr(self._water)}, earth={repr(self._earth)}, wind={repr(self._wind)})"
