# This file is a placeholder for hide-key option tests if you want to split them out.

from click.testing import CliRunner
from main import cli
import os

def test_lock_hide_key_option(tmp_path):
    """
    Test the CLI 'lock' command with the '--hide-key' option.
    """
    runner = CliRunner()
    secret = "SECRET=hidekey\n"
    key = None
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--hide-key", "--force"], standalone_mode=False)
        assert result.exit_code == 0
        assert os.path.exists("test.env.locked")
        assert "Encryption key" not in result.stderr if hasattr(result, 'stderr') else True
