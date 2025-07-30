import contextlib
import logging
from collections.abc import AsyncIterator

import click
import httpx
import uvicorn
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send


OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_UNITS = "metric"
DEFAULT_LANG = "zh_cn"


async def fetch_weather(city: str, api_key: str) -> dict[str, str]:
    """Call OpenWeather API and return a simplified weather dict.

    Raises:
        httpx.HTTPStatusError: if the response has a non-2xx status.
    """
    params = {
        "q": city,
        "appid": api_key,
        "units": DEFAULT_UNITS,
        "lang": DEFAULT_LANG,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(OPENWEATHER_URL, params=params)
        r.raise_for_status()
        data = r.json()
    # Extract a concise summary
    weather_main = data["weather"][0]["main"]
    description = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    return {
        "city": city,
        "weather": weather_main,
        "description": description,
        "temp": f"{temp}°C",
        "feels_like": f"{feels_like}°C",
        "humidity": f"{humidity}%",
    }


@click.command()  # 使用 click 库来定义命令行接口（CLI）参数
@click.option("--port", default=3000, help="Port to listen on for HTTP")
@click.option("--api-key", envvar="OPENWEATHER_API_KEY", required=True, help="OpenWeather API key (or set OPENWEATHER_API_KEY env var)",)
@click.option("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",)
@click.option("--json-response", is_flag=True, default=False, help="Enable JSON responses instead of SSE streams",)
def main(port: int, api_key: str, log_level: str, json_response: bool) -> int:
    """
    Run an MCP weather server using Streamable HTTP transport.
    """
    logging.basicConfig(level=getattr(logging, log_level.upper()), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",)
    logger = logging.getLogger("weather-server")
    app = Server("mcp-streamable-http-weather")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """
        MCP工具注册：让大模型能调用 get-weather
        """
        ctx = app.request_context
        city = arguments.get("location")
        if not city:
            raise ValueError("'location' is required in arguments")
        # Send an initial log message so the client sees streaming early.
        await ctx.session.send_log_message(level="info", data=f"Fetching weather for {city}…", logger="weather", related_request_id=ctx.request_id,)
        try:
            weather = await fetch_weather(city, api_key)
        except Exception as err:
            await ctx.session.send_log_message(level="error", data=str(err), logger="weather", related_request_id=ctx.request_id,)
            raise
        await ctx.session.send_log_message(level="info", data="Weather data fetched successfully!", logger="weather", related_request_id=ctx.request_id,)
        summary = f"{weather['city']}：{weather['description']}，温度 {weather['temp']}，体感 {weather['feels_like']}，湿度 {weather['humidity']}。"
        return [types.TextContent(type="text", text=summary),]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """
        让MCP告诉模型有哪些工具（工具列表）
        """
        return [
            types.Tool(
                name="get-weather",
                description="查询指定城市的实时天气（OpenWeather 数据）",
                inputSchema={
                    "type": "object",
                    "required": ["location"],
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "城市的英文名称，如 'Beijing'",
                        }
                    },
                },
            )
        ]

    # Session manager
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,  # 无状态；不保存历史事件
        json_response=json_response,
        stateless=True,
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:  # noqa: D401,E501
        await session_manager.handle_request(scope, receive, send)

    # Lifespan Management（生命周期管理）
    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        async with session_manager.run():
            logger.info("Weather MCP server started! 🚀")
            try:
                yield
            finally:
                logger.info("Weather MCP server shutting down…")

    # ASGI app + Uvicorn，创建了 MCP 的“HTTP 会话处理中心”，负责处理所有 /mcp 路由的请求
    starlette_app = Starlette(
        debug=False,
        routes=[Mount("/mcp", app=handle_streamable_http)],
        lifespan=lifespan,
    )
    uvicorn.run(starlette_app, host="127.0.0.1", port=port)  # 启动服务器，完整URI：http://localhost:3000/mcp
    return 0


if __name__ == "__main__":
    main()
