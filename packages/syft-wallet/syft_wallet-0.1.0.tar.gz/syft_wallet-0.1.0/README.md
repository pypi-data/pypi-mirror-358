# SyftWallet 🔐

**Unified secure management for both single secrets (API keys) and credentials (username + password) using 1Password integration**

SyftWallet intelligently handles both types of secrets that exist in 1Password:
- 🔑 **Single Values**: API keys, tokens, passwords (PASSWORD items)
- 👤 **Credentials**: Username + password combinations (LOGIN items)

## Features

- 🔐 **Secure 1Password Integration** - Primary storage using 1Password CLI
- 🔄 **Multiple Fallbacks** - System keyring and environment variables  
- ⚡ **Intelligent Caching** - Configurable TTL for performance
- 🏷️ **Tagging System** - Organize secrets with tags
- 🖥️ **CLI Interface** - Command-line tool for easy management
- 🔍 **Status Monitoring** - Check availability of all backends
- ✨ **Beautiful Jupyter Display** - Rich HTML rendering for notebooks
- 🎯 **Interactive Search Widget** - Search, select, and copy keys with one click
- 🌐 **Dynamic Vault Discovery** - Automatically finds and searches all vaults
- 🧠 **Smart Type Detection** - LOGIN vs PASSWORD items handled intelligently
- 👤 **Credential Management** - Full support for username + password combinations

## Quick Start

### Installation

```bash
pip install syft-wallet
```

### Python API

```python
import syft_wallet as wallet

# Store single secrets (API keys, tokens)
wallet.store("api_key", "secret123", tags=["api"])

# Store credentials (username + password)
wallet.store_credentials("github", "username", "password", tags=["git"])

# Smart retrieval (auto-detects type)
api_key = wallet.get("api_key")          # Returns string
github = wallet.get("github")            # Returns {"username": "...", "password": "..."}

# Specific field access
username = wallet.get_username("github")
password = wallet.get_password("github")
both = wallet.get_credentials("github")

# Beautiful Jupyter displays
keys = wallet.list_keys()         # Rich table with type info
status = wallet.status()          # Status dashboard
wallet.search_keys()              # Interactive search widget

# Terminal display
wallet.show_status()
```

### CLI Usage

```bash
# Store a single secret
syft-wallet set api_key "secret123" --tags api

# Store credentials (interactive)
syft-wallet set-credentials github --username myuser --password mypass

# Retrieve secrets
syft-wallet get api_key
syft-wallet get-credentials github

# Show status with vault info
syft-wallet status
```

## Integration with SyftBox

Works seamlessly with other SyftBox packages:

```python
import syft_wallet as wallet
import syft_nsai as nsai

# Store your API key securely
wallet.store("tinfoil_api_key", "tk_your_key_here")

# syft-nsai will automatically retrieve it
# No hardcoded keys needed!
```

## License

Apache 2.0 - See LICENSE file for details.
