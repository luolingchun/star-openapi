from click.testing import CliRunner

from star_openapi import OpenAPI
from star_openapi.cli import cli

app = OpenAPI()
runner = CliRunner()


@app.cli.command("hello", help="Say hello")
def hello(): ...


def test_command():
    cli.app = None
    cli._is_loaded_app = False
    result = runner.invoke(cli)
    assert "hello" in result.output

    cli._is_loaded_app = False
    result = runner.invoke(cli, ["run", "--help"])

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "--host" in result.output
    assert "--port" in result.output


def test_command_with_app():
    cli.app = app
    cli._is_loaded_app = False
    runner.invoke(cli, ["--app", "examples.simple_demo:app"])
    cli._is_loaded_app = False
    runner.invoke(cli, ["-a", "examples.simple_demo:app"])


def test_command_with_app_not_found():
    cli.app = None
    cli._is_loaded_app = False
    result = runner.invoke(cli, ["--verbose", "--app", "not_found:app"])
    assert "No module named 'not_found'" in result.stderr
