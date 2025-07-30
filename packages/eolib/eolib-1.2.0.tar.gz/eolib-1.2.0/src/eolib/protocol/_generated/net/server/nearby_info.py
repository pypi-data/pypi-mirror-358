# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .npc_map_info import NpcMapInfo
from .item_map_info import ItemMapInfo
from .character_map_info import CharacterMapInfo
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NearbyInfo:
    """
    Information about nearby entities
    """
    _byte_size: int = 0
    _characters_count: int = None # type: ignore [assignment]
    _characters: list[CharacterMapInfo] = None # type: ignore [assignment]
    _npcs: list[NpcMapInfo] = None # type: ignore [assignment]
    _items: list[ItemMapInfo] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def characters(self) -> list[CharacterMapInfo]:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._characters

    @characters.setter
    def characters(self, characters: list[CharacterMapInfo]) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._characters = characters
        self._characters_count = len(self._characters)

    @property
    def npcs(self) -> list[NpcMapInfo]:
        return self._npcs

    @npcs.setter
    def npcs(self, npcs: list[NpcMapInfo]) -> None:
        self._npcs = npcs

    @property
    def items(self) -> list[ItemMapInfo]:
        return self._items

    @items.setter
    def items(self, items: list[ItemMapInfo]) -> None:
        self._items = items

    @staticmethod
    def serialize(writer: EoWriter, data: "NearbyInfo") -> None:
        """
        Serializes an instance of `NearbyInfo` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NearbyInfo): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._characters_count is None:
                raise SerializationError("characters_count must be provided.")
            writer.add_char(data._characters_count)
            writer.string_sanitization_mode = True
            writer.add_byte(0xFF)
            if data._characters is None:
                raise SerializationError("characters must be provided.")
            if len(data._characters) > 252:
                raise SerializationError(f"Expected length of characters to be 252 or less, got {len(data._characters)}.")
            for i in range(data._characters_count):
                CharacterMapInfo.serialize(writer, data._characters[i])
                writer.add_byte(0xFF)
            if data._npcs is None:
                raise SerializationError("npcs must be provided.")
            for i in range(len(data._npcs)):
                NpcMapInfo.serialize(writer, data._npcs[i])
            writer.add_byte(0xFF)
            if data._items is None:
                raise SerializationError("items must be provided.")
            for i in range(len(data._items)):
                ItemMapInfo.serialize(writer, data._items[i])
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "NearbyInfo":
        """
        Deserializes an instance of `NearbyInfo` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NearbyInfo: The data to serialize.
        """
        data: NearbyInfo = NearbyInfo()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._characters_count = reader.get_char()
            reader.chunked_reading_mode = True
            reader.next_chunk()
            data._characters = []
            for i in range(data._characters_count):
                data._characters.append(CharacterMapInfo.deserialize(reader))
                reader.next_chunk()
            npcs_length = int(reader.remaining / 6)
            data._npcs = []
            for i in range(npcs_length):
                data._npcs.append(NpcMapInfo.deserialize(reader))
            reader.next_chunk()
            items_length = int(reader.remaining / 9)
            data._items = []
            for i in range(items_length):
                data._items.append(ItemMapInfo.deserialize(reader))
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NearbyInfo(byte_size={repr(self._byte_size)}, characters={repr(self._characters)}, npcs={repr(self._npcs)}, items={repr(self._items)})"
