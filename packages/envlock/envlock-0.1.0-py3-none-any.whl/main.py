"""
Envlock: Secure .env file encryption, decryption, shredding, and key rotation CLI tool.

This tool provides a command-line interface for securely locking (encrypting), unlocking (decrypting), shredding (securely deleting), and rotating the encryption key for environment secrets files. It uses Fernet symmetric encryption with a 32-byte key, supports both hex and base64 key formats, and outputs encrypted files as base64-encoded, line-wrapped text for safe storage and sharing.

Main features:
- Lock (encrypt) secrets files with a strong key
- Unlock (decrypt) locked files with the correct key
- Shred (securely delete) files to prevent recovery
- Renew (rotate) the encryption key for a locked file
- CLI options for stdin/stdout, file overwrite, key hiding, and secure memory handling
- Robust error handling and logging

Usage:
    python main.py lock   # Encrypt a file
    python main.py unlock # Decrypt a file
    python main.py renew  # Rotate key for a locked file

See --help for each command for details.
"""

import os
import sys
import click
import base64
import secrets
import logging
from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("envlock")

def to_base64(data):
    """Encode bytes to urlsafe base64 string for key display or storage."""
    return base64.urlsafe_b64encode(data).decode()

def from_hex(hex_str):
    """Convert a hex string to bytes."""
    return bytes.fromhex(hex_str)

def shred_file(file_path, passes=3):
    """Securely overwrite and delete a file to prevent recovery.

    Args:
        file_path (str): Path to the file to shred.
        passes (int): Number of overwrite passes (default: 3).
    """
    try:
        if not os.path.isfile(file_path):
            return
        length = os.path.getsize(file_path)
        with open(file_path, 'ba+', buffering=0) as f:
            for _ in range(passes):
                f.seek(0)
                f.write(secrets.token_bytes(length))
        os.remove(file_path)
    except Exception as e:
        logger.error(f"Failed to shred file: {e}")

def get_binary_key(key):
    """Get a 32-byte binary key from hex, base64, or environment variable.

    Args:
        key (str or None): Key as hex string, base64 string, or None to use ENVLOCK_ENCRYPTION_KEY env var.
    Returns:
        tuple: (key_bytes, generated) where key_bytes is the 32-byte key or None, and generated is True if a new key was generated.
    """
    if key is None:
        key = os.environ.get("ENVLOCK_ENCRYPTION_KEY")
    if key is None:
        return secrets.token_bytes(32), True  # True: generated
    if len(key) == 64:
        try:
            return from_hex(key), False
        except Exception:
            logger.error("Invalid hex key.")
            return None, False
    try:
        decoded = base64.urlsafe_b64decode(key.encode())
        if len(decoded) != 32:
            logger.error("Base64 key must decode to 32 bytes.")
            return None, False
        return decoded, False
    except Exception:
        logger.error("Invalid key format.")
        return None, False

def lock_file(input_file, key=None, show_key=True, shred=False, force=False, output_file=None):
    """Encrypt a file and write base64 output, 76 chars/line."""
    if input_file == '-':
        data = sys.stdin.buffer.read()
        input_file = 'stdin'
    else:
        if not os.path.exists(input_file):
            logger.error(f"File {input_file} does not exist.")
            sys.exit(1)
        with open(input_file, 'rb') as f:
            data = f.read()
    binary_key, generated = get_binary_key(key)
    if binary_key is None:
        sys.exit(1)
    if generated and show_key:
        print(f"Encryption key (hex): {binary_key.hex()}", file=sys.stderr)
    fernet_key = base64.urlsafe_b64encode(binary_key)
    if len(binary_key) != 32:
        logger.error("Key must be 32 bytes (64 hex chars or 32 bytes base64).")
        sys.exit(1)
    fernet = Fernet(fernet_key)
    encrypted = fernet.encrypt(data)
    b64_encrypted = base64.b64encode(encrypted).decode()
    lines = [b64_encrypted[i:i+76] for i in range(0, len(b64_encrypted), 76)]
    if output_file is None:
        output_file = input_file + '.locked' if input_file != 'stdin' else None
    if output_file and os.path.exists(output_file) and not force:
        logger.error(f"Output file {output_file} exists. Use --force to overwrite.")
        sys.exit(1)
    if output_file:
        with open(output_file, 'w') as f:
            f.write('\n'.join(lines) + '\n')
        try:
            os.chmod(output_file, 0o600)
        except Exception:
            pass
        logger.info(f"Locked file created: {output_file}")
    else:
        print('\n'.join(lines))
    if shred and input_file != 'stdin':
        shred_file(input_file)
        logger.info(f"Original file {input_file} securely deleted.")
    # Securely overwrite sensitive data
    for v in [data, encrypted, binary_key, fernet_key]:
        if isinstance(v, bytearray):
            v[:] = secrets.token_bytes(len(v))
    del data, encrypted, fernet, binary_key, fernet_key

