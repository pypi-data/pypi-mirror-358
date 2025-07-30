# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...coords import Coords
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ServerSettings:
    """
    Settings sent with WELCOME_REPLY packet
    """
    _byte_size: int = 0
    _jail_map: int = None # type: ignore [assignment]
    _rescue_map: int = None # type: ignore [assignment]
    _rescue_coords: Coords = None # type: ignore [assignment]
    _spy_and_light_guide_flood_rate: int = None # type: ignore [assignment]
    _guardian_flood_rate: int = None # type: ignore [assignment]
    _game_master_flood_rate: int = None # type: ignore [assignment]
    _high_game_master_flood_rate: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def jail_map(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._jail_map

    @jail_map.setter
    def jail_map(self, jail_map: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._jail_map = jail_map

    @property
    def rescue_map(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._rescue_map

    @rescue_map.setter
    def rescue_map(self, rescue_map: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._rescue_map = rescue_map

    @property
    def rescue_coords(self) -> Coords:
        return self._rescue_coords

    @rescue_coords.setter
    def rescue_coords(self, rescue_coords: Coords) -> None:
        self._rescue_coords = rescue_coords

    @property
    def spy_and_light_guide_flood_rate(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._spy_and_light_guide_flood_rate

    @spy_and_light_guide_flood_rate.setter
    def spy_and_light_guide_flood_rate(self, spy_and_light_guide_flood_rate: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._spy_and_light_guide_flood_rate = spy_and_light_guide_flood_rate

    @property
    def guardian_flood_rate(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._guardian_flood_rate

    @guardian_flood_rate.setter
    def guardian_flood_rate(self, guardian_flood_rate: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._guardian_flood_rate = guardian_flood_rate

    @property
    def game_master_flood_rate(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._game_master_flood_rate

    @game_master_flood_rate.setter
    def game_master_flood_rate(self, game_master_flood_rate: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._game_master_flood_rate = game_master_flood_rate

    @property
    def high_game_master_flood_rate(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._high_game_master_flood_rate

    @high_game_master_flood_rate.setter
    def high_game_master_flood_rate(self, high_game_master_flood_rate: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._high_game_master_flood_rate = high_game_master_flood_rate

    @staticmethod
    def serialize(writer: EoWriter, data: "ServerSettings") -> None:
        """
        Serializes an instance of `ServerSettings` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ServerSettings): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._jail_map is None:
                raise SerializationError("jail_map must be provided.")
            writer.add_short(data._jail_map)
            if data._rescue_map is None:
                raise SerializationError("rescue_map must be provided.")
            writer.add_short(data._rescue_map)
            if data._rescue_coords is None:
                raise SerializationError("rescue_coords must be provided.")
            Coords.serialize(writer, data._rescue_coords)
            if data._spy_and_light_guide_flood_rate is None:
                raise SerializationError("spy_and_light_guide_flood_rate must be provided.")
            writer.add_short(data._spy_and_light_guide_flood_rate)
            if data._guardian_flood_rate is None:
                raise SerializationError("guardian_flood_rate must be provided.")
            writer.add_short(data._guardian_flood_rate)
            if data._game_master_flood_rate is None:
                raise SerializationError("game_master_flood_rate must be provided.")
            writer.add_short(data._game_master_flood_rate)
            if data._high_game_master_flood_rate is None:
                raise SerializationError("high_game_master_flood_rate must be provided.")
            writer.add_short(data._high_game_master_flood_rate)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ServerSettings":
        """
        Deserializes an instance of `ServerSettings` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ServerSettings: The data to serialize.
        """
        data: ServerSettings = ServerSettings()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._jail_map = reader.get_short()
            data._rescue_map = reader.get_short()
            data._rescue_coords = Coords.deserialize(reader)
            data._spy_and_light_guide_flood_rate = reader.get_short()
            data._guardian_flood_rate = reader.get_short()
            data._game_master_flood_rate = reader.get_short()
            data._high_game_master_flood_rate = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ServerSettings(byte_size={repr(self._byte_size)}, jail_map={repr(self._jail_map)}, rescue_map={repr(self._rescue_map)}, rescue_coords={repr(self._rescue_coords)}, spy_and_light_guide_flood_rate={repr(self._spy_and_light_guide_flood_rate)}, guardian_flood_rate={repr(self._guardian_flood_rate)}, game_master_flood_rate={repr(self._game_master_flood_rate)}, high_game_master_flood_rate={repr(self._high_game_master_flood_rate)})"
