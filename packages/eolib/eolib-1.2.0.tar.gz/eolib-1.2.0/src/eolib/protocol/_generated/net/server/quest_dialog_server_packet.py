# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .dialog_quest_entry import DialogQuestEntry
from .dialog_entry import DialogEntry
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class QuestDialogServerPacket(Packet):
    """
    Quest selection dialog
    """
    _byte_size: int = 0
    _quest_count: int = None # type: ignore [assignment]
    _behavior_id: int = None # type: ignore [assignment]
    _quest_id: int = None # type: ignore [assignment]
    _session_id: int = None # type: ignore [assignment]
    _dialog_id: int = None # type: ignore [assignment]
    _quest_entries: list[DialogQuestEntry] = None # type: ignore [assignment]
    _dialog_entries: list[DialogEntry] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def behavior_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._behavior_id

    @behavior_id.setter
    def behavior_id(self, behavior_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._behavior_id = behavior_id

    @property
    def quest_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._quest_id

    @quest_id.setter
    def quest_id(self, quest_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._quest_id = quest_id

    @property
    def session_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._session_id

    @session_id.setter
    def session_id(self, session_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._session_id = session_id

    @property
    def dialog_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._dialog_id

    @dialog_id.setter
    def dialog_id(self, dialog_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._dialog_id = dialog_id

    @property
    def quest_entries(self) -> list[DialogQuestEntry]:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._quest_entries

    @quest_entries.setter
    def quest_entries(self, quest_entries: list[DialogQuestEntry]) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._quest_entries = quest_entries
        self._quest_count = len(self._quest_entries)

    @property
    def dialog_entries(self) -> list[DialogEntry]:
        return self._dialog_entries

    @dialog_entries.setter
    def dialog_entries(self, dialog_entries: list[DialogEntry]) -> None:
        self._dialog_entries = dialog_entries

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Quest

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Dialog

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        QuestDialogServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "QuestDialogServerPacket") -> None:
        """
        Serializes an instance of `QuestDialogServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (QuestDialogServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._quest_count is None:
                raise SerializationError("quest_count must be provided.")
            writer.add_char(data._quest_count)
            if data._behavior_id is None:
                raise SerializationError("behavior_id must be provided.")
            writer.add_short(data._behavior_id)
            if data._quest_id is None:
                raise SerializationError("quest_id must be provided.")
            writer.add_short(data._quest_id)
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            if data._dialog_id is None:
                raise SerializationError("dialog_id must be provided.")
            writer.add_short(data._dialog_id)
            writer.add_byte(0xFF)
            if data._quest_entries is None:
                raise SerializationError("quest_entries must be provided.")
            if len(data._quest_entries) > 252:
                raise SerializationError(f"Expected length of quest_entries to be 252 or less, got {len(data._quest_entries)}.")
            for i in range(data._quest_count):
                DialogQuestEntry.serialize(writer, data._quest_entries[i])
                writer.add_byte(0xFF)
            if data._dialog_entries is None:
                raise SerializationError("dialog_entries must be provided.")
            for i in range(len(data._dialog_entries)):
                DialogEntry.serialize(writer, data._dialog_entries[i])
                writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "QuestDialogServerPacket":
        """
        Deserializes an instance of `QuestDialogServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            QuestDialogServerPacket: The data to serialize.
        """
        data: QuestDialogServerPacket = QuestDialogServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._quest_count = reader.get_char()
            data._behavior_id = reader.get_short()
            data._quest_id = reader.get_short()
            data._session_id = reader.get_short()
            data._dialog_id = reader.get_short()
            reader.next_chunk()
            data._quest_entries = []
            for i in range(data._quest_count):
                data._quest_entries.append(DialogQuestEntry.deserialize(reader))
                reader.next_chunk()
            data._dialog_entries = []
            while reader.remaining > 0:
                data._dialog_entries.append(DialogEntry.deserialize(reader))
                reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"QuestDialogServerPacket(byte_size={repr(self._byte_size)}, behavior_id={repr(self._behavior_id)}, quest_id={repr(self._quest_id)}, session_id={repr(self._session_id)}, dialog_id={repr(self._dialog_id)}, quest_entries={repr(self._quest_entries)}, dialog_entries={repr(self._dialog_entries)})"
