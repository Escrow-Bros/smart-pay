import asyncio
import sys
from pathlib import Path
from neo3.api.wrappers import ChainFacade, GenericContract
from neo3.core import types
from neo3.wallet import utils as wallet_utils


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
    contract_hash_str = env.get("VAULT_CONTRACT_HASH")
    
    if not rpc or not contract_hash_str:
        print("❌ Missing NEO_TESTNET_RPC or VAULT_CONTRACT_HASH in .env")
        sys.exit(1)
    
    # Parse contract hash
    contract_hash = types.UInt160.from_string(contract_hash_str.replace("0x", ""))
    vault = GenericContract(contract_hash)
    
    print(f"🔍 Verifying Contract State")
    print(f"📝 Contract: {contract_hash}")
    print(f"🌐 Explorer: https://testnet.neotube.io/contract/{contract_hash}")
    print()
    
    # Setup ChainFacade (no signer needed for read-only calls)
    facade = ChainFacade(rpc)
    
    try:
        print("📊 Reading contract state...")
        print()
        
        # Get owner
        owner_receipt = await facade.test_invoke(vault.call_function("get_owner", []))
        if owner_receipt.result and owner_receipt.result.stack:
            owner_hash = types.UInt160(owner_receipt.result.stack[0].value)
            owner_addr = wallet_utils.script_hash_to_address(owner_hash)
            expected_owner = env.get("DEPLOYER_ADDR", "")
            status = "✅" if owner_addr == expected_owner else "⚠️"
            print(f"Owner:     {status} {owner_addr}")
            if owner_addr != expected_owner:
                print(f"           Expected: {expected_owner}")
        else:
            print(f"Owner:     ❌ Not set (empty address)")
        
        # Get agent
        agent_receipt = await facade.test_invoke(vault.call_function("get_agent_addr", []))
        if agent_receipt.result and agent_receipt.result.stack:
            agent_hash = types.UInt160(agent_receipt.result.stack[0].value)
            agent_addr = wallet_utils.script_hash_to_address(agent_hash)
            expected_agent = env.get("AGENT_ADDR", "")
            status = "✅" if agent_addr == expected_agent else "⚠️"
            print(f"Agent:     {status} {agent_addr}")
            if agent_addr != expected_agent:
                print(f"           Expected: {expected_agent}")
        else:
            print(f"Agent:     ❌ Not set (empty address)")
        
        # Get treasury
        treasury_receipt = await facade.test_invoke(vault.call_function("get_treasury_addr", []))
        if treasury_receipt.result and treasury_receipt.result.stack:
            treasury_hash = types.UInt160(treasury_receipt.result.stack[0].value)
            treasury_addr = wallet_utils.script_hash_to_address(treasury_hash)
            expected_treasury = env.get("TREASURY_ADDR", "")
            status = "✅" if treasury_addr == expected_treasury else "⚠️"
            print(f"Treasury:  {status} {treasury_addr}")
            if treasury_addr != expected_treasury:
                print(f"           Expected: {expected_treasury}")
        else:
            print(f"Treasury:  ❌ Not set (empty address)")
        
        # Get fee
        fee_receipt = await facade.test_invoke(vault.call_function("get_fee_bps", []))
        if fee_receipt.result and fee_receipt.result.stack:
            fee_bps = int(fee_receipt.result.stack[0].value)
            fee_percent = fee_bps / 100
            status = "✅" if fee_bps == 500 else "⚠️"
            print(f"Fee:       {status} {fee_bps} bps ({fee_percent}%)")
            if fee_bps != 500:
                print(f"           Expected: 500 bps (5%)")
        else:
            print(f"Fee:       ❌ Not set")
        
        print()
        
        # Summary
        all_set = all([
            owner_receipt.result and owner_receipt.result.stack,
            agent_receipt.result and agent_receipt.result.stack,
            treasury_receipt.result and treasury_receipt.result.stack,
            fee_receipt.result and fee_receipt.result.stack
        ])
        if all_set:
            print("🎉 Contract is fully initialized and ready!")
            print()
            print("📋 Next Steps:")
            print("   - Create a test job using create_job()")
            print("   - Worker can assign themselves using assign_worker()")
            print("   - Agent can release funds using release_funds()")
        else:
            print("⚠️  Contract is not fully initialized")
            print("   Run: python scripts/initialize_contract.py")
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
