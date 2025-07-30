# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_secondary_stats import CharacterSecondaryStats
from .character_base_stats_welcome import CharacterBaseStatsWelcome
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterStatsWelcome:
    """
    Character stats data.
    Sent upon selecting a character and entering the game.
    """
    _byte_size: int = 0
    _hp: int = None # type: ignore [assignment]
    _max_hp: int = None # type: ignore [assignment]
    _tp: int = None # type: ignore [assignment]
    _max_tp: int = None # type: ignore [assignment]
    _max_sp: int = None # type: ignore [assignment]
    _stat_points: int = None # type: ignore [assignment]
    _skill_points: int = None # type: ignore [assignment]
    _karma: int = None # type: ignore [assignment]
    _secondary: CharacterSecondaryStats = None # type: ignore [assignment]
    _base: CharacterBaseStatsWelcome = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def hp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._hp

    @hp.setter
    def hp(self, hp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._hp = hp

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
    def tp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._tp

    @tp.setter
    def tp(self, tp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._tp = tp

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
    def karma(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._karma

    @karma.setter
    def karma(self, karma: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._karma = karma

    @property
    def secondary(self) -> CharacterSecondaryStats:
        return self._secondary

    @secondary.setter
    def secondary(self, secondary: CharacterSecondaryStats) -> None:
        self._secondary = secondary

    @property
    def base(self) -> CharacterBaseStatsWelcome:
        return self._base

    @base.setter
    def base(self, base: CharacterBaseStatsWelcome) -> None:
        self._base = base

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterStatsWelcome") -> None:
        """
        Serializes an instance of `CharacterStatsWelcome` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterStatsWelcome): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._hp is None:
                raise SerializationError("hp must be provided.")
            writer.add_short(data._hp)
            if data._max_hp is None:
                raise SerializationError("max_hp must be provided.")
            writer.add_short(data._max_hp)
            if data._tp is None:
                raise SerializationError("tp must be provided.")
            writer.add_short(data._tp)
            if data._max_tp is None:
                raise SerializationError("max_tp must be provided.")
            writer.add_short(data._max_tp)
            if data._max_sp is None:
                raise SerializationError("max_sp must be provided.")
            writer.add_short(data._max_sp)
            if data._stat_points is None:
                raise SerializationError("stat_points must be provided.")
            writer.add_short(data._stat_points)
            if data._skill_points is None:
                raise SerializationError("skill_points must be provided.")
            writer.add_short(data._skill_points)
            if data._karma is None:
                raise SerializationError("karma must be provided.")
            writer.add_short(data._karma)
            if data._secondary is None:
                raise SerializationError("secondary must be provided.")
            CharacterSecondaryStats.serialize(writer, data._secondary)
            if data._base is None:
                raise SerializationError("base must be provided.")
            CharacterBaseStatsWelcome.serialize(writer, data._base)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterStatsWelcome":
        """
        Deserializes an instance of `CharacterStatsWelcome` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterStatsWelcome: The data to serialize.
        """
        data: CharacterStatsWelcome = CharacterStatsWelcome()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._hp = reader.get_short()
            data._max_hp = reader.get_short()
            data._tp = reader.get_short()
            data._max_tp = reader.get_short()
            data._max_sp = reader.get_short()
            data._stat_points = reader.get_short()
            data._skill_points = reader.get_short()
            data._karma = reader.get_short()
            data._secondary = CharacterSecondaryStats.deserialize(reader)
            data._base = CharacterBaseStatsWelcome.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterStatsWelcome(byte_size={repr(self._byte_size)}, hp={repr(self._hp)}, max_hp={repr(self._max_hp)}, tp={repr(self._tp)}, max_tp={repr(self._max_tp)}, max_sp={repr(self._max_sp)}, stat_points={repr(self._stat_points)}, skill_points={repr(self._skill_points)}, karma={repr(self._karma)}, secondary={repr(self._secondary)}, base={repr(self._base)})"
