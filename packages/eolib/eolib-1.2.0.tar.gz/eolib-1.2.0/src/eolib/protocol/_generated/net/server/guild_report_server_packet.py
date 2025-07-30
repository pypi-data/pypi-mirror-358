# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .guild_staff import GuildStaff
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class GuildReportServerPacket(Packet):
    """
    Get guild info reply
    """
    _byte_size: int = 0
    _name: str = None # type: ignore [assignment]
    _tag: str = None # type: ignore [assignment]
    _create_date: str = None # type: ignore [assignment]
    _description: str = None # type: ignore [assignment]
    _wealth: str = None # type: ignore [assignment]
    _ranks: list[str] = None # type: ignore [assignment]
    _staff_count: int = None # type: ignore [assignment]
    _staff: list[GuildStaff] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def tag(self) -> str:
        return self._tag

    @tag.setter
    def tag(self, tag: str) -> None:
        self._tag = tag

    @property
    def create_date(self) -> str:
        return self._create_date

    @create_date.setter
    def create_date(self, create_date: str) -> None:
        self._create_date = create_date

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description: str) -> None:
        self._description = description

    @property
    def wealth(self) -> str:
        return self._wealth

    @wealth.setter
    def wealth(self, wealth: str) -> None:
        self._wealth = wealth

    @property
    def ranks(self) -> list[str]:
        """
        Note:
          - Length must be `9`.
        """
        return self._ranks

    @ranks.setter
    def ranks(self, ranks: list[str]) -> None:
        """
        Note:
          - Length must be `9`.
        """
        self._ranks = ranks

    @property
    def staff(self) -> list[GuildStaff]:
        """
        Note:
          - Length must be 64008 or less.
        """
        return self._staff

    @staff.setter
    def staff(self, staff: list[GuildStaff]) -> None:
        """
        Note:
          - Length must be 64008 or less.
        """
        self._staff = staff
        self._staff_count = len(self._staff)

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Guild

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Report

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        GuildReportServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildReportServerPacket") -> None:
        """
        Serializes an instance of `GuildReportServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildReportServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
            writer.add_byte(0xFF)
            if data._tag is None:
                raise SerializationError("tag must be provided.")
            writer.add_string(data._tag)
            writer.add_byte(0xFF)
            if data._create_date is None:
                raise SerializationError("create_date must be provided.")
            writer.add_string(data._create_date)
            writer.add_byte(0xFF)
            if data._description is None:
                raise SerializationError("description must be provided.")
            writer.add_string(data._description)
            writer.add_byte(0xFF)
            if data._wealth is None:
                raise SerializationError("wealth must be provided.")
            writer.add_string(data._wealth)
            writer.add_byte(0xFF)
            if data._ranks is None:
                raise SerializationError("ranks must be provided.")
            if len(data._ranks) != 9:
                raise SerializationError(f"Expected length of ranks to be exactly 9, got {len(data._ranks)}.")
            for i in range(9):
                writer.add_string(data._ranks[i])
                writer.add_byte(0xFF)
            if data._staff_count is None:
                raise SerializationError("staff_count must be provided.")
            writer.add_short(data._staff_count)
            writer.add_byte(0xFF)
            if data._staff is None:
                raise SerializationError("staff must be provided.")
            if len(data._staff) > 64008:
                raise SerializationError(f"Expected length of staff to be 64008 or less, got {len(data._staff)}.")
            for i in range(data._staff_count):
                GuildStaff.serialize(writer, data._staff[i])
                writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildReportServerPacket":
        """
        Deserializes an instance of `GuildReportServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildReportServerPacket: The data to serialize.
        """
        data: GuildReportServerPacket = GuildReportServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._name = reader.get_string()
            reader.next_chunk()
            data._tag = reader.get_string()
            reader.next_chunk()
            data._create_date = reader.get_string()
            reader.next_chunk()
            data._description = reader.get_string()
            reader.next_chunk()
            data._wealth = reader.get_string()
            reader.next_chunk()
            data._ranks = []
            for i in range(9):
                data._ranks.append(reader.get_string())
                reader.next_chunk()
            data._staff_count = reader.get_short()
            reader.next_chunk()
            data._staff = []
            for i in range(data._staff_count):
                data._staff.append(GuildStaff.deserialize(reader))
                reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildReportServerPacket(byte_size={repr(self._byte_size)}, name={repr(self._name)}, tag={repr(self._tag)}, create_date={repr(self._create_date)}, description={repr(self._description)}, wealth={repr(self._wealth)}, ranks={repr(self._ranks)}, staff={repr(self._staff)})"
