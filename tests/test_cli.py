from click.testing import CliRunner

from star_openapi import OpenAPI
from star_openapi.cli import cli


def test_run_command_with_openapi_app():
    runner = CliRunner()

    app = OpenAPI()

    @app.cli.command("hello")
    def hello():
        print("hello world")

    result = runner.invoke(
        cli,
    )
    assert "hello" in result.output

    result = runner.invoke(cli, ["run", "--help"])

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "--host" in result.output
    assert "--port" in result.output
