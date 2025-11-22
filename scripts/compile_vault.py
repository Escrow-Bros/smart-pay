from pathlib import Path
from boa3.boa3 import Boa3

def main():
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "out"
    out_dir.mkdir(exist_ok=True)

    # compile vault
    src = root / "contracts" / "gigshield_vault.py"
    out_file = out_dir / "gigshield_vault.nef"
    Boa3.compile_and_save(str(src), output_path=str(out_file))
    print(f"Compiled vault -> {out_file}")

if __name__ == "__main__":
    main()