def unlock_file(input_file, key, output_file=None, force=False, to_stdout=False):
    """Decrypt a base64-encoded file and write output."""
    if input_file == '-':
        b64_encrypted = sys.stdin.read()
        input_file = 'stdin'
    else:
        if not os.path.exists(input_file):
            logger.error(f"File {input_file} does not exist.")
            sys.exit(1)
        with open(input_file, 'r') as f:
            b64_encrypted = f.read()
    b64_encrypted = ''.join(b64_encrypted.split())
    try:
        encrypted = base64.b64decode(b64_encrypted)
    except Exception:
        logger.error("Failed to decode base64 encrypted data.")
        sys.exit(1)
    binary_key, _ = get_binary_key(key)
    if binary_key is None:
        sys.exit(1)
    fernet_key = base64.urlsafe_b64encode(binary_key)
    if len(binary_key) != 32:
        logger.error("Key must be 32 bytes (64 hex chars or 32 bytes base64).")
        sys.exit(1)
    fernet = Fernet(fernet_key)
    try:
        decrypted = fernet.decrypt(encrypted)
    except Exception:
        logger.error("Decryption failed. Invalid key or corrupted file.")
        sys.exit(1)
    if output_file is None and not to_stdout:
        output_file = input_file[:-7] if input_file.endswith('.locked') else input_file + '.unlocked'
    if output_file and os.path.exists(output_file) and not force:
        logger.error(f"Output file {output_file} exists. Use --force to overwrite.")
        sys.exit(1)
    if to_stdout or output_file is None:
        sys.stdout.buffer.write(decrypted)
    else:
        with open(output_file, 'wb') as f:
            f.write(decrypted)
        try:
            os.chmod(output_file, 0o600)
        except Exception:
            pass
        logger.info(f"Unlocked file created: {output_file}")
    # Securely overwrite sensitive data
    for v in [decrypted, encrypted, binary_key, fernet_key]:
        if isinstance(v, bytearray):
            v[:] = secrets.token_bytes(len(v))
    del decrypted, encrypted, fernet, binary_key, fernet_key

@click.group()
def cli():
    """envlock: Secure .env file locker/unlocker CLI."""
    pass

@cli.command()
@click.option('-f', '--file', 'file_', type=click.Path(), default=None, help='File to lock (default: .env, or stdin if -)')
@click.option('-k', '--key', help='Encryption key (32-byte urlsafe base64 string)')
@click.option('-h', '--hide-key/--show-key', default=False, help='Hide generated key (default: show)')
@click.option('-s', '--shred/--no-shred', default=False, help='Securely delete original file after locking')
@click.option('--force', is_flag=True, help='Overwrite output file if exists')
@click.option('-o', '--output', 'output_file', type=click.Path(), default=None, help='Output file (default: <input>.locked)')
def lock(file_, key, hide_key, shred, force, output_file):
    """Lock (encrypt) a file or stdin, outputting a base64-encoded locked file."""
    input_file = file_ if file_ else '.env'
    if input_file == '-':
        lock_file('-', key, not hide_key, shred, force, output_file)
    else:
        if not os.path.exists(input_file):
            logger.error(f"File {input_file} does not exist. Use --file to specify a file.")
            sys.exit(1)
        lock_file(input_file, key, not hide_key, shred, force, output_file)

