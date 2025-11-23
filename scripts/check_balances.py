import argparse
import json
import sys
import ssl
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen


GAS_SYMBOL = "GAS"


def load_env(path):
    env = {}
    if not path.exists():
        raise SystemExit(".env not found. Run scripts/generate_wallets.py first.")
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def rpc_call(rpc_url, method, params):
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }).encode()
    req = Request(rpc_url, data=payload, headers={"Content-Type": "application/json"})
    # Build SSL context using certifi if available
    try:
        import certifi  # type: ignore
        context = ssl.create_default_context(cafile=certifi.where())
    except Exception:
        context = ssl.create_default_context()
    with urlopen(req, context=context) as resp:
        data = resp.read()
    return json.loads(data)


def extract_balances(res):
    r = res.get("result", {})
    return r.get("balances") or r.get("balance") or []

def get_gas_balance(rpc_url, address):
    res = rpc_call(rpc_url, "getnep17balances", [address])
    if "error" in res:
        raise RuntimeError(res["error"])
    balances = extract_balances(res)
    for b in balances:
        symbol = b.get("symbol") or ""
        if symbol.upper() == GAS_SYMBOL:
            amount_raw = int(b.get("amount", "0"))
            decimals = int(b.get("decimals", 8))
            return amount_raw / (10 ** decimals)
    return 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--addr", dest="addr", help="Check a single N3 address")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--rpc", dest="rpc", help="Override RPC URL")
    parser.add_argument("--min-gas", dest="min_gas", type=float, help="Minimum GAS threshold for OK status")
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    env = load_env(project_root / ".env")
    rpc = (args.rpc or env.get("NEO_TESTNET_RPC") or "").strip().strip("`")
    if rpc:
        parsed = urlparse(rpc)
        path_stripped = parsed.path.strip("/")
        netloc = parsed.netloc
        scheme = parsed.scheme or "https"
        if path_stripped == "443" and ":443" not in netloc:
            netloc = f"{netloc}:443"
            parsed = parsed._replace(netloc=netloc, path="/")
        # Ensure trailing slash
        if not parsed.path:
            parsed = parsed._replace(path="/")
        rpc = urlunparse(parsed)
    if not rpc:
        raise SystemExit("Set NEO_TESTNET_RPC in .env (TestNet JSON-RPC endpoint)")
    print(f"RPC: {rpc}")
    min_gas = args.min_gas if args.min_gas is not None else float(env.get("MIN_GAS_REQUIRED", 30))
    print(f"Threshold: {min_gas} GAS")

    if args.addr:
        try:
            res = rpc_call(rpc, "getnep17balances", [args.addr])
            if "error" in res:
                raise RuntimeError(res["error"])
            balances = extract_balances(res)
            gas = next((b for b in balances if (b.get("symbol") or "").upper() == GAS_SYMBOL), None)
            gas_amt = 0.0
            if gas:
                gas_amt = int(gas.get("amount", "0")) / (10 ** int(gas.get("decimals", 8)))
            status = "OK" if gas_amt >= min_gas else "LOW"
            print(f"[ADDR] {args.addr} -> GAS: {gas_amt:.2f} ({status})")
            if args.verbose:
                for b in balances:
                    amt = int(b.get("amount", "0")) / (10 ** int(b.get("decimals", 8)))
                    sym = b.get("symbol") or ""
                    print(f"  {sym} {b.get('assethash')} = {amt}")
        except Exception as e:
            print(f"[ADDR] {args.addr} -> ERROR: {e}")
            sys.exit(1)
        return

    addresses = {
        "DEPLOYER": env.get("DEPLOYER_ADDR"),
        "AGENT": env.get("AGENT_ADDR"),
        "CLIENT": env.get("CLIENT_ADDR"),
        "WORKER": env.get("WORKER_ADDR"),
        "TREASURY": env.get("TREASURY_ADDR"),
    }

    missing = [k for k, v in addresses.items() if not v]
    if missing:
        raise SystemExit(f"Missing addresses in .env: {', '.join(missing)}")

    all_ok = True
    for role, addr in addresses.items():
        try:
            res = rpc_call(rpc, "getnep17balances", [addr])
            if "error" in res:
                raise RuntimeError(res["error"])
            balances = extract_balances(res)
            gas = next((b for b in balances if (b.get("symbol") or "").upper() == GAS_SYMBOL), None)
            gas_amt = 0.0
            if gas:
                gas_amt = int(gas.get("amount", "0")) / (10 ** int(gas.get("decimals", 8)))
        except Exception as e:
            print(f"[{role}] {addr} -> ERROR: {e}")
            all_ok = False
            continue
        status = "OK" if gas_amt >= min_gas else "LOW"
        print(f"[{role}] {addr} -> GAS: {gas_amt:.2f} ({status})")
        if args.verbose:
            for b in balances:
                amt = int(b.get("amount", "0")) / (10 ** int(b.get("decimals", 8)))
                sym = b.get("symbol") or ""
                print(f"  {sym} {b.get('assethash')} = {amt}")
        all_ok &= gas_amt >= min_gas

    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()