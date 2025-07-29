from enum import Enum
from functools import cache
from os import environ, path
from pathlib import Path
from typing import Optional, Tuple

from loguru import logger
from pydantic import BaseModel, Field


class CacheLocation(str, Enum):
    NEARBY = "nearby"


class LLMDeploymentConfig(BaseModel):
    deployment_id: str = Field(
        default_factory=lambda: environ.get("OPENAI_DEPLOYMENT", "")
    )
    model: str = Field(
        default_factory=lambda: environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    )


class LLMConfig(BaseModel):
    openai_api_base: str = Field(
        default_factory=lambda: environ.get(
            "AZURE_OPENAI_ENDPOINT",
            environ.get("OPENAI_API_BASE", "https://api.openai.com"),
        ),
    )
    openai_api_key: str = Field(
        default_factory=lambda: environ.get("OPENAI_API_KEY", "")
    )
    openai_api_version: str = Field(
        default_factory=lambda: environ.get("OPENAI_API_VERSION", "2023-07-01-preview")
    )

    reasoning: LLMDeploymentConfig = Field(default_factory=LLMDeploymentConfig)
    retrieval: LLMDeploymentConfig = Field(default_factory=LLMDeploymentConfig)
    embedding: LLMDeploymentConfig = Field(default_factory=LLMDeploymentConfig)


class RongdaConfig(BaseModel):
    username: str = Field(default_factory=lambda: environ.get("RD_USER", ""))
    password: str = Field(default_factory=lambda: environ.get("RD_PASS", ""))


class AppConfig(BaseModel):
    cache_location: CacheLocation = Field(default_factory=lambda: CacheLocation.NEARBY)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    rongda: RongdaConfig = Field(default_factory=RongdaConfig)


def generate_config(rcfile: str) -> None:
    logger.warning("Generating config file.")
    config = AppConfig()
    with open(rcfile, "w") as fd:
        print(config.model_dump_json(indent=4), file=fd)


@cache
def load_config(cfg_file: str = "", gen_cfg: bool = False) -> AppConfig:
    rcfile = (
        cfg_file
        if cfg_file
        else environ.get(
            "XXY_CFG_FILE", path.join(path.expanduser("~"), ".xxy_cfg.json")
        )
    )
    if not path.exists(rcfile) or gen_cfg:
        generate_config(rcfile)

    with open(rcfile, "r") as fd:
        content = fd.read().strip()
        config = AppConfig.model_validate_json(content)
    new_content = config.model_dump_json(indent=4)
    if content != new_content:
        logger.warning("Updating config file.")
        with open(rcfile, "w") as fd:
            print(new_content, file=fd)

    return config


def get_cache_path(path: Path) -> Path:
    config = load_config()
    if config.cache_location == CacheLocation.NEARBY:
        return path.with_suffix(".xxy")
    else:
        raise NotImplementedError("Only nearby cache location is supported.")
