from click.testing import CliRunner
from zrb.cli.main import cli

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"]) 
    assert result.exit_code == 0
    assert "ZRB Toolkit" in result.output
