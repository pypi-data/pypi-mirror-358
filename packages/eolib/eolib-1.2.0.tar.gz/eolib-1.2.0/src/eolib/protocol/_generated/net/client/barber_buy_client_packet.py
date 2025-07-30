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

class BarberBuyClientPacket(Packet):
    """
    Purchasing a hair-style
    """
    _byte_size: int = 0
    _hair_style: int = None # type: ignore [assignment]
    _hair_color: int = None # type: ignore [assignment]
    _session_id: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def hair_style(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._hair_style

    @hair_style.setter
    def hair_style(self, hair_style: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._hair_style = hair_style

    @property
    def hair_color(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._hair_color

    @hair_color.setter
    def hair_color(self, hair_color: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._hair_color = hair_color

    @property
    def session_id(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._session_id

    @session_id.setter
    def session_id(self, session_id: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._session_id = session_id

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Barber

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Buy

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        BarberBuyClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "BarberBuyClientPacket") -> None:
        """
        Serializes an instance of `BarberBuyClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BarberBuyClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._hair_style is None:
                raise SerializationError("hair_style must be provided.")
            writer.add_char(data._hair_style)
            if data._hair_color is None:
                raise SerializationError("hair_color must be provided.")
            writer.add_char(data._hair_color)
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_int(data._session_id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "BarberBuyClientPacket":
        """
        Deserializes an instance of `BarberBuyClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BarberBuyClientPacket: The data to serialize.
        """
        data: BarberBuyClientPacket = BarberBuyClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._hair_style = reader.get_char()
            data._hair_color = reader.get_char()
            data._session_id = reader.get_int()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BarberBuyClientPacket(byte_size={repr(self._byte_size)}, hair_style={repr(self._hair_style)}, hair_color={repr(self._hair_color)}, session_id={repr(self._session_id)})"
