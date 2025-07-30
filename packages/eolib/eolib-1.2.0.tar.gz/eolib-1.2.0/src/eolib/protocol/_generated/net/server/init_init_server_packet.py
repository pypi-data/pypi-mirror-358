# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .pub_file import PubFile
from .players_list_friends import PlayersListFriends
from .players_list import PlayersList
from .map_file import MapFile
from .init_reply import InitReply
from .init_ban_type import InitBanType
from ..version import Version
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class InitInitServerPacket(Packet):
    """
    Reply to connection initialization and requests for unencrypted data.
    This packet is unencrypted.
    """
    _byte_size: int = 0
    _reply_code: InitReply = None # type: ignore [assignment]
    _reply_code_data: 'InitInitServerPacket.ReplyCodeData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def reply_code(self) -> InitReply:
        return self._reply_code

    @reply_code.setter
    def reply_code(self, reply_code: InitReply) -> None:
        self._reply_code = reply_code

    @property
    def reply_code_data(self) -> 'InitInitServerPacket.ReplyCodeData':
        """
        InitInitServerPacket.ReplyCodeData: Gets or sets the data associated with the `reply_code` field.
        """
        return self._reply_code_data

    @reply_code_data.setter
    def reply_code_data(self, reply_code_data: 'InitInitServerPacket.ReplyCodeData') -> None:
        self._reply_code_data = reply_code_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Init

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Init

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        InitInitServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "InitInitServerPacket") -> None:
        """
        Serializes an instance of `InitInitServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (InitInitServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._reply_code is None:
                raise SerializationError("reply_code must be provided.")
            writer.add_byte(int(data._reply_code))
            if data._reply_code == InitReply.OutOfDate:
                if not isinstance(data._reply_code_data, InitInitServerPacket.ReplyCodeDataOutOfDate):
                    raise SerializationError("Expected reply_code_data to be type InitInitServerPacket.ReplyCodeDataOutOfDate for reply_code " + InitReply(data._reply_code).name + ".")
                InitInitServerPacket.ReplyCodeDataOutOfDate.serialize(writer, data._reply_code_data)
            elif data._reply_code == InitReply.Ok:
                if not isinstance(data._reply_code_data, InitInitServerPacket.ReplyCodeDataOk):
                    raise SerializationError("Expected reply_code_data to be type InitInitServerPacket.ReplyCodeDataOk for reply_code " + InitReply(data._reply_code).name + ".")
                InitInitServerPacket.ReplyCodeDataOk.serialize(writer, data._reply_code_data)
            elif data._reply_code == InitReply.Banned:
                if not isinstance(data._reply_code_data, InitInitServerPacket.ReplyCodeDataBanned):
                    raise SerializationError("Expected reply_code_data to be type InitInitServerPacket.ReplyCodeDataBanned for reply_code " + InitReply(data._reply_code).name + ".")
                InitInitServerPacket.ReplyCodeDataBanned.serialize(writer, data._reply_code_data)
            elif data._reply_code == InitReply.WarpMap:
                if not isinstance(data._reply_code_data, InitInitServerPacket.ReplyCodeDataWarpMap):
                    raise SerializationError("Expected reply_code_data to be type InitInitServerPacket.ReplyCodeDataWarpMap for reply_code " + InitReply(data._reply_code).name + ".")
                InitInitServerPacket.ReplyCodeDataWarpMap.serialize(writer, data._reply_code_data)
            elif data._reply_code == InitReply.FileEmf:
                if not isinstance(data._reply_code_data, InitInitServerPacket.ReplyCodeDataFileEmf):
                    raise SerializationError("Expected reply_code_data to be type InitInitServerPacket.ReplyCodeDataFileEmf for reply_code " + InitReply(data._reply_code).name + ".")
                InitInitServerPacket.ReplyCodeDataFileEmf.serialize(writer, data._reply_code_data)
            elif data._reply_code == InitReply.FileEif:
                if not isinstance(data._reply_code_data, InitInitServerPacket.ReplyCodeDataFileEif):
                    raise SerializationError("Expected reply_code_data to be type InitInitServerPacket.ReplyCodeDataFileEif for reply_code " + InitReply(data._reply_code).name + ".")
                InitInitServerPacket.ReplyCodeDataFileEif.serialize(writer, data._reply_code_data)
            elif data._reply_code == InitReply.FileEnf:
                if not isinstance(data._reply_code_data, InitInitServerPacket.ReplyCodeDataFileEnf):
                    raise SerializationError("Expected reply_code_data to be type InitInitServerPacket.ReplyCodeDataFileEnf for reply_code " + InitReply(data._reply_code).name + ".")
                InitInitServerPacket.ReplyCodeDataFileEnf.serialize(writer, data._reply_code_data)
            elif data._reply_code == InitReply.FileEsf:
                if not isinstance(data._reply_code_data, InitInitServerPacket.ReplyCodeDataFileEsf):
                    raise SerializationError("Expected reply_code_data to be type InitInitServerPacket.ReplyCodeDataFileEsf for reply_code " + InitReply(data._reply_code).name + ".")
                InitInitServerPacket.ReplyCodeDataFileEsf.serialize(writer, data._reply_code_data)
            elif data._reply_code == InitReply.FileEcf:
                if not isinstance(data._reply_code_data, InitInitServerPacket.ReplyCodeDataFileEcf):
                    raise SerializationError("Expected reply_code_data to be type InitInitServerPacket.ReplyCodeDataFileEcf for reply_code " + InitReply(data._reply_code).name + ".")
                InitInitServerPacket.ReplyCodeDataFileEcf.serialize(writer, data._reply_code_data)
            elif data._reply_code == InitReply.MapMutation:
                if not isinstance(data._reply_code_data, InitInitServerPacket.ReplyCodeDataMapMutation):
                    raise SerializationError("Expected reply_code_data to be type InitInitServerPacket.ReplyCodeDataMapMutation for reply_code " + InitReply(data._reply_code).name + ".")
                InitInitServerPacket.ReplyCodeDataMapMutation.serialize(writer, data._reply_code_data)
            elif data._reply_code == InitReply.PlayersList:
                if not isinstance(data._reply_code_data, InitInitServerPacket.ReplyCodeDataPlayersList):
                    raise SerializationError("Expected reply_code_data to be type InitInitServerPacket.ReplyCodeDataPlayersList for reply_code " + InitReply(data._reply_code).name + ".")
                InitInitServerPacket.ReplyCodeDataPlayersList.serialize(writer, data._reply_code_data)
            elif data._reply_code == InitReply.PlayersListFriends:
                if not isinstance(data._reply_code_data, InitInitServerPacket.ReplyCodeDataPlayersListFriends):
                    raise SerializationError("Expected reply_code_data to be type InitInitServerPacket.ReplyCodeDataPlayersListFriends for reply_code " + InitReply(data._reply_code).name + ".")
                InitInitServerPacket.ReplyCodeDataPlayersListFriends.serialize(writer, data._reply_code_data)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "InitInitServerPacket":
        """
        Deserializes an instance of `InitInitServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            InitInitServerPacket: The data to serialize.
        """
        data: InitInitServerPacket = InitInitServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._reply_code = InitReply(reader.get_byte())
            if data._reply_code == InitReply.OutOfDate:
                data._reply_code_data = InitInitServerPacket.ReplyCodeDataOutOfDate.deserialize(reader)
            elif data._reply_code == InitReply.Ok:
                data._reply_code_data = InitInitServerPacket.ReplyCodeDataOk.deserialize(reader)
            elif data._reply_code == InitReply.Banned:
                data._reply_code_data = InitInitServerPacket.ReplyCodeDataBanned.deserialize(reader)
            elif data._reply_code == InitReply.WarpMap:
                data._reply_code_data = InitInitServerPacket.ReplyCodeDataWarpMap.deserialize(reader)
            elif data._reply_code == InitReply.FileEmf:
                data._reply_code_data = InitInitServerPacket.ReplyCodeDataFileEmf.deserialize(reader)
            elif data._reply_code == InitReply.FileEif:
                data._reply_code_data = InitInitServerPacket.ReplyCodeDataFileEif.deserialize(reader)
            elif data._reply_code == InitReply.FileEnf:
                data._reply_code_data = InitInitServerPacket.ReplyCodeDataFileEnf.deserialize(reader)
            elif data._reply_code == InitReply.FileEsf:
                data._reply_code_data = InitInitServerPacket.ReplyCodeDataFileEsf.deserialize(reader)
            elif data._reply_code == InitReply.FileEcf:
                data._reply_code_data = InitInitServerPacket.ReplyCodeDataFileEcf.deserialize(reader)
            elif data._reply_code == InitReply.MapMutation:
                data._reply_code_data = InitInitServerPacket.ReplyCodeDataMapMutation.deserialize(reader)
            elif data._reply_code == InitReply.PlayersList:
                data._reply_code_data = InitInitServerPacket.ReplyCodeDataPlayersList.deserialize(reader)
            elif data._reply_code == InitReply.PlayersListFriends:
                data._reply_code_data = InitInitServerPacket.ReplyCodeDataPlayersListFriends.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"InitInitServerPacket(byte_size={repr(self._byte_size)}, reply_code={repr(self._reply_code)}, reply_code_data={repr(self._reply_code_data)})"

    ReplyCodeData = Union['InitInitServerPacket.ReplyCodeDataOutOfDate', 'InitInitServerPacket.ReplyCodeDataOk', 'InitInitServerPacket.ReplyCodeDataBanned', 'InitInitServerPacket.ReplyCodeDataWarpMap', 'InitInitServerPacket.ReplyCodeDataFileEmf', 'InitInitServerPacket.ReplyCodeDataFileEif', 'InitInitServerPacket.ReplyCodeDataFileEnf', 'InitInitServerPacket.ReplyCodeDataFileEsf', 'InitInitServerPacket.ReplyCodeDataFileEcf', 'InitInitServerPacket.ReplyCodeDataMapMutation', 'InitInitServerPacket.ReplyCodeDataPlayersList', 'InitInitServerPacket.ReplyCodeDataPlayersListFriends', None]
    """
    Data associated with different values of the `reply_code` field.
    """

    class ReplyCodeDataOutOfDate:
        """
        Data associated with reply_code value InitReply.OutOfDate
        """
        _byte_size: int = 0
        _version: Version = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def version(self) -> Version:
            return self._version

        @version.setter
        def version(self, version: Version) -> None:
            self._version = version

        @staticmethod
        def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataOutOfDate") -> None:
            """
            Serializes an instance of `InitInitServerPacket.ReplyCodeDataOutOfDate` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (InitInitServerPacket.ReplyCodeDataOutOfDate): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._version is None:
                    raise SerializationError("version must be provided.")
                Version.serialize(writer, data._version)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataOutOfDate":
            """
            Deserializes an instance of `InitInitServerPacket.ReplyCodeDataOutOfDate` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                InitInitServerPacket.ReplyCodeDataOutOfDate: The data to serialize.
            """
            data: InitInitServerPacket.ReplyCodeDataOutOfDate = InitInitServerPacket.ReplyCodeDataOutOfDate()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._version = Version.deserialize(reader)
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"InitInitServerPacket.ReplyCodeDataOutOfDate(byte_size={repr(self._byte_size)}, version={repr(self._version)})"

    class ReplyCodeDataOk:
        """
        Data associated with reply_code value InitReply.Ok
        """
        _byte_size: int = 0
        _seq1: int = None # type: ignore [assignment]
        _seq2: int = None # type: ignore [assignment]
        _server_encryption_multiple: int = None # type: ignore [assignment]
        _client_encryption_multiple: int = None # type: ignore [assignment]
        _player_id: int = None # type: ignore [assignment]
        _challenge_response: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def seq1(self) -> int:
            """
            Note:
              - Value range is 0-255.
            """
            return self._seq1

        @seq1.setter
        def seq1(self, seq1: int) -> None:
            """
            Note:
              - Value range is 0-255.
            """
            self._seq1 = seq1

        @property
        def seq2(self) -> int:
            """
            Note:
              - Value range is 0-255.
            """
            return self._seq2

        @seq2.setter
        def seq2(self, seq2: int) -> None:
            """
            Note:
              - Value range is 0-255.
            """
            self._seq2 = seq2

        @property
        def server_encryption_multiple(self) -> int:
            """
            Note:
              - Value range is 0-255.
            """
            return self._server_encryption_multiple

        @server_encryption_multiple.setter
        def server_encryption_multiple(self, server_encryption_multiple: int) -> None:
            """
            Note:
              - Value range is 0-255.
            """
            self._server_encryption_multiple = server_encryption_multiple

        @property
        def client_encryption_multiple(self) -> int:
            """
            Note:
              - Value range is 0-255.
            """
            return self._client_encryption_multiple

        @client_encryption_multiple.setter
        def client_encryption_multiple(self, client_encryption_multiple: int) -> None:
            """
            Note:
              - Value range is 0-255.
            """
            self._client_encryption_multiple = client_encryption_multiple

        @property
        def player_id(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._player_id

        @player_id.setter
        def player_id(self, player_id: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._player_id = player_id

        @property
        def challenge_response(self) -> int:
            """
            Note:
              - Value range is 0-16194276.
            """
            return self._challenge_response

        @challenge_response.setter
        def challenge_response(self, challenge_response: int) -> None:
            """
            Note:
              - Value range is 0-16194276.
            """
            self._challenge_response = challenge_response

        @staticmethod
        def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataOk") -> None:
            """
            Serializes an instance of `InitInitServerPacket.ReplyCodeDataOk` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (InitInitServerPacket.ReplyCodeDataOk): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._seq1 is None:
                    raise SerializationError("seq1 must be provided.")
                writer.add_byte(data._seq1)
                if data._seq2 is None:
                    raise SerializationError("seq2 must be provided.")
                writer.add_byte(data._seq2)
                if data._server_encryption_multiple is None:
                    raise SerializationError("server_encryption_multiple must be provided.")
                writer.add_byte(data._server_encryption_multiple)
                if data._client_encryption_multiple is None:
                    raise SerializationError("client_encryption_multiple must be provided.")
                writer.add_byte(data._client_encryption_multiple)
                if data._player_id is None:
                    raise SerializationError("player_id must be provided.")
                writer.add_short(data._player_id)
                if data._challenge_response is None:
                    raise SerializationError("challenge_response must be provided.")
                writer.add_three(data._challenge_response)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataOk":
            """
            Deserializes an instance of `InitInitServerPacket.ReplyCodeDataOk` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                InitInitServerPacket.ReplyCodeDataOk: The data to serialize.
            """
            data: InitInitServerPacket.ReplyCodeDataOk = InitInitServerPacket.ReplyCodeDataOk()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._seq1 = reader.get_byte()
                data._seq2 = reader.get_byte()
                data._server_encryption_multiple = reader.get_byte()
                data._client_encryption_multiple = reader.get_byte()
                data._player_id = reader.get_short()
                data._challenge_response = reader.get_three()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"InitInitServerPacket.ReplyCodeDataOk(byte_size={repr(self._byte_size)}, seq1={repr(self._seq1)}, seq2={repr(self._seq2)}, server_encryption_multiple={repr(self._server_encryption_multiple)}, client_encryption_multiple={repr(self._client_encryption_multiple)}, player_id={repr(self._player_id)}, challenge_response={repr(self._challenge_response)})"

    class ReplyCodeDataBanned:
        """
        Data associated with reply_code value InitReply.Banned
        """
        _byte_size: int = 0
        _ban_type: InitBanType = None # type: ignore [assignment]
        _ban_type_data: 'InitInitServerPacket.ReplyCodeDataBanned.BanTypeData' = None

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def ban_type(self) -> InitBanType:
            return self._ban_type

        @ban_type.setter
        def ban_type(self, ban_type: InitBanType) -> None:
            self._ban_type = ban_type

        @property
        def ban_type_data(self) -> 'InitInitServerPacket.ReplyCodeDataBanned.BanTypeData':
            """
            InitInitServerPacket.ReplyCodeDataBanned.BanTypeData: Gets or sets the data associated with the `ban_type` field.
            """
            return self._ban_type_data

        @ban_type_data.setter
        def ban_type_data(self, ban_type_data: 'InitInitServerPacket.ReplyCodeDataBanned.BanTypeData') -> None:
            self._ban_type_data = ban_type_data

        @staticmethod
        def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataBanned") -> None:
            """
            Serializes an instance of `InitInitServerPacket.ReplyCodeDataBanned` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (InitInitServerPacket.ReplyCodeDataBanned): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._ban_type is None:
                    raise SerializationError("ban_type must be provided.")
                writer.add_byte(int(data._ban_type))
                if data._ban_type == 0:
                    if not isinstance(data._ban_type_data, InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0):
                        raise SerializationError("Expected ban_type_data to be type InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0 for ban_type " + InitBanType(data._ban_type).name + ".")
                    InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0.serialize(writer, data._ban_type_data)
                elif data._ban_type == InitBanType.Temporary:
                    if not isinstance(data._ban_type_data, InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary):
                        raise SerializationError("Expected ban_type_data to be type InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary for ban_type " + InitBanType(data._ban_type).name + ".")
                    InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary.serialize(writer, data._ban_type_data)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataBanned":
            """
            Deserializes an instance of `InitInitServerPacket.ReplyCodeDataBanned` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                InitInitServerPacket.ReplyCodeDataBanned: The data to serialize.
            """
            data: InitInitServerPacket.ReplyCodeDataBanned = InitInitServerPacket.ReplyCodeDataBanned()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._ban_type = InitBanType(reader.get_byte())
                if data._ban_type == 0:
                    data._ban_type_data = InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0.deserialize(reader)
                elif data._ban_type == InitBanType.Temporary:
                    data._ban_type_data = InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary.deserialize(reader)
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"InitInitServerPacket.ReplyCodeDataBanned(byte_size={repr(self._byte_size)}, ban_type={repr(self._ban_type)}, ban_type_data={repr(self._ban_type_data)})"

        BanTypeData = Union['InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0', 'InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary', None]
        """
        Data associated with different values of the `ban_type` field.
        """

        class BanTypeData0:
            """
            Data associated with ban_type value 0

            The official client treats any value below 2 as a temporary ban.
            The official server sends 1, but some game server implementations
            erroneously send 0.
            """
            _byte_size: int = 0
            _minutes_remaining: int = None # type: ignore [assignment]

            @property
            def byte_size(self) -> int:
                """
                Returns the size of the data that this was deserialized from.

                Returns:
                    int: The size of the data that this was deserialized from.
                """
                return self._byte_size

            @property
            def minutes_remaining(self) -> int:
                """
                Note:
                  - Value range is 0-255.
                """
                return self._minutes_remaining

            @minutes_remaining.setter
            def minutes_remaining(self, minutes_remaining: int) -> None:
                """
                Note:
                  - Value range is 0-255.
                """
                self._minutes_remaining = minutes_remaining

            @staticmethod
            def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0") -> None:
                """
                Serializes an instance of `InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0` to the provided `EoWriter`.

                Args:
                    writer (EoWriter): The writer that the data will be serialized to.
                    data (InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0): The data to serialize.
                """
                old_string_sanitization_mode: bool = writer.string_sanitization_mode
                try:
                    if data._minutes_remaining is None:
                        raise SerializationError("minutes_remaining must be provided.")
                    writer.add_byte(data._minutes_remaining)
                finally:
                    writer.string_sanitization_mode = old_string_sanitization_mode

            @staticmethod
            def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0":
                """
                Deserializes an instance of `InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0` from the provided `EoReader`.

                Args:
                    reader (EoReader): The writer that the data will be serialized to.

                Returns:
                    InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0: The data to serialize.
                """
                data: InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0 = InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0()
                old_chunked_reading_mode: bool = reader.chunked_reading_mode
                try:
                    reader_start_position: int = reader.position
                    data._minutes_remaining = reader.get_byte()
                    data._byte_size = reader.position - reader_start_position
                    return data
                finally:
                    reader.chunked_reading_mode = old_chunked_reading_mode

            def __repr__(self):
                return f"InitInitServerPacket.ReplyCodeDataBanned.BanTypeData0(byte_size={repr(self._byte_size)}, minutes_remaining={repr(self._minutes_remaining)})"

        class BanTypeDataTemporary:
            """
            Data associated with ban_type value InitBanType.Temporary
            """
            _byte_size: int = 0
            _minutes_remaining: int = None # type: ignore [assignment]

            @property
            def byte_size(self) -> int:
                """
                Returns the size of the data that this was deserialized from.

                Returns:
                    int: The size of the data that this was deserialized from.
                """
                return self._byte_size

            @property
            def minutes_remaining(self) -> int:
                """
                Note:
                  - Value range is 0-255.
                """
                return self._minutes_remaining

            @minutes_remaining.setter
            def minutes_remaining(self, minutes_remaining: int) -> None:
                """
                Note:
                  - Value range is 0-255.
                """
                self._minutes_remaining = minutes_remaining

            @staticmethod
            def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary") -> None:
                """
                Serializes an instance of `InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary` to the provided `EoWriter`.

                Args:
                    writer (EoWriter): The writer that the data will be serialized to.
                    data (InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary): The data to serialize.
                """
                old_string_sanitization_mode: bool = writer.string_sanitization_mode
                try:
                    if data._minutes_remaining is None:
                        raise SerializationError("minutes_remaining must be provided.")
                    writer.add_byte(data._minutes_remaining)
                finally:
                    writer.string_sanitization_mode = old_string_sanitization_mode

            @staticmethod
            def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary":
                """
                Deserializes an instance of `InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary` from the provided `EoReader`.

                Args:
                    reader (EoReader): The writer that the data will be serialized to.

                Returns:
                    InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary: The data to serialize.
                """
                data: InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary = InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary()
                old_chunked_reading_mode: bool = reader.chunked_reading_mode
                try:
                    reader_start_position: int = reader.position
                    data._minutes_remaining = reader.get_byte()
                    data._byte_size = reader.position - reader_start_position
                    return data
                finally:
                    reader.chunked_reading_mode = old_chunked_reading_mode

            def __repr__(self):
                return f"InitInitServerPacket.ReplyCodeDataBanned.BanTypeDataTemporary(byte_size={repr(self._byte_size)}, minutes_remaining={repr(self._minutes_remaining)})"

    class ReplyCodeDataWarpMap:
        """
        Data associated with reply_code value InitReply.WarpMap
        """
        _byte_size: int = 0
        _map_file: MapFile = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def map_file(self) -> MapFile:
            return self._map_file

        @map_file.setter
        def map_file(self, map_file: MapFile) -> None:
            self._map_file = map_file

        @staticmethod
        def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataWarpMap") -> None:
            """
            Serializes an instance of `InitInitServerPacket.ReplyCodeDataWarpMap` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (InitInitServerPacket.ReplyCodeDataWarpMap): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._map_file is None:
                    raise SerializationError("map_file must be provided.")
                MapFile.serialize(writer, data._map_file)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataWarpMap":
            """
            Deserializes an instance of `InitInitServerPacket.ReplyCodeDataWarpMap` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                InitInitServerPacket.ReplyCodeDataWarpMap: The data to serialize.
            """
            data: InitInitServerPacket.ReplyCodeDataWarpMap = InitInitServerPacket.ReplyCodeDataWarpMap()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._map_file = MapFile.deserialize(reader)
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"InitInitServerPacket.ReplyCodeDataWarpMap(byte_size={repr(self._byte_size)}, map_file={repr(self._map_file)})"

    class ReplyCodeDataFileEmf:
        """
        Data associated with reply_code value InitReply.FileEmf
        """
        _byte_size: int = 0
        _map_file: MapFile = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def map_file(self) -> MapFile:
            return self._map_file

        @map_file.setter
        def map_file(self, map_file: MapFile) -> None:
            self._map_file = map_file

        @staticmethod
        def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataFileEmf") -> None:
            """
            Serializes an instance of `InitInitServerPacket.ReplyCodeDataFileEmf` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (InitInitServerPacket.ReplyCodeDataFileEmf): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._map_file is None:
                    raise SerializationError("map_file must be provided.")
                MapFile.serialize(writer, data._map_file)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataFileEmf":
            """
            Deserializes an instance of `InitInitServerPacket.ReplyCodeDataFileEmf` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                InitInitServerPacket.ReplyCodeDataFileEmf: The data to serialize.
            """
            data: InitInitServerPacket.ReplyCodeDataFileEmf = InitInitServerPacket.ReplyCodeDataFileEmf()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._map_file = MapFile.deserialize(reader)
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"InitInitServerPacket.ReplyCodeDataFileEmf(byte_size={repr(self._byte_size)}, map_file={repr(self._map_file)})"

    class ReplyCodeDataFileEif:
        """
        Data associated with reply_code value InitReply.FileEif
        """
        _byte_size: int = 0
        _pub_file: PubFile = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def pub_file(self) -> PubFile:
            return self._pub_file

        @pub_file.setter
        def pub_file(self, pub_file: PubFile) -> None:
            self._pub_file = pub_file

        @staticmethod
        def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataFileEif") -> None:
            """
            Serializes an instance of `InitInitServerPacket.ReplyCodeDataFileEif` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (InitInitServerPacket.ReplyCodeDataFileEif): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._pub_file is None:
                    raise SerializationError("pub_file must be provided.")
                PubFile.serialize(writer, data._pub_file)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataFileEif":
            """
            Deserializes an instance of `InitInitServerPacket.ReplyCodeDataFileEif` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                InitInitServerPacket.ReplyCodeDataFileEif: The data to serialize.
            """
            data: InitInitServerPacket.ReplyCodeDataFileEif = InitInitServerPacket.ReplyCodeDataFileEif()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._pub_file = PubFile.deserialize(reader)
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"InitInitServerPacket.ReplyCodeDataFileEif(byte_size={repr(self._byte_size)}, pub_file={repr(self._pub_file)})"

    class ReplyCodeDataFileEnf:
        """
        Data associated with reply_code value InitReply.FileEnf
        """
        _byte_size: int = 0
        _pub_file: PubFile = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def pub_file(self) -> PubFile:
            return self._pub_file

        @pub_file.setter
        def pub_file(self, pub_file: PubFile) -> None:
            self._pub_file = pub_file

        @staticmethod
        def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataFileEnf") -> None:
            """
            Serializes an instance of `InitInitServerPacket.ReplyCodeDataFileEnf` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (InitInitServerPacket.ReplyCodeDataFileEnf): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._pub_file is None:
                    raise SerializationError("pub_file must be provided.")
                PubFile.serialize(writer, data._pub_file)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataFileEnf":
            """
            Deserializes an instance of `InitInitServerPacket.ReplyCodeDataFileEnf` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                InitInitServerPacket.ReplyCodeDataFileEnf: The data to serialize.
            """
            data: InitInitServerPacket.ReplyCodeDataFileEnf = InitInitServerPacket.ReplyCodeDataFileEnf()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._pub_file = PubFile.deserialize(reader)
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"InitInitServerPacket.ReplyCodeDataFileEnf(byte_size={repr(self._byte_size)}, pub_file={repr(self._pub_file)})"

    class ReplyCodeDataFileEsf:
        """
        Data associated with reply_code value InitReply.FileEsf
        """
        _byte_size: int = 0
        _pub_file: PubFile = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def pub_file(self) -> PubFile:
            return self._pub_file

        @pub_file.setter
        def pub_file(self, pub_file: PubFile) -> None:
            self._pub_file = pub_file

        @staticmethod
        def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataFileEsf") -> None:
            """
            Serializes an instance of `InitInitServerPacket.ReplyCodeDataFileEsf` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (InitInitServerPacket.ReplyCodeDataFileEsf): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._pub_file is None:
                    raise SerializationError("pub_file must be provided.")
                PubFile.serialize(writer, data._pub_file)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataFileEsf":
            """
            Deserializes an instance of `InitInitServerPacket.ReplyCodeDataFileEsf` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                InitInitServerPacket.ReplyCodeDataFileEsf: The data to serialize.
            """
            data: InitInitServerPacket.ReplyCodeDataFileEsf = InitInitServerPacket.ReplyCodeDataFileEsf()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._pub_file = PubFile.deserialize(reader)
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"InitInitServerPacket.ReplyCodeDataFileEsf(byte_size={repr(self._byte_size)}, pub_file={repr(self._pub_file)})"

    class ReplyCodeDataFileEcf:
        """
        Data associated with reply_code value InitReply.FileEcf
        """
        _byte_size: int = 0
        _pub_file: PubFile = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def pub_file(self) -> PubFile:
            return self._pub_file

        @pub_file.setter
        def pub_file(self, pub_file: PubFile) -> None:
            self._pub_file = pub_file

        @staticmethod
        def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataFileEcf") -> None:
            """
            Serializes an instance of `InitInitServerPacket.ReplyCodeDataFileEcf` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (InitInitServerPacket.ReplyCodeDataFileEcf): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._pub_file is None:
                    raise SerializationError("pub_file must be provided.")
                PubFile.serialize(writer, data._pub_file)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataFileEcf":
            """
            Deserializes an instance of `InitInitServerPacket.ReplyCodeDataFileEcf` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                InitInitServerPacket.ReplyCodeDataFileEcf: The data to serialize.
            """
            data: InitInitServerPacket.ReplyCodeDataFileEcf = InitInitServerPacket.ReplyCodeDataFileEcf()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._pub_file = PubFile.deserialize(reader)
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"InitInitServerPacket.ReplyCodeDataFileEcf(byte_size={repr(self._byte_size)}, pub_file={repr(self._pub_file)})"

    class ReplyCodeDataMapMutation:
        """
        Data associated with reply_code value InitReply.MapMutation
        """
        _byte_size: int = 0
        _map_file: MapFile = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def map_file(self) -> MapFile:
            return self._map_file

        @map_file.setter
        def map_file(self, map_file: MapFile) -> None:
            self._map_file = map_file

        @staticmethod
        def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataMapMutation") -> None:
            """
            Serializes an instance of `InitInitServerPacket.ReplyCodeDataMapMutation` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (InitInitServerPacket.ReplyCodeDataMapMutation): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._map_file is None:
                    raise SerializationError("map_file must be provided.")
                MapFile.serialize(writer, data._map_file)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataMapMutation":
            """
            Deserializes an instance of `InitInitServerPacket.ReplyCodeDataMapMutation` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                InitInitServerPacket.ReplyCodeDataMapMutation: The data to serialize.
            """
            data: InitInitServerPacket.ReplyCodeDataMapMutation = InitInitServerPacket.ReplyCodeDataMapMutation()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._map_file = MapFile.deserialize(reader)
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"InitInitServerPacket.ReplyCodeDataMapMutation(byte_size={repr(self._byte_size)}, map_file={repr(self._map_file)})"

    class ReplyCodeDataPlayersList:
        """
        Data associated with reply_code value InitReply.PlayersList
        """
        _byte_size: int = 0
        _players_list: PlayersList = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def players_list(self) -> PlayersList:
            return self._players_list

        @players_list.setter
        def players_list(self, players_list: PlayersList) -> None:
            self._players_list = players_list

        @staticmethod
        def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataPlayersList") -> None:
            """
            Serializes an instance of `InitInitServerPacket.ReplyCodeDataPlayersList` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (InitInitServerPacket.ReplyCodeDataPlayersList): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.string_sanitization_mode = True
                if data._players_list is None:
                    raise SerializationError("players_list must be provided.")
                PlayersList.serialize(writer, data._players_list)
                writer.string_sanitization_mode = False
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataPlayersList":
            """
            Deserializes an instance of `InitInitServerPacket.ReplyCodeDataPlayersList` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                InitInitServerPacket.ReplyCodeDataPlayersList: The data to serialize.
            """
            data: InitInitServerPacket.ReplyCodeDataPlayersList = InitInitServerPacket.ReplyCodeDataPlayersList()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.chunked_reading_mode = True
                data._players_list = PlayersList.deserialize(reader)
                reader.chunked_reading_mode = False
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"InitInitServerPacket.ReplyCodeDataPlayersList(byte_size={repr(self._byte_size)}, players_list={repr(self._players_list)})"

    class ReplyCodeDataPlayersListFriends:
        """
        Data associated with reply_code value InitReply.PlayersListFriends
        """
        _byte_size: int = 0
        _players_list: PlayersListFriends = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def players_list(self) -> PlayersListFriends:
            return self._players_list

        @players_list.setter
        def players_list(self, players_list: PlayersListFriends) -> None:
            self._players_list = players_list

        @staticmethod
        def serialize(writer: EoWriter, data: "InitInitServerPacket.ReplyCodeDataPlayersListFriends") -> None:
            """
            Serializes an instance of `InitInitServerPacket.ReplyCodeDataPlayersListFriends` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (InitInitServerPacket.ReplyCodeDataPlayersListFriends): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                writer.string_sanitization_mode = True
                if data._players_list is None:
                    raise SerializationError("players_list must be provided.")
                PlayersListFriends.serialize(writer, data._players_list)
                writer.string_sanitization_mode = False
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "InitInitServerPacket.ReplyCodeDataPlayersListFriends":
            """
            Deserializes an instance of `InitInitServerPacket.ReplyCodeDataPlayersListFriends` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                InitInitServerPacket.ReplyCodeDataPlayersListFriends: The data to serialize.
            """
            data: InitInitServerPacket.ReplyCodeDataPlayersListFriends = InitInitServerPacket.ReplyCodeDataPlayersListFriends()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                reader.chunked_reading_mode = True
                data._players_list = PlayersListFriends.deserialize(reader)
                reader.chunked_reading_mode = False
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"InitInitServerPacket.ReplyCodeDataPlayersListFriends(byte_size={repr(self._byte_size)}, players_list={repr(self._players_list)})"
