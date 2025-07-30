# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .admin_message_type import AdminMessageType
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class AdminInteractReplyServerPacket(Packet):
    """
    Incoming admin message
    """
    _byte_size: int = 0
    _message_type: AdminMessageType = None # type: ignore [assignment]
    _message_type_data: 'AdminInteractReplyServerPacket.MessageTypeData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def message_type(self) -> AdminMessageType:
        return self._message_type

    @message_type.setter
    def message_type(self, message_type: AdminMessageType) -> None:
        self._message_type = message_type

    @property
    def message_type_data(self) -> 'AdminInteractReplyServerPacket.MessageTypeData':
        """
        AdminInteractReplyServerPacket.MessageTypeData: Gets or sets the data associated with the `message_type` field.
        """
        return self._message_type_data

    @message_type_data.setter
    def message_type_data(self, message_type_data: 'AdminInteractReplyServerPacket.MessageTypeData') -> None:
        self._message_type_data = message_type_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.AdminInteract

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
        AdminInteractReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AdminInteractReplyServerPacket") -> None:
        """
        Serializes an instance of `AdminInteractReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AdminInteractReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._message_type is None:
                raise SerializationError("message_type must be provided.")
            writer.add_char(int(data._message_type))
            writer.add_byte(0xFF)
            if data._message_type == AdminMessageType.Message:
                if not isinstance(data._message_type_data, AdminInteractReplyServerPacket.MessageTypeDataMessage):
                    raise SerializationError("Expected message_type_data to be type AdminInteractReplyServerPacket.MessageTypeDataMessage for message_type " + AdminMessageType(data._message_type).name + ".")
                AdminInteractReplyServerPacket.MessageTypeDataMessage.serialize(writer, data._message_type_data)
            elif data._message_type == AdminMessageType.Report:
                if not isinstance(data._message_type_data, AdminInteractReplyServerPacket.MessageTypeDataReport):
                    raise SerializationError("Expected message_type_data to be type AdminInteractReplyServerPacket.MessageTypeDataReport for message_type " + AdminMessageType(data._message_type).name + ".")
                AdminInteractReplyServerPacket.MessageTypeDataReport.serialize(writer, data._message_type_data)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "AdminInteractReplyServerPacket":
        """
        Deserializes an instance of `AdminInteractReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AdminInteractReplyServerPacket: The data to serialize.
        """
        data: AdminInteractReplyServerPacket = AdminInteractReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._message_type = AdminMessageType(reader.get_char())
            reader.next_chunk()
            if data._message_type == AdminMessageType.Message:
                data._message_type_data = AdminInteractReplyServerPacket.MessageTypeDataMessage.deserialize(reader)
            elif data._message_type == AdminMessageType.Report:
                data._message_type_data = AdminInteractReplyServerPacket.MessageTypeDataReport.deserialize(reader)
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AdminInteractReplyServerPacket(byte_size={repr(self._byte_size)}, message_type={repr(self._message_type)}, message_type_data={repr(self._message_type_data)})"

    MessageTypeData = Union['AdminInteractReplyServerPacket.MessageTypeDataMessage', 'AdminInteractReplyServerPacket.MessageTypeDataReport', None]
    """
    Data associated with different values of the `message_type` field.
    """

    class MessageTypeDataMessage:
        """
        Data associated with message_type value AdminMessageType.Message
        """
        _byte_size: int = 0
        _player_name: str = None # type: ignore [assignment]
        _message: str = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def player_name(self) -> str:
            return self._player_name

        @player_name.setter
        def player_name(self, player_name: str) -> None:
            self._player_name = player_name

        @property
        def message(self) -> str:
            return self._message

        @message.setter
        def message(self, message: str) -> None:
            self._message = message

        @staticmethod
        def serialize(writer: EoWriter, data: "AdminInteractReplyServerPacket.MessageTypeDataMessage") -> None:
            """
            Serializes an instance of `AdminInteractReplyServerPacket.MessageTypeDataMessage` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (AdminInteractReplyServerPacket.MessageTypeDataMessage): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._player_name is None:
                    raise SerializationError("player_name must be provided.")
                writer.add_string(data._player_name)
                writer.add_byte(0xFF)
                if data._message is None:
                    raise SerializationError("message must be provided.")
                writer.add_string(data._message)
                writer.add_byte(0xFF)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "AdminInteractReplyServerPacket.MessageTypeDataMessage":
            """
            Deserializes an instance of `AdminInteractReplyServerPacket.MessageTypeDataMessage` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                AdminInteractReplyServerPacket.MessageTypeDataMessage: The data to serialize.
            """
            data: AdminInteractReplyServerPacket.MessageTypeDataMessage = AdminInteractReplyServerPacket.MessageTypeDataMessage()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._player_name = reader.get_string()
                reader.next_chunk()
                data._message = reader.get_string()
                reader.next_chunk()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"AdminInteractReplyServerPacket.MessageTypeDataMessage(byte_size={repr(self._byte_size)}, player_name={repr(self._player_name)}, message={repr(self._message)})"

    class MessageTypeDataReport:
        """
        Data associated with message_type value AdminMessageType.Report
        """
        _byte_size: int = 0
        _player_name: str = None # type: ignore [assignment]
        _message: str = None # type: ignore [assignment]
        _reportee_name: str = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def player_name(self) -> str:
            return self._player_name

        @player_name.setter
        def player_name(self, player_name: str) -> None:
            self._player_name = player_name

        @property
        def message(self) -> str:
            return self._message

        @message.setter
        def message(self, message: str) -> None:
            self._message = message

        @property
        def reportee_name(self) -> str:
            return self._reportee_name

        @reportee_name.setter
        def reportee_name(self, reportee_name: str) -> None:
            self._reportee_name = reportee_name

        @staticmethod
        def serialize(writer: EoWriter, data: "AdminInteractReplyServerPacket.MessageTypeDataReport") -> None:
            """
            Serializes an instance of `AdminInteractReplyServerPacket.MessageTypeDataReport` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (AdminInteractReplyServerPacket.MessageTypeDataReport): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._player_name is None:
                    raise SerializationError("player_name must be provided.")
                writer.add_string(data._player_name)
                writer.add_byte(0xFF)
                if data._message is None:
                    raise SerializationError("message must be provided.")
                writer.add_string(data._message)
                writer.add_byte(0xFF)
                if data._reportee_name is None:
                    raise SerializationError("reportee_name must be provided.")
                writer.add_string(data._reportee_name)
                writer.add_byte(0xFF)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "AdminInteractReplyServerPacket.MessageTypeDataReport":
            """
            Deserializes an instance of `AdminInteractReplyServerPacket.MessageTypeDataReport` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                AdminInteractReplyServerPacket.MessageTypeDataReport: The data to serialize.
            """
            data: AdminInteractReplyServerPacket.MessageTypeDataReport = AdminInteractReplyServerPacket.MessageTypeDataReport()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._player_name = reader.get_string()
                reader.next_chunk()
                data._message = reader.get_string()
                reader.next_chunk()
                data._reportee_name = reader.get_string()
                reader.next_chunk()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"AdminInteractReplyServerPacket.MessageTypeDataReport(byte_size={repr(self._byte_size)}, player_name={repr(self._player_name)}, message={repr(self._message)}, reportee_name={repr(self._reportee_name)})"
