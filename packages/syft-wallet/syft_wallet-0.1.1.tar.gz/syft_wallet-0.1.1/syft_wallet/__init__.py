"""
SyftWallet - Secure key and secret management for SyftBox using 1Password integration

This package provides secure storage and retrieval of API keys, tokens, and other
sensitive information using 1Password as the backend. It includes fallback mechanisms
and integrates seamlessly with the SyftBox ecosystem.

Example usage:
    import syft_wallet as wallet
    
    # Store a key
    wallet.store("tinfoil_api_key", "tk_your_api_key_here", tags=["ai", "api"])
    
    # Retrieve a key
    api_key = wallet.get("tinfoil_api_key")
    
    # Use with environment variable fallback
    api_key = wallet.get("tinfoil_api_key", env_var="TINFOIL_API_KEY")
    
    # List all stored keys
    keys = wallet.list_keys()
"""

__version__ = "0.1.1"

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import keyring
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table

# Jupyter display support
try:
    from IPython.display import HTML, display, clear_output
    HAS_IPYTHON = True
except ImportError:
    HAS_IPYTHON = False

try:
    import ipywidgets as widgets
    HAS_WIDGETS = True
except ImportError:
    HAS_WIDGETS = False

# Load environment variables
load_dotenv()

console = Console()


class AccessRequest:
    """Represents a request to access a secret"""
    
    def __init__(self, key_name: str, app_name: str, reason: str, requested_at: float = None):
        self.key_name = key_name
        self.app_name = app_name
        self.reason = reason
        self.requested_at = requested_at or time.time()


class ApprovalManager:
    """Manages approval requests for secret access using native OS dialogs"""
    
    def __init__(self):
        self.approval_timeout = 300  # 5 minutes
        
    def request_approval(self, key_name: str, app_name: str, reason: str) -> bool:
        """
        Request approval for accessing a secret using native system dialogs.
        Works even in background tasks and processes.
        
        Args:
            key_name: Name of the secret being requested
            app_name: Name of the application requesting access
            reason: Reason why the secret is needed
            
        Returns:
            True if approved, False if denied
        """
        request = AccessRequest(key_name, app_name, reason)
        
        # Try native system dialog first - works in background tasks
        try:
            return self._show_native_dialog(request)
        except Exception as e:
            console.print(f"[yellow]Native dialog failed ({e}), falling back to CLI[/yellow]")
            # Fall back to CLI if native dialog fails
            return self._show_cli_approval(request)
    
    def _show_native_dialog(self, request: AccessRequest) -> bool:
        """Show native OS dialog for approval"""
        import platform
        
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            return self._show_macos_dialog(request)
        elif system == "windows":
            return self._show_windows_dialog(request)
        else:  # Linux and others
            return self._show_linux_dialog(request)
    
    def _show_macos_dialog(self, request: AccessRequest) -> bool:
        """Show native macOS dialog using AppleScript"""
        import subprocess
        
        # Create the AppleScript dialog
        script = f'''
        display dialog "🔐 Secret Access Request

Secret: {request.key_name}
Application: {request.app_name}
Reason: {request.reason}

⚠️ SECURITY WARNING:
Only approve if you trust '{request.app_name}' and understand why it needs access to this secret.

Do you want to allow access?" ¬
        buttons {{"Deny", "Approve"}} ¬
        default button "Deny" ¬
        cancel button "Deny" ¬
        with title "SyftWallet Security" ¬
        with icon caution ¬
        giving up after {self.approval_timeout}
        '''
        
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=self.approval_timeout + 10
            )
            
            # If user clicked "Approve" or pressed Enter (default), result will contain "Approve"
            approved = "Approve" in result.stdout
            
            if approved:
                console.print(f"[green]✅ Access to '{request.key_name}' approved for {request.app_name}[/green]")
            else:
                console.print(f"[red]❌ Access to '{request.key_name}' denied for {request.app_name}[/red]")
                
            return approved
            
        except subprocess.TimeoutExpired:
            console.print("[yellow]⏰ Approval request timed out[/yellow]")
            return False
        except subprocess.CalledProcessError:
            # User clicked "Deny" or cancelled
            console.print(f"[red]❌ Access to '{request.key_name}' denied for {request.app_name}[/red]")
            return False
        except Exception as e:
            console.print(f"[yellow]Error showing macOS dialog: {e}[/yellow]")
            raise
    
    def _show_windows_dialog(self, request: AccessRequest) -> bool:
        """Show native Windows dialog"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            import threading
            import queue
            
            # Create response queue
            response_queue = queue.Queue()
            
            def show_dialog():
                try:
                    # Create hidden root window
                    root = tk.Tk()
                    root.withdraw()  # Hide the root window
                    root.attributes('-topmost', True)  # Keep on top
                    
                    # Show the messagebox
                    title = "SyftWallet Security - Secret Access Request"
                    message = f"""🔐 Secret Access Request

Secret: {request.key_name}
Application: {request.app_name}
Reason: {request.reason}

⚠️ SECURITY WARNING:
Only approve if you trust '{request.app_name}' and understand why it needs access to this secret.

Do you want to allow access?"""
                    
                    result = messagebox.askyesno(title, message, icon='warning')
                    response_queue.put(result)
                    root.destroy()
                    
                except Exception as e:
                    response_queue.put(False)
                    console.print(f"[yellow]Error in Windows dialog: {e}[/yellow]")
            
            # Show dialog in separate thread to avoid blocking
            dialog_thread = threading.Thread(target=show_dialog)
            dialog_thread.daemon = True
            dialog_thread.start()
            
            # Wait for response with timeout
            try:
                approved = response_queue.get(timeout=self.approval_timeout)
                
                if approved:
                    console.print(f"[green]✅ Access to '{request.key_name}' approved for {request.app_name}[/green]")
                else:
                    console.print(f"[red]❌ Access to '{request.key_name}' denied for {request.app_name}[/red]")
                    
                return approved
                
            except queue.Empty:
                console.print("[yellow]⏰ Approval request timed out[/yellow]")
                return False
                
        except ImportError:
            # tkinter not available, try PowerShell
            return self._show_windows_powershell_dialog(request)
    
    def _show_windows_powershell_dialog(self, request: AccessRequest) -> bool:
        """Show Windows dialog using PowerShell"""
        import subprocess
        
        script = f'''
        Add-Type -AssemblyName PresentationFramework
        $result = [System.Windows.MessageBox]::Show(
            "🔐 Secret Access Request`n`nSecret: {request.key_name}`nApplication: {request.app_name}`nReason: {request.reason}`n`n⚠️ SECURITY WARNING:`nOnly approve if you trust '{request.app_name}' and understand why it needs access to this secret.`n`nDo you want to allow access?",
            "SyftWallet Security",
            [System.Windows.MessageBoxButton]::YesNo,
            [System.Windows.MessageBoxImage]::Warning
        )
        if ($result -eq "Yes") {{ exit 0 }} else {{ exit 1 }}
        '''
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True,
                timeout=self.approval_timeout + 10
            )
            
            approved = result.returncode == 0
            
            if approved:
                console.print(f"[green]✅ Access to '{request.key_name}' approved for {request.app_name}[/green]")
            else:
                console.print(f"[red]❌ Access to '{request.key_name}' denied for {request.app_name}[/red]")
                
            return approved
            
        except subprocess.TimeoutExpired:
            console.print("[yellow]⏰ Approval request timed out[/yellow]")
            return False
        except Exception as e:
            console.print(f"[yellow]Error showing Windows PowerShell dialog: {e}[/yellow]")
            raise
    
    def _show_linux_dialog(self, request: AccessRequest) -> bool:
        """Show Linux dialog using zenity or similar tools"""
        import subprocess
        import shutil
        
        # Try zenity first (most common)
        if shutil.which("zenity"):
            return self._show_zenity_dialog(request)
        
        # Try kdialog (KDE)
        if shutil.which("kdialog"):
            return self._show_kdialog_dialog(request)
        
        # Try xmessage as last resort
        if shutil.which("xmessage"):
            return self._show_xmessage_dialog(request)
        
        # No GUI dialog available
        raise Exception("No GUI dialog tool available on this Linux system")
    
    def _show_zenity_dialog(self, request: AccessRequest) -> bool:
        """Show dialog using zenity"""
        import subprocess
        
        text = f"""🔐 Secret Access Request

