from star_openapi import OpenAPI
from tests import config


def test_config():
    app = OpenAPI()
    app.config.from_object(config)
    assert "SWAGGER_CONFIG" in app.config.keys()
    assert "JWT" in app.config.keys()
