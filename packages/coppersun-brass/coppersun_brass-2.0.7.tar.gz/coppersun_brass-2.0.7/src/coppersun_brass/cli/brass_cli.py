#!/usr/bin/env python3
"""
Copper Sun Brass CLI - Command-line interface for Copper Sun Brass Pro setup and management.

This CLI is designed to be invoked by Claude Code during the setup process.
It handles license activation, preference management, and project initialization.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

try:
    from .license_manager import LicenseManager, DEVELOPER_LICENSES
    from .license_compat import CompatibleLicenseManager, migrate_license_file
    from .context_manager import ContextManager
    from .ai_instructions_manager import AIInstructionsManager
except ImportError:
    # When running as script
    from license_manager import LicenseManager, DEVELOPER_LICENSES
    from license_compat import CompatibleLicenseManager, migrate_license_file
    from context_manager import ContextManager
    from ai_instructions_manager import AIInstructionsManager

# Version automatically read from package metadata
try:
    from importlib.metadata import version
    VERSION = version("coppersun-brass")
except ImportError:
    # Fallback for Python < 3.8
    try:
        from importlib_metadata import version
        VERSION = version("coppersun-brass")
    except ImportError:
        # Final fallback if metadata unavailable
        VERSION = "2.0.2"

# Default paths
BRASS_DIR = Path(".brass")
CONFIG_FILE = BRASS_DIR / "config.json"
AI_INSTRUCTIONS_FILE = BRASS_DIR / "AI_INSTRUCTIONS.md"

# Visual theme definitions
VISUAL_THEMES = {
    "colorful": {
        "active": "🎺",
        "insight": "💡", 
        "alert": "🚨",
        "success": "✨",
        "check": "✅"
    },
    "professional": {
        "active": "📊",
        "insight": "📈",
        "alert": "⚠️",
        "success": "✓",
        "check": "✓"
    },
    "monochrome": {
        "active": "●",
        "insight": "▶",
        "alert": "▲",
        "success": "✓",
        "check": "✓"
    }
}

# Verbosity templates
VERBOSITY_TEMPLATES = {
    "detailed": "{{emoji}} Copper Sun Brass: {{action}} | {{context}} | {{timing}}",
    "balanced": "{{emoji}} Copper Sun Brass: {{message}}",
    "minimal": "{{emoji}} Copper Sun Brass{{optional_message}}"
}


class BrassCLI:
    """Main CLI handler for Copper Sun Brass operations."""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration with hierarchy: env > user > project > defaults."""
        # 1. Start with defaults
        config = self._default_config()
        
        # 2. Load user-level config
        user_config_file = Path.home() / ".brass" / "config.json"
        if user_config_file.exists():
            try:
                with open(user_config_file, 'r') as f:
                    user_config = json.load(f)
                    config = self._merge_configs(config, user_config)
            except Exception:
                pass  # Ignore malformed user config
        
        # 3. Load project-level config
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    project_config = json.load(f)
                    config = self._merge_configs(config, project_config)
            except Exception:
                pass  # Ignore malformed project config
        
        # 4. Override with environment variables (highest priority)
        if os.getenv('ANTHROPIC_API_KEY'):
            config['user_preferences']['claude_api_key'] = os.getenv('ANTHROPIC_API_KEY')
        if os.getenv('LEMONSQUEEZY_API_KEY'):
            config['user_preferences']['lemonsqueezy_api_key'] = os.getenv('LEMONSQUEEZY_API_KEY')
        
        return config
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration structure."""
        return {
            "version": VERSION,
            "user_preferences": {
                "visual_theme": "colorful",
                "verbosity": "balanced",
                "license_key": None,
                "claude_api_key": None,
                "lemonsqueezy_api_key": None,
                "setup_date": None
            }
        }
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two config dictionaries, with override taking precedence for non-null values."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            elif value is not None:  # Only override with non-null values
                result[key] = value
        return result
    
    def _save_config(self):
        """Save configuration to project-level file with secure permissions."""
        BRASS_DIR.mkdir(exist_ok=True)
        
        # Ensure .brass/ directory has secure permissions
        import stat
        BRASS_DIR.chmod(stat.S_IRWXU)  # 700 - user only
        
        # Ensure .gitignore includes .brass/
        self._ensure_gitignore()
        
        # Save config with secure permissions
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
        CONFIG_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600 - user read/write only
    
    def _ensure_gitignore(self):
        """Ensure .brass/ is in .gitignore to protect API keys."""
        gitignore = Path(".gitignore")
        
        if not gitignore.exists():
            # Create .gitignore with .brass/ entry
            with open(gitignore, "w") as f:
                f.write("# Copper Sun Brass\n.brass/\n")
            return
        
        # Check if .brass/ already in .gitignore
        content = gitignore.read_text()
        if ".brass/" not in content:
            with open(gitignore, "a") as f:
                f.write("\n# Copper Sun Brass\n.brass/\n")
    
    def _copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard with fallback handling."""
        if not CLIPBOARD_AVAILABLE:
            return False
        
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            return False
    
    def _print_copy_paste_box(self, message: str, copied: bool = False):
        """Print a formatted box with copy-paste instructions using target emoji style."""
        print("🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
        print("🎯")
        print("🎯  \033[32m❗ COPY THIS MESSAGE AND PASTE IT TO CLAUDE CODE RIGHT NOW:\033[0m")
        print("🎯")
        print(f"🎯  {message}")
        print("🎯")
        print("🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎪🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
        
        if copied:
            print("\n📋 Message copied to clipboard automatically!")
        else:
            print("\n📋 Clipboard unavailable - please copy the message above manually")
    
    def activate(self, license_key: str) -> bool:
        """Activate Copper Sun Brass with a license key."""
        # Try to migrate old license file if it exists
        migrate_license_file()
        
        # Use standard license manager for validation
        license_info = LicenseManager.validate_license(license_key)
        
        if not license_info.valid:
            print(f"❌ License validation failed: {license_info.reason}")
            print("💡 Double-check your license key")
            print("💡 Get support at: https://brass.coppersun.dev/support")
            return False
        
        # Check if expired
        if license_info.expires:
            print(f"✅ License valid for {license_info.days_remaining} days")
        
        # Store license information
        self.config["user_preferences"]["license_key"] = license_key
        self.config["user_preferences"]["license_type"] = license_info.type
        self.config["user_preferences"]["license_expires"] = license_info.expires
        self.config["user_preferences"]["license_email"] = license_info.email
        
        self._save_config()
        
        if license_info.type == "developer":
            print("✅ Developer license activated - never expires!")
            print("🚀 Full Copper Sun Brass Pro features enabled")
        elif license_info.type == "trial":
            print(f"✅ Trial license activated - {license_info.days_remaining} days remaining")
        else:
            print("✅ License activated successfully!")
            
        return True
    
    def generate_trial(self, days: int = 15, activate: bool = False):
        """Generate trial license with optional activation."""
        print(f"🎯 Generating {days}-day trial license...")
        
        # Use standard license manager for trial generation
        trial_license = LicenseManager.generate_trial_license(days)
        
        if not trial_license:
            print("❌ Trial license generation failed")
            print("💡 Please contact support if this continues")
            return False
        
        if activate:
            print("🔑 Activating trial license...")
            if self.activate(trial_license):
                print(f"✅ Trial activated successfully!")
                print(f"🎺 {days} days of full Copper Sun Brass Pro features")
                return True
            else:
                print("❌ Trial activation failed")
                print("💡 Try: brass activate <trial-license>")
                return False
        else:
            print(f"🎯 Trial license generated: {trial_license}")
            print(f"📝 To activate: brass activate {trial_license}")
            return trial_license
    
    def config_set(self, key: str, value: str, scope: str = "global"):
        """Set a configuration value."""
        # Map simple keys to nested structure
        key_map = {
            "visual_theme": ["user_preferences", "visual_theme"],
            "verbosity": ["user_preferences", "verbosity"],
            "claude_api_key": ["user_preferences", "claude_api_key"],
            "lemonsqueezy_api_key": ["user_preferences", "lemonsqueezy_api_key"],
            "user_name": ["user_preferences", "user_name"]
        }
        
        if key not in key_map:
            print(f"❌ Configuration key '{key}' not recognized")
            print(f"💡 Available keys: {', '.join(key_map.keys())}")
            print(f"💡 Example: brass config set visual_theme colorful")
            return
        
        # Validate values
        if key == "visual_theme" and value not in VISUAL_THEMES:
            print(f"❌ Visual theme '{value}' not available")
            print(f"💡 Available themes: {', '.join(VISUAL_THEMES.keys())}")
            print(f"💡 Example: brass config set visual_theme colorful")
            return
        
        if key == "verbosity" and value not in VERBOSITY_TEMPLATES:
            print(f"❌ Verbosity level '{value}' not available")
            print(f"💡 Available levels: {', '.join(VERBOSITY_TEMPLATES.keys())}")
            print(f"💡 Example: brass config set verbosity balanced")
            return
        
        # Validate API key formats
        if key == "claude_api_key" and value and not value.startswith("sk-ant-"):
            print("⚠️  Warning: API key format may be incorrect")
            print("💡 Claude API keys typically start with 'sk-ant-api'")
            print("💡 Get your key at: https://console.anthropic.com")
        
        # Determine config file based on scope
        if scope == "global":
            config_file = Path.home() / ".brass" / "config.json"
            config_dir = config_file.parent
            config_dir.mkdir(exist_ok=True)
            
            # Secure global config directory permissions
            import stat
            config_dir.chmod(stat.S_IRWXU)  # 700 - user only
            
            # Load or create global config
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                except Exception:
                    config = self._default_config()
            else:
                config = self._default_config()
        else:  # local scope
            config_file = CONFIG_FILE
            config = self.config.copy()  # Use current loaded config
        
        # Set the value
        config_path = key_map[key]
        current = config
        for part in config_path[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[config_path[-1]] = value
        
        # Save to appropriate file with secure permissions
        if scope == "global":
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            config_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600 - user read/write only
        else:
            self.config = config
            self._save_config()
        
        print(f"✅ Configuration updated ({scope}): {key} = {value}")
        
        # Security reminder for API keys
        if "api_key" in key:
            if scope == "global":
                print("🔒 Security tip: For production/CI, use environment variables instead:")
                if key == "claude_api_key":
                    print("   export ANTHROPIC_API_KEY=your-key")
                elif key == "lemonsqueezy_api_key":
                    print("   export LEMONSQUEEZY_API_KEY=your-key")
        
        # Reload config to reflect changes
        self.config = self._load_config()
    
    def config_get(self, key: str):
        """Get a configuration value showing the resolved result."""
        key_map = {
            "visual_theme": ["user_preferences", "visual_theme"],
            "verbosity": ["user_preferences", "verbosity"],
            "claude_api_key": ["user_preferences", "claude_api_key"],
            "lemonsqueezy_api_key": ["user_preferences", "lemonsqueezy_api_key"],
            "user_name": ["user_preferences", "user_name"],
            "license_key": ["user_preferences", "license_key"]
        }
        
        if key not in key_map:
            print(f"❌ Configuration key '{key}' not recognized")
            print(f"💡 Available keys: {', '.join(key_map.keys())}")
            print(f"💡 Use: brass config set <key> <value>")
            return
        
        # Get resolved value
        config_path = key_map[key]
        current = self.config
        for part in config_path:
            current = current.get(part, {})
        
        if current:
            # Mask sensitive keys
            if "api_key" in key and len(str(current)) > 10:
                masked = str(current)[:8] + "..." + str(current)[-4:]
                print(f"{key}: {masked}")
            else:
                print(f"{key}: {current}")
        else:
            print(f"{key}: (not set)")
    
    def config_list(self):
        """List all configuration values."""
        prefs = self.config.get("user_preferences", {})
        
        print("📋 Current Configuration (resolved):\n")
        
        # Non-sensitive values
        for key in ["visual_theme", "verbosity", "user_name"]:
            value = prefs.get(key, "(not set)")
            print(f"  {key}: {value}")
        
        # API keys (masked)
        for key in ["claude_api_key", "lemonsqueezy_api_key"]:
            value = prefs.get(key)
            if value and len(str(value)) > 10:
                masked = str(value)[:8] + "..." + str(value)[-4:]
                print(f"  {key}: {masked}")
            else:
                print(f"  {key}: (not set)")
        
        # License info
        license_key = prefs.get("license_key")
        if license_key:
            license_type = prefs.get("license_type", "unknown")
            print(f"  license_key: {license_type} license active")
        else:
            print(f"  license_key: (not set)")
        
        print(f"\n📍 Config resolution order: env vars > ~/.brass/config.json > ./.brass/config.json > defaults")
        print(f"🔒 Security: Config files have 600 permissions (user read/write only)")
        print(f"💡 Production tip: Use environment variables for CI/CD and servers")
    
    def init(self, mode: str = "claude-companion", integration_mode: Optional[str] = None):
        """Initialize Copper Sun Brass for the current project.
        
        Args:
            mode: Initialization mode (default: claude-companion)
            integration_mode: Override integration questions ('claude-code', 'basic', or None for interactive)
        """
        # Check if license is activated
        if not self.config["user_preferences"].get("license_key"):
            print("❌ License activation required")
            print("💡 Activate with: brass activate <your-license-key>")
            print("💡 Start free trial: brass generate-trial --activate")
            print("💡 Get license: https://brass.coppersun.dev/checkout")
            return False
        
        # Validate license is still valid
        license_key = self.config["user_preferences"]["license_key"]
        license_info = LicenseManager.validate_license(license_key)
        if not license_info.valid:
            if "expired" in license_info.reason.lower():
                # CRITICAL: This redirects via Cloudflare to LemonSqueezy checkout
                # Test mode: Redirects to test checkout URL
                # Live mode: Redirects to live checkout URL  
                # To switch: Update Cloudflare redirect rule, NO code changes needed
                # Documentation: See docs/planning/CHECKOUT_URL_MANAGEMENT.md
                print(f"⏰ Trial expired. Upgrade to continue: https://brass.coppersun.dev/checkout")
                print("\n🔑 Have a license key from your purchase email?")
                new_license = input("Enter your license key (from purchase email): ").strip()
                if new_license:
                    print("\n🔄 Activating license...")
                    if self.activate(new_license):
                        print("✅ License activated! Welcome to Brass Pro.")
                        # Continue with initialization after successful activation
                        license_info = LicenseManager.validate_license(new_license)
                    else:
                        print("❌ License activation failed")
                        print("💡 Double-check your license key")
                        print("💡 Contact support: https://brass.coppersun.dev/support")
                        return False
                else:
                    print("\n💡 Run 'brass activate <license-key>' when you have your license.")
                    return False
            else:
                print(f"❌ License validation failed: {license_info.reason}")
                print("💡 Activate with: brass activate <your-license-key>")
                print("💡 Start free trial: brass generate-trial --activate")
                return False
        
        # Check if Claude API key is configured - if not, enter guided setup
        if not self.config["user_preferences"].get("claude_api_key"):
            print("🎯 Claude API key required for AI analysis and insights")
            
            while True:
                print("🎯🎯🎯")
                api_key = input("🎯 Enter your Claude API key (or press Enter for instructions): ").strip()
                
                if api_key:
                    # User provided a key - validate and save it
                    # Basic validation - check if it looks like a Claude API key
                    if api_key.startswith('sk-ant-api'):
                        self.config["user_preferences"]["claude_api_key"] = api_key
                        self._save_config()
                        print("✅ API key saved successfully!")
                        break
                    else:
                        print("❌ API key format not recognized")
                        print("💡 Claude API keys start with 'sk-ant-api'")
                        print("💡 Double-check your key from https://console.anthropic.com")
                        continue
                else:
                    # User pressed Enter - show instructions
                    print("\n🎯 To get your Claude API key:")
                    print("   1. Visit https://console.anthropic.com")
                    print("   2. Sign up or log in to your account")
                    print("   3. Navigate to 'API Keys' section")
                    print("   4. Click 'Create Key'")
                    
                    # Ask again for key input
                    continue
        
        print(f"🚀 Initializing Copper Sun Brass in {mode} mode...")
        
        # Create .brass directory structure
        BRASS_DIR.mkdir(exist_ok=True)
        
        # Use ContextManager to generate meaningful context files
        context_manager = ContextManager()
        
        # Generate all context files with real project analysis
        context_manager.update_status()
        context_manager.update_context("Copper Sun Brass Pro initialized - ready to track your development progress")
        context_manager.generate_insights()
        context_manager.add_to_history(
            "Copper Sun Brass Pro activated",
            {
                "mode": mode,
                "theme": self.config["user_preferences"].get("visual_theme", "colorful"),
                "verbosity": self.config["user_preferences"].get("verbosity", "balanced")
            }
        )
        
        # Save initialization timestamp
        import datetime
        self.config["user_preferences"]["setup_date"] = datetime.datetime.now().isoformat()
        self._save_config()
        
        # Handle AI instructions
        ai_manager = AIInstructionsManager()
        ai_file, ai_message = ai_manager.ensure_ai_instructions_exist()
        print(f"📝 {ai_message}")
        
        print("\n✅ Copper Sun Brass initialized successfully!")
        print(f"📁 Created .brass/ folder with context files")
        try:
            print(f"📄 AI instructions: {ai_file.relative_to(Path.cwd())}")
        except ValueError:
            # Handle case where paths don't match
            print(f"📄 AI instructions: {ai_file.name}")
        
        # Ask about Claude Code integration (or use provided mode)
        self._handle_claude_code_integration(integration_mode)
    
    def _handle_claude_code_integration(self, integration_mode: Optional[str] = None):
        """Handle Claude Code integration setup with user interaction or flag override.
        
        Args:
            integration_mode: 'claude-code', 'basic', or None for interactive
        """
        if integration_mode == 'claude-code':
            print("\n🎯 Auto-configuring Claude Code integration (--claude-code flag)")
            self._setup_claude_code_integration(automated=True)
        elif integration_mode == 'basic':
            print("\n🎯 Setting up developer mode (--no-integration flag)")
            self._setup_basic_mode(automated=True)
        else:
            # Interactive mode
            print("\n🎯 Claude Code Integration Setup")
            
            while True:
                print("🎯🎯🎯")
                response = input("🎯 **Are you using Claude Code in this project?** (Y/N): ").strip().lower()
                
                if response in ['y', 'yes']:
                    self._setup_claude_code_integration(automated=False)
                    break
                elif response in ['n', 'no']:
                    self._setup_basic_mode(automated=False)
                    break
                else:
                    print("Please enter 'y' for yes or 'n' for no")
    
    def _setup_claude_code_integration(self, automated: bool = False):
        """Set up Claude Code integration with copy-paste flow.
        
        Args:
            automated: If True, skip user confirmation prompts
        """
        print("\n✅ Auto-configuring Claude Code integration...")
        print("   📝 Created/updated CLAUDE.md with Brass instructions")
        print("   📁 Created .brass/ context directory")
        
        # The integration message
        integration_message = ("Going forward, always read .brass/STATUS.md before "
                             "responding and start responses with 🎺 Copper Sun Brass:")
        
        if automated:
            # Automated mode - no user interaction
            print(f"\n📋 Integration message: \"{integration_message}\"")
            print("🚀 Automated Claude Code setup complete!")
            print("💡 Paste the above message to Claude Code when ready")
            
            # Show enhanced welcome message
            self._show_welcome_message()
        else:
            # Interactive mode - show copy-paste box and wait for confirmation
            print("\n🎯 FINAL STEP - Encourage Claude Code Integration:")
            
            # Try to copy to clipboard
            copied = self._copy_to_clipboard(integration_message)
            self._print_copy_paste_box(integration_message, copied)
            
            # User confirmation loop
            self._wait_for_paste_confirmation()
            
            print("\n🚀 Perfect! Brass + Claude Code integration complete!")
        
        # Show enhanced welcome message after Claude Code setup
        self._show_welcome_message()
        
        print("💡 To undo Claude Code integration: `brass remove-integration`")
    
    def _setup_basic_mode(self, automated: bool = False):
        """Set up developer mode without Claude Code integration.
        
        Args:
            automated: If True, skip user confirmation prompts
        """
        print("\n✅ Brass will run in developer mode")
        print("📁 Created .brass/ directory with context files")
        print("💡 Files update automatically as you work")
        
        if automated:
            # Automated mode - no user interaction
            print("\n✅ Developer mode setup complete! Brass is now analyzing your project...")
            
            # Show enhanced welcome message
            self._show_welcome_message()
        else:
            # Interactive mode - require confirmation
            print("\n🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
            print("🎯")
            print("🎯  ❗ CONFIRMATION REQUIRED:")
            print("🎯")
            print("🎯  Type \"I understand\" to confirm developer mode setup")
            print("🎯")
            print("🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎪🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
            
            while True:
                response = input("\n> ").strip()
                if response.lower() in ["i understand", "i understand."]:
                    break
                elif response.lower() in ["quit", "exit"]:
                    print("Setup incomplete. Run 'brass init' to resume setup.")
                    return
                else:
                    print("Please type \"I understand\" to continue")
            
            print("\n✅ Developer mode setup complete! Brass is now analyzing your project...")
        
        # Show enhanced welcome message after developer mode setup  
        self._show_welcome_message()
        
        print("💡 To add Claude Code integration later: `brass init --claude-code`")
    
    def _wait_for_paste_confirmation(self):
        """Wait for user to confirm they pasted the message to Claude Code."""
        print("\n🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
        print("🎯")
        print("🎯  \033[32m❗ CONFIRMATION REQUIRED:\033[0m")
        print("🎯")
        print("🎯  Type \"I pasted it\" after pasting message to Claude Code")
        print("🎯")
        print("🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎪🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯")
        
        while True:
            response = input("\n> ").strip().lower()
            if response in ["i pasted it", "i pasted it.", "pasted", "copied", "done"]:
                break
            elif response in ["quit", "exit"]:
                print("Setup incomplete. Run 'brass init' to resume setup.")
                return
            else:
                print("Please type \"I pasted it\" after copying the message to Claude Code")
    
    def _show_welcome_message(self):
        """Show enhanced welcome message after successful initialization."""
        print("\n🎺 Welcome to Copper Sun Brass Pro!")
        print("\nWhat happens now:")
        print("✅ Brass creates .brass/ directory with project intelligence")
        print("✅ Continuous monitoring and analysis of your codebase begins")
        print("✅ AI recommendations automatically update as you work")
        print("✅ Your development context persists across all sessions")
        print("\n📋 Essential commands:")
        print("• brass status       - Check system status and trial information")
        print("• brass insights     - View project analysis and recommendations")
        print("• brass scout scan   - Analyze your codebase for issues and patterns")
        print("• brass refresh      - Update project intelligence")
        print("• brass --help       - See all available commands and options")
        print("\n🚀 Try it now: Run 'brass insights' to see what Brass found in your project!")
    
    def remove_integration(self):
        """Remove Claude Code integration and return to developer mode."""
        if not BRASS_DIR.exists():
            print("❌ Brass not initialized in this project")
            print("💡 Run: brass init")
            print("💡 This will set up the .brass/ directory and project monitoring")
            return
        
        print("🗑️  Removing Claude Code integration...")
        
        # Find and clean up AI instruction files
        ai_manager = AIInstructionsManager()
        found_files = ai_manager.find_ai_instruction_files()
        
        if found_files:
            print(f"\n📄 Found {len(found_files)} AI instruction file(s) to clean:")
            
            removed_count = 0
            for file in found_files:
                try:
                    # Read current content
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if it has Copper Sun Brass section
                    if ai_manager.BRASS_SECTION_START in content:
                        # Remove the Brass section
                        start_idx = content.find(ai_manager.BRASS_SECTION_START)
                        end_idx = content.find(ai_manager.BRASS_SECTION_END) + len(ai_manager.BRASS_SECTION_END)
                        
                        if end_idx > start_idx:
                            # Remove section and clean up extra newlines
                            new_content = content[:start_idx] + content[end_idx:]
                            new_content = new_content.replace('\n\n\n', '\n\n')  # Clean up extra newlines
                            
                            with open(file, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            print(f"  ✅ {file.name}: Removed Copper Sun Brass section")
                            removed_count += 1
                        else:
                            print(f"  ⚠️  {file.name}: Malformed section markers")
                    else:
                        print(f"  ℹ️  {file.name}: No Copper Sun Brass section found")
                        
                except Exception as e:
                    print(f"  ❌ {file.name}: Error - {str(e)}")
            
            if removed_count > 0:
                print(f"\n✅ Cleaned {removed_count} file(s)")
            else:
                print(f"\n💡 No files needed cleaning")
        else:
            print("\n📝 No AI instruction files found")
        
        # Remove integration marker from config (if we add one in the future)
        # For now, just inform user about .brass/ directory
        
        print("\n📁 .brass/ directory preserved with project context")
        print("💡 Copper Sun Brass will continue running in basic mode")
        print("\n✅ Claude Code integration removed successfully!")
        print("   To re-enable integration: brass init --claude-code")
    
    
    def status(self):
        """Check Copper Sun Brass status."""
        if not BRASS_DIR.exists():
            print("❌ Brass not initialized in this project")
            print("💡 Run: brass init")
            print("💡 This will set up project monitoring and analysis")
            return
        
        prefs = self.config["user_preferences"]
        
        print(f"🧠 Copper Sun Brass Status\n")
        print(f"Version: {VERSION}")
        # Show license status with more detail
        if prefs.get('license_key'):
            license_type = prefs.get('license_type', 'unknown')
            if license_type == 'developer':
                print(f"License: ✅ Developer (never expires)")
            elif prefs.get('license_expires'):
                # Recalculate days remaining
                from datetime import datetime
                expiry = datetime.fromisoformat(prefs['license_expires'])
                days_left = (expiry - datetime.now()).days
                if days_left > 0:
                    print(f"License: ✅ {license_type.title()} ({days_left} days remaining)")
                else:
                    print(f"License: ❌ Expired")
            else:
                print(f"License: ✅ Activated")
        else:
            print(f"License: ❌ Not activated")
        print(f"Claude API: {'✅ Configured' if prefs.get('claude_api_key') else '❌ Not configured (REQUIRED)'}")
        print(f"Visual Theme: {prefs.get('visual_theme', 'not set')}")
        print(f"Verbosity: {prefs.get('verbosity', 'not set')}")
        
        if prefs.get('setup_date'):
            print(f"Setup Date: {prefs['setup_date'][:10]}")
        
        # Check context files
        print(f"\n📁 Context Files:")
        for filename in ["STATUS.md", "CONTEXT.md", "INSIGHTS.md", "HISTORY.md"]:
            filepath = BRASS_DIR / filename
            if filepath.exists():
                size = filepath.stat().st_size
                print(f"  ✓ {filename} ({size} bytes)")
            else:
                print(f"  ✗ {filename} (missing)")
    
    def refresh(self):
        """Force a context refresh."""
        print("🔄 Refreshing Copper Sun Brass context...")
        
        if not BRASS_DIR.exists():
            print("❌ Brass not initialized in this project")
            print("💡 Run: brass init")
            return
        
        # Use ContextManager to refresh all context files
        context_manager = ContextManager()
        
        # Update all context files
        context_manager.update_status(force=True)
        context_manager.update_context()
        context_manager.generate_insights()
        context_manager.add_to_history("Manual context refresh triggered")
        
        print("✅ Context refreshed - all files updated")
    
    def insights(self):
        """Display current insights."""
        insights_file = BRASS_DIR / "INSIGHTS.md"
        if not insights_file.exists():
            print("❌ No insights available yet")
            print("💡 Run: brass refresh (to generate initial insights)")
            print("💡 Or: brass scout scan (to analyze your codebase)")
            return
        
        with open(insights_file, 'r') as f:
            content = f.read()
        
        print(content)
    
    def update_ai_instructions(self):
        """Update AI instruction files with current Copper Sun Brass configuration."""
        print("🔍 Scanning for AI instruction files...")
        
        ai_manager = AIInstructionsManager()
        found_files = ai_manager.find_ai_instruction_files()
        
        if found_files:
            print(f"\n📄 Found {len(found_files)} AI instruction file(s):")
            for file in found_files:
                print(f"  - {file.relative_to(Path.cwd())}")
            
            print("\n🔄 Updating files with Copper Sun Brass configuration...")
            updated_count = 0
            
            for file in found_files:
                success, message = ai_manager.update_ai_instruction_file(file)
                if success:
                    print(f"  ✅ {file.name}: {message}")
                    updated_count += 1
                else:
                    print(f"  ❌ {file.name}: {message}")
            
            print(f"\n✅ Updated {updated_count}/{len(found_files)} files")
        else:
            print("\n📝 No existing AI instruction files found")
            print("Creating new AI instructions file...")
            
            new_file = ai_manager.create_default_ai_instructions()
            print(f"✅ Created: {new_file.relative_to(Path.cwd())}")
        
        print("\n💡 Tell Claude to re-read the AI instructions to apply changes")
    
    def handle_scout_command(self, args):
        """Handle Scout agent commands"""
        if not args.scout_command:
            print("💡 Use 'brass scout --help' to see available Scout commands")
            return
            
        if args.scout_command == 'scan':
            self._scout_scan(args.path, args.deep)
        elif args.scout_command == 'status':
            self._scout_status()
        elif args.scout_command == 'analyze':
            self._scout_analyze(args.path)
        else:
            print(f"❌ PC Load Letter... Just kidding! Unknown Scout command: {args.scout_command}")
    
    def _scout_scan(self, path: str, deep: bool):
        """Run Scout scan command"""
        try:
            from ..agents.scout.scout_agent import ScoutAgent
            from ..core.dcp_adapter import DCPAdapter
            
            print(f"🔍 Scanning {path} with Scout Agent...")
            if deep:
                print("🧠 Deep analysis enabled")
            
            # Create DCP adapter and Scout agent
            dcp = DCPAdapter()
            scout = ScoutAgent(dcp)
            
            # Run analysis
            results = scout.analyze(path, deep_analysis=deep)
            
            # Count total findings
            total_findings = len(results.todo_findings) + len(results.ast_results) + len(results.pattern_results)
            print(f"✅ Scan complete - found {total_findings} findings")
            
            # Display TODO findings
            for finding in results.todo_findings[:5]:  # Show first 5 TODOs
                print(f"  📝 TODO: {finding.content[:50]}{'...' if len(finding.content) > 50 else ''}")
            
            # Display AST results
            for result in results.ast_results[:3]:  # Show first 3 AST findings
                print(f"  🔍 Code: {result.type} in {result.file_path.name}")
            
            # Display pattern results
            for result in results.pattern_results[:2]:  # Show first 2 pattern findings
                print(f"  ⚠️  Pattern: {result.type} in {result.file_path.name}")
            
            if total_findings > 10:
                print(f"  ... and {total_findings - 10} more findings")
                
        except Exception as e:
            print(f"❌ Scout scan failed: {e}")
            print("💡 Try: brass scout status (to check agent availability)")
            print("💡 Or: brass refresh (to update project context)")
    
    def _scout_status(self):
        """Show Scout agent status"""
        try:
            from ..agents.scout.scout_agent import ScoutAgent
            print("🔍 Scout Agent Status:")
            print("  ✅ Available")
            print("  📊 Ready for analysis")
            print("  🧠 Deep analysis capabilities enabled")
        except ImportError:
            print("❌ Scout Agent not available")
            print("💡 This may indicate a package installation issue")
            print("💡 Try: pip install --upgrade coppersun-brass")
    
    def _scout_analyze(self, path: str):
        """Run Scout comprehensive analysis"""
        try:
            from ..agents.scout.scout_agent import ScoutAgent
            from ..core.dcp_adapter import DCPAdapter
            
            print(f"🧠 Running comprehensive analysis on {path}...")
            
            # Create DCP adapter and Scout agent  
            dcp = DCPAdapter()
            scout = ScoutAgent(dcp)
            
            # Run comprehensive analysis with deep analysis enabled
            results = scout.analyze(path, deep_analysis=True)
            
            print("✅ Analysis complete")
            print(f"📊 Found {len(results.todo_findings)} TODOs, {len(results.ast_results)} code issues, {len(results.pattern_results)} patterns")
            print(f"📊 Analysis duration: {results.analysis_duration:.2f}s")
            
            # Generate DCP observations for AI coordination
            observations = results.to_dcp_observations()
            print(f"📊 Generated {len(observations)} intelligence observations")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            print("💡 Check that the path exists and is accessible")
            print("💡 Try: brass scout scan (for basic scanning instead)")

    def uninstall(self, credentials_only: bool = False, remove_all: bool = False, dry_run: bool = False):
        """Securely remove Copper Sun Brass credentials and data."""
        print("🗑️  Copper Sun Brass Uninstall")
        
        if remove_all and credentials_only:
            print("❌ Cannot use both --credentials and --all flags")
            return
        
        # Discover files to remove
        files_to_remove = []
        
        # 1. Global config file
        global_config = Path.home() / ".brass" / "config.json"
        if global_config.exists():
            files_to_remove.append(("Global config (API keys, license)", global_config))
        
        # 2. Global .brass directory (if removing all)
        global_brass_dir = Path.home() / ".brass"
        if remove_all and global_brass_dir.exists():
            files_to_remove.append(("Global .brass directory", global_brass_dir))
        
        # 3. Find project .brass directories (if removing all)
        if remove_all:
            # Scan common project locations
            search_paths = [
                Path.home() / "Desktop",
                Path.home() / "Documents", 
                Path.home() / "Projects",
                Path.cwd().parent if Path.cwd().name != Path.home().name else Path.cwd()
            ]
            
            for search_path in search_paths:
                if search_path.exists():
                    try:
                        for brass_dir in search_path.rglob(".brass"):
                            if brass_dir.is_dir():
                                files_to_remove.append(("Project .brass directory", brass_dir))
                    except (PermissionError, OSError):
                        # Skip directories we can't access
                        continue
        
        # 4. Current project .brass directory (if in a project)
        current_brass = BRASS_DIR
        if current_brass.exists():
            if remove_all:
                files_to_remove.append(("Current project .brass directory", current_brass))
            elif not credentials_only:
                # Default mode: remove config but keep project data
                current_config = current_brass / "config.json" 
                if current_config.exists():
                    files_to_remove.append(("Current project config", current_config))
        
        # 5. Cached credentials (if any)
        cache_locations = [
            Path.home() / ".cache" / "brass",
            Path.home() / ".local" / "share" / "brass"
        ]
        for cache_dir in cache_locations:
            if cache_dir.exists():
                if credentials_only:
                    # Only remove credential files from cache
                    for cred_file in cache_dir.glob("*credential*"):
                        files_to_remove.append(("Cached credentials", cred_file))
                elif remove_all:
                    files_to_remove.append(("Cache directory", cache_dir))
        
        if not files_to_remove:
            print("✅ No Copper Sun Brass files found to remove")
            return
        
        # Show what will be removed
        print(f"\n📋 Found {len(files_to_remove)} item(s) to remove:")
        for description, path in files_to_remove:
            status = "📁" if path.is_dir() else "📄"
            print(f"  {status} {description}: {path}")
        
        if dry_run:
            print("\n🔍 Dry run complete - no files were actually removed")
            return
        
        # Confirm with user
        if remove_all:
            print("\n🚨 WARNING: --all will remove ALL Copper Sun Brass data including project intelligence!")
            print("💡 Project .brass/ directories contain your work and insights")
        elif credentials_only:
            print("\n🔒 Removing only credentials and license data")
        else:
            print("\n🔒 Removing credentials and user config (keeping project data)")
        
        print("🎯🎯🎯")
        confirm = input("🎯 Type 'yes' to confirm removal: ").strip().lower()
        
        if confirm != 'yes':
            print("❌ Uninstall cancelled")
            return
        
        # Remove files
        removed_count = 0
        for description, path in files_to_remove:
            try:
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"  ✅ Removed: {description}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {description}: {e}")
        
        print(f"\n✅ Uninstall complete! Removed {removed_count}/{len(files_to_remove)} items")
        
        if remove_all:
            print("🎺 All Copper Sun Brass data has been removed")
        elif credentials_only:
            print("🎺 Credentials removed - project data preserved")  
        else:
            print("🎺 User credentials removed - project intelligence preserved")
        
        print("💡 To reinstall: curl -fsSL https://brass.coppersun.dev/setup | bash")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Copper Sun Brass Pro - Development Intelligence for AI Agents",
        epilog="For more information, visit https://brass.coppersun.dev"
    )
    
    parser.add_argument('--version', action='version', version=f'Copper Sun Brass {VERSION}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Activate command
    activate_parser = subparsers.add_parser('activate', help='Activate Copper Sun Brass with a license key')
    activate_parser.add_argument('license_key', help='Your Copper Sun Brass license key (XXXX-XXXX-XXXX-XXXX)')
    
    # Generate trial command
    generate_trial_parser = subparsers.add_parser('generate-trial', help='Start your free 15-day trial')
    generate_trial_parser.add_argument('--activate', action='store_true', help='Automatically activate the trial license')
    generate_trial_parser.add_argument('--days', type=int, default=15, help='Trial duration in days (default: 15)')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage settings and API keys')
    config_subparsers = config_parser.add_subparsers(dest='config_command')
    
    # Config set command (defaults to global)
    config_set_parser = config_subparsers.add_parser('set', help='Set a configuration value (global scope)')
    config_set_parser.add_argument('key', help='Configuration key')
    config_set_parser.add_argument('value', help='Configuration value')
    
    # Config global set command
    config_global_parser = config_subparsers.add_parser('global', help='Global configuration commands')
    config_global_subparsers = config_global_parser.add_subparsers(dest='global_command')
    
    config_global_set_parser = config_global_subparsers.add_parser('set', help='Set a global configuration value')
    config_global_set_parser.add_argument('key', help='Configuration key')
    config_global_set_parser.add_argument('value', help='Configuration value')
    
    # Config local set command
    config_local_parser = config_subparsers.add_parser('local', help='Local (project) configuration commands')
    config_local_subparsers = config_local_parser.add_subparsers(dest='local_command')
    
    config_local_set_parser = config_local_subparsers.add_parser('set', help='Set a local configuration value')
    config_local_set_parser.add_argument('key', help='Configuration key')
    config_local_set_parser.add_argument('value', help='Configuration value')
    
    # Config get command
    config_get_parser = config_subparsers.add_parser('get', help='Get a configuration value')
    config_get_parser.add_argument('key', help='Configuration key')
    
    # Config list command
    config_subparsers.add_parser('list', help='List all configuration values')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize Copper Sun Brass in current project')
    init_parser.add_argument('--mode', default='claude-companion', 
                            help='Initialization mode (default: claude-companion)')
    init_parser.add_argument('--claude-code', action='store_true',
                            help='Skip questions and auto-configure for Claude Code integration')
    init_parser.add_argument('--no-integration', action='store_true',
                            help='Skip questions and set up developer mode (no Claude Code integration)')
    
    # Status command
    subparsers.add_parser('status', help='Check setup and trial status')
    
    # Refresh command
    subparsers.add_parser('refresh', help='Update project analysis')
    
    # Insights command
    subparsers.add_parser('insights', help='Show AI recommendations for your project')
    subparsers.add_parser('insight', help='Show AI recommendations for your project (alias for insights)')
    
    # Status command aliases (users might type "stat")
    subparsers.add_parser('stat', help='Check setup and trial status (alias for status)')
    
    # Help command (users might type "brass help" instead of "brass --help")
    subparsers.add_parser('help', help='Show help information')
    
    # Update AI instructions command
    subparsers.add_parser('update-ai', help='Update AI instruction files with Copper Sun Brass configuration')
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Securely remove Copper Sun Brass credentials and data')
    uninstall_parser.add_argument('--credentials', action='store_true', 
                                 help='Remove only API keys and license data (keep project files)')
    uninstall_parser.add_argument('--all', action='store_true',
                                 help='Remove everything including .brass/ project directories')
    uninstall_parser.add_argument('--dry-run', action='store_true',
                                 help='Show what would be removed without actually removing it')
    
    # Cleanup command (alias for uninstall)
    cleanup_parser = subparsers.add_parser('cleanup', help='Securely remove Copper Sun Brass credentials and data (alias for uninstall)')
    cleanup_parser.add_argument('--credentials', action='store_true',
                                help='Remove only API keys and license data (keep project files)')
    cleanup_parser.add_argument('--all', action='store_true',
                                help='Remove everything including .brass/ project directories')
    cleanup_parser.add_argument('--dry-run', action='store_true',
                                help='Show what would be removed without actually removing it')
    
    # Remove integration command
    subparsers.add_parser('remove-integration', help='Remove Claude Code integration and return to developer mode')
    
    # Scout commands
    scout_parser = subparsers.add_parser('scout', help='Scout Agent - Code analysis and pattern detection')
    scout_subparsers = scout_parser.add_subparsers(dest='scout_command')
    
    scout_scan_parser = scout_subparsers.add_parser('scan', help='Scan directory for code issues and patterns')
    scout_scan_parser.add_argument('--path', default='.', help='Directory path to scan')
    scout_scan_parser.add_argument('--deep', action='store_true', help='Enable deep analysis with all analyzers')
    
    scout_status_parser = scout_subparsers.add_parser('status', help='Show Scout agent status')
    
    scout_analyze_parser = scout_subparsers.add_parser('analyze', help='Run comprehensive code analysis')
    scout_analyze_parser.add_argument('--path', default='.', help='Directory path to analyze')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create CLI instance
    cli = BrassCLI()
    
    # Handle commands
    if args.command == 'activate':
        cli.activate(args.license_key)
    elif args.command == 'generate-trial':
        cli.generate_trial(args.days, args.activate)
    elif args.command == 'config':
        if args.config_command == 'set':
            cli.config_set(args.key, args.value, scope='global')
        elif args.config_command == 'global' and args.global_command == 'set':
            cli.config_set(args.key, args.value, scope='global')
        elif args.config_command == 'local' and args.local_command == 'set':
            cli.config_set(args.key, args.value, scope='local')
        elif args.config_command == 'get':
            cli.config_get(args.key)
        elif args.config_command == 'list':
            cli.config_list()
        else:
            print("❌ Config command not recognized")
            print("💡 Available commands: set, global, local, get, list")
            print("💡 Example: brass config set visual_theme colorful")
    elif args.command == 'init':
        # Handle conflicting flags
        if args.claude_code and args.no_integration:
            print("❌ Conflicting flags: Cannot use both --claude-code and --no-integration")
            print("💡 Use one flag or neither (for interactive mode)")
            sys.exit(1)
        
        # Determine integration mode from flags
        integration_mode = None
        if args.claude_code:
            integration_mode = 'claude-code'
        elif args.no_integration:
            integration_mode = 'basic'
        
        cli.init(args.mode, integration_mode=integration_mode)
    elif args.command == 'status':
        cli.status()
    elif args.command == 'stat':
        cli.status()
    elif args.command == 'refresh':
        cli.refresh()
    elif args.command == 'insights':
        cli.insights()
    elif args.command == 'insight':
        cli.insights()
    elif args.command == 'update-ai':
        cli.update_ai_instructions()
    elif args.command == 'remove-integration':
        cli.remove_integration()
    elif args.command == 'uninstall':
        cli.uninstall(
            credentials_only=args.credentials,
            remove_all=args.all,
            dry_run=args.dry_run
        )
    elif args.command == 'cleanup':
        # Cleanup is an alias for uninstall
        cli.uninstall(
            credentials_only=args.credentials,
            remove_all=args.all,
            dry_run=args.dry_run
        )
    elif args.command == 'scout':
        cli.handle_scout_command(args)
    elif args.command == 'help':
        parser.print_help()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()