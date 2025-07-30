# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .map_warp_row import MapWarpRow
from .map_type import MapType
from .map_timed_effect import MapTimedEffect
from .map_tile_spec_row import MapTileSpecRow
from .map_sign import MapSign
from .map_npc import MapNpc
from .map_music_control import MapMusicControl
from .map_legacy_door_key import MapLegacyDoorKey
from .map_item import MapItem
from .map_graphic_layer import MapGraphicLayer
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class Emf:
    """
    Endless Map File
    """
    _byte_size: int = 0
    _rid: list[int] = None # type: ignore [assignment]
    _name: str = None # type: ignore [assignment]
    _type: MapType = None # type: ignore [assignment]
    _timed_effect: MapTimedEffect = None # type: ignore [assignment]
    _music_id: int = None # type: ignore [assignment]
    _music_control: MapMusicControl = None # type: ignore [assignment]
    _ambient_sound_id: int = None # type: ignore [assignment]
    _width: int = None # type: ignore [assignment]
    _height: int = None # type: ignore [assignment]
    _fill_tile: int = None # type: ignore [assignment]
    _map_available: bool = None # type: ignore [assignment]
    _can_scroll: bool = None # type: ignore [assignment]
    _relog_x: int = None # type: ignore [assignment]
    _relog_y: int = None # type: ignore [assignment]
    _npcs_count: int = None # type: ignore [assignment]
    _npcs: list[MapNpc] = None # type: ignore [assignment]
    _legacy_door_keys_count: int = None # type: ignore [assignment]
    _legacy_door_keys: list[MapLegacyDoorKey] = None # type: ignore [assignment]
    _items_count: int = None # type: ignore [assignment]
    _items: list[MapItem] = None # type: ignore [assignment]
    _tile_spec_rows_count: int = None # type: ignore [assignment]
    _tile_spec_rows: list[MapTileSpecRow] = None # type: ignore [assignment]
    _warp_rows_count: int = None # type: ignore [assignment]
    _warp_rows: list[MapWarpRow] = None # type: ignore [assignment]
    _graphic_layers: list[MapGraphicLayer] = None # type: ignore [assignment]
    _signs_count: int = None # type: ignore [assignment]
    _signs: list[MapSign] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def rid(self) -> list[int]:
        """
        Note:
          - Length must be `2`.
          - Element value range is 0-64008.
        """
        return self._rid

    @rid.setter
    def rid(self, rid: list[int]) -> None:
        """
        Note:
          - Length must be `2`.
          - Element value range is 0-64008.
        """
        self._rid = rid

    @property
    def name(self) -> str:
        """
        Note:
          - Length must be `24` or less.
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Note:
          - Length must be `24` or less.
        """
        self._name = name

    @property
    def type(self) -> MapType:
        return self._type

    @type.setter
    def type(self, type: MapType) -> None:
        self._type = type

    @property
    def timed_effect(self) -> MapTimedEffect:
        return self._timed_effect

    @timed_effect.setter
    def timed_effect(self, timed_effect: MapTimedEffect) -> None:
        self._timed_effect = timed_effect

    @property
    def music_id(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._music_id

    @music_id.setter
    def music_id(self, music_id: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._music_id = music_id

    @property
    def music_control(self) -> MapMusicControl:
        return self._music_control

    @music_control.setter
    def music_control(self, music_control: MapMusicControl) -> None:
        self._music_control = music_control

    @property
    def ambient_sound_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._ambient_sound_id

    @ambient_sound_id.setter
    def ambient_sound_id(self, ambient_sound_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._ambient_sound_id = ambient_sound_id

    @property
    def width(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._width

    @width.setter
    def width(self, width: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._width = width

    @property
    def height(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._height

    @height.setter
    def height(self, height: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._height = height

    @property
    def fill_tile(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._fill_tile

    @fill_tile.setter
    def fill_tile(self, fill_tile: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._fill_tile = fill_tile

    @property
    def map_available(self) -> bool:
        return self._map_available

    @map_available.setter
    def map_available(self, map_available: bool) -> None:
        self._map_available = map_available

    @property
    def can_scroll(self) -> bool:
        return self._can_scroll

    @can_scroll.setter
    def can_scroll(self, can_scroll: bool) -> None:
        self._can_scroll = can_scroll

    @property
    def relog_x(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._relog_x

    @relog_x.setter
    def relog_x(self, relog_x: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._relog_x = relog_x

    @property
    def relog_y(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._relog_y

    @relog_y.setter
    def relog_y(self, relog_y: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._relog_y = relog_y

    @property
    def npcs(self) -> list[MapNpc]:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._npcs

    @npcs.setter
    def npcs(self, npcs: list[MapNpc]) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._npcs = npcs
        self._npcs_count = len(self._npcs)

    @property
    def legacy_door_keys(self) -> list[MapLegacyDoorKey]:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._legacy_door_keys

    @legacy_door_keys.setter
    def legacy_door_keys(self, legacy_door_keys: list[MapLegacyDoorKey]) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._legacy_door_keys = legacy_door_keys
        self._legacy_door_keys_count = len(self._legacy_door_keys)

    @property
    def items(self) -> list[MapItem]:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._items

    @items.setter
    def items(self, items: list[MapItem]) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._items = items
        self._items_count = len(self._items)

    @property
    def tile_spec_rows(self) -> list[MapTileSpecRow]:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._tile_spec_rows

    @tile_spec_rows.setter
    def tile_spec_rows(self, tile_spec_rows: list[MapTileSpecRow]) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._tile_spec_rows = tile_spec_rows
        self._tile_spec_rows_count = len(self._tile_spec_rows)

    @property
    def warp_rows(self) -> list[MapWarpRow]:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._warp_rows

    @warp_rows.setter
    def warp_rows(self, warp_rows: list[MapWarpRow]) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._warp_rows = warp_rows
        self._warp_rows_count = len(self._warp_rows)

    @property
    def graphic_layers(self) -> list[MapGraphicLayer]:
        """
        The 9 layers of map graphics.
        Order is [Ground, Object, Overlay, Down Wall, Right Wall, Roof, Top, Shadow, Overlay2]

        Note:
          - Length must be `9`.
        """
        return self._graphic_layers

    @graphic_layers.setter
    def graphic_layers(self, graphic_layers: list[MapGraphicLayer]) -> None:
        """
        The 9 layers of map graphics.
        Order is [Ground, Object, Overlay, Down Wall, Right Wall, Roof, Top, Shadow, Overlay2]

        Note:
          - Length must be `9`.
        """
        self._graphic_layers = graphic_layers

    @property
    def signs(self) -> list[MapSign]:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._signs

    @signs.setter
    def signs(self, signs: list[MapSign]) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._signs = signs
        self._signs_count = len(self._signs)

    @staticmethod
    def serialize(writer: EoWriter, data: "Emf") -> None:
        """
        Serializes an instance of `Emf` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (Emf): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_fixed_string("EMF", 3, False)
            if data._rid is None:
                raise SerializationError("rid must be provided.")
            if len(data._rid) != 2:
                raise SerializationError(f"Expected length of rid to be exactly 2, got {len(data._rid)}.")
            for i in range(2):
                writer.add_short(data._rid[i])
            if data._name is None:
                raise SerializationError("name must be provided.")
            if len(data._name) > 24:
                raise SerializationError(f"Expected length of name to be 24 or less, got {len(data._name)}.")
            writer.add_fixed_encoded_string(data._name, 24, True)
            if data._type is None:
                raise SerializationError("type must be provided.")
            writer.add_char(int(data._type))
            if data._timed_effect is None:
                raise SerializationError("timed_effect must be provided.")
            writer.add_char(int(data._timed_effect))
            if data._music_id is None:
                raise SerializationError("music_id must be provided.")
            writer.add_char(data._music_id)
            if data._music_control is None:
                raise SerializationError("music_control must be provided.")
            writer.add_char(int(data._music_control))
            if data._ambient_sound_id is None:
                raise SerializationError("ambient_sound_id must be provided.")
            writer.add_short(data._ambient_sound_id)
            if data._width is None:
                raise SerializationError("width must be provided.")
            writer.add_char(data._width)
            if data._height is None:
                raise SerializationError("height must be provided.")
            writer.add_char(data._height)
            if data._fill_tile is None:
                raise SerializationError("fill_tile must be provided.")
            writer.add_short(data._fill_tile)
            if data._map_available is None:
                raise SerializationError("map_available must be provided.")
            writer.add_char(1 if data._map_available else 0)
            if data._can_scroll is None:
                raise SerializationError("can_scroll must be provided.")
            writer.add_char(1 if data._can_scroll else 0)
            if data._relog_x is None:
                raise SerializationError("relog_x must be provided.")
            writer.add_char(data._relog_x)
            if data._relog_y is None:
                raise SerializationError("relog_y must be provided.")
            writer.add_char(data._relog_y)
            writer.add_char(0)
            if data._npcs_count is None:
                raise SerializationError("npcs_count must be provided.")
            writer.add_char(data._npcs_count)
            if data._npcs is None:
                raise SerializationError("npcs must be provided.")
            if len(data._npcs) > 252:
                raise SerializationError(f"Expected length of npcs to be 252 or less, got {len(data._npcs)}.")
            for i in range(data._npcs_count):
                MapNpc.serialize(writer, data._npcs[i])
            if data._legacy_door_keys_count is None:
                raise SerializationError("legacy_door_keys_count must be provided.")
            writer.add_char(data._legacy_door_keys_count)
            if data._legacy_door_keys is None:
                raise SerializationError("legacy_door_keys must be provided.")
            if len(data._legacy_door_keys) > 252:
                raise SerializationError(f"Expected length of legacy_door_keys to be 252 or less, got {len(data._legacy_door_keys)}.")
            for i in range(data._legacy_door_keys_count):
                MapLegacyDoorKey.serialize(writer, data._legacy_door_keys[i])
            if data._items_count is None:
                raise SerializationError("items_count must be provided.")
            writer.add_char(data._items_count)
            if data._items is None:
                raise SerializationError("items must be provided.")
            if len(data._items) > 252:
                raise SerializationError(f"Expected length of items to be 252 or less, got {len(data._items)}.")
            for i in range(data._items_count):
                MapItem.serialize(writer, data._items[i])
            if data._tile_spec_rows_count is None:
                raise SerializationError("tile_spec_rows_count must be provided.")
            writer.add_char(data._tile_spec_rows_count)
            if data._tile_spec_rows is None:
                raise SerializationError("tile_spec_rows must be provided.")
            if len(data._tile_spec_rows) > 252:
                raise SerializationError(f"Expected length of tile_spec_rows to be 252 or less, got {len(data._tile_spec_rows)}.")
            for i in range(data._tile_spec_rows_count):
                MapTileSpecRow.serialize(writer, data._tile_spec_rows[i])
            if data._warp_rows_count is None:
                raise SerializationError("warp_rows_count must be provided.")
            writer.add_char(data._warp_rows_count)
            if data._warp_rows is None:
                raise SerializationError("warp_rows must be provided.")
            if len(data._warp_rows) > 252:
                raise SerializationError(f"Expected length of warp_rows to be 252 or less, got {len(data._warp_rows)}.")
            for i in range(data._warp_rows_count):
                MapWarpRow.serialize(writer, data._warp_rows[i])
            if data._graphic_layers is None:
                raise SerializationError("graphic_layers must be provided.")
            if len(data._graphic_layers) != 9:
                raise SerializationError(f"Expected length of graphic_layers to be exactly 9, got {len(data._graphic_layers)}.")
            for i in range(9):
                MapGraphicLayer.serialize(writer, data._graphic_layers[i])
            if data._signs_count is None:
                raise SerializationError("signs_count must be provided.")
            writer.add_char(data._signs_count)
            if data._signs is None:
                raise SerializationError("signs must be provided.")
            if len(data._signs) > 252:
                raise SerializationError(f"Expected length of signs to be 252 or less, got {len(data._signs)}.")
            for i in range(data._signs_count):
                MapSign.serialize(writer, data._signs[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "Emf":
        """
        Deserializes an instance of `Emf` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            Emf: The data to serialize.
        """
        data: Emf = Emf()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_fixed_string(3, False)
            data._rid = []
            for i in range(2):
                data._rid.append(reader.get_short())
            data._name = reader.get_fixed_encoded_string(24, True)
            data._type = MapType(reader.get_char())
            data._timed_effect = MapTimedEffect(reader.get_char())
            data._music_id = reader.get_char()
            data._music_control = MapMusicControl(reader.get_char())
            data._ambient_sound_id = reader.get_short()
            data._width = reader.get_char()
            data._height = reader.get_char()
            data._fill_tile = reader.get_short()
            data._map_available = reader.get_char() != 0
            data._can_scroll = reader.get_char() != 0
            data._relog_x = reader.get_char()
            data._relog_y = reader.get_char()
            reader.get_char()
            data._npcs_count = reader.get_char()
            data._npcs = []
            for i in range(data._npcs_count):
                data._npcs.append(MapNpc.deserialize(reader))
            data._legacy_door_keys_count = reader.get_char()
            data._legacy_door_keys = []
            for i in range(data._legacy_door_keys_count):
                data._legacy_door_keys.append(MapLegacyDoorKey.deserialize(reader))
            data._items_count = reader.get_char()
            data._items = []
            for i in range(data._items_count):
                data._items.append(MapItem.deserialize(reader))
            data._tile_spec_rows_count = reader.get_char()
            data._tile_spec_rows = []
            for i in range(data._tile_spec_rows_count):
                data._tile_spec_rows.append(MapTileSpecRow.deserialize(reader))
            data._warp_rows_count = reader.get_char()
            data._warp_rows = []
            for i in range(data._warp_rows_count):
                data._warp_rows.append(MapWarpRow.deserialize(reader))
            data._graphic_layers = []
            for i in range(9):
                data._graphic_layers.append(MapGraphicLayer.deserialize(reader))
            data._signs_count = reader.get_char()
            data._signs = []
            for i in range(data._signs_count):
                data._signs.append(MapSign.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"Emf(byte_size={repr(self._byte_size)}, rid={repr(self._rid)}, name={repr(self._name)}, type={repr(self._type)}, timed_effect={repr(self._timed_effect)}, music_id={repr(self._music_id)}, music_control={repr(self._music_control)}, ambient_sound_id={repr(self._ambient_sound_id)}, width={repr(self._width)}, height={repr(self._height)}, fill_tile={repr(self._fill_tile)}, map_available={repr(self._map_available)}, can_scroll={repr(self._can_scroll)}, relog_x={repr(self._relog_x)}, relog_y={repr(self._relog_y)}, npcs={repr(self._npcs)}, legacy_door_keys={repr(self._legacy_door_keys)}, items={repr(self._items)}, tile_spec_rows={repr(self._tile_spec_rows)}, warp_rows={repr(self._warp_rows)}, graphic_layers={repr(self._graphic_layers)}, signs={repr(self._signs)})"
