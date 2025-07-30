# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .dialog_reply import DialogReply
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class QuestAcceptClientPacket(Packet):
    """
    Response to a quest NPC dialog
    """
    _byte_size: int = 0
    _session_id: int = None # type: ignore [assignment]
    _dialog_id: int = None # type: ignore [assignment]
    _quest_id: int = None # type: ignore [assignment]
    _npc_index: int = None # type: ignore [assignment]
    _reply_type: DialogReply = None # type: ignore [assignment]
    _reply_type_data: 'QuestAcceptClientPacket.ReplyTypeData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

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
    def npc_index(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._npc_index

    @npc_index.setter
    def npc_index(self, npc_index: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._npc_index = npc_index

    @property
    def reply_type(self) -> DialogReply:
        return self._reply_type

    @reply_type.setter
    def reply_type(self, reply_type: DialogReply) -> None:
        self._reply_type = reply_type

    @property
    def reply_type_data(self) -> 'QuestAcceptClientPacket.ReplyTypeData':
        """
        QuestAcceptClientPacket.ReplyTypeData: Gets or sets the data associated with the `reply_type` field.
        """
        return self._reply_type_data

    @reply_type_data.setter
    def reply_type_data(self, reply_type_data: 'QuestAcceptClientPacket.ReplyTypeData') -> None:
        self._reply_type_data = reply_type_data

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
        return PacketAction.Accept

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        QuestAcceptClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "QuestAcceptClientPacket") -> None:
        """
        Serializes an instance of `QuestAcceptClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (QuestAcceptClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            if data._dialog_id is None:
                raise SerializationError("dialog_id must be provided.")
            writer.add_short(data._dialog_id)
            if data._quest_id is None:
                raise SerializationError("quest_id must be provided.")
            writer.add_short(data._quest_id)
            if data._npc_index is None:
                raise SerializationError("npc_index must be provided.")
            writer.add_short(data._npc_index)
            if data._reply_type is None:
                raise SerializationError("reply_type must be provided.")
            writer.add_char(int(data._reply_type))
            if data._reply_type == DialogReply.Link:
                if not isinstance(data._reply_type_data, QuestAcceptClientPacket.ReplyTypeDataLink):
                    raise SerializationError("Expected reply_type_data to be type QuestAcceptClientPacket.ReplyTypeDataLink for reply_type " + DialogReply(data._reply_type).name + ".")
                QuestAcceptClientPacket.ReplyTypeDataLink.serialize(writer, data._reply_type_data)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "QuestAcceptClientPacket":
        """
        Deserializes an instance of `QuestAcceptClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            QuestAcceptClientPacket: The data to serialize.
        """
        data: QuestAcceptClientPacket = QuestAcceptClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._session_id = reader.get_short()
            data._dialog_id = reader.get_short()
            data._quest_id = reader.get_short()
            data._npc_index = reader.get_short()
            data._reply_type = DialogReply(reader.get_char())
            if data._reply_type == DialogReply.Link:
                data._reply_type_data = QuestAcceptClientPacket.ReplyTypeDataLink.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"QuestAcceptClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, dialog_id={repr(self._dialog_id)}, quest_id={repr(self._quest_id)}, npc_index={repr(self._npc_index)}, reply_type={repr(self._reply_type)}, reply_type_data={repr(self._reply_type_data)})"

    ReplyTypeData = Union['QuestAcceptClientPacket.ReplyTypeDataLink', None]
    """
    Data associated with different values of the `reply_type` field.
    """

    class ReplyTypeDataLink:
        """
        Data associated with reply_type value DialogReply.Link
        """
        _byte_size: int = 0
        _action: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def action(self) -> int:
            """
            Note:
              - Value range is 0-252.
            """
            return self._action

        @action.setter
        def action(self, action: int) -> None:
            """
            Note:
              - Value range is 0-252.
            """
            self._action = action

        @staticmethod
        def serialize(writer: EoWriter, data: "QuestAcceptClientPacket.ReplyTypeDataLink") -> None:
            """
            Serializes an instance of `QuestAcceptClientPacket.ReplyTypeDataLink` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (QuestAcceptClientPacket.ReplyTypeDataLink): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._action is None:
                    raise SerializationError("action must be provided.")
                writer.add_char(data._action)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "QuestAcceptClientPacket.ReplyTypeDataLink":
            """
            Deserializes an instance of `QuestAcceptClientPacket.ReplyTypeDataLink` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                QuestAcceptClientPacket.ReplyTypeDataLink: The data to serialize.
            """
            data: QuestAcceptClientPacket.ReplyTypeDataLink = QuestAcceptClientPacket.ReplyTypeDataLink()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._action = reader.get_char()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"QuestAcceptClientPacket.ReplyTypeDataLink(byte_size={repr(self._byte_size)}, action={repr(self._action)})"
