# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PartyExpShare:
    """
    EXP gain for a member of the player's party
    """
    _byte_size: int = 0
    _player_id: int = None # type: ignore [assignment]
    _experience: int = None # type: ignore [assignment]
    _level_up: int = None # type: ignore [assignment]

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
    def experience(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._experience

    @experience.setter
    def experience(self, experience: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._experience = experience

    @property
    def level_up(self) -> int:
        """
        A value greater than 0 is "new level" and indicates the player leveled up.

        Note:
          - Value range is 0-252.
        """
        return self._level_up

    @level_up.setter
    def level_up(self, level_up: int) -> None:
        """
        A value greater than 0 is "new level" and indicates the player leveled up.

        Note:
          - Value range is 0-252.
        """
        self._level_up = level_up

    @staticmethod
    def serialize(writer: EoWriter, data: "PartyExpShare") -> None:
        """
        Serializes an instance of `PartyExpShare` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PartyExpShare): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._experience is None:
                raise SerializationError("experience must be provided.")
            writer.add_int(data._experience)
            if data._level_up is None:
                raise SerializationError("level_up must be provided.")
            writer.add_char(data._level_up)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "PartyExpShare":
        """
        Deserializes an instance of `PartyExpShare` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PartyExpShare: The data to serialize.
        """
        data: PartyExpShare = PartyExpShare()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._player_id = reader.get_short()
            data._experience = reader.get_int()
            data._level_up = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PartyExpShare(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, experience={repr(self._experience)}, level_up={repr(self._level_up)})"
