"""A lightweigth MCP server for the MQTT protocol."""

from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.prompts.prompt import Message
from fastmcp.resources import ResourceTemplate
from fastmcp.tools import Tool
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

from mqtt_mcp.mqtt_client import AsyncMQTTClient


class Auth(BaseModel):
    key: Optional[str] = None


class MQTT(BaseModel):
    host: str = "127.0.0.1"
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None


class Settings(BaseSettings):
    auth: Auth = Auth()
    mqtt: MQTT = MQTT()
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__"
    )


settings = Settings()

mcp = FastMCP(
    name="MQTT MCP Server",
    auth=(
        BearerAuthProvider(public_key=settings.auth.key) if settings.auth.key else None
    ),
)


async def receive_message(
    topic: str,
    host: str = settings.mqtt.host,
    port: int = settings.mqtt.port,
    username: str | None = settings.mqtt.username,
    password: str | None = settings.mqtt.password,
    timeout: int = 60,
) -> str:
    """Receives a message published to the specified topic, if any."""
    try:
        async with AsyncMQTTClient(host, port, username, password) as client:
            return await client.receive(topic, timeout)
    except Exception as e:
        raise RuntimeError(f"{e}") from e


mcp.add_template(
    ResourceTemplate.from_function(
        fn=receive_message, uri_template="mqtt://{host}:{port}/{topic*}"
    )
)

mcp.add_tool(
    Tool.from_function(
        fn=receive_message,
        annotations={
            "title": "Receive Message",
            "readOnlyHint": True,
            "openWorldHint": True,
        },
    )
)


@mcp.tool(
    annotations={
        "title": "Publish Message",
        "readOnlyHint": False,
        "openWorldHint": True,
    }
)
async def publish_message(
    topic: str,
    message: str,
    host: str = settings.mqtt.host,
    port: int = settings.mqtt.port,
    username: str | None = settings.mqtt.username,
    password: str | None = settings.mqtt.password,
) -> str:
    """Publishes a message to the specified topic."""
    try:
        async with AsyncMQTTClient(host, port, username, password) as client:
            await client.publish(topic, message)
        return f"Publish to {topic} on {host}:{port} has succedeed"
    except Exception as e:
        raise RuntimeError(f"{e}") from e


@mcp.prompt(name="mqtt_help", tags={"mqtt", "help"})
def mqtt_help() -> list[Message]:
    """Provides examples of how to use the MQTT MCP server."""
    return [
        Message("Here are examples of how to publish and receives messages:"),
        Message('Publish {"foo":"bar"} to topic "devices/foo" on 127.0.0.1:1883.'),
        Message(
            'Receive a message from topic "devices/bar", waiting up to 30 seconds.'
        ),
    ]


@mcp.prompt(name="mqtt_error", tags={"mqtt", "error"})
def mqtt_error(error: str | None = None) -> list[Message]:
    """Asks the user how to handle an error."""
    return (
        [
            Message(f"ERROR: {error!r}"),
            Message("Would you like to retry, change parameters, or abort?"),
        ]
        if error
        else []
    )
