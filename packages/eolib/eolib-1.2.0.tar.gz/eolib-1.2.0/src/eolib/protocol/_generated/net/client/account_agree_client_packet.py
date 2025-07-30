# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class AccountAgreeClientPacket(Packet):
    """
    Change password
    """
    _byte_size: int = 0
    _username: str = None # type: ignore [assignment]
    _old_password: str = None # type: ignore [assignment]
    _new_password: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, username: str) -> None:
        self._username = username

    @property
    def old_password(self) -> str:
        return self._old_password

    @old_password.setter
    def old_password(self, old_password: str) -> None:
        self._old_password = old_password

    @property
    def new_password(self) -> str:
        return self._new_password

    @new_password.setter
    def new_password(self, new_password: str) -> None:
        self._new_password = new_password

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Account

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Agree

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        AccountAgreeClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AccountAgreeClientPacket") -> None:
        """
        Serializes an instance of `AccountAgreeClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AccountAgreeClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._username is None:
                raise SerializationError("username must be provided.")
            writer.add_string(data._username)
            writer.add_byte(0xFF)
            if data._old_password is None:
                raise SerializationError("old_password must be provided.")
            writer.add_string(data._old_password)
            writer.add_byte(0xFF)
            if data._new_password is None:
                raise SerializationError("new_password must be provided.")
            writer.add_string(data._new_password)
            writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "AccountAgreeClientPacket":
        """
        Deserializes an instance of `AccountAgreeClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AccountAgreeClientPacket: The data to serialize.
        """
        data: AccountAgreeClientPacket = AccountAgreeClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._username = reader.get_string()
            reader.next_chunk()
            data._old_password = reader.get_string()
            reader.next_chunk()
            data._new_password = reader.get_string()
            reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AccountAgreeClientPacket(byte_size={repr(self._byte_size)}, username={repr(self._username)}, old_password={repr(self._old_password)}, new_password={repr(self._new_password)})"
