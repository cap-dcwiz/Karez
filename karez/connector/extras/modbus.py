import logging
from contextlib import asynccontextmanager

from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException, ModbusIOException
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient

from ...config import OptionalConfigEntity
from ..base import PullConnectorBase
from ...utils import generator_to_list


class Connector(PullConnectorBase):
    READING_FUNCTION = {
        # "coils": "read_coils", # Not supported yet
        # "discrete inputs": "read_discrete_inputs", # Not supported yet
        "holding registers": "read_holding_registers",
        "input registers": "read_input_registers",
    }

    DECODE_FUNC = {
        # "string": "decode_string", # Not supported yet
        # "bits": "decode_bits",
        # "8int": "decode_8bit_int",
        "8uint": "decode_8bit_uint",
        "16int": "decode_16bit_int",
        "16uint": "decode_16bit_uint",
        "32int": "decode_32bit_int",
        "32uint": "decode_32bit_uint",
        "16float": "decode_16bit_float",
        "32float": "decode_32bit_float",
        "64int": "decode_64bit_int",
        "64uint": "decode_64bit_uint",
        # "ignore", "skip_bytes", # Not supported yet
        "64float": "decode_64bit_float",
    }

    TYPE_SIZE = {
        "16int": 1,
        "16uint": 1,
        "32int": 2,
        "32uint": 2,
        "16float": 1,
        "32float": 2,
        "64int": 4,
        "64uint": 4,
        "64float": 4,
    }

    def __init__(self, *args, **kwargs):
        super(Connector, self).__init__(*args, **kwargs)

    @asynccontextmanager
    async def create_client(self):
        yield {}

    def get_client(self, client_cache, host, port):
        if (host, port) not in client_cache:
            client_cache[(host, port)] = ModbusTcpClient(host, port)
        return client_cache[(host, port)]

    @classmethod
    def role_description(cls):
        return "Connector for Modbus TCP."

    @classmethod
    def config_entities(cls):
        yield from super(Connector, cls).config_entities()
        yield OptionalConfigEntity("host", NotImplemented, "Host of modbus gateway")
        yield OptionalConfigEntity("port", NotImplemented, "Port of modbus gateway")
        yield OptionalConfigEntity("unit", NotImplemented, "Default device unit")
        yield OptionalConfigEntity(
            "region", "holding registers", "Default region of registers"
        )
        yield OptionalConfigEntity("data_type", "32float", "Default data type")
        yield OptionalConfigEntity(
            "byte_order",
            0,
            "Default byte order (0 for little endian and 1 for big endian)",
        )
        yield OptionalConfigEntity(
            "word_order",
            0,
            "Default word order (0 for little endian and 1 for big endian)",
        )

    def read_data_point(
        self,
        client_cache,
        name,
        host,
        port,
        address,
        count,
        unit,
        byte_order,
        word_order,
        read_func,
        decode_func,
    ):
        client = self.get_client(client_cache, host, port)
        response = getattr(client, read_func)(address=address, count=count, unit=unit)
        decoder = BinaryPayloadDecoder.fromRegisters(
            registers=response.registers, byteorder=byte_order, wordorder=word_order
        )
        return dict(name=name, value=getattr(decoder, decode_func)())

    @staticmethod
    def _read_data_point_info(**kwargs):
        if "client_cache" in kwargs:
            kwargs.popitem("client_cache")
        return dict(kwargs)

    @staticmethod
    def _endian_order(v):
        return Endian.Little if v == 0 else Endian.Big

    @generator_to_list
    async def fetch_data(self, client_cache, entities):
        for entity in entities:
            name = entity["Name"]
            host = entity.get("Host", self.config.host)
            port = int(entity.get("Port", self.config.port))

            region = entity.get("Region", self.config.region).lower()
            if region not in self.READING_FUNCTION:
                raise RuntimeError(f"Unknown region: {region}")

            data_type = entity.get("Type", self.config.data_type)
            if data_type not in self.TYPE_SIZE:
                raise RuntimeError(f"Unknown data type: {data_type}")

            byte_order = entity.get("ByteOrder", self.config.byte_order)
            word_order = entity.get("WordOrder", self.config.word_order)

            func = self.read_data_point
            try:
                yield func(
                    client_cache=client_cache,
                    name=name,
                    host=host,
                    port=port,
                    address=int(entity["Offset"]),
                    count=self.TYPE_SIZE[data_type],
                    unit=int(entity.get("Unit", self.config.unit)),
                    byte_order=self._endian_order(byte_order),
                    word_order=self._endian_order(word_order),
                    read_func=self.READING_FUNCTION[region],
                    decode_func=self.DECODE_FUNC[data_type],
                )
            except ConnectionException:
                logging.error(f"Unable to connect to {host}:{port}")
            except ModbusIOException:
                logging.error(f"Unable to read {name}")
