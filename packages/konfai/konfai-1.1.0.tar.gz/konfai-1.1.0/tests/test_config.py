import pytest
from konfai.utils.config import config

class Dummy:

    @config("Test")
    def __init__(self, a: int = 1, b: str = "ok"):
        self.a = a
        self.b = b

def test_config_instantiation(monkeypatch):
    import os
    os.environ['KONFAI_CONFIG_FILE'] = "./tests/dummy_data/dummy_config.yml"
    os.environ['KONFAI_CONFIG_PATH'] = "Test"

    dummy = Dummy()
    assert dummy.a == 42
    assert dummy.b == "hello"