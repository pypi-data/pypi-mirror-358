"""A lightweigth MCP server for the Modbus protocol."""

from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.prompts.prompt import Message
from fastmcp.resources import ResourceTemplate
from fastmcp.tools import Tool
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymodbus.client import AsyncModbusTcpClient
from typing import Optional


class Auth(BaseModel):
    key: Optional[str] = None


class Modbus(BaseModel):
    host: str = "127.0.0.1"
    port: int = 502
    unit: int = 1


class Settings(BaseSettings):
    auth: Auth = Auth()
    modbus: Modbus = Modbus()
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__"
    )


settings = Settings()

_READ_FN = {
    0: ("read_coils", 1),
    1: ("read_discrete_inputs", 10001),
    3: ("read_input_registers", 30001),
    4: ("read_holding_registers", 40001),
}

_WRITE_FN = {0: ("write_coils", 1), 4: ("write_registers", 40001)}

mcp = FastMCP(
    name="Modbus MCP Server",
    auth=(
        BearerAuthProvider(public_key=settings.auth.key) if settings.auth.key else None
    ),
)


async def read_registers(
    host: str = settings.modbus.host,
    port: int = settings.modbus.port,
    address: int = 40001,
    count: int = 1,
    unit: int = settings.modbus.unit,
) -> int | list[int]:
    """Reads the contents of one or more registers on a remote unit."""
    try:
        async with AsyncModbusTcpClient(host, port=port) as client:
            func, offset = _READ_FN[address // 10000]
            method = getattr(client, func)
            res = await method(address - offset, count=count, slave=unit)
            out = getattr(res, "registers", []) or getattr(res, "bits", [])
            return [int(x) for x in out] if count > 1 else out[0]
    except Exception as e:
        raise RuntimeError(
            f"Could not read {address} ({count}) from {host}:{port}"
        ) from e


mcp.add_template(
    ResourceTemplate.from_function(
        fn=read_registers,
        uri_template="tcp://{host}:{port}/{address}?count={count}&unit={unit}",
    )
)

mcp.add_tool(
    Tool.from_function(
        fn=read_registers,
        annotations={
            "title": "Read Registers",
            "readOnlyHint": True,
            "openWorldHint": True,
        },
    )
)


@mcp.tool(
    annotations={
        "title": "Write Registers",
        "readOnlyHint": False,
        "openWorldHint": True,
    }
)
async def write_registers(
    data: list[int],
    host: str = settings.modbus.host,
    port: int = settings.modbus.port,
    address: int = 40001,
    unit: int = settings.modbus.unit,
) -> str:
    """Writes data to one or more registers on a remote unit."""
    try:
        async with AsyncModbusTcpClient(host, port=port) as client:
            func, offset = _WRITE_FN[address // 10000]
            method = getattr(client, func)
            res = await method(address - offset, data, slave=unit)
            if res.isError():
                raise RuntimeError(f"Could not write to {address} on {host}:{port}")
            return f"Write to {address} on {host}:{port} has succedeed"
    except Exception as e:
        raise RuntimeError(f"{e}") from e


@mcp.tool(
    annotations={
        "title": "Mask Write Register",
        "readOnlyHint": False,
        "openWorldHint": True,
    }
)
async def mask_write_register(
    host: str = settings.modbus.host,
    port: int = settings.modbus.port,
    address: int = 40001,
    and_mask: int = 0xFFFF,
    or_mask: int = 0x0000,
    unit: int = settings.modbus.unit,
) -> str:
    """Mask writes data to a specified register."""
    try:
        async with AsyncModbusTcpClient(host, port=port) as client:
            res = await client.mask_write_register(
                address=(address - 40001),
                and_mask=and_mask,
                or_mask=or_mask,
                slave=unit,
            )
            if res.isError():
                raise RuntimeError(
                    f"Could not mask write to {address} on {host}:{port}"
                )
            return f"Mask write to {address} on {host}:{port} has succedeed"
    except Exception as e:
        raise RuntimeError(f"{e}") from e


@mcp.prompt(name="modbus_help", tags={"modbus", "help"})
def modbus_help() -> list[Message]:
    """Provides examples of how to use the Modbus MCP server."""
    return [
        Message("Here are examples of how to read and write registers:"),
        Message("Please read the value of register 40001 on 127.0.0.1:502."),
        Message("Set register 40005 to 123 on host 192.168.1.10, unit 3."),
        Message("Write [1, 2, 3] to holding registers starting at address 40010."),
        Message("What is the status of input register 30010 on 10.0.0.5?"),
    ]


@mcp.prompt(name="modbus_error", tags={"modbus", "error"})
def modbus_error(error: str | None = None) -> list[Message]:
    """Asks the user how to handle an error."""
    return (
        [
            Message(f"ERROR: {error!r}"),
            Message("Would you like to retry, change parameters, or abort?"),
        ]
        if error
        else []
    )
