# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from typing import Union
from .warp_type import WarpType
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class WarpRequestServerPacket(Packet):
    """
    Warp request from server
    """
    _byte_size: int = 0
    _warp_type: WarpType = None # type: ignore [assignment]
    _map_id: int = None # type: ignore [assignment]
    _warp_type_data: 'WarpRequestServerPacket.WarpTypeData' = None
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
    def warp_type(self) -> WarpType:
        return self._warp_type

    @warp_type.setter
    def warp_type(self, warp_type: WarpType) -> None:
        self._warp_type = warp_type

    @property
    def map_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._map_id

    @map_id.setter
    def map_id(self, map_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._map_id = map_id

    @property
    def warp_type_data(self) -> 'WarpRequestServerPacket.WarpTypeData':
        """
        WarpRequestServerPacket.WarpTypeData: Gets or sets the data associated with the `warp_type` field.
        """
        return self._warp_type_data

    @warp_type_data.setter
    def warp_type_data(self, warp_type_data: 'WarpRequestServerPacket.WarpTypeData') -> None:
        self._warp_type_data = warp_type_data

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

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Warp

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Request

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        WarpRequestServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "WarpRequestServerPacket") -> None:
        """
        Serializes an instance of `WarpRequestServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WarpRequestServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._warp_type is None:
                raise SerializationError("warp_type must be provided.")
            writer.add_char(int(data._warp_type))
            if data._map_id is None:
                raise SerializationError("map_id must be provided.")
            writer.add_short(data._map_id)
            if data._warp_type == WarpType.MapSwitch:
                if not isinstance(data._warp_type_data, WarpRequestServerPacket.WarpTypeDataMapSwitch):
                    raise SerializationError("Expected warp_type_data to be type WarpRequestServerPacket.WarpTypeDataMapSwitch for warp_type " + WarpType(data._warp_type).name + ".")
                WarpRequestServerPacket.WarpTypeDataMapSwitch.serialize(writer, data._warp_type_data)
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "WarpRequestServerPacket":
        """
        Deserializes an instance of `WarpRequestServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WarpRequestServerPacket: The data to serialize.
        """
        data: WarpRequestServerPacket = WarpRequestServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._warp_type = WarpType(reader.get_char())
            data._map_id = reader.get_short()
            if data._warp_type == WarpType.MapSwitch:
                data._warp_type_data = WarpRequestServerPacket.WarpTypeDataMapSwitch.deserialize(reader)
            data._session_id = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WarpRequestServerPacket(byte_size={repr(self._byte_size)}, warp_type={repr(self._warp_type)}, map_id={repr(self._map_id)}, warp_type_data={repr(self._warp_type_data)}, session_id={repr(self._session_id)})"

    WarpTypeData = Union['WarpRequestServerPacket.WarpTypeDataMapSwitch', None]
    """
    Data associated with different values of the `warp_type` field.
    """

    class WarpTypeDataMapSwitch:
        """
        Data associated with warp_type value WarpType.MapSwitch
        """
        _byte_size: int = 0
        _map_rid: list[int] = None # type: ignore [assignment]
        _map_file_size: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def map_rid(self) -> list[int]:
            """
            Note:
              - Length must be `2`.
              - Element value range is 0-64008.
            """
            return self._map_rid

        @map_rid.setter
        def map_rid(self, map_rid: list[int]) -> None:
            """
            Note:
              - Length must be `2`.
              - Element value range is 0-64008.
            """
            self._map_rid = map_rid

        @property
        def map_file_size(self) -> int:
            """
            Note:
              - Value range is 0-16194276.
            """
            return self._map_file_size

        @map_file_size.setter
        def map_file_size(self, map_file_size: int) -> None:
            """
            Note:
              - Value range is 0-16194276.
            """
            self._map_file_size = map_file_size

        @staticmethod
        def serialize(writer: EoWriter, data: "WarpRequestServerPacket.WarpTypeDataMapSwitch") -> None:
            """
            Serializes an instance of `WarpRequestServerPacket.WarpTypeDataMapSwitch` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (WarpRequestServerPacket.WarpTypeDataMapSwitch): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._map_rid is None:
                    raise SerializationError("map_rid must be provided.")
                if len(data._map_rid) != 2:
                    raise SerializationError(f"Expected length of map_rid to be exactly 2, got {len(data._map_rid)}.")
                for i in range(2):
                    writer.add_short(data._map_rid[i])
                if data._map_file_size is None:
                    raise SerializationError("map_file_size must be provided.")
                writer.add_three(data._map_file_size)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "WarpRequestServerPacket.WarpTypeDataMapSwitch":
            """
            Deserializes an instance of `WarpRequestServerPacket.WarpTypeDataMapSwitch` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                WarpRequestServerPacket.WarpTypeDataMapSwitch: The data to serialize.
            """
            data: WarpRequestServerPacket.WarpTypeDataMapSwitch = WarpRequestServerPacket.WarpTypeDataMapSwitch()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._map_rid = []
                for i in range(2):
                    data._map_rid.append(reader.get_short())
                data._map_file_size = reader.get_three()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"WarpRequestServerPacket.WarpTypeDataMapSwitch(byte_size={repr(self._byte_size)}, map_rid={repr(self._map_rid)}, map_file_size={repr(self._map_file_size)})"
