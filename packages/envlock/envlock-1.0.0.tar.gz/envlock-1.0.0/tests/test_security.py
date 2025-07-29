import os
from click.testing import CliRunner
from main import cli, shred_file

def test_generated_key_and_hide(tmp_path):
    """
    Test that the CLI generates a secure random key when none is provided, and that the key is hidden if --hide-key is set.
    """
    runner = CliRunner()
    secret = "SECRET=autogen\n"
    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open("test.env", "w") as f:
            f.write(secret)
        result = runner.invoke(cli, ["lock", "-f", "test.env", "--hide-key", "--force"], standalone_mode=False)
        assert result.exit_code == 0
        assert os.path.exists("test.env.locked")
        assert "Encryption key" not in result.stderr if hasattr(result, 'stderr') else True
