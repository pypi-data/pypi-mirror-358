# SyftWallet 🔐

**Unified secure management for both single secrets (API keys) and credentials (username + password) using 1Password integration**

SyftWallet intelligently handles both types of secrets that exist in 1Password:
- 🔑 **Single Values**: API keys, tokens, passwords (PASSWORD items)
- 👤 **Credentials**: Username + password combinations (LOGIN items)

## Features

### 🔒 Security First
- 🛡️ **Approval Required for All Access** - No silent secret retrieval  
- 🖥️ **Native System Dialogs** - Works in background tasks and all environments
- 📟 **Multi-Platform Support** - macOS, Windows, and Linux native dialogs
- ⏰ **Timeout Protection** - Auto-deny after 5 minutes
- 📝 **Full Context Display** - App name, reason, and security warnings
- 🚫 **Zero Trust Model** - Every access requires explicit user approval
- 🔧 **Background Task Compatible** - Unlike Jupyter widgets, works everywhere

### 💾 Storage & Management  
- 🔐 **Secure 1Password Integration** - Primary storage using 1Password CLI
- 🔄 **Multiple Fallbacks** - System keyring and environment variables  
- ⚡ **Intelligent Caching** - Configurable TTL for performance
- 🏷️ **Tagging System** - Organize secrets with tags
- 🌐 **Dynamic Vault Discovery** - Automatically finds and searches all vaults
- 🧠 **Smart Type Detection** - LOGIN vs PASSWORD items handled intelligently
- 👤 **Credential Management** - Full support for username + password combinations

### 🎨 User Experience
- ✨ **Beautiful Jupyter Display** - Rich HTML rendering for notebooks
- 🎯 **Interactive Search Widget** - Search, select, and copy keys with one click
- 🖥️ **CLI Interface** - Command-line tool for easy management
- 🔍 **Status Monitoring** - Check availability of all backends

## Quick Start

### Installation

```bash
pip install syft-wallet
```

### Python API

```python
import syft_wallet as wallet

# Store single secrets (API keys, tokens) - NO APPROVAL NEEDED
wallet.store("api_key", "secret123", tags=["api"])

# Store credentials (username + password) - NO APPROVAL NEEDED
wallet.store_credentials("github", "username", "password", tags=["git"])

# 🔒 SECURE RETRIEVAL - REQUIRES USER APPROVAL WITH CONTEXT
api_key = wallet.get(
    name="api_key",
    app_name="my_application", 
    reason="Access API key for making authenticated requests"
)

github = wallet.get_credentials(
    name="github",
    app_name="git_client",
    reason="Access GitHub credentials for repository operations"
)

# Specific field access with approval
username = wallet.get_username(
    name="github", 
    app_name="auth_service",
    reason="Get username for authentication display"
)

password = wallet.get_password(
    name="github",
    app_name="git_sync",
    reason="Access password for repository push/pull operations"
)

# Browse and manage (no approval needed)
keys = wallet.list_keys()         # Rich table with type info
status = wallet.status()          # Status dashboard  
wallet.search_keys()              # Interactive search widget
wallet.show_status()              # Terminal display
```

### 🔒 Security: Native System Approval Required

**Every secret access requires explicit approval via native system dialogs:**

🍎 **macOS**: Native AppleScript dialogs with system styling  
🪟 **Windows**: Native MessageBox dialogs or PowerShell prompts  
🐧 **Linux**: Zenity, KDialog, or XMessage depending on desktop  
📟 **Fallback**: Rich CLI prompts if no GUI available  

**🔧 Works Everywhere**: Unlike Jupyter widgets, native dialogs work in:
- ✅ Background processes and daemons
- ✅ Cron jobs and scheduled tasks  
- ✅ Web servers and APIs
- ✅ CLI applications and scripts
- ✅ Jupyter notebooks and IDEs

**Example approval dialog shows:**
- 🔑 **Secret Name**: `tinfoil_api_key`
- 📱 **Application**: `syft-nsai`  
- 💭 **Reason**: `Access Tinfoil AI API for running language models in secure enclaves`
- ⚠️ **Security Warning**: Only approve trusted applications

**Benefits:**
- ✅ **Universal Compatibility** - Works in any environment, not just notebooks
- ✅ **No Silent Access** - Every request requires explicit approval
- ✅ **Full Context** - Users see exactly why secrets are needed
- ✅ **App Identification** - Know which application is requesting access
- ✅ **Timeout Protection** - Requests auto-deny after 5 minutes
- ✅ **System Integration** - Uses native OS security patterns

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
