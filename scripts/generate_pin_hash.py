import hashlib
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/generate_pin_hash.py <PIN>", file=sys.stderr)
        return 1

    pin = sys.argv[1]
    print(hashlib.sha256(pin.encode("utf-8")).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
