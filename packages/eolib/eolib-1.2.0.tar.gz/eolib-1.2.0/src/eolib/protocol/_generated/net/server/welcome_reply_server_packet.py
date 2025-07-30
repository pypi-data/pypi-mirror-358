# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from typing import Union
from .welcome_code import WelcomeCode
from .server_settings import ServerSettings
from .nearby_info import NearbyInfo
from .login_message_code import LoginMessageCode
from .equipment_welcome import EquipmentWelcome
from .character_stats_welcome import CharacterStatsWelcome
from ..weight import Weight
from ..spell import Spell
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ..item import Item
from ...admin_level import AdminLevel
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class WelcomeReplyServerPacket(Packet):
    """
    Reply to selecting a character / entering game
    """
    _byte_size: int = 0
    _welcome_code: WelcomeCode = None # type: ignore [assignment]
    _welcome_code_data: 'WelcomeReplyServerPacket.WelcomeCodeData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def welcome_code(self) -> WelcomeCode:
        return self._welcome_code

    @welcome_code.setter
    def welcome_code(self, welcome_code: WelcomeCode) -> None:
        self._welcome_code = welcome_code

    @property
    def welcome_code_data(self) -> 'WelcomeReplyServerPacket.WelcomeCodeData':
        """
        WelcomeReplyServerPacket.WelcomeCodeData: Gets or sets the data associated with the `welcome_code` field.
        """
        return self._welcome_code_data

    @welcome_code_data.setter
    def welcome_code_data(self, welcome_code_data: 'WelcomeReplyServerPacket.WelcomeCodeData') -> None:
        self._welcome_code_data = welcome_code_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Welcome

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Reply

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        WelcomeReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "WelcomeReplyServerPacket") -> None:
        """
        Serializes an instance of `WelcomeReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WelcomeReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._welcome_code is None:
                raise SerializationError("welcome_code must be provided.")
            writer.add_short(int(data._welcome_code))
            writer.string_sanitization_mode = True
            if data._welcome_code == WelcomeCode.SelectCharacter:
                if not isinstance(data._welcome_code_data, WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter):
                    raise SerializationError("Expected welcome_code_data to be type WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter for welcome_code " + WelcomeCode(data._welcome_code).name + ".")
                WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter.serialize(writer, data._welcome_code_data)
            elif data._welcome_code == WelcomeCode.EnterGame:
                if not isinstance(data._welcome_code_data, WelcomeReplyServerPacket.WelcomeCodeDataEnterGame):
                    raise SerializationError("Expected welcome_code_data to be type WelcomeReplyServerPacket.WelcomeCodeDataEnterGame for welcome_code " + WelcomeCode(data._welcome_code).name + ".")
                WelcomeReplyServerPacket.WelcomeCodeDataEnterGame.serialize(writer, data._welcome_code_data)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "WelcomeReplyServerPacket":
        """
        Deserializes an instance of `WelcomeReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WelcomeReplyServerPacket: The data to serialize.
        """
        data: WelcomeReplyServerPacket = WelcomeReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._welcome_code = WelcomeCode(reader.get_short())
            reader.chunked_reading_mode = True
            if data._welcome_code == WelcomeCode.SelectCharacter:
                data._welcome_code_data = WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter.deserialize(reader)
            elif data._welcome_code == WelcomeCode.EnterGame:
                data._welcome_code_data = WelcomeReplyServerPacket.WelcomeCodeDataEnterGame.deserialize(reader)
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WelcomeReplyServerPacket(byte_size={repr(self._byte_size)}, welcome_code={repr(self._welcome_code)}, welcome_code_data={repr(self._welcome_code_data)})"

    WelcomeCodeData = Union['WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter', 'WelcomeReplyServerPacket.WelcomeCodeDataEnterGame', None]
    """
    Data associated with different values of the `welcome_code` field.
    """

    class WelcomeCodeDataSelectCharacter:
        """
        Data associated with welcome_code value WelcomeCode.SelectCharacter
        """
        _byte_size: int = 0
        _session_id: int = None # type: ignore [assignment]
        _character_id: int = None # type: ignore [assignment]
        _map_id: int = None # type: ignore [assignment]
        _map_rid: list[int] = None # type: ignore [assignment]
        _map_file_size: int = None # type: ignore [assignment]
        _eif_rid: list[int] = None # type: ignore [assignment]
        _eif_length: int = None # type: ignore [assignment]
        _enf_rid: list[int] = None # type: ignore [assignment]
        _enf_length: int = None # type: ignore [assignment]
        _esf_rid: list[int] = None # type: ignore [assignment]
        _esf_length: int = None # type: ignore [assignment]
        _ecf_rid: list[int] = None # type: ignore [assignment]
        _ecf_length: int = None # type: ignore [assignment]
        _name: str = None # type: ignore [assignment]
        _title: str = None # type: ignore [assignment]
        _guild_name: str = None # type: ignore [assignment]
        _guild_rank_name: str = None # type: ignore [assignment]
        _class_id: int = None # type: ignore [assignment]
        _guild_tag: str = None # type: ignore [assignment]
        _admin: AdminLevel = None # type: ignore [assignment]
        _level: int = None # type: ignore [assignment]
        _experience: int = None # type: ignore [assignment]
        _usage: int = None # type: ignore [assignment]
        _stats: CharacterStatsWelcome = None # type: ignore [assignment]
        _equipment: EquipmentWelcome = None # type: ignore [assignment]
        _guild_rank: int = None # type: ignore [assignment]
        _settings: ServerSettings = None # type: ignore [assignment]
        _login_message_code: LoginMessageCode = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

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
        def character_id(self) -> int:
            """
            Note:
              - Value range is 0-4097152080.
            """
            return self._character_id

        @character_id.setter
        def character_id(self, character_id: int) -> None:
            """
            Note:
              - Value range is 0-4097152080.
            """
            self._character_id = character_id

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

        @property
        def eif_rid(self) -> list[int]:
            """
            Note:
              - Length must be `2`.
              - Element value range is 0-64008.
            """
            return self._eif_rid

        @eif_rid.setter
        def eif_rid(self, eif_rid: list[int]) -> None:
            """
            Note:
              - Length must be `2`.
              - Element value range is 0-64008.
            """
            self._eif_rid = eif_rid

        @property
        def eif_length(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._eif_length

        @eif_length.setter
        def eif_length(self, eif_length: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._eif_length = eif_length

        @property
        def enf_rid(self) -> list[int]:
            """
            Note:
              - Length must be `2`.
              - Element value range is 0-64008.
            """
            return self._enf_rid

        @enf_rid.setter
        def enf_rid(self, enf_rid: list[int]) -> None:
            """
            Note:
              - Length must be `2`.
              - Element value range is 0-64008.
            """
            self._enf_rid = enf_rid

        @property
        def enf_length(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._enf_length

        @enf_length.setter
        def enf_length(self, enf_length: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._enf_length = enf_length

        @property
        def esf_rid(self) -> list[int]:
            """
            Note:
              - Length must be `2`.
              - Element value range is 0-64008.
            """
            return self._esf_rid

        @esf_rid.setter
        def esf_rid(self, esf_rid: list[int]) -> None:
            """
            Note:
              - Length must be `2`.
              - Element value range is 0-64008.
            """
            self._esf_rid = esf_rid

        @property
        def esf_length(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._esf_length

        @esf_length.setter
        def esf_length(self, esf_length: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._esf_length = esf_length

        @property
        def ecf_rid(self) -> list[int]:
            """
            Note:
              - Length must be `2`.
              - Element value range is 0-64008.
            """
            return self._ecf_rid

        @ecf_rid.setter
        def ecf_rid(self, ecf_rid: list[int]) -> None:
            """
            Note:
              - Length must be `2`.
              - Element value range is 0-64008.
            """
            self._ecf_rid = ecf_rid

        @property
        def ecf_length(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._ecf_length

        @ecf_length.setter
        def ecf_length(self, ecf_length: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._ecf_length = ecf_length

        @property
        def name(self) -> str:
            return self._name

        @name.setter
        def name(self, name: str) -> None:
            self._name = name

        @property
        def title(self) -> str:
            return self._title

        @title.setter
        def title(self, title: str) -> None:
            self._title = title

        @property
        def guild_name(self) -> str:
            return self._guild_name

        @guild_name.setter
        def guild_name(self, guild_name: str) -> None:
            self._guild_name = guild_name

        @property
        def guild_rank_name(self) -> str:
            return self._guild_rank_name

        @guild_rank_name.setter
        def guild_rank_name(self, guild_rank_name: str) -> None:
            self._guild_rank_name = guild_rank_name

        @property
        def class_id(self) -> int:
            """
            Note:
              - Value range is 0-252.
            """
            return self._class_id

        @class_id.setter
        def class_id(self, class_id: int) -> None:
            """
            Note:
              - Value range is 0-252.
            """
            self._class_id = class_id

        @property
        def guild_tag(self) -> str:
            """
            Note:
              - Length must be `3`.
            """
            return self._guild_tag

        @guild_tag.setter
        def guild_tag(self, guild_tag: str) -> None:
            """
            Note:
              - Length must be `3`.
            """
            self._guild_tag = guild_tag

        @property
        def admin(self) -> AdminLevel:
            return self._admin

        @admin.setter
        def admin(self, admin: AdminLevel) -> None:
            self._admin = admin

        @property
        def level(self) -> int:
            """
            Note:
              - Value range is 0-252.
            """
            return self._level

        @level.setter
        def level(self, level: int) -> None:
            """
            Note:
              - Value range is 0-252.
            """
            self._level = level

        @property
        def experience(self) -> int:
            """
            Note:
              - Value range is 0-4097152080.
            """
            return self._experience

        @experience.setter
        def experience(self, experience: int) -> None:
            """
            Note:
              - Value range is 0-4097152080.
            """
            self._experience = experience

        @property
        def usage(self) -> int:
            """
            Note:
              - Value range is 0-4097152080.
            """
            return self._usage

        @usage.setter
        def usage(self, usage: int) -> None:
            """
            Note:
              - Value range is 0-4097152080.
            """
            self._usage = usage

        @property
        def stats(self) -> CharacterStatsWelcome:
            return self._stats

        @stats.setter
        def stats(self, stats: CharacterStatsWelcome) -> None:
            self._stats = stats

        @property
        def equipment(self) -> EquipmentWelcome:
            return self._equipment

        @equipment.setter
        def equipment(self, equipment: EquipmentWelcome) -> None:
            self._equipment = equipment

        @property
        def guild_rank(self) -> int:
            """
            Note:
              - Value range is 0-252.
            """
            return self._guild_rank

        @guild_rank.setter
        def guild_rank(self, guild_rank: int) -> None:
            """
            Note:
              - Value range is 0-252.
            """
            self._guild_rank = guild_rank

        @property
        def settings(self) -> ServerSettings:
            return self._settings

        @settings.setter
        def settings(self, settings: ServerSettings) -> None:
            self._settings = settings

        @property
        def login_message_code(self) -> LoginMessageCode:
            return self._login_message_code

        @login_message_code.setter
        def login_message_code(self, login_message_code: LoginMessageCode) -> None:
            self._login_message_code = login_message_code

        @staticmethod
        def serialize(writer: EoWriter, data: "WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter") -> None:
            """
            Serializes an instance of `WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._session_id is None:
                    raise SerializationError("session_id must be provided.")
                writer.add_short(data._session_id)
                if data._character_id is None:
                    raise SerializationError("character_id must be provided.")
                writer.add_int(data._character_id)
                if data._map_id is None:
                    raise SerializationError("map_id must be provided.")
                writer.add_short(data._map_id)
                if data._map_rid is None:
                    raise SerializationError("map_rid must be provided.")
                if len(data._map_rid) != 2:
                    raise SerializationError(f"Expected length of map_rid to be exactly 2, got {len(data._map_rid)}.")
                for i in range(2):
                    writer.add_short(data._map_rid[i])
                if data._map_file_size is None:
                    raise SerializationError("map_file_size must be provided.")
                writer.add_three(data._map_file_size)
                if data._eif_rid is None:
                    raise SerializationError("eif_rid must be provided.")
                if len(data._eif_rid) != 2:
                    raise SerializationError(f"Expected length of eif_rid to be exactly 2, got {len(data._eif_rid)}.")
                for i in range(2):
                    writer.add_short(data._eif_rid[i])
                if data._eif_length is None:
                    raise SerializationError("eif_length must be provided.")
                writer.add_short(data._eif_length)
                if data._enf_rid is None:
                    raise SerializationError("enf_rid must be provided.")
                if len(data._enf_rid) != 2:
                    raise SerializationError(f"Expected length of enf_rid to be exactly 2, got {len(data._enf_rid)}.")
                for i in range(2):
                    writer.add_short(data._enf_rid[i])
                if data._enf_length is None:
                    raise SerializationError("enf_length must be provided.")
                writer.add_short(data._enf_length)
                if data._esf_rid is None:
                    raise SerializationError("esf_rid must be provided.")
                if len(data._esf_rid) != 2:
                    raise SerializationError(f"Expected length of esf_rid to be exactly 2, got {len(data._esf_rid)}.")
                for i in range(2):
                    writer.add_short(data._esf_rid[i])
                if data._esf_length is None:
                    raise SerializationError("esf_length must be provided.")
                writer.add_short(data._esf_length)
                if data._ecf_rid is None:
                    raise SerializationError("ecf_rid must be provided.")
                if len(data._ecf_rid) != 2:
                    raise SerializationError(f"Expected length of ecf_rid to be exactly 2, got {len(data._ecf_rid)}.")
                for i in range(2):
                    writer.add_short(data._ecf_rid[i])
                if data._ecf_length is None:
                    raise SerializationError("ecf_length must be provided.")
                writer.add_short(data._ecf_length)
                if data._name is None:
                    raise SerializationError("name must be provided.")
                writer.add_string(data._name)
                writer.add_byte(0xFF)
                if data._title is None:
                    raise SerializationError("title must be provided.")
                writer.add_string(data._title)
                writer.add_byte(0xFF)
                if data._guild_name is None:
                    raise SerializationError("guild_name must be provided.")
                writer.add_string(data._guild_name)
                writer.add_byte(0xFF)
                if data._guild_rank_name is None:
                    raise SerializationError("guild_rank_name must be provided.")
                writer.add_string(data._guild_rank_name)
                writer.add_byte(0xFF)
                if data._class_id is None:
                    raise SerializationError("class_id must be provided.")
                writer.add_char(data._class_id)
                if data._guild_tag is None:
                    raise SerializationError("guild_tag must be provided.")
                if len(data._guild_tag) != 3:
                    raise SerializationError(f"Expected length of guild_tag to be exactly 3, got {len(data._guild_tag)}.")
                writer.add_fixed_string(data._guild_tag, 3, False)
                if data._admin is None:
                    raise SerializationError("admin must be provided.")
                writer.add_char(int(data._admin))
                if data._level is None:
                    raise SerializationError("level must be provided.")
                writer.add_char(data._level)
                if data._experience is None:
                    raise SerializationError("experience must be provided.")
                writer.add_int(data._experience)
                if data._usage is None:
                    raise SerializationError("usage must be provided.")
                writer.add_int(data._usage)
                if data._stats is None:
                    raise SerializationError("stats must be provided.")
                CharacterStatsWelcome.serialize(writer, data._stats)
                if data._equipment is None:
                    raise SerializationError("equipment must be provided.")
                EquipmentWelcome.serialize(writer, data._equipment)
                if data._guild_rank is None:
                    raise SerializationError("guild_rank must be provided.")
                writer.add_char(data._guild_rank)
                if data._settings is None:
                    raise SerializationError("settings must be provided.")
                ServerSettings.serialize(writer, data._settings)
                if data._login_message_code is None:
                    raise SerializationError("login_message_code must be provided.")
                writer.add_char(int(data._login_message_code))
                writer.add_byte(0xFF)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter":
            """
            Deserializes an instance of `WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter: The data to serialize.
            """
            data: WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter = WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._session_id = reader.get_short()
                data._character_id = reader.get_int()
                data._map_id = reader.get_short()
                data._map_rid = []
                for i in range(2):
                    data._map_rid.append(reader.get_short())
                data._map_file_size = reader.get_three()
                data._eif_rid = []
                for i in range(2):
                    data._eif_rid.append(reader.get_short())
                data._eif_length = reader.get_short()
                data._enf_rid = []
                for i in range(2):
                    data._enf_rid.append(reader.get_short())
                data._enf_length = reader.get_short()
                data._esf_rid = []
                for i in range(2):
                    data._esf_rid.append(reader.get_short())
                data._esf_length = reader.get_short()
                data._ecf_rid = []
                for i in range(2):
                    data._ecf_rid.append(reader.get_short())
                data._ecf_length = reader.get_short()
                data._name = reader.get_string()
                reader.next_chunk()
                data._title = reader.get_string()
                reader.next_chunk()
                data._guild_name = reader.get_string()
                reader.next_chunk()
                data._guild_rank_name = reader.get_string()
                reader.next_chunk()
                data._class_id = reader.get_char()
                data._guild_tag = reader.get_fixed_string(3, False)
                data._admin = AdminLevel(reader.get_char())
                data._level = reader.get_char()
                data._experience = reader.get_int()
                data._usage = reader.get_int()
                data._stats = CharacterStatsWelcome.deserialize(reader)
                data._equipment = EquipmentWelcome.deserialize(reader)
                data._guild_rank = reader.get_char()
                data._settings = ServerSettings.deserialize(reader)
                data._login_message_code = LoginMessageCode(reader.get_char())
                reader.next_chunk()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"WelcomeReplyServerPacket.WelcomeCodeDataSelectCharacter(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, character_id={repr(self._character_id)}, map_id={repr(self._map_id)}, map_rid={repr(self._map_rid)}, map_file_size={repr(self._map_file_size)}, eif_rid={repr(self._eif_rid)}, eif_length={repr(self._eif_length)}, enf_rid={repr(self._enf_rid)}, enf_length={repr(self._enf_length)}, esf_rid={repr(self._esf_rid)}, esf_length={repr(self._esf_length)}, ecf_rid={repr(self._ecf_rid)}, ecf_length={repr(self._ecf_length)}, name={repr(self._name)}, title={repr(self._title)}, guild_name={repr(self._guild_name)}, guild_rank_name={repr(self._guild_rank_name)}, class_id={repr(self._class_id)}, guild_tag={repr(self._guild_tag)}, admin={repr(self._admin)}, level={repr(self._level)}, experience={repr(self._experience)}, usage={repr(self._usage)}, stats={repr(self._stats)}, equipment={repr(self._equipment)}, guild_rank={repr(self._guild_rank)}, settings={repr(self._settings)}, login_message_code={repr(self._login_message_code)})"

    class WelcomeCodeDataEnterGame:
        """
        Data associated with welcome_code value WelcomeCode.EnterGame
        """
        _byte_size: int = 0
        _news: list[str] = None # type: ignore [assignment]
        _weight: Weight = None # type: ignore [assignment]
        _items: list[Item] = None # type: ignore [assignment]
        _spells: list[Spell] = None # type: ignore [assignment]
        _nearby: NearbyInfo = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def news(self) -> list[str]:
            """
            Note:
              - Length must be `9`.
            """
            return self._news

        @news.setter
        def news(self, news: list[str]) -> None:
            """
            Note:
              - Length must be `9`.
            """
            self._news = news

        @property
        def weight(self) -> Weight:
            return self._weight

        @weight.setter
        def weight(self, weight: Weight) -> None:
            self._weight = weight

        @property
        def items(self) -> list[Item]:
            return self._items

        @items.setter
        def items(self, items: list[Item]) -> None:
            self._items = items

        @property
        def spells(self) -> list[Spell]:
            return self._spells

        @spells.setter
        def spells(self, spells: list[Spell]) -> None:
            self._spells = spells

        @property
        def nearby(self) -> NearbyInfo:
            return self._nearby

        @nearby.setter
        def nearby(self, nearby: NearbyInfo) -> None:
            self._nearby = nearby

        @staticmethod
        def serialize(writer: EoWriter, data: "WelcomeReplyServerPacket.WelcomeCodeDataEnterGame") -> None:
            """
            Serializes an instance of `WelcomeReplyServerPacket.WelcomeCodeDataEnterGame` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (WelcomeReplyServerPacket.WelcomeCodeDataEnterGame): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.add_byte(0xFF)
                if data._news is None:
                    raise SerializationError("news must be provided.")
                if len(data._news) != 9:
                    raise SerializationError(f"Expected length of news to be exactly 9, got {len(data._news)}.")
                for i in range(9):
                    writer.add_string(data._news[i])
                    writer.add_byte(0xFF)
                if data._weight is None:
                    raise SerializationError("weight must be provided.")
                Weight.serialize(writer, data._weight)
                if data._items is None:
                    raise SerializationError("items must be provided.")
                for i in range(len(data._items)):
                    Item.serialize(writer, data._items[i])
                writer.add_byte(0xFF)
                if data._spells is None:
                    raise SerializationError("spells must be provided.")
                for i in range(len(data._spells)):
                    Spell.serialize(writer, data._spells[i])
                writer.add_byte(0xFF)
                if data._nearby is None:
                    raise SerializationError("nearby must be provided.")
                NearbyInfo.serialize(writer, data._nearby)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "WelcomeReplyServerPacket.WelcomeCodeDataEnterGame":
            """
            Deserializes an instance of `WelcomeReplyServerPacket.WelcomeCodeDataEnterGame` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                WelcomeReplyServerPacket.WelcomeCodeDataEnterGame: The data to serialize.
            """
            data: WelcomeReplyServerPacket.WelcomeCodeDataEnterGame = WelcomeReplyServerPacket.WelcomeCodeDataEnterGame()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.next_chunk()
                data._news = []
                for i in range(9):
                    data._news.append(reader.get_string())
                    reader.next_chunk()
                data._weight = Weight.deserialize(reader)
                items_length = int(reader.remaining / 6)
                data._items = []
                for i in range(items_length):
                    data._items.append(Item.deserialize(reader))
                reader.next_chunk()
                spells_length = int(reader.remaining / 4)
                data._spells = []
                for i in range(spells_length):
                    data._spells.append(Spell.deserialize(reader))
                reader.next_chunk()
                data._nearby = NearbyInfo.deserialize(reader)
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"WelcomeReplyServerPacket.WelcomeCodeDataEnterGame(byte_size={repr(self._byte_size)}, news={repr(self._news)}, weight={repr(self._weight)}, items={repr(self._items)}, spells={repr(self._spells)}, nearby={repr(self._nearby)})"
