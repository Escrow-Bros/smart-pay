from pathlib import Path
from neo3.wallet.account import Account

ROLES = ["DEPLOYER", "AGENT", "CLIENT", "WORKER", "TREASURY"]

def main():
    project_root = Path(__file__).resolve().parents[1]
    env_path = project_root / ".env"

    lines = []
    for role in ROLES:
        acct = Account.create_new()
        addr = acct.address
        if acct.private_key is None:
            raise SystemExit("Unexpected watch-only account; no private key generated")
        wif = Account.private_key_to_wif(acct.private_key)
        lines.append(f"{role}_WIF={wif}")
        lines.append(f"{role}_ADDR={addr}")
        lines.append("")

    with open(env_path, "a") as f:
        f.write("\n")
        f.write("\n".join(lines))
        f.write("\n")

    print("Appended 5 Neo N3 TestNet wallets to .env")
    print("Addresses:")
    for i in range(0, len(lines), 3):
        addr_line = lines[i+1]
        print(f"- {addr_line.split('=')[1]}")
    print(f"\nSaved: {env_path}")

if __name__ == "__main__":
    main()