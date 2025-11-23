import asyncio
import json
import sys
from pathlib import Path
from neo3.wallet.account import Account
from neo3.api.wrappers import ChainFacade, GenericContract
from neo3.api.helpers.signing import sign_with_account
from neo3.network.payloads.verification import Signer
from neo3.core import types
from neo3.api import noderpc


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
    
    if not rpc or not deployer_wif:
        print("❌ Missing NEO_TESTNET_RPC or DEPLOYER_WIF in .env")
        sys.exit(1)
    
    # Load deployer account
    deployer = Account.from_wif(deployer_wif)
    print(f"🔑 Deployer: {deployer.address}")
    
    # Load compiled contract files
    nef_path = root / "out" / "gigshield_vault.nef"
    manifest_path = root / "out" / "gigshield_vault.manifest.json"
    
    if not nef_path.exists() or not manifest_path.exists():
        print("❌ Contract files not found. Run compile_vault.py first.")
        sys.exit(1)
    
    # Read NEF as bytes
    with open(nef_path, "rb") as f:
        nef_bytes = f.read()
    
    # Read manifest as minified JSON string
    with open(manifest_path, "r") as f:
        manifest_data = json.load(f)
        manifest_json = json.dumps(manifest_data, separators=(',', ':'))
    
    print(f"📄 NEF size: {len(nef_bytes)} bytes")
    print(f"📄 Manifest size: {len(manifest_json)} bytes")
    
    print(f"\n🚀 Deploying contract to {rpc}...")
    print(f"   Contract: gigshield_vault")
    print(f"   Deployer: {deployer.address}")
    
    try:
        # ContractManagement native contract
        contract_mgmt_hash = types.UInt160.from_string("fffdc93764dbaddd97c48f252a53ea4643faa3fd")
        contract_mgmt = GenericContract(contract_mgmt_hash)
        
        # Setup ChainFacade with signer
        facade = ChainFacade(rpc, receipt_timeout=30.0)
        facade.add_signer(
            sign_with_account(deployer),
            Signer(deployer.script_hash)
        )
        
        print("📡 Sending deployment transaction...")
        
        # Use invoke_fast to send transaction without waiting for receipt
        tx_hash = await facade.invoke_fast(
            contract_mgmt.call_function("deploy", [nef_bytes, manifest_json])
        )
        
        print(f"\n✅ Deployment transaction sent!")
        print(f"   TX Hash: {tx_hash}")
        print(f"   Waiting for confirmation (~20 seconds)...")
        
        # Wait for transaction to be included in a block
        await asyncio.sleep(20)
        
        # Extract contract hash from transaction notification
        print("📋 Extracting contract hash from transaction...")
        async with noderpc.NeoRpcClient(rpc) as client:
            try:
                tx_hash_obj = types.UInt256.from_string(str(tx_hash))
                app_log = await client.get_application_log_transaction(tx_hash_obj)
                
                # Look for Deploy notification from ContractManagement
                if app_log and app_log.execution:
                    execution = app_log.execution
                    
                    if execution.state.name == 'HALT':
                        # Find Deploy notification
                        for notif in execution.notifications:
                            if notif.event_name == 'Deploy':
                                # Contract hash is in the notification state
                                state_items = notif.state.value if hasattr(notif.state, 'value') else []
                                if state_items and len(state_items) > 0:
                                    contract_hash_bytes = state_items[0].value
                                    contract_hash = types.UInt160(contract_hash_bytes)
                                    
                                    print(f"\n✅ Contract deployed successfully!")
                                    print(f"   Contract Hash: {contract_hash}")
                                    print(f"   Gas Consumed: {execution.gas_consumed / 100_000_000:.8f} GAS")
                                    
                                    # Save to .env
                                    env_path = root / ".env"
                                    with open(env_path, "a") as f:
                                        f.write(f"\n# Contract Deployment (TASK-006)\n")
                                        f.write(f"# TX: {tx_hash}\n")
                                        f.write(f"VAULT_CONTRACT_HASH={contract_hash}\n")
                                    
                                    print(f"\n📝 Contract hash saved to .env")
                                    print(f"\n🔍 View: https://testnet.neotube.io/contract/{contract_hash}")
                                    return
                    
                    else:
                        print(f"❌ Transaction failed with state: {execution.state.name}")
                        if hasattr(execution, 'exception') and execution.exception:
                            print(f"   Exception: {execution.exception}")
            
            except Exception as e:
                print(f"⚠️  Could not automatically extract contract hash: {e}")
        
        print(f"\n📋 Manual verification required:")
        print(f"   1. Check transaction:")
        print(f"      https://testnet.neotube.io/transaction/{tx_hash}")
        print(f"   2. Look for 'Deploy' notification")
        print(f"   3. Copy contract hash and add to .env:")
        print(f"      VAULT_CONTRACT_HASH=<hash>")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
