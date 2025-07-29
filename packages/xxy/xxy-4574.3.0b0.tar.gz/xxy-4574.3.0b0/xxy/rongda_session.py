import aiohttp
from loguru import logger
from rongda_mcp_server.login import login

from xxy.config import load_config


async def get_rongda_seesion() -> aiohttp.ClientSession:
    config = load_config()
    if get_rongda_seesion.session is None:  # type: ignore[attr-defined]
        logger.info(f"🔒 Logging in to Rongda... with user {config.rongda.username}")
        get_rongda_seesion.session = await login(  # type: ignore[attr-defined]
            config.rongda.username, config.rongda.password
        )
    return get_rongda_seesion.session  # type: ignore


get_rongda_seesion.session = None  # type: ignore[attr-defined]
