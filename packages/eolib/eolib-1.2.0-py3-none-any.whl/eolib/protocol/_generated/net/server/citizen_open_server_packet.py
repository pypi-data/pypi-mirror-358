# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CitizenOpenServerPacket(Packet):
    """
    Response from talking to a citizenship NPC
    """
    _byte_size: int = 0
    _behavior_id: int = None # type: ignore [assignment]
    _current_home_id: int = None # type: ignore [assignment]
    _session_id: int = None # type: ignore [assignment]
    _questions: list[str] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def behavior_id(self) -> int:
        """
        Note:
          - Value range is 0-16194276.
        """
        return self._behavior_id

    @behavior_id.setter
    def behavior_id(self, behavior_id: int) -> None:
        """
        Note:
          - Value range is 0-16194276.
        """
        self._behavior_id = behavior_id

    @property
    def current_home_id(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._current_home_id

    @current_home_id.setter
    def current_home_id(self, current_home_id: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._current_home_id = current_home_id

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
    def questions(self) -> list[str]:
        """
        Note:
          - Length must be `3`.
        """
        return self._questions

    @questions.setter
    def questions(self, questions: list[str]) -> None:
        """
        Note:
          - Length must be `3`.
        """
        self._questions = questions

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Citizen

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
        CitizenOpenServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "CitizenOpenServerPacket") -> None:
        """
        Serializes an instance of `CitizenOpenServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CitizenOpenServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._behavior_id is None:
                raise SerializationError("behavior_id must be provided.")
            writer.add_three(data._behavior_id)
            if data._current_home_id is None:
                raise SerializationError("current_home_id must be provided.")
            writer.add_char(data._current_home_id)
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            writer.add_byte(0xFF)
            if data._questions is None:
                raise SerializationError("questions must be provided.")
            if len(data._questions) != 3:
                raise SerializationError(f"Expected length of questions to be exactly 3, got {len(data._questions)}.")
            for i in range(3):
                if i > 0:
                    writer.add_byte(0xFF)
                writer.add_string(data._questions[i])
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CitizenOpenServerPacket":
        """
        Deserializes an instance of `CitizenOpenServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CitizenOpenServerPacket: The data to serialize.
        """
        data: CitizenOpenServerPacket = CitizenOpenServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._behavior_id = reader.get_three()
            data._current_home_id = reader.get_char()
            data._session_id = reader.get_short()
            reader.next_chunk()
            data._questions = []
            for i in range(3):
                data._questions.append(reader.get_string())
                if i + 1 < 3:
                    reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CitizenOpenServerPacket(byte_size={repr(self._byte_size)}, behavior_id={repr(self._behavior_id)}, current_home_id={repr(self._current_home_id)}, session_id={repr(self._session_id)}, questions={repr(self._questions)})"
