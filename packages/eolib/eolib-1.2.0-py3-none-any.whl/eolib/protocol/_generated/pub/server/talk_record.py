# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .talk_message_record import TalkMessageRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TalkRecord:
    """
    Record of Talk data in an Endless Talk File
    """
    _byte_size: int = 0
    _npc_id: int = None # type: ignore [assignment]
    _rate: int = None # type: ignore [assignment]
    _messages_count: int = None # type: ignore [assignment]
    _messages: list[TalkMessageRecord] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npc_id(self) -> int:
        """
        ID of the NPC that will talk

        Note:
          - Value range is 0-64008.
        """
        return self._npc_id

    @npc_id.setter
    def npc_id(self, npc_id: int) -> None:
        """
        ID of the NPC that will talk

        Note:
          - Value range is 0-64008.
        """
        self._npc_id = npc_id

    @property
    def rate(self) -> int:
        """
        Chance that the NPC will talk (0-100)

        Note:
          - Value range is 0-252.
        """
        return self._rate

    @rate.setter
    def rate(self, rate: int) -> None:
        """
        Chance that the NPC will talk (0-100)

        Note:
          - Value range is 0-252.
        """
        self._rate = rate

    @property
    def messages(self) -> list[TalkMessageRecord]:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._messages

    @messages.setter
    def messages(self, messages: list[TalkMessageRecord]) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._messages = messages
        self._messages_count = len(self._messages)

    @staticmethod
    def serialize(writer: EoWriter, data: "TalkRecord") -> None:
        """
        Serializes an instance of `TalkRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TalkRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._npc_id is None:
                raise SerializationError("npc_id must be provided.")
            writer.add_short(data._npc_id)
            if data._rate is None:
                raise SerializationError("rate must be provided.")
            writer.add_char(data._rate)
            if data._messages_count is None:
                raise SerializationError("messages_count must be provided.")
            writer.add_char(data._messages_count)
            if data._messages is None:
                raise SerializationError("messages must be provided.")
            if len(data._messages) > 252:
                raise SerializationError(f"Expected length of messages to be 252 or less, got {len(data._messages)}.")
            for i in range(data._messages_count):
                TalkMessageRecord.serialize(writer, data._messages[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "TalkRecord":
        """
        Deserializes an instance of `TalkRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TalkRecord: The data to serialize.
        """
        data: TalkRecord = TalkRecord()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._npc_id = reader.get_short()
            data._rate = reader.get_char()
            data._messages_count = reader.get_char()
            data._messages = []
            for i in range(data._messages_count):
                data._messages.append(TalkMessageRecord.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TalkRecord(byte_size={repr(self._byte_size)}, npc_id={repr(self._npc_id)}, rate={repr(self._rate)}, messages={repr(self._messages)})"
