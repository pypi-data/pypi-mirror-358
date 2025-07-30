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

class TradeAgreeClientPacket(Packet):
    """
    Mark trade as agreed
    """
    _byte_size: int = 0
    _agree: bool = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def agree(self) -> bool:
        return self._agree

    @agree.setter
    def agree(self, agree: bool) -> None:
        self._agree = agree

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Trade

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
        TradeAgreeClientPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "TradeAgreeClientPacket") -> None:
        """
        Serializes an instance of `TradeAgreeClientPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TradeAgreeClientPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._agree is None:
                raise SerializationError("agree must be provided.")
            writer.add_char(1 if data._agree else 0)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "TradeAgreeClientPacket":
        """
        Deserializes an instance of `TradeAgreeClientPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TradeAgreeClientPacket: The data to serialize.
        """
        data: TradeAgreeClientPacket = TradeAgreeClientPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._agree = reader.get_char() != 0
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TradeAgreeClientPacket(byte_size={repr(self._byte_size)}, agree={repr(self._agree)})"
