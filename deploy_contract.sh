#!/bin/bash
# Deploy the upgraded smart contract with location support

echo "🚀 Deploying GigSmartPay Vault Contract (with GPS Location)"
echo "============================================================"
echo ""
echo "⚠️  IMPORTANT: This will deploy a NEW contract on Neo N3 Testnet"
echo "   The old contract will remain but won't be used."
echo ""
echo "📋 Pre-deployment checklist:"
echo "   ✅ Contract compiled (gigshield_vault.nef exists)"
echo "   ✅ New params: latitude, longitude"
echo "   ❓ Do you have testnet GAS for deployment (~10-20 GAS)?"
echo ""

read -p "Continue with deployment? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

echo ""
echo "🔧 Activating Python environment..."
source .venv/bin/activate

echo "🚀 Running deployment script..."
python3 scripts/deploy_contract.py

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Verify deployment on NeoTube (link provided above)"
echo "   2. Update CONTRACT_HASH in .env (should be auto-updated)"
echo "   3. Restart your backend: kill backend, then 'python3 backend/api.py'"
echo "   4. Test job creation with location data"
echo ""
