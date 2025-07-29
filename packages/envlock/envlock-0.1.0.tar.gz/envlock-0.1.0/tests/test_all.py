# This file is for legacy or integration tests that don't fit elsewhere.
# You can remove this if not needed.

from click.testing import CliRunner
from main import cli
import os

def test_cli_integration(tmp_path):
    """
    Integration test: lock, unlock, renew, and shred in sequence.
    """
    runner = CliRunner()
    secret = "SECRET=integration\n"
    key = "a" * 64
    new_key = "b" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        # Lock
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0
        # Renew
        result = runner.invoke(cli, ["renew", "-f", "test.env.locked", "--old-key", key, "--new-key", new_key, "--show-key"], standalone_mode=False)
        assert result.exit_code == 0
        # Unlock
        result = runner.invoke(cli, ["unlock", "-f", "test.env.locked", "--key", new_key, "--force", "--output", "test.env.unlocked"], standalone_mode=False)
        assert result.exit_code == 0
        with open("test.env.unlocked") as f:
            assert f.read() == secret
        # Shred
        from main import shred_file
        shred_file("test.env.unlocked")
        assert not os.path.exists("test.env.unlocked")