Secret: {request.key_name}
Application: {request.app_name}
Reason: {request.reason}

⚠️ SECURITY WARNING:
Only approve if you trust '{request.app_name}' and understand why it needs access to this secret.

Do you want to allow access?"""
        
        try:
            result = subprocess.run([
                "zenity", "--question",
                "--title=SyftWallet Security",
                "--text=" + text,
                "--ok-label=Approve",
                "--cancel-label=Deny",
                f"--timeout={self.approval_timeout}"
            ], timeout=self.approval_timeout + 10)
            
            approved = result.returncode == 0
            
            if approved:
                console.print(f"[green]✅ Access to '{request.key_name}' approved for {request.app_name}[/green]")
            else:
                console.print(f"[red]❌ Access to '{request.key_name}' denied for {request.app_name}[/red]")
                
            return approved
            
        except subprocess.TimeoutExpired:
            console.print("[yellow]⏰ Approval request timed out[/yellow]")
            return False
        except Exception as e:
            console.print(f"[yellow]Error showing zenity dialog: {e}[/yellow]")
            raise
    
    def _show_kdialog_dialog(self, request: AccessRequest) -> bool:
        """Show dialog using kdialog"""
        import subprocess
        
        text = f"""🔐 Secret Access Request

Secret: {request.key_name}
Application: {request.app_name}
Reason: {request.reason}

⚠️ SECURITY WARNING:
Only approve if you trust '{request.app_name}' and understand why it needs access to this secret.

Do you want to allow access?"""
        
        try:
            result = subprocess.run([
                "kdialog", "--yesno", text,
                "--title", "SyftWallet Security"
            ], timeout=self.approval_timeout + 10)
            
            approved = result.returncode == 0
            
            if approved:
                console.print(f"[green]✅ Access to '{request.key_name}' approved for {request.app_name}[/green]")
            else:
                console.print(f"[red]❌ Access to '{request.key_name}' denied for {request.app_name}[/red]")
                
            return approved
            
        except subprocess.TimeoutExpired:
            console.print("[yellow]⏰ Approval request timed out[/yellow]")
            return False
        except Exception as e:
            console.print(f"[yellow]Error showing kdialog: {e}[/yellow]")
            raise
    
    def _show_xmessage_dialog(self, request: AccessRequest) -> bool:
        """Show dialog using xmessage"""
        import subprocess
        
        text = f"""SyftWallet Security - Secret Access Request

Secret: {request.key_name}
Application: {request.app_name}
Reason: {request.reason}

WARNING: Only approve if you trust '{request.app_name}'
and understand why it needs access to this secret.

