# This file is a placeholder for empty/binary file tests if you want to split them out.

from click.testing import CliRunner
from main import cli
import os

def test_lock_and_unlock_empty_file(tmp_path):
    """
    Test locking and unlocking an empty file.
    """
    runner = CliRunner()
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        open("empty.env", "w").close()
        result = runner.invoke(cli, ["lock", "-f", "empty.env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0
        result2 = runner.invoke(cli, ["unlock", "-f", "empty.env.locked", "--key", key, "--force", "--output", "empty.env.unlocked"], standalone_mode=False)
        assert result2.exit_code == 0
        with open("empty.env.unlocked") as f:
            assert f.read() == ""

def test_lock_and_unlock_binary_file(tmp_path):
    """
    Test locking and unlocking a binary file.
    """
    runner = CliRunner()
    key = "a" * 64
    binary_data = bytes([0, 255, 127, 128, 10, 13, 0, 1])
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("bin.env", "wb") as f:
            f.write(binary_data)
        result = runner.invoke(cli, ["lock", "-f", "bin.env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0
        result2 = runner.invoke(cli, ["unlock", "-f", "bin.env.locked", "--key", key, "--force", "--output", "bin.env.unlocked"], standalone_mode=False)
        assert result2.exit_code == 0
        with open("bin.env.unlocked", "rb") as f:
            assert f.read() == binary_data

def test_unicode_secret(tmp_path):
    """
    Test locking and unlocking a file containing Unicode characters.
    """
    runner = CliRunner()
    secret = "SECRET=üñîçødë\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("unicode.env", "w", encoding="utf-8") as f:
            f.write(secret)
        result = runner.invoke(cli, ["lock", "-f", "unicode.env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0
        result2 = runner.invoke(cli, ["unlock", "-f", "unicode.env.locked", "--key", key, "--force", "--output", "unicode.env.unlocked"], standalone_mode=False)
        assert result2.exit_code == 0
        with open("unicode.env.unlocked", encoding="utf-8") as f:
            assert f.read() == secret
