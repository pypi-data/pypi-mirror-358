from main import lock_file
import tempfile
import os

def test_base64_line_wrapping(tmp_path):
    """
    Test that lock_file base64 output is line-wrapped at 76 characters.
    """
    secret = b"A" * 200
    key = b"a" * 32
    input_path = tmp_path / "wrap.env"
    input_path.write_bytes(secret)
    output_path = tmp_path / "wrap.env.locked"
    lock_file(str(input_path), key=key.hex(), show_key=False, shred=False, force=True, output_file=str(output_path))
    with open(output_path) as f:
        lines = f.read().splitlines()
        for line in lines:
            assert len(line) <= 76

def test_large_file_lock_unlock(tmp_path):
    """
    Test locking and unlocking a large file (several MBs).
    """
    from click.testing import CliRunner
    from main import cli
    import os
    runner = CliRunner()
    key = "a" * 64
    data = os.urandom(1024 * 1024 * 5)  # 5 MB
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("large.env", "wb") as f:
            f.write(data)
        result = runner.invoke(cli, ["lock", "-f", "large.env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0
        result2 = runner.invoke(cli, ["unlock", "-f", "large.env.locked", "--key", key, "--force", "--output", "large.env.unlocked"], standalone_mode=False)
        assert result2.exit_code == 0
        with open("large.env.unlocked", "rb") as f:
            assert f.read() == data

# Utility and edge-case tests can go here if needed in the future.