Click OK to APPROVE, Cancel to DENY"""
        
        try:
            result = subprocess.run([
                "xmessage", "-center", "-timeout", str(self.approval_timeout),
                "-buttons", "OK:0,Cancel:1", text
            ], timeout=self.approval_timeout + 10)
            
            approved = result.returncode == 0
            
            if approved:
                console.print(f"[green]✅ Access to '{request.key_name}' approved for {request.app_name}[/green]")
            else:
                console.print(f"[red]❌ Access to '{request.key_name}' denied for {request.app_name}[/red]")
                
            return approved
            
        except subprocess.TimeoutExpired:
            console.print("[yellow]⏰ Approval request timed out[/yellow]")
            return False
        except Exception as e:
            console.print(f"[yellow]Error showing xmessage: {e}[/yellow]")
            raise
    
    def _show_cli_approval(self, request: AccessRequest) -> bool:
        """Show CLI approval prompt as fallback"""
        console.print("\n" + "="*60)
        console.print("🔐 [bold]SECRET ACCESS REQUEST[/bold]")
        console.print("="*60)
        console.print(f"[bold]Secret Name:[/bold] [yellow]{request.key_name}[/yellow]")
        console.print(f"[bold]Application:[/bold] [blue]{request.app_name}[/blue]")
        console.print(f"[bold]Reason:[/bold] [dim]{request.reason}[/dim]")
        console.print(f"[bold]Requested At:[/bold] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request.requested_at))}")
        console.print("\n[yellow]⚠️  Only approve if you trust this application and understand why it needs your secret.[/yellow]")
        console.print("="*60)
        
        while True:
            try:
                response = input("\nDo you want to approve this request? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    console.print(f"[green]✅ Access to '{request.key_name}' approved for {request.app_name}[/green]")
                    return True
                elif response in ['n', 'no', '']:
                    console.print(f"[red]❌ Access to '{request.key_name}' denied for {request.app_name}[/red]")
                    return False
                else:
                    console.print("[yellow]Please answer 'y' for yes or 'n' for no.[/yellow]")
            except (KeyboardInterrupt, EOFError):
                console.print(f"\n[red]❌ Access to '{request.key_name}' denied for {request.app_name}[/red]")
                return False


# Global approval manager instance
_approval_manager = ApprovalManager()


class KeysList:
    """A beautiful list of keys that renders nicely in Jupyter"""
    
    def __init__(self, keys: List[Dict[str, Any]], title: str = "Keys"):
        self.keys = keys
        self.title = title
    
    def __len__(self):
        return len(self.keys)
    
    def __iter__(self):
        return iter(self.keys)
    
    def __getitem__(self, index):
        return self.keys[index]
    
    def __repr__(self):
        return f"KeysList({len(self.keys)} keys)"
    
    def _repr_html_(self):
        """Beautiful HTML representation for Jupyter"""
        if not HAS_IPYTHON:
            return str(self)
        
        html = f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 8px 0; background-color: #f9f9f9;">
            <h3 style="margin: 0 0 16px 0; color: #333; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;">
                🔐 {self.title} ({len(self.keys)} items)
            </h3>
            <div style="max-height: 400px; overflow-y: auto;">
                <table style="width: 100%; border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;">
                    <thead>
                        <tr style="background-color: #e9ecef; border-bottom: 2px solid #dee2e6;">
                            <th style="padding: 12px; text-align: left; font-weight: 600; color: #495057;">Name</th>
                            <th style="padding: 12px; text-align: left; font-weight: 600; color: #495057;">Type</th>
                            <th style="padding: 12px; text-align: left; font-weight: 600; color: #495057;">Vault</th>
                            <th style="padding: 12px; text-align: left; font-weight: 600; color: #495057;">Fields</th>
                            <th style="padding: 12px; text-align: left; font-weight: 600; color: #495057;">Tags</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for i, key in enumerate(self.keys):
            row_bg = "#ffffff" if i % 2 == 0 else "#f8f9fa"
            tags = ", ".join(key.get("tags", []))
            tags_display = tags if tags else "<em>No tags</em>"
            
            # Truncate long names
            name = key.get("name", "")
            if len(name) > 40:
                name = name[:37] + "..."
            
            # Get category and fields info
            category = key.get("category", "UNKNOWN")
            fields = key.get("fields", [])
            fields_display = ", ".join(fields) if fields else "unknown"
            
            # Color code categories
            category_colors = {
                "LOGIN": "#28a745",     # Green
                "PASSWORD": "#007bff",  # Blue
                "SECURE_NOTE": "#6f42c1",  # Purple
            }
            category_color = category_colors.get(category, "#6c757d")  # Gray for unknown
            
            html += f"""
                        <tr style="background-color: {row_bg}; border-bottom: 1px solid #dee2e6;">
                            <td style="padding: 12px; font-weight: 500; color: #212529;">{name}</td>
                            <td style="padding: 12px; color: #6c757d;">
                                <span style="background-color: {category_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; font-weight: 500;">
                                    {category}
                                </span>
                            </td>
                            <td style="padding: 12px; color: #6c757d;">
                                <span style="background-color: #e7f3ff; color: #0066cc; padding: 2px 8px; border-radius: 12px; font-size: 0.875em;">
                                    {key.get('vault', 'Unknown')}
                                </span>
                            </td>
                            <td style="padding: 12px; color: #495057; font-family: monospace; font-size: 0.75em;">{fields_display}</td>
                            <td style="padding: 12px; color: #6c757d; font-size: 0.875em;">{tags_display}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return html
    
    def filter_by_vault(self, vault: str) -> 'KeysList':
        """Filter keys by vault"""
        filtered = [key for key in self.keys if key.get('vault') == vault]
        return KeysList(filtered, f"Keys from {vault} vault")
    
    def filter_by_tag(self, tag: str) -> 'KeysList':
        """Filter keys by tag"""
        filtered = [key for key in self.keys if tag in key.get('tags', [])]
        return KeysList(filtered, f"Keys tagged with '{tag}'")
    
    def search(self, query: str) -> 'KeysList':
        """Search keys by name"""
        query_lower = query.lower()
        filtered = [key for key in self.keys if query_lower in key.get('name', '').lower()]
        return KeysList(filtered, f"Keys matching '{query}'")


