import base64
from main import get_binary_key

def test_invalid_hex_key():
    """
    Test that get_binary_key returns None for an invalid hex key string.
    """
    key = 'zz' * 32
    val, generated = get_binary_key(key)
    assert val is None
    assert generated is False

def test_invalid_base64_key():
    """
    Test that get_binary_key returns None for an invalid base64 key string.
    """
    key = '!' * 32
    val, generated = get_binary_key(key)
    assert val is None
    assert generated is False

def test_wrong_length_key():
    """
    Test that get_binary_key returns None for a base64 key of the wrong length.
    """
    key = base64.urlsafe_b64encode(b'1234567890123456').decode()
    val, generated = get_binary_key(key)
    assert val is None
    assert generated is False

def test_unlock_with_corrupted_key(tmp_path):
    """
    Test unlocking with a corrupted (non-hex/non-base64) key.
    """
    from click.testing import CliRunner
    from main import cli
    runner = CliRunner()
    secret = "SECRET=corruptkey\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        bad_key = "!@#$%^&*()" * 6
        result = runner.invoke(cli, ["unlock", "-f", "test.env.locked", "--key", bad_key, "--force", "--output", "test.env.unlocked"], standalone_mode=False)
        assert result.exit_code != 0
