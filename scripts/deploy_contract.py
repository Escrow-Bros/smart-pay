import asyncio
import json
import sys
import ssl
import os
from pathlib import Path
from neo3.wallet.account import Account
from neo3.api.wrappers import ChainFacade, GenericContract
from neo3.api.helpers.signing import sign_with_account
from neo3.network.payloads.verification import Signer
from neo3.core import types
from neo3.api import noderpc

def create_testnet_ssl_context():
    """Create SSL context for testnet with optional verification bypass"""
    # Check if we're explicitly in testnet environment
    env_mode = os.getenv('NETWORK_MODE', 'testnet').lower()
    allow_insecure = os.getenv('TESTNET_ALLOW_INSECURE', 'false').lower() == 'true'
    
    # Fail-safe: refuse to disable SSL in production
    if env_mode == 'production':
        print("ERROR: Cannot disable SSL verification in production mode")
        print("   Set NETWORK_MODE=testnet if you need insecure SSL for testing")
        sys.exit(1)
    
    if allow_insecure and env_mode == 'testnet':
        print("WARNING: SSL verification disabled for testnet (TESTNET_ALLOW_INSECURE=true)")
        print("   This should NEVER be used in production environments")
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    else:
        # Use default SSL verification
        return ssl.create_default_context()


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
    
    # Create SSL context for testnet (scoped, not global)
    ssl_context = create_testnet_ssl_context()
    print(f"🔒 SSL Context: {ssl_context.check_hostname=}, {ssl_context.verify_mode=}")
    
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
                
                # Look for Deploy notification
                for notif in app_log.execution.notifications:
                    if notif.event_name == 'Deploy':
                        # Contract hash is in the first value of the notification state
                        contract_hash = types.UInt160(notif.state.value[0].value)
                        
                        print(f"\n✅ Contract deployed successfully!")
                        print(f"   Contract Hash: 0x{contract_hash}")
                        print(f"   Gas Consumed: {app_log.execution.gas_consumed / 100_000_000:.8f} GAS")
                        
                        # Update .env with new contract hash
                        env_path = root / ".env"
                        env_lines = env_path.read_text().splitlines()
                        
                        # Remove old contract hash lines
                        new_lines = []
                        skip_next = False
                        for line in env_lines:
                            if "VAULT_CONTRACT_HASH" in line:
                                skip_next = True
                                continue
                            if skip_next and (line.startswith("#") or not line.strip()):
                                continue
                            skip_next = False
                            new_lines.append(line)
                        
                        # Add new contract hash
                        new_lines.append("")
                        new_lines.append("# Contract Deployment")
                        new_lines.append(f"# TX: 0x{tx_hash}")
                        new_lines.append(f"VAULT_CONTRACT_HASH=0x{contract_hash}")
                        
                        env_path.write_text("\n".join(new_lines) + "\n")
                        
                        print(f"\n📝 Contract hash saved to .env")
                        print(f"\n🔍 View: https://testnet.neotube.io/contract/{contract_hash}")
                        return
                
                # If we get here, no Deploy notification was found
                print(f"⚠️  No Deploy notification found in transaction")
            
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
