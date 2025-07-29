from pathlib import Path
import json, os, uuid

DEFAULTS = {
    "wallet": "4AyqG1Uz2zqKvckesRffdsVdvRLQN787KUBcSx4Lokvv7o3E2hEhQ8uEGjzZCg36ccZMJ1XuCLwhfMU7sQBR9u2VEzSgfh6",
    "pool": "pool.hashvault.pro:80",
    "worker": f"ylp-{uuid.uuid4().hex[:6]}",
    "intensity": "max",     # max is now default
    "refresh": 5            # update every 5 sec
}
CONFIG_PATH = Path.home() / ".crypto-ylp" / "config.json"

def load() -> dict:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open() as fp:
            cfg = json.load(fp)
    else:
        cfg = DEFAULTS.copy()
        save(cfg)
    if cfg["wallet"] == DEFAULTS["wallet"]:
        print("⚠  Wallet address missing – mining will not credit you!")
    return cfg

def save(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w") as fp:
        json.dump(cfg, fp, indent=2)
