# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PartyMember:
    """
    A member of the player's party
    """
    _byte_size: int = 0
    _player_id: int = None # type: ignore [assignment]
    _leader: bool = None # type: ignore [assignment]
    _level: int = None # type: ignore [assignment]
    _hp_percentage: int = None # type: ignore [assignment]
    _name: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._player_id

    @player_id.setter
    def player_id(self, player_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._player_id = player_id

    @property
    def leader(self) -> bool:
        return self._leader

    @leader.setter
    def leader(self, leader: bool) -> None:
        self._leader = leader

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
    def hp_percentage(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._hp_percentage

    @hp_percentage.setter
    def hp_percentage(self, hp_percentage: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._hp_percentage = hp_percentage

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @staticmethod
    def serialize(writer: EoWriter, data: "PartyMember") -> None:
        """
        Serializes an instance of `PartyMember` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PartyMember): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._leader is None:
                raise SerializationError("leader must be provided.")
            writer.add_char(1 if data._leader else 0)
            if data._level is None:
                raise SerializationError("level must be provided.")
            writer.add_char(data._level)
            if data._hp_percentage is None:
                raise SerializationError("hp_percentage must be provided.")
            writer.add_char(data._hp_percentage)
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "PartyMember":
        """
        Deserializes an instance of `PartyMember` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PartyMember: The data to serialize.
        """
        data: PartyMember = PartyMember()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._player_id = reader.get_short()
            data._leader = reader.get_char() != 0
            data._level = reader.get_char()
            data._hp_percentage = reader.get_char()
            data._name = reader.get_string()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PartyMember(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, leader={repr(self._leader)}, level={repr(self._level)}, hp_percentage={repr(self._hp_percentage)}, name={repr(self._name)})"
