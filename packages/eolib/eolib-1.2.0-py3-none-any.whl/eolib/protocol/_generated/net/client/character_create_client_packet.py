# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...gender import Gender
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterCreateClientPacket(Packet):
    """
    Confirm creating a character
    """
    _byte_size: int = 0
    _session_id: int = None # type: ignore [assignment]
    _gender: Gender = None # type: ignore [assignment]
    _hair_style: int = None # type: ignore [assignment]
    _hair_color: int = None # type: ignore [assignment]
    _skin: int = None # type: ignore [assignment]
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
    def gender(self) -> Gender:
        return self._gender

    @gender.setter
    def gender(self, gender: Gender) -> None:
        self._gender = gender

    @property
    def hair_style(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._hair_style

    @hair_style.setter
    def hair_style(self, hair_style: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._hair_style = hair_style

    @property
    def hair_color(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._hair_color

    @hair_color.setter
    def hair_color(self, hair_color: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._hair_color = hair_color

    @property
    def skin(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._skin

    @skin.setter
    def skin(self, skin: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._skin = skin

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Character

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
        CharacterCreateClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterCreateClientPacket") -> None:
        """
        Serializes an instance of `CharacterCreateClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterCreateClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            if data._gender is None:
                raise SerializationError("gender must be provided.")
            writer.add_short(int(data._gender))
            if data._hair_style is None:
                raise SerializationError("hair_style must be provided.")
            writer.add_short(data._hair_style)
            if data._hair_color is None:
                raise SerializationError("hair_color must be provided.")
            writer.add_short(data._hair_color)
            if data._skin is None:
                raise SerializationError("skin must be provided.")
            writer.add_short(data._skin)
            writer.add_byte(0xFF)
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
            writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterCreateClientPacket":
        """
        Deserializes an instance of `CharacterCreateClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterCreateClientPacket: The data to serialize.
        """
        data: CharacterCreateClientPacket = CharacterCreateClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._session_id = reader.get_short()
            data._gender = Gender(reader.get_short())
            data._hair_style = reader.get_short()
            data._hair_color = reader.get_short()
            data._skin = reader.get_short()
            reader.next_chunk()
            data._name = reader.get_string()
            reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterCreateClientPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, gender={repr(self._gender)}, hair_style={repr(self._hair_style)}, hair_color={repr(self._hair_color)}, skin={repr(self._skin)}, name={repr(self._name)})"
