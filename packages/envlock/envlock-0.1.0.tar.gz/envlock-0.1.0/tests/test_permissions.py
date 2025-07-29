import os
from click.testing import CliRunner
from main import cli, shred_file

def test_shred_file_permission_error(tmp_path, monkeypatch):
    """
    Test that shred_file handles permission errors gracefully and logs an error.
    """
    file_path = tmp_path / "protected.txt"
    file_path.write_text("secret")
    def raise_perm_error(path):
        raise PermissionError("No permission to delete")
    monkeypatch.setattr(os, "remove", raise_perm_error)
    try:
        shred_file(str(file_path))
    except Exception as e:
        assert False, f"shred_file raised an exception: {e}"

def test_lock_invalid_output_permission(tmp_path, monkeypatch):
    """
    Test that the lock command handles permission errors when writing the output file.
    """
    runner = CliRunner()
    secret = "SECRET=permerror\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        def raise_perm_error(*args, **kwargs):
            if args[0].endswith(".locked") and 'w' in args[1]:
                raise PermissionError("No permission to write")
            return open.__wrapped__(*args, **kwargs)
        monkeypatch.setattr("builtins.open", raise_perm_error)
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code != 0

def test_unlock_invalid_output_permission(tmp_path, monkeypatch):
    """
    Test that the unlock command handles permission errors when writing the output file.
    """
    runner = CliRunner()
    secret = "SECRET=permerror2\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        runner.invoke(cli, ["lock", "-f", "test.env", "--key", key, "--force"], standalone_mode=False)
        def raise_perm_error(*args, **kwargs):
            if args[0].endswith(".unlocked") and 'w' in args[1]:
                raise PermissionError("No permission to write")
            return open.__wrapped__(*args, **kwargs)
        monkeypatch.setattr("builtins.open", raise_perm_error)
        result = runner.invoke(cli, ["unlock", "-f", "test.env.locked", "--key", key, "--force", "--output", "test.env.unlocked"], standalone_mode=False)
        assert result.exit_code != 0

def test_lock_file_readonly(tmp_path):
    """
    Test locking a file that is read-only (should still succeed on most OSes, but test for robustness).
    """
    from click.testing import CliRunner
    from main import cli
    import os
    runner = CliRunner()
    secret = "SECRET=readonly\n"
    key = "a" * 64
    with runner.isolated_filesystem(temp_dir=tmp_path):
        file_path = os.path.join(tmp_path, "test.env")
        with open(file_path, "w") as f:
            f.write(secret)
        os.chmod(file_path, 0o444)
        result = runner.invoke(cli, ["lock", "-f", file_path, "--key", key, "--force"], standalone_mode=False)
        assert result.exit_code == 0

def test_unlock_invalid_base64(tmp_path):
    """
    Test unlocking a file with invalid base64 content.
    """
    from click.testing import CliRunner
    from main import cli
    key = "a" * 64
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("bad.locked", "w") as f:
            f.write("notbase64!!")
        result = runner.invoke(cli, ["unlock", "-f", "bad.locked", "--key", key], standalone_mode=False)
        assert result.exit_code != 0
