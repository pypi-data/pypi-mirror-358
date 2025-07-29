import json
from os import mkdir, path, remove, rename

from sapiumai_common_tools.info import PROJECT_NAME, PROJECT_VERSION


class TestInfo:

    def test_project_name(self):
        assert PROJECT_NAME == "sapiumai_common_tools"

    def test_project_version(self):
        # update this when you update the version in pyproject.toml
        assert PROJECT_VERSION == "0.1.1"


class TestLogger:
    def setup_method(self):
        if path.exists(path="./logs/log.txt"):
            remove(path="./logs/log.txt")

    def test_log_exists(self):
        from sapiumai_common_tools.logger import setup_logger

        logger = setup_logger(name="TestLogger")
        logger.info(msg="Test log")

        assert path.exists(path="./logs/log.txt")

    def teardown_method(self):
        if path.exists(path="./logs/log.txt"):
            remove(path="./logs/log.txt")


class TestConfig:

    def setup_class(self):
        if not path.exists(path="./config"):
            mkdir(path="./config")
        if path.exists(path="./config/config.json"):
            rename(src="./config/config.json", dst="./config/config.json.bak")

        sample_data = {"project": "sapium-agent", "env": "test"}
        with open(file="./config/config.json", mode="w") as f:
            json.dump(obj=sample_data, fp=f)

    def teardown_class(self):
        if path.exists(path="./config/config.json"):
            remove(path="./config/config.json")

        if path.exists(path="./config/config.json.bak"):
            rename(src="./config/config.json.bak", dst="./config/config.json")

    def test_config_exists(self):
        from sapiumai_common_tools.config import config

        assert config != {}
        assert config["project"] == "sapium-agent"
        assert config["env"] == "test"
