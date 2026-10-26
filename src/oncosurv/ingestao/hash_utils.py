import hashlib
from pathlib import Path


def compute_file_sha256(filepath: Path | str, chunk_size: int = 65536) -> str:
    """Calcula o hash SHA-256 de um arquivo para garantir reprodutibilidade e versionamento (REG-15)."""
    sha256 = hashlib.sha256()
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()

