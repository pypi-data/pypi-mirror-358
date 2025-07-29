# This file is a placeholder for stdin/stdout and piping tests if you want to split them out.

from click.testing import CliRunner
from main import cli
import pytest

def test_lock_and_unlock_stdin_stdout(tmp_path):
    """
    Test locking and unlocking environment secrets using stdin and stdout.
    """
    runner = CliRunner()
    secret = "SECRET=fromstdin\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["lock", "-f", "-", "--key", key], input=secret, standalone_mode=False)
        assert result.exit_code == 0
        b64_data = result.output.strip().replace("\n", "")
        assert b64_data
        result2 = runner.invoke(cli, ["unlock", "-f", "-", "--key", key, "--stdout"], input=result.output, standalone_mode=False)
        assert result2.exit_code == 0
        assert secret in result2.stdout

def test_unlock_stdout_binary(tmp_path):
    """
    Test --stdout for unlock with binary data.
    """
    runner = CliRunner()
    key = "a" * 64
    binary_data = bytes([0, 255, 127, 128, 10, 13, 0, 1])
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("bin.env", "wb") as f:
            f.write(binary_data)
        runner.invoke(cli, ["lock", "-f", "bin.env", "--key", key, "--force"], standalone_mode=False)
        result = runner.invoke(cli, ["unlock", "-f", "bin.env.locked", "--key", key, "--stdout"], standalone_mode=False)
        assert result.exit_code == 0
        # Click >=8.1.0 provides stdout_bytes for binary output
        if hasattr(result, "stdout_bytes"):
            assert binary_data == result.stdout_bytes
        else:
            pytest.skip("Click's CliRunner does not support binary stdout; cannot test exact binary output.")
