# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterSecondaryStats:
    """
    The 5 secondary character stats
    """
    _byte_size: int = 0
    _min_damage: int = None # type: ignore [assignment]
    _max_damage: int = None # type: ignore [assignment]
    _accuracy: int = None # type: ignore [assignment]
    _evade: int = None # type: ignore [assignment]
    _armor: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def min_damage(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._min_damage

    @min_damage.setter
    def min_damage(self, min_damage: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._min_damage = min_damage

    @property
    def max_damage(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_damage

    @max_damage.setter
    def max_damage(self, max_damage: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_damage = max_damage

    @property
    def accuracy(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._accuracy

    @accuracy.setter
    def accuracy(self, accuracy: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._accuracy = accuracy

    @property
    def evade(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._evade

    @evade.setter
    def evade(self, evade: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._evade = evade

    @property
    def armor(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._armor

    @armor.setter
    def armor(self, armor: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._armor = armor

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterSecondaryStats") -> None:
        """
        Serializes an instance of `CharacterSecondaryStats` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterSecondaryStats): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._min_damage is None:
                raise SerializationError("min_damage must be provided.")
            writer.add_short(data._min_damage)
            if data._max_damage is None:
                raise SerializationError("max_damage must be provided.")
            writer.add_short(data._max_damage)
            if data._accuracy is None:
                raise SerializationError("accuracy must be provided.")
            writer.add_short(data._accuracy)
            if data._evade is None:
                raise SerializationError("evade must be provided.")
            writer.add_short(data._evade)
            if data._armor is None:
                raise SerializationError("armor must be provided.")
            writer.add_short(data._armor)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterSecondaryStats":
        """
        Deserializes an instance of `CharacterSecondaryStats` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterSecondaryStats: The data to serialize.
        """
        data: CharacterSecondaryStats = CharacterSecondaryStats()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._min_damage = reader.get_short()
            data._max_damage = reader.get_short()
            data._accuracy = reader.get_short()
            data._evade = reader.get_short()
            data._armor = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterSecondaryStats(byte_size={repr(self._byte_size)}, min_damage={repr(self._min_damage)}, max_damage={repr(self._max_damage)}, accuracy={repr(self._accuracy)}, evade={repr(self._evade)}, armor={repr(self._armor)})"
