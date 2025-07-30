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

class AccountCreateClientPacket(Packet):
    """
    Confirm creating an account
    """
    _byte_size: int = 0
    _session_id: int = None # type: ignore [assignment]
    _username: str = None # type: ignore [assignment]
    _password: str = None # type: ignore [assignment]
    _full_name: str = None # type: ignore [assignment]
    _location: str = None # type: ignore [assignment]
    _email: str = None # type: ignore [assignment]
    _computer: str = None # type: ignore [assignment]
    _hdid: str = None # type: ignore [assignment]

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
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, username: str) -> None:
        self._username = username

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, password: str) -> None:
        self._password = password

    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, full_name: str) -> None:
        self._full_name = full_name

    @property
    def location(self) -> str:
        return self._location

    @location.setter
    def location(self, location: str) -> None:
        self._location = location

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email: str) -> None:
        self._email = email

    @property
    def computer(self) -> str:
        return self._computer

    @computer.setter
    def computer(self, computer: str) -> None:
        self._computer = computer

    @property
    def hdid(self) -> str:
        return self._hdid

    @hdid.setter
    def hdid(self, hdid: str) -> None:
        self._hdid = hdid

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
        return PacketAction.Create

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        AccountCreateClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AccountCreateClientPacket") -> None:
        """
        Serializes an instance of `AccountCreateClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AccountCreateClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            writer.add_byte(0xFF)
            if data._username is None:
                raise SerializationError("username must be provided.")
            writer.add_string(data._username)
            writer.add_byte(0xFF)
            if data._password is None:
                raise SerializationError("password must be provided.")
            writer.add_string(data._password)
            writer.add_byte(0xFF)
            if data._full_name is None:
                raise SerializationError("full_name must be provided.")
            writer.add_string(data._full_name)
            writer.add_byte(0xFF)
            if data._location is None:
                raise SerializationError("location must be provided.")
            writer.add_string(data._location)
            writer.add_byte(0xFF)
            if data._email is None:
                raise SerializationError("email must be provided.")
            writer.add_string(data._email)
            writer.add_byte(0xFF)
            if data._computer is None:
                raise SerializationError("computer must be provided.")
            writer.add_string(data._computer)
            writer.add_byte(0xFF)
            if data._hdid is None:
                raise SerializationError("hdid must be provided.")
            writer.add_string(data._hdid)
            writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "AccountCreateClientPacket":
        """
        Deserializes an instance of `AccountCreateClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AccountCreateClientPacket: The data to serialize.
        """
        data: AccountCreateClientPacket = AccountCreateClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._session_id = reader.get_short()
            reader.next_chunk()
            data._username = reader.get_string()
            reader.next_chunk()
            data._password = reader.get_string()
            reader.next_chunk()
            data._full_name = reader.get_string()
            reader.next_chunk()
            data._location = reader.get_string()
            reader.next_chunk()
            data._email = reader.get_string()
            reader.next_chunk()
            data._computer = reader.get_string()
            reader.next_chunk()
            data._hdid = reader.get_string()
            reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AccountCreateClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, username={repr(self._username)}, password={repr(self._password)}, full_name={repr(self._full_name)}, location={repr(self._location)}, email={repr(self._email)}, computer={repr(self._computer)}, hdid={repr(self._hdid)})"
