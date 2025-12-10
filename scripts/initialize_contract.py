import asyncio
import sys
from pathlib import Path
from neo3.wallet.account import Account
from neo3.api.wrappers import ChainFacade, GenericContract
from neo3.api.helpers.signing import sign_with_account
from neo3.network.payloads.verification import Signer
from neo3.core import types
from neo3.wallet import utils as wallet_utils

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from utils.ssl_helpers import create_testnet_ssl_context


async def main():
    root = Path(__file__).resolve().parents[1]
    
    # Load environment variables
    env = {}
    for line in (root / ".env").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    
    rpc = env.get("NEO_TESTNET_RPC")
    deployer_wif = env.get("DEPLOYER_WIF")
    deployer_addr = env.get("DEPLOYER_ADDR")
    agent_addr = env.get("AGENT_ADDR")
    treasury_addr = env.get("TREASURY_ADDR")
    contract_hash_str = env.get("VAULT_CONTRACT_HASH")
    
    if not all([rpc, deployer_wif, deployer_addr, agent_addr, treasury_addr, contract_hash_str]):
        print("❌ Missing required environment variables in .env")
        print("   Required: NEO_TESTNET_RPC, DEPLOYER_WIF, DEPLOYER_ADDR,")
        print("            AGENT_ADDR, TREASURY_ADDR, VAULT_CONTRACT_HASH")
        sys.exit(1)
    
    # Create SSL context for testnet (scoped, not global)
    ssl_context = create_testnet_ssl_context()
    print(f"🔒 SSL Context: verify_mode={ssl_context.verify_mode}")
    
    # Load deployer account
    deployer = Account.from_wif(deployer_wif)
    print(f"🔑 Deployer: {deployer.address}")
    
    # Parse contract hash
    contract_hash = types.UInt160.from_string(contract_hash_str.replace("0x", ""))
    vault = GenericContract(contract_hash)
    
    # Convert Neo addresses to script hashes
    deployer_script_hash = wallet_utils.address_to_script_hash(deployer_addr)
    agent_script_hash = wallet_utils.address_to_script_hash(agent_addr)
    treasury_script_hash = wallet_utils.address_to_script_hash(treasury_addr)
    
    print(f"📝 Contract: {contract_hash}")
    print(f"\n🎯 Initialization Plan:")
    print(f"   1. set_owner({deployer_addr})")
    print(f"   2. set_agent({agent_addr})")
    print(f"   3. set_treasury({treasury_addr})")
    print(f"   4. set_arbiter({agent_addr})  # Use agent as arbiter")
    print("   5. set_fee_bps(500)  # 5% fee")
    print()
    
    # Setup ChainFacade
    facade = ChainFacade(rpc, receipt_timeout=30.0)
    facade.add_signer(
        sign_with_account(deployer),
        Signer(deployer.script_hash)
    )
    
    try:
        # Step 1: Set Owner
        print("1️⃣  Setting owner...")
        tx1 = await facade.invoke_fast(
            vault.call_function("set_owner", [deployer_script_hash])
        )
        print(f"   ✅ Transaction sent: {tx1}")
        print("   ⏳ Waiting for confirmation...")
        await asyncio.sleep(20)
        
        # Step 2: Set Agent
        print("\n2️⃣  Setting agent...")
        tx2 = await facade.invoke_fast(
            vault.call_function("set_agent", [agent_script_hash])
        )
        print(f"   ✅ Transaction sent: {tx2}")
        print("   ⏳ Waiting for confirmation...")
        await asyncio.sleep(20)
        
        # Step 3: Set Treasury
        print("\n3️⃣  Setting treasury...")
        tx3 = await facade.invoke_fast(
            vault.call_function("set_treasury", [treasury_script_hash])
        )
        print(f"   ✅ Transaction sent: {tx3}")
        print("   ⏳ Waiting for confirmation...")
        await asyncio.sleep(20)
        
        # Step 4: Set Arbiter (use same agent address for MVP)
        print("\n4️⃣  Setting arbiter...")
        tx4 = await facade.invoke_fast(
            vault.call_function("set_arbiter", [agent_script_hash])
        )
        print(f"   ✅ Transaction sent: {tx4}")
        print("   ⏳ Waiting for confirmation...")
        await asyncio.sleep(20)
        
        # Step 5: Set Fee (500 basis points = 5%)
        print("\n5️⃣  Setting fee to 5%...")
        tx5 = await facade.invoke_fast(
            vault.call_function("set_fee_bps", [500])
        )
        print(f"   ✅ Transaction sent: {tx5}")
        print("   ⏳ Waiting for confirmation...")
        await asyncio.sleep(20)
        
        print("\n🎉 Contract initialization complete!")
        print("\n📋 Contract State:")
        print(f"   Owner: {deployer_addr}")
        print(f"   Agent: {agent_addr}")
        print(f"   Treasury: {treasury_addr}")
        print(f"   Arbiter: {agent_addr}  (same as agent)")
        print("   Fee: 5% (500 bps)")
        print("\n✅ Ready to create jobs and resolve disputes!")
        print(f"🔍 View on Dora: https://testnet.neotube.io/contract/{contract_hash}")
        
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
