# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_secondary_stats import CharacterSecondaryStats
from .character_elemental_stats import CharacterElementalStats
from .character_base_stats import CharacterBaseStats
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterStatsInfoLookup:
    """
    Character stats data.
    Sent with character info lookups.
    """
    _byte_size: int = 0
    _hp: int = None # type: ignore [assignment]
    _max_hp: int = None # type: ignore [assignment]
    _tp: int = None # type: ignore [assignment]
    _max_tp: int = None # type: ignore [assignment]
    _base_stats: CharacterBaseStats = None # type: ignore [assignment]
    _secondary_stats: CharacterSecondaryStats = None # type: ignore [assignment]
    _elemental_stats: CharacterElementalStats = None # type: ignore [assignment]

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
    def base_stats(self) -> CharacterBaseStats:
        return self._base_stats

    @base_stats.setter
    def base_stats(self, base_stats: CharacterBaseStats) -> None:
        self._base_stats = base_stats

    @property
    def secondary_stats(self) -> CharacterSecondaryStats:
        return self._secondary_stats

    @secondary_stats.setter
    def secondary_stats(self, secondary_stats: CharacterSecondaryStats) -> None:
        self._secondary_stats = secondary_stats

    @property
    def elemental_stats(self) -> CharacterElementalStats:
        return self._elemental_stats

    @elemental_stats.setter
    def elemental_stats(self, elemental_stats: CharacterElementalStats) -> None:
        self._elemental_stats = elemental_stats

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterStatsInfoLookup") -> None:
        """
        Serializes an instance of `CharacterStatsInfoLookup` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterStatsInfoLookup): The data to serialize.
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
            if data._base_stats is None:
                raise SerializationError("base_stats must be provided.")
            CharacterBaseStats.serialize(writer, data._base_stats)
            if data._secondary_stats is None:
                raise SerializationError("secondary_stats must be provided.")
            CharacterSecondaryStats.serialize(writer, data._secondary_stats)
            if data._elemental_stats is None:
                raise SerializationError("elemental_stats must be provided.")
            CharacterElementalStats.serialize(writer, data._elemental_stats)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterStatsInfoLookup":
        """
        Deserializes an instance of `CharacterStatsInfoLookup` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterStatsInfoLookup: The data to serialize.
        """
        data: CharacterStatsInfoLookup = CharacterStatsInfoLookup()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._hp = reader.get_short()
            data._max_hp = reader.get_short()
            data._tp = reader.get_short()
            data._max_tp = reader.get_short()
            data._base_stats = CharacterBaseStats.deserialize(reader)
            data._secondary_stats = CharacterSecondaryStats.deserialize(reader)
            data._elemental_stats = CharacterElementalStats.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterStatsInfoLookup(byte_size={repr(self._byte_size)}, hp={repr(self._hp)}, max_hp={repr(self._max_hp)}, tp={repr(self._tp)}, max_tp={repr(self._max_tp)}, base_stats={repr(self._base_stats)}, secondary_stats={repr(self._secondary_stats)}, elemental_stats={repr(self._elemental_stats)})"
