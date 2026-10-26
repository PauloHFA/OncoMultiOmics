import json
import logging
from pathlib import Path
import requests
from tqdm import tqdm

from oncosurv.ingestao.hash_utils import compute_file_sha256

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def download_file(
    url: str,
    dest_path: Path | str,
    manifest_path: Path | str | None = None,
    chunk_size: int = 1048576,  # 1MB
    force: bool = False,
) -> Path:
    """Baixa um arquivo de URL com barra de progresso e registra hash SHA-256 (REG-15).

    Args:
        url: URL pública do recurso
        dest_path: Caminho de destino local
        manifest_path: Caminho opcional do arquivo JSON com histórico de downloads e hashes
        chunk_size: Tamanho do buffer de streaming
        force: Se True, faz novo download mesmo se o arquivo já existir

    Returns:
        Path do arquivo salvo
    """
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists() and not force:
        sha256 = compute_file_sha256(dest)
        logger.info("Arquivo já existente: %s (SHA-256: %s)", dest, sha256)
        return dest

    logger.info("Iniciando download de: %s -> %s", url, dest)
    headers = {"User-Agent": "OncoMultiOmics-Survival-Engine/1.0"}
    response = requests.get(url, stream=True, headers=headers, timeout=60)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))

    with open(dest, "wb") as f, tqdm(
        desc=dest.name,
        total=total_size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))

    sha256 = compute_file_sha256(dest)
    logger.info("Download concluído com sucesso. SHA-256: %s", sha256)

    # Registrar no manifesto
    if manifest_path:
        manifest_file = Path(manifest_path)
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        manifest_data = {}
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as mf:
                    manifest_data = json.load(mf)
            except Exception:
                manifest_data = {}

        manifest_data[dest.name] = {
            "source_url": url,
            "local_path": str(dest.as_posix()),
            "sha256": sha256,
            "bytes": dest.stat().st_size,
        }
        with open(manifest_file, "w", encoding="utf-8") as mf:
            json.dump(manifest_data, mf, indent=2)

    return dest

