# This file is a placeholder for isolated filesystem or environment tests if you want to split them out.

from click.testing import CliRunner
from main import cli
import os

def test_isolated_filesystem(tmp_path):
    """
    Test that the CLI works in an isolated filesystem and does not affect the real filesystem.
    """
    runner = CliRunner()
    secret = "SECRET=isolated\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0
        assert os.path.exists("test.env.locked")
    # After context, file should not exist in real fs
    assert not os.path.exists(os.path.join(tmp_path, "test.env.locked"))
