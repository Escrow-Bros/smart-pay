# Services Module

Infrastructure services for GigShield platform.

## 📦 Services

### `storage.py` (TASK-012)
IPFS upload handler via 4Everland.

**Usage:**
```python
from services.storage import upload_to_ipfs

url = upload_to_ipfs(image_bytes, "proof.jpg")
```

### `api_server.py`
Flask API server for agent endpoints.

### `config.py`
Configuration utilities and helpers.

## ⚙️ Configuration

All services use environment variables from `.env`:

```env
# 4Everland IPFS
EVERLAND_BUCKET_NAME=your-bucket
EVERLAND_ACCESS_KEY=your-key
EVERLAND_SECRET_KEY=your-secret
EVERLAND_ENDPOINT=https://endpoint.4everland.co
```

## 🎯 Design Principle

**Services** are infrastructure components that:
- ❌ Don't use LLMs or make AI decisions
- ✅ Provide utility functions
- ✅ Handle external integrations (IPFS, APIs, etc.)
- ✅ Are reusable across the platform

**Agents** are AI components that:
- ✅ Use LLMs for reasoning and decisions
- ✅ Powered by SpoonOS
- ✅ Make intelligent choices
- ✅ Located in `/agent` folder

## 📚 Documentation

See `/docs/STORAGE_MODULE.md` for detailed storage documentation.

