# -*- coding: utf-8 -*-

import asyncio
import json
import random
import os
import logging
from typing import Optional, Union, Dict, List, Any
import typer
from my_cli_utilities_common.http_helpers import make_async_request
from my_cli_utilities_common.pagination import paginated_display
from my_cli_utilities_common.config import BaseConfig, ValidationUtils, LoggingUtils

# Initialize logger and disable noise
logger = LoggingUtils.setup_logger('account_pool_cli')
logging.getLogger("httpx").setLevel(logging.WARNING)

# Create main app
app = typer.Typer(
    name="ap",
    help="🏦 Account Pool CLI - Account Management Tools",
    add_completion=False,
    rich_markup_mode="rich"
)

# Configuration constants
class Config(BaseConfig):
    BASE_URL = "https://account-pool-mthor.int.rclabenv.com"
    ACCOUNTS_ENDPOINT = f"{BASE_URL}/accounts"
    ACCOUNT_SETTINGS_ENDPOINT = f"{BASE_URL}/accountSettings"
    CACHE_FILE = BaseConfig.get_cache_file("account_pool_cli_cache.json")
    DEFAULT_ENV_NAME = "webaqaxmn"
    DEFAULT_BRAND = "1210"
    DISPLAY_WIDTH = 80
    CACHE_DISPLAY_WIDTH = 60
    MAX_DISPLAY_LENGTH = 80


