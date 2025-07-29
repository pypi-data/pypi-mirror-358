from click.testing import CliRunner
from main import cli
import os


def test_lock_and_unlock_cli(tmp_path):
    """
    Test the CLI lock and unlock functionality.
    """
    runner = CliRunner()
    secret = "SECRET=1234\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0
        assert os.path.exists("test.env.locked")
        result = runner.invoke(cli, ["unlock", "-f", "test.env.locked", "--key", key, "--force", "--output", "test.env.unlocked"], standalone_mode=False)
        assert result.exit_code == 0
        assert os.path.exists("test.env.unlocked")
        with open("test.env.unlocked") as f:
            assert f.read() == secret

def test_invalid_key_cli(tmp_path):
    """
    Test that attempting to unlock an environment file with an invalid key using the CLI does not produce a valid unlocked file.
    """
    runner = CliRunner()
    secret = "SECRET=5678\n"
    key = "a" * 64
    wrong_key = "b" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0
        assert os.path.exists("test.env.locked")
        result = runner.invoke(cli, ["unlock", "-f", "test.env.locked", "--key", wrong_key, "--force", "--output", "test.env.unlocked"], standalone_mode=False)
        assert not (os.path.exists("test.env.unlocked") and open("test.env.unlocked").read() == secret)

def test_lock_file_already_exists(tmp_path):
    """
    Test the behavior of the 'lock' command when the lock file already exists.
    """
    runner = CliRunner()
    secret = "SECRET=9999\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        with open("test.env.locked", "w") as f:
            f.write("dummy")
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--key", key], standalone_mode=False)
        assert result.exit_code != 0
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0
        assert os.path.exists("test.env.locked")

def test_unlock_file_does_not_exist(tmp_path):
    """
    Test that attempting to unlock a non-existent locked file returns a non-zero exit code.
    """
    runner = CliRunner()
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["unlock", "-f", "notfound.locked", "--key", key], standalone_mode=False)
        assert result.exit_code != 0

def test_lock_file_does_not_exist(tmp_path):
    """
    Test that the CLI returns a non-zero exit code when attempting to lock a non-existent environment file.
    """
    runner = CliRunner()
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["lock", "-f", "notfound.env", "--key", key], standalone_mode=False)
        assert result.exit_code != 0

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

def test_renew_command(tmp_path):
    """
    Test the CLI 'renew' command for key rotation.
    """
    runner = CliRunner()
    secret = "SECRET=renew\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        new_key = "b" * 64
        result = runner.invoke(cli, ["renew", "-f", "test.env.locked", "--old-key", key, "--new-key", new_key, "--show-key"], standalone_mode=False)
        assert result.exit_code == 0
        result2 = runner.invoke(cli, ["unlock", "-f", "test.env.locked", "--key", new_key, "--force", "--output", "test.env.unlocked"], standalone_mode=False)
        assert result2.exit_code == 0
        with open("test.env.unlocked") as f:
            assert f.read() == secret

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

def test_cli_help_outputs():
    """
    Test that --help for each command prints usage and does not error.
    """
    from main import cli
    runner = CliRunner()
    for cmd in [[], ["lock"], ["unlock"], ["renew"]]:
        result = runner.invoke(cli, cmd + ["--help"])
        assert result.exit_code == 0
        assert "Usage" in result.output

def test_cli_missing_required_args():
    """
    Test that missing required arguments produce a nonzero exit code.
    """
    from main import cli
    runner = CliRunner()
    # lock with no file present
    result = runner.invoke(cli, ["lock", "-f", "notfound.env", "--key", "a" * 64], standalone_mode=False)
    assert result.exit_code != 0
    # unlock with no file present
    result = runner.invoke(cli, ["unlock", "-f", "notfound.locked", "--key", "a" * 64], standalone_mode=False)
    assert result.exit_code != 0
