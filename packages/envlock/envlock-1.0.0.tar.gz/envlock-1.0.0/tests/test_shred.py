import os
from main import shred_file

def test_shred_file(tmp_path):
    """
    Test that shred_file securely deletes a file.
    """
    file_path = tmp_path / "tobeshredded.txt"
    file_path.write_text("secret")
    shred_file(str(file_path))
    assert not file_path.exists()

def test_shred_file_nonexistent():
    """
    Test that shred_file does not raise an error when called on a non-existent file.
    """
    try:
        shred_file("this_file_does_not_exist.txt")
    except Exception as e:
        assert False, f"shred_file raised an exception: {e}"

def test_shred_after_lock(tmp_path):
    """
    Test that --shred deletes the original file after locking.
    """
    from click.testing import CliRunner
    from main import cli
    runner = CliRunner()
    secret = "SECRET=shred\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force", "--shred"], standalone_mode=False)
        assert result.exit_code == 0
        assert not os.path.exists("test.env")
        assert os.path.exists("test.env.locked")
