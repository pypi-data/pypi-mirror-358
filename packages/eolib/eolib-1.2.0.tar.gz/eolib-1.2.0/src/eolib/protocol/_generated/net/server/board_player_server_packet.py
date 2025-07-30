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

class BoardPlayerServerPacket(Packet):
    """
    Reply to reading a post on a town board
    """
    _byte_size: int = 0
    _post_id: int = None # type: ignore [assignment]
    _post_body: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def post_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._post_id

    @post_id.setter
    def post_id(self, post_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._post_id = post_id

    @property
    def post_body(self) -> str:
        return self._post_body

    @post_body.setter
    def post_body(self, post_body: str) -> None:
        self._post_body = post_body

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Board

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Player

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        BoardPlayerServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "BoardPlayerServerPacket") -> None:
        """
        Serializes an instance of `BoardPlayerServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BoardPlayerServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._post_id is None:
                raise SerializationError("post_id must be provided.")
            writer.add_short(data._post_id)
            if data._post_body is None:
                raise SerializationError("post_body must be provided.")
            writer.add_string(data._post_body)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "BoardPlayerServerPacket":
        """
        Deserializes an instance of `BoardPlayerServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BoardPlayerServerPacket: The data to serialize.
        """
        data: BoardPlayerServerPacket = BoardPlayerServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._post_id = reader.get_short()
            data._post_body = reader.get_string()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BoardPlayerServerPacket(byte_size={repr(self._byte_size)}, post_id={repr(self._post_id)}, post_body={repr(self._post_body)})"
