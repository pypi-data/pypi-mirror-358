# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .board_post_listing import BoardPostListing
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class BoardOpenServerPacket(Packet):
    """
    Reply to opening a town board
    """
    _byte_size: int = 0
    _board_id: int = None # type: ignore [assignment]
    _posts_count: int = None # type: ignore [assignment]
    _posts: list[BoardPostListing] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def board_id(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._board_id

    @board_id.setter
    def board_id(self, board_id: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._board_id = board_id

    @property
    def posts(self) -> list[BoardPostListing]:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._posts

    @posts.setter
    def posts(self, posts: list[BoardPostListing]) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._posts = posts
        self._posts_count = len(self._posts)

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
        return PacketAction.Open

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        BoardOpenServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "BoardOpenServerPacket") -> None:
        """
        Serializes an instance of `BoardOpenServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BoardOpenServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._board_id is None:
                raise SerializationError("board_id must be provided.")
            writer.add_char(data._board_id)
            if data._posts_count is None:
                raise SerializationError("posts_count must be provided.")
            writer.add_char(data._posts_count)
            if data._posts is None:
                raise SerializationError("posts must be provided.")
            if len(data._posts) > 252:
                raise SerializationError(f"Expected length of posts to be 252 or less, got {len(data._posts)}.")
            for i in range(data._posts_count):
                BoardPostListing.serialize(writer, data._posts[i])
                writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "BoardOpenServerPacket":
        """
        Deserializes an instance of `BoardOpenServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BoardOpenServerPacket: The data to serialize.
        """
        data: BoardOpenServerPacket = BoardOpenServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._board_id = reader.get_char()
            data._posts_count = reader.get_char()
            data._posts = []
            for i in range(data._posts_count):
                data._posts.append(BoardPostListing.deserialize(reader))
                reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BoardOpenServerPacket(byte_size={repr(self._byte_size)}, board_id={repr(self._board_id)}, posts={repr(self._posts)})"
