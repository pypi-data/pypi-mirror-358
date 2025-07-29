from datetime import timedelta
from time import sleep
from uuid import uuid4

import pytest

from extratools_core.config import Config, ConfigLevel, ConfigSource


def test_config() -> None:
    config = Config(ttl=timedelta(seconds=1))

    with pytest.raises(LookupError):
        config.get("STAGE")

    config.register_source(ConfigSource(
        "default",
        ConfigLevel.DEFAULT,
        {
            "STAGE": "test",
        },
    ))
    assert config.get("STAGE") == "test"

    config.set_in_adhoc("STAGE", "local")
    assert config.get("STAGE") == "local"
    config.set_in_adhoc("STAGE", "test")
    assert config.get("STAGE") == "test"

    config.register_source(ConfigSource(
        "dynamic",
        ConfigLevel.DYNAMIC,
        lambda: {
            "TEST_ID": str(uuid4()),
        },
    ))
    first_test_id = config.get(".TEST_ID")
    assert config.get(".TEST_ID") == first_test_id
    sleep(1)
    assert config.get(".TEST_ID") != first_test_id
