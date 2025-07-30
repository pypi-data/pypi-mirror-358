# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .skill_master_reply import SkillMasterReply
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class StatSkillReplyServerPacket(Packet):
    """
    Response from unsuccessful action at a skill master
    """
    _byte_size: int = 0
    _reply_code: SkillMasterReply = None # type: ignore [assignment]
    _reply_code_data: 'StatSkillReplyServerPacket.ReplyCodeData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def reply_code(self) -> SkillMasterReply:
        return self._reply_code

    @reply_code.setter
    def reply_code(self, reply_code: SkillMasterReply) -> None:
        self._reply_code = reply_code

    @property
    def reply_code_data(self) -> 'StatSkillReplyServerPacket.ReplyCodeData':
        """
        StatSkillReplyServerPacket.ReplyCodeData: Gets or sets the data associated with the `reply_code` field.
        """
        return self._reply_code_data

    @reply_code_data.setter
    def reply_code_data(self, reply_code_data: 'StatSkillReplyServerPacket.ReplyCodeData') -> None:
        self._reply_code_data = reply_code_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.StatSkill

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Reply

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        StatSkillReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "StatSkillReplyServerPacket") -> None:
        """
        Serializes an instance of `StatSkillReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (StatSkillReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._reply_code is None:
                raise SerializationError("reply_code must be provided.")
            writer.add_short(int(data._reply_code))
            if data._reply_code == SkillMasterReply.WrongClass:
                if not isinstance(data._reply_code_data, StatSkillReplyServerPacket.ReplyCodeDataWrongClass):
                    raise SerializationError("Expected reply_code_data to be type StatSkillReplyServerPacket.ReplyCodeDataWrongClass for reply_code " + SkillMasterReply(data._reply_code).name + ".")
                StatSkillReplyServerPacket.ReplyCodeDataWrongClass.serialize(writer, data._reply_code_data)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "StatSkillReplyServerPacket":
        """
        Deserializes an instance of `StatSkillReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            StatSkillReplyServerPacket: The data to serialize.
        """
        data: StatSkillReplyServerPacket = StatSkillReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._reply_code = SkillMasterReply(reader.get_short())
            if data._reply_code == SkillMasterReply.WrongClass:
                data._reply_code_data = StatSkillReplyServerPacket.ReplyCodeDataWrongClass.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"StatSkillReplyServerPacket(byte_size={repr(self._byte_size)}, reply_code={repr(self._reply_code)}, reply_code_data={repr(self._reply_code_data)})"

    ReplyCodeData = Union['StatSkillReplyServerPacket.ReplyCodeDataWrongClass', None]
    """
    Data associated with different values of the `reply_code` field.
    """

    class ReplyCodeDataWrongClass:
        """
        Data associated with reply_code value SkillMasterReply.WrongClass
        """
        _byte_size: int = 0
        _class_id: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def class_id(self) -> int:
            """
            Note:
              - Value range is 0-252.
            """
            return self._class_id

        @class_id.setter
        def class_id(self, class_id: int) -> None:
            """
            Note:
              - Value range is 0-252.
            """
            self._class_id = class_id

        @staticmethod
        def serialize(writer: EoWriter, data: "StatSkillReplyServerPacket.ReplyCodeDataWrongClass") -> None:
            """
            Serializes an instance of `StatSkillReplyServerPacket.ReplyCodeDataWrongClass` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (StatSkillReplyServerPacket.ReplyCodeDataWrongClass): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._class_id is None:
                    raise SerializationError("class_id must be provided.")
                writer.add_char(data._class_id)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "StatSkillReplyServerPacket.ReplyCodeDataWrongClass":
            """
            Deserializes an instance of `StatSkillReplyServerPacket.ReplyCodeDataWrongClass` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                StatSkillReplyServerPacket.ReplyCodeDataWrongClass: The data to serialize.
            """
            data: StatSkillReplyServerPacket.ReplyCodeDataWrongClass = StatSkillReplyServerPacket.ReplyCodeDataWrongClass()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._class_id = reader.get_char()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"StatSkillReplyServerPacket.ReplyCodeDataWrongClass(byte_size={repr(self._byte_size)}, class_id={repr(self._class_id)})"
