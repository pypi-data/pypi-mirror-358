import platform, tarfile, urllib.request, shutil
from pathlib import Path

XMRIG_URLS = {
    "Linux": "https://github.com/xmrig/xmrig/releases/latest/download/xmrig-6.22.0-linux-static-x64.tar.gz",
    "Windows": "https://github.com/xmrig/xmrig/releases/latest/download/xmrig-6.22.0-msvc-win64.zip",
    "Darwin": "https://github.com/xmrig/xmrig/releases/latest/download/xmrig-6.22.0-macos-universal.tar.gz",
}
BIN_DIR = Path.home() / ".crypto-ylp" / "xmrig"

def ensure_xmrig() -> Path:
    if (BIN_DIR / "xmrig").exists():
        return BIN_DIR / "xmrig"
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    url = XMRIG_URLS.get(platform.system())
    if not url:
        raise RuntimeError("Unsupported OS")

    print(f"Downloading XMRig to {BIN_DIR}...")
    tgz_path = BIN_DIR / "xmrig.tgz"
    urllib.request.urlretrieve(url, tgz_path)

    if tgz_path.suffix == ".zip":
        shutil.unpack_archive(tgz_path, BIN_DIR)
    else:
        with tarfile.open(tgz_path) as tar:
            tar.extractall(BIN_DIR)
    tgz_path.unlink()

    xmrig = next(BIN_DIR.rglob("xmrig*"), None)
    if not xmrig:
        raise RuntimeError("Could not find xmrig binary after extraction.")
    xmrig.chmod(0o755)
    return xmrig
