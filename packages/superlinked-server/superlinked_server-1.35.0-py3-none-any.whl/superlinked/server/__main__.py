import uvicorn
from fastapi import FastAPI

from superlinked.server.app import ServerApp
from superlinked.server.configuration.app_config import AppConfig
from superlinked.server.logger import ServerLoggerConfigurator


def get_app() -> FastAPI:
    return ServerApp().app


def main() -> None:
    app_config = AppConfig()
    ServerLoggerConfigurator.setup_logger(app_config)
    uvicorn.run(
        "superlinked.server.__main__:get_app",
        host=app_config.SERVER_HOST,
        port=app_config.SERVER_PORT,
        workers=app_config.WORKER_COUNT,
        log_config=None,
        factory=True,
        loop="asyncio",
    )


if __name__ == "__main__":
    main()
