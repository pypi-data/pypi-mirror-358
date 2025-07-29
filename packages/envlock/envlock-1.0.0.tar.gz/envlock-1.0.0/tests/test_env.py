import os
from click.testing import CliRunner
from main import cli, get_binary_key

def test_envlock_encryption_key_env_var(tmp_path, monkeypatch):
    """
    Test that the CLI uses ENVLOCK_ENCRYPTION_KEY environment variable if no key is provided.
    """
    runner = CliRunner()
    secret = "SECRET=envvar\n"
    key = "c" * 64
    monkeypatch.setenv("ENVLOCK_ENCRYPTION_KEY", key)
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--force"], standalone_mode=False)
        assert result.exit_code == 0
        assert os.path.exists("test.env.locked")
        result2 = runner.invoke(cli, ["unlock", "-f", "test.env.locked", "--force", "--output", "test.env.unlocked"], env={"ENVLOCK_ENCRYPTION_KEY": key}, standalone_mode=False)
        assert result2.exit_code == 0
        with open("test.env.unlocked") as f:
            assert f.read() == secret

def test_get_binary_key_env_var(monkeypatch):
    """
    Test get_binary_key returns the key from ENVLOCK_ENCRYPTION_KEY if no key is provided.
    """
    key = "d" * 64
    monkeypatch.setenv("ENVLOCK_ENCRYPTION_KEY", key)
    val, generated = get_binary_key(None)
    assert val is not None
    assert generated is False

def test_env_var_precedence(tmp_path, monkeypatch):
    """
    Test that --key takes precedence over ENVLOCK_ENCRYPTION_KEY.
    """
    runner = CliRunner()
    secret = "SECRET=precedence\n"
    key = "a" * 64
    wrong_key = "b" * 64
    monkeypatch.setenv("ENVLOCK_ENCRYPTION_KEY", wrong_key)
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0
        result2 = runner.invoke(cli, ["unlock", "-f", "test.env.locked", "--key", key, "--force", "--output", "test.env.unlocked"], standalone_mode=False)
        assert result2.exit_code == 0
        with open("test.env.unlocked") as f:
            assert f.read() == secret
