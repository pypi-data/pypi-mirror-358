# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class LevelUpStats:
    """
    Level and stat updates
    """
    _byte_size: int = 0
    _level: int = None # type: ignore [assignment]
    _stat_points: int = None # type: ignore [assignment]
    _skill_points: int = None # type: ignore [assignment]
    _max_hp: int = None # type: ignore [assignment]
    _max_tp: int = None # type: ignore [assignment]
    _max_sp: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def level(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._level

    @level.setter
    def level(self, level: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._level = level

    @property
    def stat_points(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._stat_points

    @stat_points.setter
    def stat_points(self, stat_points: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._stat_points = stat_points

    @property
    def skill_points(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._skill_points

    @skill_points.setter
    def skill_points(self, skill_points: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._skill_points = skill_points

    @property
    def max_hp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_hp

    @max_hp.setter
    def max_hp(self, max_hp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_hp = max_hp

    @property
    def max_tp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_tp

    @max_tp.setter
    def max_tp(self, max_tp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_tp = max_tp

    @property
    def max_sp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_sp

    @max_sp.setter
    def max_sp(self, max_sp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_sp = max_sp

    @staticmethod
    def serialize(writer: EoWriter, data: "LevelUpStats") -> None:
        """
        Serializes an instance of `LevelUpStats` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (LevelUpStats): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._level is None:
                raise SerializationError("level must be provided.")
            writer.add_char(data._level)
            if data._stat_points is None:
                raise SerializationError("stat_points must be provided.")
            writer.add_short(data._stat_points)
            if data._skill_points is None:
                raise SerializationError("skill_points must be provided.")
            writer.add_short(data._skill_points)
            if data._max_hp is None:
                raise SerializationError("max_hp must be provided.")
            writer.add_short(data._max_hp)
            if data._max_tp is None:
                raise SerializationError("max_tp must be provided.")
            writer.add_short(data._max_tp)
            if data._max_sp is None:
                raise SerializationError("max_sp must be provided.")
            writer.add_short(data._max_sp)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "LevelUpStats":
        """
        Deserializes an instance of `LevelUpStats` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            LevelUpStats: The data to serialize.
        """
        data: LevelUpStats = LevelUpStats()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._level = reader.get_char()
            data._stat_points = reader.get_short()
            data._skill_points = reader.get_short()
            data._max_hp = reader.get_short()
            data._max_tp = reader.get_short()
            data._max_sp = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"LevelUpStats(byte_size={repr(self._byte_size)}, level={repr(self._level)}, stat_points={repr(self._stat_points)}, skill_points={repr(self._skill_points)}, max_hp={repr(self._max_hp)}, max_tp={repr(self._max_tp)}, max_sp={repr(self._max_sp)})"
