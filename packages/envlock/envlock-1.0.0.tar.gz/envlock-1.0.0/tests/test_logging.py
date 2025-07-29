import pytest
from click.testing import CliRunner
from main import cli

def test_lock_invalid_key_logs_error(caplog, tmp_path):
    """
    Test that logger.error is called for invalid key format in lock command.
    """
    runner = CliRunner()
    test_file = tmp_path / "test.env"
    test_file.write_text("SECRET=foo")
    # Invalid key (not 32 bytes hex or base64)
    with caplog.at_level("ERROR"):
        result = runner.invoke(cli, ["lock", "-f", str(test_file), "--key", "shortkey"])
    assert result.exit_code != 0
    assert any(
        "Invalid key format." in m or "Base64 key must decode to 32 bytes." in m
        for m in caplog.messages
    )

def test_unlock_missing_file_logs_error(caplog):
    """
    Test that logger.error is called when unlocking a missing file.
    """
    runner = CliRunner()
    with caplog.at_level("ERROR"):
        result = runner.invoke(cli, ["unlock", "-f", "no_such_file", "--key", "a"*64])
    assert result.exit_code != 0
    assert any("does not exist" in m for m in caplog.messages)

def test_lock_output_exists_logs_error(caplog, tmp_path):
    """
    Test that logger.error is called when output file already exists in lock command.
    """
    runner = CliRunner()
    test_file = tmp_path / "test.env"
    out_file = tmp_path / "test.env.locked"
    test_file.write_text("SECRET=foo")
    out_file.write_text("already here")
    with caplog.at_level("ERROR"):
        result = runner.invoke(cli, ["lock", "-f", str(test_file), "--key", "a"*64])
    assert result.exit_code != 0
    assert any("Output file" in m and "exists" in m for m in caplog.messages)