class WalletStatus:
    """Beautiful wallet status display for Jupyter"""
    
    def __init__(self, status_data: Dict[str, Any], vault_summary: Dict[str, int]):
        self.status_data = status_data
        self.vault_summary = vault_summary
    
    def __repr__(self):
        return f"WalletStatus({len(self.vault_summary)} vaults)"
    
    def _repr_html_(self):
        """Beautiful HTML representation for Jupyter"""
        if not HAS_IPYTHON:
            return str(self)
        
        # Status indicators
        op_status = "✅ Available" if self.status_data.get("1password_available") else "❌ Not Available"
        op_color = "#28a745" if self.status_data.get("1password_available") else "#dc3545"
        
        keyring_status = "✅ Enabled" if self.status_data.get("keyring_available") else "⚠️ Disabled"
        keyring_color = "#28a745" if self.status_data.get("keyring_available") else "#ffc107"
        
        env_status = "✅ Enabled" if self.status_data.get("env_fallback") else "⚠️ Disabled"
        env_color = "#28a745" if self.status_data.get("env_fallback") else "#ffc107"
        
        total_keys = sum(self.vault_summary.values())
        
        html = f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 8px 0; background-color: #f9f9f9;">
            <h3 style="margin: 0 0 20px 0; color: #333; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;">
                🔐 SyftWallet Status
            </h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #e9ecef;">
                    <h4 style="margin: 0 0 12px 0; color: #495057;">Backend Status</h4>
                    <div style="margin-bottom: 8px;">
                        <span style="color: {op_color}; font-weight: 600;">1Password CLI:</span> {op_status}
                    </div>
                    <div style="margin-bottom: 8px;">
                        <span style="color: {keyring_color}; font-weight: 600;">System Keyring:</span> {keyring_status}
                    </div>
                    <div>
                        <span style="color: {env_color}; font-weight: 600;">Environment Variables:</span> {env_status}
                    </div>
                </div>
                
                <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #e9ecef;">
                    <h4 style="margin: 0 0 12px 0; color: #495057;">Cache Info</h4>
                    <div style="margin-bottom: 8px;">
                        <span style="font-weight: 600;">Cached Keys:</span> {self.status_data.get('cached_keys', 0)}
                    </div>
                    <div>
                        <span style="font-weight: 600;">Cache TTL:</span> {self.status_data.get('cache_duration', 300)}s
                    </div>
                </div>
            </div>
            
            <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #e9ecef;">
                <h4 style="margin: 0 0 12px 0; color: #495057;">📊 Vault Summary ({total_keys} total keys)</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 12px;">
        """
        
        for vault_name, count in self.vault_summary.items():
            html += f"""
                    <div style="background: #e7f3ff; color: #0066cc; padding: 8px 16px; border-radius: 16px; font-weight: 500; border: 1px solid #b3d9ff;">
                        {vault_name}: {count} keys
                    </div>
            """
        
        html += """
                </div>
            </div>
        </div>
        """
        
        return html


class InteractiveKeySearch:
    """Interactive search widget for keys similar to syft-datasets"""
    
    def __init__(self, keys: List[Dict[str, Any]], title: str = "Search Keys"):
        self.keys = keys
        self.title = title
    
    def __repr__(self):
        return f"InteractiveKeySearch({len(self.keys)} keys)"
    
    def _repr_html_(self):
        """Interactive HTML widget for searching and selecting keys"""
        if not HAS_IPYTHON:
            return str(self)
        
        container_id = f"wallet-search-{hash(str(self.keys)) % 10000}"
        
        html = f"""
        <style>
        .wallet-container {{
            max-height: 600px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin: 10px 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fff;
        }}
        .wallet-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px 8px 0 0;
            margin: 0;
        }}
        .wallet-header h3 {{
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }}
        .wallet-header p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
            font-size: 14px;
        }}
        .wallet-controls {{
            padding: 15px 20px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        .wallet-search-box {{
            flex: 1;
            padding: 10px 15px;
            border: 2px solid #e9ecef;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s;
        }}
        .wallet-search-box:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        .wallet-btn {{
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
            text-decoration: none;
        }}
        .wallet-btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
        .wallet-btn-secondary {{
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        }}
        .wallet-btn-secondary:hover {{
            box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
        }}
        .wallet-table-container {{
            max-height: 400px;
            overflow-y: auto;
        }}
        .wallet-keys-table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
            margin: 0;
        }}
        .wallet-keys-table th {{
            background-color: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .wallet-keys-table td {{
            border-bottom: 1px solid #f1f3f4;
            padding: 12px 15px;
            vertical-align: top;
        }}
        .wallet-keys-table tr {{
            cursor: pointer;
            transition: background-color 0.2s;
        }}
        .wallet-keys-table tr:hover {{
            background-color: #f8f9fa;
        }}
        .wallet-keys-table tr.wallet-selected {{
            background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
            border-left: 4px solid #667eea;
        }}
        .wallet-key-name {{
            color: #212529;
            font-weight: 600;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .wallet-vault-badge {{
            background: linear-gradient(135deg, #e7f3ff 0%, #f0f4ff 100%);
            color: #0066cc;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            border: 1px solid #b3d9ff;
        }}
        .wallet-tags {{
            color: #6c757d;
            font-size: 12px;
            font-style: italic;
        }}
        .wallet-created {{
            color: #6c757d;
            font-size: 12px;
        }}
        .wallet-output {{
            padding: 20px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-top: 1px solid #dee2e6;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 13px;
            color: #495057;
            white-space: pre-wrap;
            overflow-x: auto;
            display: none;
        }}
        .wallet-status {{
            padding: 10px 20px;
            background-color: #e9ecef;
            font-size: 12px;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }}
        .wallet-no-results {{
            padding: 40px 20px;
            text-align: center;
            color: #6c757d;
            font-style: italic;
        }}
        </style>
        
        <div class="wallet-container" id="{container_id}">
            <div class="wallet-header">
                <h3>🔐 {self.title}</h3>
                <p>Search and select a key to generate code for clipboard</p>
            </div>
            <div class="wallet-controls">
                <input type="text" class="wallet-search-box" placeholder="🔍 Search keys by name, vault, or tags..." 
                       onkeyup="filterKeys('{container_id}')">
                <button class="wallet-btn wallet-btn-secondary" onclick="clearSelection('{container_id}')">Clear</button>
            </div>
            <div class="wallet-table-container" id="{container_id}-table-container">
                <table class="wallet-keys-table">
                    <thead>
                        <tr>
                            <th>Key Name</th>
                            <th>Type</th>
                            <th>Vault</th>
                            <th>Fields</th>
                            <th>Tags</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for i, key in enumerate(self.keys):
            tags = ", ".join(key.get("tags", []))
            tags_display = tags if tags else "<em>No tags</em>"
            name = key.get("name", "")
            vault = key.get("vault", "Unknown")
            category = key.get("category", "UNKNOWN")
            fields = key.get("fields", [])
            fields_display = ", ".join(fields) if fields else "unknown"
            
            # Color code categories
            category_colors = {
                "LOGIN": "#28a745",     # Green
                "PASSWORD": "#007bff",  # Blue
                "SECURE_NOTE": "#6f42c1",  # Purple
            }
            category_color = category_colors.get(category, "#6c757d")  # Gray for unknown
            
            # Escape quotes for JavaScript
            name_escaped = name.replace('"', '\\"').replace("'", "\\'")
            category_escaped = category.replace('"', '\\"').replace("'", "\\'")
            
            html += f"""
            <tr data-name="{name.lower()}" data-vault="{vault.lower()}" data-tags="{tags.lower()}" data-category="{category.lower()}"
                onclick="selectKey('{container_id}', '{name_escaped}', '{category_escaped}', this)">
                <td class="wallet-key-name" title="{name}">{name}</td>
                <td>
                    <span style="background-color: {category_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 500;">{category}</span>
                </td>
                <td>
                    <span class="wallet-vault-badge">{vault}</span>
                </td>
                <td style="font-family: monospace; font-size: 11px; color: #495057;">{fields_display}</td>
                <td class="wallet-tags">{tags_display}</td>
            </tr>
            """
        
        html += f"""
                    </tbody>
                </table>
                <div class="wallet-no-results" id="{container_id}-no-results" style="display: none;">
                    🔍 No keys found matching your search
                </div>
            </div>
            <div class="wallet-status" id="{container_id}-status">
                {len(self.keys)} keys available • Click a key to generate code
            </div>
            <div class="wallet-output" id="{container_id}-output">
                # Click a key above to generate wallet.get() code
            </div>
        </div>
        
        <script>
        function filterKeys(containerId) {{
            const searchBox = document.querySelector(`#${{containerId}} .wallet-search-box`);
            const table = document.querySelector(`#${{containerId}} .wallet-keys-table tbody`);
            const rows = table.querySelectorAll('tr');
            const noResults = document.querySelector(`#${{containerId}}-no-results`);
            const searchTerm = searchBox.value.toLowerCase();
            
            let visibleCount = 0;
            rows.forEach(row => {{
                const name = row.dataset.name || '';
                const vault = row.dataset.vault || '';
                const tags = row.dataset.tags || '';
                const isVisible = name.includes(searchTerm) || vault.includes(searchTerm) || tags.includes(searchTerm);
                row.style.display = isVisible ? '' : 'none';
                if (isVisible) visibleCount++;
            }});
            
            // Show/hide no results message
            if (visibleCount === 0 && searchTerm) {{
                noResults.style.display = 'block';
                table.style.display = 'none';
            }} else {{
                noResults.style.display = 'none';
                table.style.display = 'table';
            }}
            
            updateStatus(containerId, visibleCount);
        }}
        
        function selectKey(containerId, keyName, category, rowElement) {{
            // Clear previous selections
            const table = document.querySelector(`#${{containerId}} .wallet-keys-table tbody`);
            const rows = table.querySelectorAll('tr');
            rows.forEach(row => row.classList.remove('wallet-selected'));
            
            // Select current row
            rowElement.classList.add('wallet-selected');
            
            // Generate code based on category
            let code = '';
            let clipboardCode = '';
            
            if (category === 'LOGIN') {{
                code = `# Get credentials (returns dict with 'username' and 'password'):
credentials = wallet.get_credentials(
    name="${{keyName}}",
    app_name="your_app_name", 
    reason="why you need this credential"
)
username = credentials['username']
password = credentials['password']

# Or get individual fields:
username = wallet.get_username(
    name="${{keyName}}", 
    app_name="your_app_name", 
    reason="why you need the username"
)
password = wallet.get_password(
    name="${{keyName}}", 
    app_name="your_app_name", 
    reason="why you need the password"
)

# Or use the smart default (returns dict for LOGIN items):
result = wallet.get(
    name="${{keyName}}", 
    app_name="your_app_name", 
    reason="why you need this credential"
)  # Returns {{'username': '...', 'password': '...'}}`;
                clipboardCode = `wallet.get_credentials(name="${{keyName}}", app_name="your_app_name", reason="why you need this credential")`;
            }} else if (category === 'PASSWORD') {{
                code = `# Get password (single value):
password = wallet.get(
    name="${{keyName}}", 
    app_name="your_app_name", 
    reason="why you need this password"
)

# Or explicitly get password field:
password = wallet.get_password(
    name="${{keyName}}", 
    app_name="your_app_name", 
    reason="why you need this password"
)

# With environment variable fallback:
password = wallet.get(
    name="${{keyName}}", 
    app_name="your_app_name", 
    reason="why you need this password", 
    env_var="YOUR_ENV_VAR_NAME"
)`;
                clipboardCode = `wallet.get(name="${{keyName}}", app_name="your_app_name", reason="why you need this password")`;
            }} else {{
                code = `# Get the selected key:
value = wallet.get(
    name="${{keyName}}", 
    app_name="your_app_name", 
    reason="why you need this secret"
)

# Or with environment variable fallback:
value = wallet.get(
    name="${{keyName}}", 
    app_name="your_app_name", 
    reason="why you need this secret", 
    env_var="YOUR_ENV_VAR_NAME"
)`;
                clipboardCode = `wallet.get(name="${{keyName}}", app_name="your_app_name", reason="why you need this secret")`;
            }}
            
            const output = document.querySelector(`#${{containerId}}-output`);
            output.textContent = code;
            output.style.display = 'block';
            
            // Copy to clipboard
            navigator.clipboard.writeText(clipboardCode).then(() => {{
                // Show success feedback
                const status = document.querySelector(`#${{containerId}}-status`);
                const originalText = status.textContent;
                status.textContent = `✅ Copied to clipboard: ${{clipboardCode}}`;
                status.style.color = '#28a745';
                status.style.fontWeight = '600';
                
                // Reset status after 3 seconds
                setTimeout(() => {{
                    status.textContent = originalText;
                    status.style.color = '#6c757d';
                    status.style.fontWeight = 'normal';
                }}, 3000);
            }}).catch(err => {{
                console.warn('Could not copy to clipboard:', err);
                // Still show the code for manual copying
            }});
        }}
        
        function clearSelection(containerId) {{
            const table = document.querySelector(`#${{containerId}} .wallet-keys-table tbody`);
            const rows = table.querySelectorAll('tr');
            rows.forEach(row => row.classList.remove('wallet-selected'));
            
            const output = document.querySelector(`#${{containerId}}-output`);
            output.style.display = 'none';
            
            const searchBox = document.querySelector(`#${{containerId}} .wallet-search-box`);
            searchBox.value = '';
            
            filterKeys(containerId);
        }}
        
        function updateStatus(containerId, visibleCount) {{
            const status = document.querySelector(`#${{containerId}}-status`);
            const totalKeys = {len(self.keys)};
            
            if (visibleCount === totalKeys) {{
                status.textContent = `${{totalKeys}} keys available • Click a key to generate code`;
            }} else {{
                status.textContent = `${{visibleCount}} of ${{totalKeys}} keys shown • Click a key to generate code`;
            }}
        }}
        </script>
        """
        
        return html


class SecretItem(BaseModel):
    """Represents a secret item stored in the wallet"""
    
    name: str = Field(..., description="Name/identifier of the secret")
    value: str = Field(..., description="The secret value")
    tags: List[str] = Field(default_factory=list, description="Tags for organization")
    created_at: float = Field(default_factory=time.time, description="Creation timestamp")
    description: Optional[str] = Field(None, description="Optional description")
    vault: Optional[str] = Field(None, description="1Password vault name")


class WalletConfig(BaseModel):
    """Configuration for the wallet"""
    
    default_vault: Optional[str] = Field(default=None, description="Default 1Password vault (auto-detected if None)")
    cache_duration: int = Field(default=300, description="Cache duration in seconds")
    use_1password: bool = Field(default=True, description="Whether to use 1Password CLI")
    fallback_to_keyring: bool = Field(default=True, description="Fallback to system keyring")
    fallback_to_env: bool = Field(default=True, description="Fallback to environment variables")


class SyftWallet:
    """
    Secure wallet for managing API keys and secrets using 1Password integration
    """
    
    def __init__(self, config: Optional[WalletConfig] = None):
        self.config = config or WalletConfig()
        self._cache: Dict[str, SecretItem] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._op_available: Optional[bool] = None
        
        # Auto-detect best default vault if using default config
        if config is None:
            self._auto_configure_default_vault()
        
        # Create cache directory
        self.cache_dir = Path.home() / ".syft" / "wallet_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption key for local cache
        self._init_encryption()
    
    def _init_encryption(self) -> None:
        """Initialize encryption key for local cache"""
        key_file = self.cache_dir / ".key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                self._encryption_key = f.read()
        else:
            self._encryption_key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self._encryption_key)
            # Restrict permissions
            os.chmod(key_file, 0o600)
        
        self._cipher = Fernet(self._encryption_key)
    
    def _auto_configure_default_vault(self) -> None:
        """Auto-configure the default vault based on available vaults"""
        available_vaults = self._get_available_vaults()
        
        if not available_vaults:
            return  # Keep current default (None)
        
        # Use the first available vault as default for storage operations
        # This is only used when explicitly storing to a default vault
        self.config.default_vault = available_vaults[0]
    
    def _is_op_available(self) -> bool:
        """Check if 1Password CLI is available and authenticated"""
        if self._op_available is not None:
            return self._op_available
        
        try:
            # Check if op command exists
            result = subprocess.run(
                ["op", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                self._op_available = False
                return False
            
            # Check if authenticated
            result = subprocess.run(
                ["op", "account", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            self._op_available = result.returncode == 0
            
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            self._op_available = False
        
        return self._op_available
    
    def _get_available_vaults(self) -> List[str]:
        """Get list of available 1Password vaults"""
        if not self.config.use_1password or not self._is_op_available():
            return []
        
        try:
            result = subprocess.run(
                ["op", "vault", "list", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return [vault.get("name", "") for vault in data if vault.get("name")]
                
        except (subprocess.TimeoutExpired, json.JSONDecodeError, subprocess.SubprocessError):
            pass
        
        return []
    
    def _get_from_1password(self, name: str, field: str = "auto", vault: Optional[str] = None) -> Optional[Union[str, Dict[str, str]]]:
        """
        Retrieve a secret from 1Password
        
        Args:
            name: Item name
            field: Field to retrieve ("auto", "password", "username", "both", or specific field)
            vault: Vault to search in
            
        Returns:
            String value, dict with username/password, or None
        """
        if not self.config.use_1password or not self._is_op_available():
            return None
        
        # If no vault specified, search all vaults
        vaults_to_search = [vault] if vault else self._get_available_vaults()
        if not vaults_to_search and self.config.default_vault:
            vaults_to_search = [self.config.default_vault]
        
        for search_vault in vaults_to_search:
            try:
                vault_arg = ["--vault", search_vault]
                
                # Try to get the item
                result = subprocess.run(
                    ["op", "item", "get", name] + vault_arg + ["--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    fields = {f.get("id", ""): f.get("value", "") for f in data.get("fields", [])}
                    category = data.get("category", "")
                    
                    # Handle different field requests
                    if field == "auto":
                        # Smart default: password for PASSWORD items, both for LOGIN items
                        if category == "PASSWORD":
                            return fields.get("password")
                        elif category == "LOGIN":
                            username = fields.get("username", "")
                            password = fields.get("password", "")
                            if username and password:
                                return {"username": username, "password": password}
                            elif password:
                                return password
                            elif username:
                                return username
                        else:
                            # For other types, try to find any field with a value
                            for field_id, value in fields.items():
                                if value and field_id not in ["notesPlain"]:
                                    return value
                    
                    elif field == "both":
                        username = fields.get("username", "")
                        password = fields.get("password", "")
                        return {"username": username or "", "password": password or ""}
                    
                    elif field in fields:
                        return fields.get(field)
                        
            except (subprocess.TimeoutExpired, json.JSONDecodeError, subprocess.SubprocessError):
                continue  # Try next vault
        
        return None
    
    def _store_in_1password(self, name: str, value: str, tags: List[str] = None, 
                           description: str = None, vault: Optional[str] = None) -> bool:
        """Store a secret in 1Password"""
        if not self.config.use_1password or not self._is_op_available():
            return False
        
        # Determine which vault to use
        target_vault = vault
        if not target_vault:
            target_vault = self.config.default_vault
            if not target_vault:
                available_vaults = self._get_available_vaults()
                target_vault = available_vaults[0] if available_vaults else None
        
        if not target_vault:
            return False  # No vault available
        
        try:
            vault_arg = ["--vault", target_vault]
            
            # Create the item
            cmd = ["op", "item", "create"] + vault_arg + ["--category", "password"]
            cmd.extend(["--title", name])
            cmd.extend([f"password={value}"])
            
            if tags:
                cmd.extend(["--tags", ",".join(tags)])
            
            if description:
                cmd.extend([f"notesPlain={description}"])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            console.print(f"[yellow]Warning: Error storing in 1Password: {e}[/yellow]")
            return False
    
    def _get_from_keyring(self, name: str) -> Optional[str]:
        """Retrieve a secret from system keyring"""
        if not self.config.fallback_to_keyring:
            return None
        
        try:
            return keyring.get_password("syft-wallet", name)
        except Exception as e:
            console.print(f"[yellow]Warning: Error accessing keyring: {e}[/yellow]")
            return None
    
    def _store_in_keyring(self, name: str, value: str) -> bool:
        """Store a secret in system keyring"""
        if not self.config.fallback_to_keyring:
            return False
        
        try:
            keyring.set_password("syft-wallet", name, value)
            return True
        except Exception as e:
            console.print(f"[yellow]Warning: Error storing in keyring: {e}[/yellow]")
            return False
    
    def _get_from_env(self, name: str, env_var: Optional[str] = None) -> Optional[str]:
        """Retrieve a secret from environment variables"""
        if not self.config.fallback_to_env:
            return None
        
        # Try the provided env var first, then uppercase version of name
        env_names = []
        if env_var:
            env_names.append(env_var)
        env_names.extend([name.upper(), name])
        
        for env_name in env_names:
            value = os.getenv(env_name)
            if value:
                return value
        
        return None
    
    def _is_cache_valid(self, name: str) -> bool:
        """Check if cached value is still valid"""
        if name not in self._cache_timestamps:
            return False
        
        age = time.time() - self._cache_timestamps[name]
        return age < self.config.cache_duration
    
    def store(self, name: str, value: str, tags: List[str] = None, 
              description: str = None, vault: Optional[str] = None) -> bool:
        """
        Store a secret securely
        
        Args:
            name: Name/identifier for the secret
            value: The secret value to store
            tags: Optional tags for organization
            description: Optional description
            vault: 1Password vault name (uses default if not specified)
        
        Returns:
            True if stored successfully, False otherwise
        """
        tags = tags or []
        
        # Determine which vault to use for storage
        storage_vault = vault
        if not storage_vault:
            # If no vault specified, use default vault or first available vault
            storage_vault = self.config.default_vault
            if not storage_vault:
                available_vaults = self._get_available_vaults()
                storage_vault = available_vaults[0] if available_vaults else None
        
        # Create secret item
        secret = SecretItem(
            name=name,
            value=value,
            tags=tags,
            description=description,
            vault=storage_vault
        )
        
        # Try to store in 1Password first
        if self._store_in_1password(name, value, tags, description, storage_vault):
            console.print(f"[green]✓ Stored '{name}' in 1Password[/green]")
            
            # Cache the secret
            self._cache[name] = secret
            self._cache_timestamps[name] = time.time()
            return True
        
        # Fallback to keyring
        if self._store_in_keyring(name, value):
            console.print(f"[blue]✓ Stored '{name}' in system keyring[/blue]")
            
            # Cache the secret
            self._cache[name] = secret
            self._cache_timestamps[name] = time.time()
            return True
        
        console.print(f"[red]✗ Failed to store '{name}'[/red]")
        return False
    
    def get(self, name: str, app_name: str, reason: str, field: str = "auto", env_var: Optional[str] = None) -> Optional[Union[str, Dict[str, str]]]:
        """
        Retrieve a secret by name and field with user approval
        
        Args:
            name: Name/identifier of the secret
            app_name: Name of the application requesting access
            reason: Reason why the secret is needed
            field: Which field to retrieve ("auto", "password", "username", "both")
            env_var: Environment variable name to check as fallback
        
        Returns:
            Secret value, dict with username/password, or None if not found or denied
        """
        # Always require approval for secret access
        if not _approval_manager.request_approval(name, app_name, reason):
            console.print(f"[red]❌ Access to '{name}' denied by user[/red]")
            return None
        
        # For non-auto fields or "both", don't use cache since it only stores simple values
        cache_key = f"{name}:{field}" if field != "auto" else name
        
        # Check cache first (only for simple string values)
        if field in ["auto", "password"] and self._is_cache_valid(name):
            cached_value = self._cache[name].value
            if isinstance(cached_value, str):
                return cached_value
        
        # Try 1Password
        value = self._get_from_1password(name, field)
        if value:
            # Cache simple string results
            if isinstance(value, str) and field in ["auto", "password"]:
                secret = SecretItem(name=name, value=value)
                self._cache[name] = secret
                self._cache_timestamps[name] = time.time()
            return value
        
        # For non-1Password fallbacks, only support simple string values
        if field in ["auto", "password"]:
            # Try keyring
            value = self._get_from_keyring(name)
            if value:
                return value
            
            # Try environment variables
            value = self._get_from_env(name, env_var)
            if value:
                return value
        
        return None
    
    def get_credentials(self, name: str, app_name: str, reason: str, vault: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        Get both username and password for a login item with user approval
        
        Args:
            name: Name of the login item
            app_name: Name of the application requesting access
            reason: Reason why the credentials are needed
            vault: Optional vault to search in
            
        Returns:
            Dict with 'username' and 'password' keys, or None if not found or denied
        """
        # Request approval first
        if not _approval_manager.request_approval(name, app_name, reason):
            console.print(f"[red]❌ Access to credentials '{name}' denied by user[/red]")
            return None
            
        result = self._get_from_1password(name, "both", vault)
        if isinstance(result, dict):
            return result
        return None
    
    def get_password(self, name: str, app_name: str, reason: str, vault: Optional[str] = None, env_var: Optional[str] = None) -> Optional[str]:
        """
        Get just the password field from an item with user approval
        
        Args:
            name: Name of the item
            app_name: Name of the application requesting access
            reason: Reason why the password is needed
            vault: Optional vault to search in
            env_var: Environment variable fallback
            
        Returns:
            Password string or None if not found or denied
        """
        return self.get(name, app_name, reason, "password", env_var)
    
    def get_username(self, name: str, app_name: str, reason: str, vault: Optional[str] = None) -> Optional[str]:
        """
        Get just the username field from an item with user approval
        
        Args:
            name: Name of the item
            app_name: Name of the application requesting access
            reason: Reason why the username is needed
            vault: Optional vault to search in
            
        Returns:
            Username string or None if not found or denied
        """
        return self.get(name, app_name, reason, "username")
    
    def store_credentials(self, name: str, username: str, password: str, 
                         tags: List[str] = None, description: str = None, 
                         vault: Optional[str] = None) -> bool:
        """
        Store a username and password as a login item
        
        Args:
            name: Name for the login item
            username: Username/login
            password: Password
            tags: Optional tags
            description: Optional description
            vault: Optional vault to store in
            
        Returns:
            True if stored successfully
        """
        return self._store_credentials_in_1password(name, username, password, tags, description, vault)
    
    def _store_credentials_in_1password(self, name: str, username: str, password: str,
                                      tags: List[str] = None, description: str = None,
                                      vault: Optional[str] = None) -> bool:
        """Store credentials in 1Password as a LOGIN item"""
        if not self.config.use_1password or not self._is_op_available():
            return False
        
        # Determine which vault to use
        target_vault = vault
        if not target_vault:
            target_vault = self.config.default_vault
            if not target_vault:
                available_vaults = self._get_available_vaults()
                target_vault = available_vaults[0] if available_vaults else None
        
        if not target_vault:
            return False
        
        try:
            vault_arg = ["--vault", target_vault]
            
            # Create login item
            cmd = ["op", "item", "create"] + vault_arg + ["--category", "login"]
            cmd.extend(["--title", name])
            cmd.extend([f"username={username}"])
            cmd.extend([f"password={password}"])
            
            if tags:
                cmd.extend(["--tags", ",".join(tags)])
            
            if description:
                cmd.extend([f"notesPlain={description}"])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                console.print(f"[green]✓ Stored credentials for '{name}' in 1Password[/green]")
                return True
            else:
                console.print(f"[red]✗ Failed to store credentials for '{name}': {result.stderr}[/red]")
                return False
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            console.print(f"[yellow]Warning: Error storing credentials in 1Password: {e}[/yellow]")
            return False
    
    def list_keys(self, vault: Optional[str] = None, jupyter: bool = True) -> Union[List[Dict[str, Any]], KeysList]:
        """
        List all stored keys
        
        Args:
            vault: 1Password vault to list from (optional). If None, searches all vaults.
            jupyter: Return beautiful KeysList for Jupyter display (default: True)
        
        Returns:
            KeysList for beautiful Jupyter display or List of dictionaries with key information
        """
        keys = []
        
        # Get from 1Password
        if self.config.use_1password and self._is_op_available():
            # If no vault specified, search all vaults
            vaults_to_search = [vault] if vault else self._get_available_vaults()
            if not vaults_to_search and self.config.default_vault:
                vaults_to_search = [self.config.default_vault]
            
            for search_vault in vaults_to_search:
                try:
                    vault_arg = ["--vault", search_vault]
                    
                    result = subprocess.run(
                        ["op", "item", "list"] + vault_arg + ["--format", "json"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        data = json.loads(result.stdout)
                        for item in data:
                            category = item.get("category", "UNKNOWN")
                            # Determine available fields based on category
                            fields = []
                            if category == "LOGIN":
                                fields = ["username", "password"]
                            elif category == "PASSWORD":
                                fields = ["password"]
                            else:
                                fields = ["custom"]
                            
                            keys.append({
                                "name": item.get("title", ""),
                                "id": item.get("id", ""),
                                "vault": item.get("vault", {}).get("name", ""),
                                "created_at": item.get("created_at", ""),
                                "tags": item.get("tags", []),
                                "category": category,
                                "fields": fields
                            })
                    
                except (subprocess.TimeoutExpired, json.JSONDecodeError, subprocess.SubprocessError):
                    continue  # Try next vault
        
        if jupyter:
            title = f"Keys from {vault} vault" if vault else "All Keys"
            return KeysList(keys, title)
        return keys
    
    def delete(self, name: str, vault: Optional[str] = None) -> bool:
        """
        Delete a secret
        
        Args:
            name: Name/identifier of the secret to delete
            vault: 1Password vault (optional). If None, searches all vaults.
        
        Returns:
            True if deleted successfully, False otherwise
        """
        success = False
        
        # Delete from 1Password
        if self.config.use_1password and self._is_op_available():
            # If no vault specified, search all vaults to find the item
            vaults_to_search = [vault] if vault else self._get_available_vaults()
            if not vaults_to_search and self.config.default_vault:
                vaults_to_search = [self.config.default_vault]
            
            for search_vault in vaults_to_search:
                try:
                    vault_arg = ["--vault", search_vault]
                    
                    result = subprocess.run(
                        ["op", "item", "delete", name] + vault_arg,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        console.print(f"[green]✓ Deleted '{name}' from 1Password ({search_vault})[/green]")
                        success = True
                        break  # Found and deleted, no need to check other vaults
                    
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    continue  # Try next vault
        
        # Delete from keyring
        if self.config.fallback_to_keyring:
            try:
                keyring.delete_password("syft-wallet", name)
                console.print(f"[blue]✓ Deleted '{name}' from keyring[/blue]")
                success = True
            except Exception:
                pass
        
        # Clear from cache
        if name in self._cache:
            del self._cache[name]
            del self._cache_timestamps[name]
        
        return success
    
    def status_dict(self) -> Dict[str, Any]:
        """Get wallet status information as a dictionary"""
        return {
            "1password_available": self._is_op_available(),
            "keyring_available": self.config.fallback_to_keyring,
            "env_fallback": self.config.fallback_to_env,
            "cached_keys": len(self._cache),
            "default_vault": self.config.default_vault,
            "cache_duration": self.config.cache_duration
        }
    
    def show_status(self) -> None:
        """Display wallet status in a nice table"""
        status = self.status_dict()
        
        table = Table(title="SyftWallet Status")
        table.add_column("Component", style="bold")
        table.add_column("Status", style="bold")
        table.add_column("Details")
        
        # 1Password status
        op_status = "✓ Available" if status["1password_available"] else "✗ Not Available"
        op_color = "green" if status["1password_available"] else "red"
        
        # Show available vaults
        available_vaults = self._get_available_vaults()
        default_vault = status['default_vault'] or "Auto-detected"
        vault_info = f"Default: {default_vault}"
        if available_vaults:
            vault_info += f" | Available: {', '.join(available_vaults)}"
        
        table.add_row("1Password CLI", f"[{op_color}]{op_status}[/{op_color}]", vault_info)
        
        # Keyring status
        kr_status = "✓ Enabled" if status["keyring_available"] else "✗ Disabled"
        kr_color = "green" if status["keyring_available"] else "yellow"
        table.add_row("System Keyring", f"[{kr_color}]{kr_status}[/{kr_color}]", "Fallback storage")
        
        # Environment variables
        env_status = "✓ Enabled" if status["env_fallback"] else "✗ Disabled"
        env_color = "green" if status["env_fallback"] else "yellow"
        table.add_row("Environment Variables", f"[{env_color}]{env_status}[/{env_color}]", "Fallback source")
        
        # Cache info
        table.add_row("Cache", f"[blue]{status['cached_keys']} keys[/blue]", 
                     f"TTL: {status['cache_duration']}s")
        
        console.print(table)
        
        # Show vault summary
        if available_vaults:
            console.print("\n[bold]Vault Summary:[/bold]")
            for vault_name in available_vaults:
                vault_keys = self.list_keys(vault=vault_name, jupyter=False)
                console.print(f"  • {vault_name}: {len(vault_keys)} items")
    
    def status(self) -> WalletStatus:
        """Get beautiful status display for Jupyter"""
        status_data = self.status_dict()
        
        # Get vault summary
        vault_summary = {}
        available_vaults = self._get_available_vaults()
        for vault_name in available_vaults:
            vault_keys = self.list_keys(vault=vault_name, jupyter=False)
            vault_summary[vault_name] = len(vault_keys)
        
        return WalletStatus(status_data, vault_summary)
    
    def search_keys(self, vault: Optional[str] = None) -> InteractiveKeySearch:
        """Get interactive search widget for keys"""
        keys = self.list_keys(vault=vault, jupyter=False)
        title = f"Search Keys from {vault} vault" if vault else "Search All Keys"
        return InteractiveKeySearch(keys, title)


# Global wallet instance
_wallet = SyftWallet()

# Convenience functions for easy access
def store(name: str, value: str, tags: List[str] = None, 
          description: str = None, vault: Optional[str] = None) -> bool:
    """Store a secret securely"""
    return _wallet.store(name, value, tags, description, vault)

def get(name: str, app_name: str, reason: str, field: str = "auto", env_var: Optional[str] = None) -> Optional[Union[str, Dict[str, str]]]:
    """Get a secret value or credentials with user approval"""
    return _wallet.get(name, app_name, reason, field, env_var)

def get_credentials(name: str, app_name: str, reason: str, vault: Optional[str] = None) -> Optional[Dict[str, str]]:
    """Get username and password for a login item with user approval"""
    return _wallet.get_credentials(name, app_name, reason, vault)

def get_password(name: str, app_name: str, reason: str, vault: Optional[str] = None, env_var: Optional[str] = None) -> Optional[str]:
    """Get just the password field with user approval"""
    return _wallet.get_password(name, app_name, reason, vault, env_var)

def get_username(name: str, app_name: str, reason: str, vault: Optional[str] = None) -> Optional[str]:
    """Get just the username field with user approval"""
    return _wallet.get_username(name, app_name, reason, vault)

def store_credentials(name: str, username: str, password: str, 
                     tags: List[str] = None, description: str = None, 
                     vault: Optional[str] = None) -> bool:
    """Store username and password as a login item"""
    return _wallet.store_credentials(name, username, password, tags, description, vault)

def list_keys(vault: Optional[str] = None, jupyter: bool = True) -> Union[List[Dict[str, Any]], KeysList]:
    """List all stored keys"""
    return _wallet.list_keys(vault, jupyter)

def delete(name: str, vault: Optional[str] = None) -> bool:
    """Delete a secret"""
    return _wallet.delete(name, vault)

def status_dict() -> Dict[str, Any]:
    """Get wallet status as dictionary"""
    return _wallet.status_dict()

def show_status() -> None:
    """Show wallet status"""
    _wallet.show_status()

def status() -> WalletStatus:
    """Get beautiful status display for Jupyter"""
    return _wallet.status()

def search_keys(vault: Optional[str] = None) -> InteractiveKeySearch:
    """Get interactive search widget for keys"""
    return _wallet.search_keys(vault)

# Convenience alias for even simpler access
keys = _wallet  # Allow `keys.search_keys()` similar to `syd.datasets`

# Export public API
__all__ = [
    "SyftWallet",
    "WalletConfig", 
    "SecretItem",
    "KeysList",
    "WalletStatus",
    "InteractiveKeySearch",
    "store",
    "store_credentials",
    "get",
    "get_credentials",
    "get_password",
    "get_username",
    "list_keys",
    "delete",
    "status",
    "status_dict",
    "show_status",
    "search_keys",
    "keys",
]