class CacheManager:
    """Handles cache operations for account types."""
    
    @staticmethod
    def save_cache(account_types: List[str], filter_keyword: Optional[str], brand: str) -> None:
        """Save account types to cache."""
        cache_data = {
            "account_types": account_types,
            "filter_keyword": filter_keyword,
            "brand": brand
        }
        try:
            with open(Config.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    @staticmethod
    def load_cache() -> Optional[Dict[str, Any]]:
        """Load cache data."""
        try:
            with open(Config.CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return None
    
    @staticmethod
    def get_account_type_by_index(index: int) -> Optional[str]:
        """Get account type by index from cache."""
        cache_data = CacheManager.load_cache()
        if not cache_data:
            typer.echo("❌ No cached account types found. Please run 'ap types' first", err=True)
            return None
        
        account_types = cache_data.get("account_types", [])
        if 1 <= index <= len(account_types):
            return account_types[index - 1]
        else:
            typer.echo(f"❌ Index {index} is out of range. Available indices: 1-{len(account_types)}", err=True)
            typer.echo("💡 Please run 'ap types' first to see available account types")
            return None
    
    @staticmethod
    def clear_cache() -> bool:
        """Clear the cache file."""
        try:
            if os.path.exists(Config.CACHE_FILE):
                os.remove(Config.CACHE_FILE)
                typer.echo("✅ Cache cleared successfully")
                return True
            else:
                typer.echo("ℹ️  No cache file to clear")
                return False
        except Exception as e:
            typer.echo(f"❌ Failed to clear cache: {e}", err=True)
            return False


class AccountDisplayManager:
    """Handles account information display."""
    
    @staticmethod
    def display_account_info(account: Dict) -> None:
        """Display account information in a user-friendly format."""
        typer.echo("\n✅ Account Found!")
        typer.echo("=" * 50)
        
        # Extract key information
        account_id = account.get("accountId", "N/A")
        main_number = account.get("mainNumber", "N/A")
        account_type = account.get("accountType", "N/A")
        env_name = account.get("envName", "N/A")
        email_domain = account.get("companyEmailDomain", "N/A")
        created_at = account.get("createdAt", "N/A")
        mongo_id = account.get("_id", "N/A")
        
        # Format creation date
        if created_at != "N/A":
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_at = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            except:
                pass
        
        # Display information
        display_phone = main_number.lstrip('+') if main_number != "N/A" else main_number
        typer.echo(f"📱 Phone Number:    {display_phone}")
        typer.echo(f"🆔 Account ID:      {account_id}")
        typer.echo(f"🏷️  Account Type:    {account_type}")
        typer.echo(f"🌐 Environment:     {env_name}")
        typer.echo(f"📧 Email Domain:    {email_domain}")
        typer.echo(f"📅 Created:         {created_at}")
        typer.echo(f"🔗 MongoDB ID:      {mongo_id}")
        
        # Show lock status
        locked = account.get("locked", [])
        if locked and len(locked) > 0:
            typer.echo(f"🔒 Status:          🔴 LOCKED")
            typer.echo(f"   Locked Count:    {len(locked)} item(s)")
            for i, lock_item in enumerate(locked, 1):
                if isinstance(lock_item, dict):
                    lock_type = lock_item.get("accountType", "Unknown")
                    lock_phone = lock_item.get("mainNumber", "N/A")
                    typer.echo(f"   Lock #{i}:        Type: {lock_type}")
                    if lock_phone != "N/A":
                        typer.echo(f"                    Phone: {lock_phone}")
                else:
                    typer.echo(f"   Lock #{i}:        {str(lock_item)}")
        else:
            typer.echo(f"🔒 Status:          🟢 AVAILABLE")
        
        typer.echo("=" * 50)


class AccountManager:
    """Core account management functionality."""
    
    def __init__(self):
        self.display_manager = AccountDisplayManager()
    
    async def fetch_random_account(self, env_name: str, account_type: str) -> None:
        """Fetch a random account asynchronously."""
        params = {"envName": env_name, "accountType": account_type}
        
        typer.echo(f"\n🔍 Searching for account...")
        typer.echo(f"   🏷️  Account Type: {account_type}")
        typer.echo(f"   🌐 Environment: {env_name}")
        
        response_data = await make_async_request(Config.ACCOUNTS_ENDPOINT, params=params)
        if not response_data:
            return

        try:
            accounts_list = response_data.get("accounts")
            if accounts_list:
                random_account = random.choice(accounts_list)
                self.display_manager.display_account_info(random_account)
            else:
                typer.echo("⚠️  No matching accounts found", err=True)
        except (TypeError, KeyError) as e:
            typer.echo(f"❌ Failed to extract account information: {e}", err=True)

    async def fetch_account_by_id(self, account_id: str, env_name: str) -> None:
        """Fetch account details by ID asynchronously."""
        url = f"{Config.ACCOUNTS_ENDPOINT}/{account_id}"
        params = {"envName": env_name}
        
        typer.echo(f"\n🔍 Looking up account by ID...")
        typer.echo(f"   🆔 Account ID: {account_id}")
        typer.echo(f"   🌐 Environment: {env_name}")
        
        account_details = await make_async_request(url, params=params)
        if account_details:
            self.display_manager.display_account_info(account_details)

    async def fetch_info_by_main_number(self, main_number: Union[str, int], env_name: str) -> None:
        """Fetch account info by main number asynchronously."""
        main_number_str = ValidationUtils.normalize_phone_number(main_number)
        params = {"envName": env_name}
        
        typer.echo(f"\n🔍 Looking up account by phone number...")
        typer.echo(f"   📱 Phone Number: {main_number_str}")
        typer.echo(f"   🌐 Environment: {env_name}")
        
        response_data = await make_async_request(Config.ACCOUNTS_ENDPOINT, params=params)
        if not response_data:
            return

        try:
            accounts_list = response_data.get("accounts")
            if accounts_list:
                matching_accounts = [
                    account for account in accounts_list 
                    if account.get("mainNumber") == main_number_str
                ]
                
                if matching_accounts:
                    self.display_manager.display_account_info(matching_accounts[0])
                else:
                    typer.echo(f"⚠️  No account found with phone number: {main_number_str}")
            else:
                typer.echo("⚠️  No accounts found in response")
        except (TypeError, KeyError) as e:
            typer.echo(f"❌ Failed to process account data: {e}", err=True)

    async def list_account_types(self, filter_keyword: Optional[str] = None, brand: str = Config.DEFAULT_BRAND) -> None:
        """List account types asynchronously."""
        params = {"brand": brand}
        
        typer.echo(f"\n🔍 Fetching account types...")
        typer.echo(f"   🏷️  Brand: {brand}")
        if filter_keyword:
            typer.echo(f"   🔍 Filter: {filter_keyword}")
        
        response_data = await make_async_request(Config.ACCOUNT_SETTINGS_ENDPOINT, params=params)
        if not response_data:
            return

        try:
            account_settings = response_data.get("accountSettings", [])
            if account_settings:
                typer.echo(f"   ✅ Found {len(account_settings)} account types")
                self._display_account_types(account_settings, filter_keyword, brand)
            else:
                typer.echo("⚠️  No account settings found")
        except Exception as e:
            typer.echo(f"❌ Failed to process account types: {e}", err=True)

    def _display_account_types(self, account_settings: List[Dict], filter_keyword: Optional[str], brand: str) -> None:
        """Display account types with filtering and caching."""
        filtered_settings = account_settings
        
        if filter_keyword:
            filtered_settings = [
                setting for setting in account_settings
                if filter_keyword.lower() in setting.get("accountType", "").lower()
            ]
        
        if not filtered_settings:
            typer.echo("⚠️  No account types match the filter criteria")
            return
        
        # Extract and cache account types
        account_types = [setting.get("accountType", "") for setting in filtered_settings]
        CacheManager.save_cache(account_types, filter_keyword, brand)
        
        def display_account_type(setting: Dict, index: int) -> None:
            account_type = setting.get("accountType", "N/A")
            formatted_type = ValidationUtils.format_account_type_display(account_type)
            typer.echo(f"\n{index}. {formatted_type}")
        
        title = f"🏷️  Account Types (Brand: {brand})"
        if filter_keyword:
            title += f" - Filter: '{filter_keyword}'"
        
        paginated_display(filtered_settings, display_account_type, title, Config.PAGE_SIZE, Config.DISPLAY_WIDTH)
        
        typer.echo("\n" + "=" * Config.DISPLAY_WIDTH)
        typer.echo(f"💡 Use 'ap get <index>' to get random account by type index")
        typer.echo(f"💡 Use 'ap cache' to view cached types")
        typer.echo("=" * Config.DISPLAY_WIDTH)


# Global account manager instance
account_manager = AccountManager()


# Command definitions
@app.command("get")
def get_random_account(
    account_type: str = typer.Argument(..., help="Account type string or index number"),
    env_name: str = typer.Option(Config.DEFAULT_ENV_NAME, "--env", "-e", help="Environment name")
):
    """🎲 Get a random account from the Account Pool"""
    if ValidationUtils.is_numeric_string(account_type):
        index = int(account_type)
        actual_account_type = CacheManager.get_account_type_by_index(index)
        if actual_account_type is None:
            raise typer.Exit(1)
        typer.echo(f"ℹ️  Using account type from index {index}: {actual_account_type}")
        asyncio.run(account_manager.fetch_random_account(env_name, actual_account_type))
    else:
        asyncio.run(account_manager.fetch_random_account(env_name, account_type))


@app.command("by-id")
def get_account_by_id(
    account_id: str = typer.Argument(..., help="Account ID to lookup"),
    env_name: str = typer.Option(Config.DEFAULT_ENV_NAME, "--env", "-e", help="Environment name")
):
    """🆔 Get account details by Account ID"""
    asyncio.run(account_manager.fetch_account_by_id(account_id, env_name))


@app.command("info")
def get_info_by_phone(
    main_number: str = typer.Argument(..., help="Phone number to lookup"),
    env_name: str = typer.Option(Config.DEFAULT_ENV_NAME, "--env", "-e", help="Environment name")
):
    """📱 Get account info by phone number"""
    asyncio.run(account_manager.fetch_info_by_main_number(main_number, env_name))


@app.command("types")
def list_account_types(
    filter_keyword: Optional[str] = typer.Argument(None, help="Filter account types by keyword (optional)"),
    brand: str = typer.Option(Config.DEFAULT_BRAND, "--brand", "-b", help="Brand ID")
):
    """📋 List available account types"""
    asyncio.run(account_manager.list_account_types(filter_keyword, brand))


@app.command("cache")
def manage_cache(
    action: Optional[str] = typer.Argument(None, help="Cache action: 'clear' to clear cache, empty to show status")
):
    """🗄️  Manage account types cache"""
    if action == "clear":
        CacheManager.clear_cache()
    else:
        _show_cache_status()


def _show_cache_status() -> None:
    """Show cache status and contents."""
    cache_data = CacheManager.load_cache()
    if not cache_data:
        typer.echo("ℹ️  Cache is empty. Run 'ap types' to populate it.")
        return
    
    account_types = cache_data.get("account_types", [])
    filter_keyword = cache_data.get("filter_keyword")
    brand = cache_data.get("brand")
    
    typer.echo(f"📦 Cache Status: {len(account_types)} account types cached")
    if brand:
        typer.echo(f"🏷️  Brand: {brand}")
    if filter_keyword:
        typer.echo(f"🔍 Filter: {filter_keyword}")
    
    def display_cached_type(item: str, index: int) -> None:
        """Helper to display a single cached item."""
        display_text = item if len(item) <= Config.MAX_DISPLAY_LENGTH else f"{item[:Config.MAX_DISPLAY_LENGTH - 3]}..."
        typer.echo(f"{index}. {display_text}")

    # 使用分页显示
    paginated_display(
        items=account_types,
        display_func=display_cached_type,
        title="📋 Cached Account Types:",
        page_size=10,  # 每页显示10个
        display_width=Config.CACHE_DISPLAY_WIDTH
    )
    
    typer.echo("=" * Config.CACHE_DISPLAY_WIDTH)
    typer.echo("💡 Use 'ap get <index>' to get account by type index")


def main_cli_function() -> None:
    """Main entry point for Account Pool CLI"""
    app()


if __name__ == "__main__":
    main_cli_function()
