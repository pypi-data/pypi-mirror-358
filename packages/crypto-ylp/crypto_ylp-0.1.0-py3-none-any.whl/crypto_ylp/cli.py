import argparse
from .miner import run
from .config import load, save

def main():
    parser = argparse.ArgumentParser(
        prog="crypto-ylp",
        description="Simple XMR miner wrapper written in Python."
    )
    parser.add_argument("-w", "--wallet", help="Monero wallet address")
    parser.add_argument("-p", "--pool", help="Pool URL:port")
    parser.add_argument("-i", "--intensity", choices=["low", "high", "max"], help="CPU usage mode")
    args = parser.parse_args()

    cfg = load()
    for k in ("wallet", "pool", "intensity"):
        v = getattr(args, k)
        if v:
            cfg[k] = v
    save(cfg)
    run()