@cli.command()
@click.option('-f', '--file', 'file_', type=click.Path(), default=None, help='File to unlock (default: .env.locked, or stdin if -)')
@click.option('-k', '--key', help='Encryption key (32-byte urlsafe base64 string)')
@click.option('--force', is_flag=True, help='Overwrite output file if exists')
@click.option('-o', '--output', 'output_file', type=click.Path(), default=None, help='Output file (default: <input>.unlocked)')
@click.option('--stdout', is_flag=True, help='Write output to stdout')
def unlock(file_, key, force, output_file, stdout):
    """Unlock a file (default: .env.locked) or stdin (-)"""
    input_file = file_ if file_ else '.env.locked'
    if input_file == '-':
        unlock_file('-', key, output_file, force, stdout)
    else:
        if not os.path.exists(input_file):
            logger.error(f"File {input_file} does not exist. Use --file to specify a file.")
            sys.exit(1)
        unlock_file(input_file, key, output_file, force, stdout)

@cli.command()
@click.option('-f', '--file', 'file_', type=click.Path(exists=True), help='File to renew (default: .env.locked)')
@click.option('--old-key', required=True, help='Current encryption key (hex or base64)')
@click.option('--new-key', help='New encryption key (hex or base64, optional)')
@click.option('-h', '--hide-key/--show-key', default=False, help='Hide generated new key (default: show)')
def renew(file_, old_key, new_key, hide_key):
    """Re-encrypt (rotate key) for a locked file, updating the encryption key."""
    input_file = file_ if file_ else '.env.locked'
    if not os.path.exists(input_file):
        logger.error(f"File {input_file} does not exist. Use --file to specify a file.")
        return
    # Read base64-encoded text, decode to bytes
    with open(input_file, 'r') as f:
        b64_encrypted = f.read()
    b64_encrypted = ''.join(b64_encrypted.split())
    try:
        encrypted = base64.b64decode(b64_encrypted)
    except Exception:
        logger.error("Failed to decode base64 encrypted data.")
        return
    old_binary_key, _ = get_binary_key(old_key)
    if old_binary_key is None:
        return
    old_fernet_key = base64.urlsafe_b64encode(old_binary_key)
    if len(old_binary_key) != 32:
        logger.error("Old key must be 32 bytes (64 hex chars or 32 bytes base64).")
        return
    fernet = Fernet(old_fernet_key)
    try:
        decrypted = fernet.decrypt(encrypted)
    except Exception:
        logger.error("Decryption failed. Invalid old key or corrupted file.")
        return
    # Encrypt with new key
    new_binary_key, generated = get_binary_key(new_key)
    if new_binary_key is None:
        return
    new_fernet_key = base64.urlsafe_b64encode(new_binary_key)
    if len(new_binary_key) != 32:
        logger.error("New key must be 32 bytes (64 hex chars or 32 bytes base64).")
        return
    new_fernet = Fernet(new_fernet_key)
    new_encrypted = new_fernet.encrypt(decrypted)
    # Write as base64-encoded, line-wrapped text
    b64_new_encrypted = base64.b64encode(new_encrypted).decode()
    lines = [b64_new_encrypted[i:i+76] for i in range(0, len(b64_new_encrypted), 76)]
    with open(input_file, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    logger.info(f"File re-encrypted with new key: {input_file}")
    if generated and not hide_key:
        print(f"New encryption key (hex): {new_binary_key.hex()}")
    # Securely overwrite sensitive data
    for v in [decrypted, encrypted, old_binary_key, old_fernet_key, new_binary_key, new_fernet_key]:
        if isinstance(v, bytearray):
            v[:] = secrets.token_bytes(len(v))
    del decrypted, encrypted, old_binary_key, old_fernet_key, new_binary_key, new_fernet_key

if __name__ == '__main__':
    cli()
