# This file is a placeholder for example-based or tutorial tests if needed.

from click.testing import CliRunner
from main import cli
import os

def test_example_usage(tmp_path):
    """
    Example test: lock and unlock a file using the CLI, for documentation/tutorial purposes.
    """
    runner = CliRunner()
    secret = "SECRET=example\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open(".env", "w") as f:
            f.write(secret)
        result = runner.invoke(cli, ["lock", "-f", ".env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0
        result2 = runner.invoke(cli, ["unlock", "-f", ".env.locked", "--key", key, "--force", "--output", ".env.unlocked"], standalone_mode=False)
        assert result2.exit_code == 0
        with open(".env.unlocked") as f:
            assert f.read() == secret
