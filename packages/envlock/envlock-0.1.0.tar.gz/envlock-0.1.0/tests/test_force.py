# This file is a placeholder for --force flag tests if you want to split them out.

from click.testing import CliRunner
from main import cli
import os

def test_lock_force_overwrite(tmp_path):
    """
    Test that the --force flag allows overwriting an existing locked file.
    """
    runner = CliRunner()
    secret = "SECRET=force\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        with open("test.env.locked", "w") as f:
            f.write("dummy")
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0
        assert os.path.exists("test.env.locked")
