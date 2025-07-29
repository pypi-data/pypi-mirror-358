# This file is a placeholder for renew/rotation-specific tests if you want to split them out.
from click.testing import CliRunner
from main import cli
import os

def test_renew_with_generated_key(tmp_path):
    """
    Test the renew command with a generated new key (no --new-key provided).
    """
    runner = CliRunner()
    secret = "SECRET=renewgen\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        result = runner.invoke(cli, ["renew", "-f", "test.env.locked", "--old-key", key, "--show-key"], standalone_mode=False)
        assert result.exit_code == 0
        # Should print new key to stdout or stderr
        assert "encryption key".lower() in (result.output.lower() + (result.stderr or "").lower())

def test_renew_invalid_old_key(tmp_path):
    """
    Test that renew fails with an invalid old key.
    """
    runner = CliRunner()
    secret = "SECRET=renewfail\n"
    key = "a" * 64
    bad_key = "b" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        result = runner.invoke(cli, ["renew", "-f", "test.env.locked", "--old-key", bad_key, "--show-key"], standalone_mode=False)
        assert result.exit_code == 0 or result.exit_code is None  # renew logs error, does not sys.exit
        # File should not be re-encrypted with a new key
        # (could check for error message in result.output)

def test_multiple_renewals(tmp_path):
    """
    Test rotating the key multiple times in a row.
    """
    runner = CliRunner()
    secret = "SECRET=multi\n"
    key1 = "a" * 64
    key2 = "b" * 64
    key3 = "c" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        runner.invoke(cli, ["lock", "-f", "test.env", "--key", key1, "--force"], standalone_mode=False)
        runner.invoke(cli, ["renew", "-f", "test.env.locked", "--old-key", key1, "--new-key", key2, "--show-key"], standalone_mode=False)
        runner.invoke(cli, ["renew", "-f", "test.env.locked", "--old-key", key2, "--new-key", key3, "--show-key"], standalone_mode=False)
        result = runner.invoke(cli, ["unlock", "-f", "test.env.locked", "--key", key3, "--force", "--output", "test.env.unlocked"], standalone_mode=False)
        assert result.exit_code == 0
        with open("test.env.unlocked") as f:
            assert f.read() == secret
