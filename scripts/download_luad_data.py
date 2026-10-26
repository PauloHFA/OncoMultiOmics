"""Script de ingestão e download versionado dos dados TCGA-LUAD (Fase 1).

Garante conformidade com REG-15 (reprodutibilidade e versionamento por hash).
"""
import sys
from pathlib import Path

# Adiciona src ao path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import json
import logging
import requests

from oncosurv.ingestao.download import download_file
from oncosurv.ingestao.hash_utils import compute_file_sha256

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

URLS = {
    "tcga_cdr": {
        "url": "https://tcga-pancan-atlas-hub.s3.us-east-1.amazonaws.com/download/Survival_SupplementalTable_S1_20171025_xena_sp",
        "dest": "data/raw/TCGA_CDR_SupplementalTable_S1.tsv",
    },
    "luad_rna_seq": {
        "url": "https://tcga-xena-hub.s3.us-east-1.amazonaws.com/download/TCGA.LUAD.sampleMap%2FHiSeqV2.gz",
        "dest": "data/raw/TCGA_LUAD_HiSeqV2.gz",
    },
}

API_ENDPOINTS = {
    "luad_cbioportal_patient": {
        "url": "https://www.cbioportal.org/api/studies/luad_tcga_pan_can_atlas_2018/clinical-data?clinicalDataType=PATIENT",
        "dest": "data/raw/luad_cbioportal_patient.json",
    },
    "luad_cbioportal_sample": {
        "url": "https://www.cbioportal.org/api/studies/luad_tcga_pan_can_atlas_2018/clinical-data?clinicalDataType=SAMPLE",
        "dest": "data/raw/luad_cbioportal_sample.json",
    },
}


def download_api_json(url: str, dest_path: Path, manifest_path: Path) -> Path:
    if dest_path.exists():
        logger.info("Arquivo JSON já existe: %s", dest_path)
        return dest_path

    logger.info("Baixando endpoint API: %s -> %s", url, dest_path)
    resp = requests.get(url, headers={"User-Agent": "OncoMultiOmics/1.0"}, timeout=60)
    resp.raise_for_status()
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(resp.text)

    sha256 = compute_file_sha256(dest_path)
    logger.info("Download de API concluído. SHA-256: %s", sha256)

    manifest_data = {}
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as mf:
            manifest_data = json.load(mf)
    manifest_data[dest_path.name] = {
        "source_url": url,
        "local_path": str(dest_path.as_posix()),
        "sha256": sha256,
        "bytes": dest_path.stat().st_size,
    }
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest_data, mf, indent=2)

    return dest_path


def main():
    root = Path(__file__).resolve().parent.parent
    manifest_path = root / "data" / "raw" / "manifest.json"

    print("=" * 60)
    print("Iniciando Ingestão de Dados TCGA-LUAD (Fase 1)")
    print("=" * 60)

    for key, info in URLS.items():
        dest = root / info["dest"]
        print(f"\n[+] Verificando/Baixando {key}...")
        download_file(
            url=info["url"],
            dest_path=dest,
            manifest_path=manifest_path,
        )

    for key, info in API_ENDPOINTS.items():
        dest = root / info["dest"]
        print(f"\n[+] Verificando/Baixando {key}...")
        download_api_json(
            url=info["url"],
            dest_path=dest,
            manifest_path=manifest_path,
        )

    print("\nTodos os arquivos verificados/baixados e hashes registrados em data/raw/manifest.json!")


if __name__ == "__main__":
    main()
