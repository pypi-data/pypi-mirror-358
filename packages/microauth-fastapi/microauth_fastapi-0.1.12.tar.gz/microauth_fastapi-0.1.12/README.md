# FastAPI MicroAuth Integration

This repository provides a minimal FastAPI library to verify JWT tokens issued by a MicroAuth tenant. It only requires your tenant domain to construct the JWKS URI and fetch public keys for token verification.

## Features

 - Token Verification: Automatically fetches and caches public keys from your MicroAuth tenant's JWKS endpoint. 
 - Minimal Configuration: Only the tenant domain is required—no client secrets or credentials.

## Installation

```bash
pip install fastapi-microauth
```

## Usage

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi_microauth import MicroAuthVerifier

app = FastAPI()
# Provide only your tenant domain (e.g., "tenant.microauth.com")
verifier = MicroAuthVerifier(tenant_domain='your-tenant-domain')

@app.get('/protected')
def protected_route(user=Depends(verifier.get_current_user)):
    return {'message': f'Hello, {user.name}!'}
```

## Configuration

- TENANT_DOMAIN: Your MicroAuth tenant domain used to build the JWKS URI: https://{TENANT_DOMAIN}/.well-known/jwks.json.

## Caching & Timeouts

 - The library caches JWKS keys in memory and refreshes periodically. 
 - Optional parameters for cache duration and HTTP timeouts can be added in future releases.

## License

MIT © MicroAuth