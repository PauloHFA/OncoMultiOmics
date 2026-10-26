"""Download versionado da coorte externa independente GSE31210 (Fase 5 / REG-08)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from oncosurv.ingestao.download import download_file

URL_GSE31210 = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE31nnn/GSE31210/matrix/GSE31210_series_matrix.txt.gz"
DEST_PATH = "data/external/GSE31210_series_matrix.txt.gz"
MANIFEST_PATH = "data/raw/manifest.json"


def main():
    root = Path(__file__).resolve().parent.parent
    dest = root / DEST_PATH
    manifest = root / MANIFEST_PATH
    print("=" * 60)
    print("Iniciando Download da Coorte Externa GSE31210 (GEO / NCBI)")
    print("=" * 60)
    download_file(
        url=URL_GSE31210,
        dest_path=dest,
        manifest_path=manifest,
    )
    print("\nDownload da coorte externa concluído com sucesso!")


if __name__ == "__main__":
    main()

