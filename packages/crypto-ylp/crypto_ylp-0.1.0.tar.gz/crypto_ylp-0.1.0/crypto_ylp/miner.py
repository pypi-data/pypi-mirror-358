import asyncio, re, os
from .downloader import ensure_xmrig

HASHRATE_RE = re.compile(r"speed\s+(\d+\.\d+)\sH/s")

DEFAULT_WALLET = "48dEohL5G62qvvRtrG8aHUFVjNMP5ZKWcWQXR1m29os1iGo7Zq4ZUEJXgByXZLM2ZAcxJeE78QvUExKTX3eYKm4fQZEuUbH"
DEFAULT_POOL   = "gulf.moneroocean.stream:10128"

INTENSITY_PRESETS = {
    "low": {
        "threads": "auto", "map": "1/3", "extra": []
    },
    "high": {
        "threads": "auto", "map": "3/4", "extra": []
    },
    "max": {
        "threads": "auto",
        "map": "4/4",
        "extra": [
            "--huge-pages",
            "--randomx-mode=fast",
            "--randomx-init=4",
            "--cpu-priority", "5",
            "--asm=auto",
            "--randomx-1gb-pages"
        ]
    }
}

async def _stream_hashrate(proc, refresh: int, silent: bool):
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        line = line.decode(errors="ignore")
        if silent and not "speed" in line:
            continue
        match = HASHRATE_RE.search(line)
        if match:
            hashrate = float(match.group(1))
            print(f"\r🔄  Hashrate: {hashrate:.2f} H/s", end="", flush=True)
        await asyncio.sleep(refresh)

async def _spawn(wallet, pool, worker, intensity, refresh, silent):
    xmrig_bin = ensure_xmrig()
    preset = INTENSITY_PRESETS[intensity]

    args = [
        str(xmrig_bin),
        "-o", pool,
        "-u", wallet,
        "-k",
        "-a", "rx/0",
        "--threads", preset["threads"],
        "--cpu-affinity", preset["map"],
        "-p", worker,
        *preset["extra"]
    ]

    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=os.environ.copy(),
    )
    await _stream_hashrate(proc, refresh, silent)

def run(wallet_address=None, intensity="max", silent=False, pool=None, worker=None, refresh=5):
    wallet = wallet_address or DEFAULT_WALLET
    worker = worker or "ylp-py"
    pool = pool or DEFAULT_POOL

    print(f"crypto-ylp started | wallet: {wallet[:8]}… | mode: {intensity} | silent: {silent}")
    try:
        asyncio.run(_spawn(wallet, pool, worker, intensity, refresh, silent))
    except KeyboardInterrupt:
        print("\n👋  Exiting gracefully …")
