# -*- coding: utf-8 -*-

import logging
import subprocess
import re
from typing import Optional, Dict, List
import typer

from my_cli_utilities_common.http_helpers import make_sync_request
from my_cli_utilities_common.config import BaseConfig, LoggingUtils
from .display_managers import DeviceDisplayManager
from .host_display import HostDisplayManager
from .device_filters import DeviceFilter
from .host_filters import HostFilter

# Initialize logger and disable noise
logger = LoggingUtils.setup_logger('device_spy_cli')
logging.getLogger("httpx").setLevel(logging.WARNING)

# Create main app
app = typer.Typer(
    name="ds",
    help="📱 Device Spy CLI - Device Management Tools",
    add_completion=False,
    rich_markup_mode="rich"
)


class Config(BaseConfig):
    """Configuration constants for Device Spy CLI."""
    BASE_URL = "https://device-spy-mthor.int.rclabenv.com"
    HOSTS_ENDPOINT = f"{BASE_URL}/api/v1/hosts"
    ALL_DEVICES_ENDPOINT = f"{BASE_URL}/api/v1/hosts/get_all_devices"
    DEVICE_ASSETS_ENDPOINT = f"{BASE_URL}/api/v1/device_assets/"


class DataManager:
    """Centralized data management with caching and memory optimization."""
    
    def __init__(self, cache_timeout: int = 300):  # 5 minutes default
        self._devices_cache = None
        self._hosts_cache = None
        self._devices_cache_time = 0
        self._hosts_cache_time = 0
        self.cache_timeout = cache_timeout
    
    def _is_cache_expired(self, cache_time: float) -> bool:
        """Check if cache has expired."""
        import time
        return time.time() - cache_time > self.cache_timeout
    
    def get_devices(self, force_refresh: bool = False) -> Optional[List[Dict]]:
        """Get all devices data with caching and expiration."""
        import time
        
        if (self._devices_cache is None or 
            force_refresh or 
            self._is_cache_expired(self._devices_cache_time)):
            try:
                response_data = make_sync_request(Config.ALL_DEVICES_ENDPOINT)
                if response_data and "data" in response_data:
                    self._devices_cache = response_data["data"]
                    self._devices_cache_time = time.time()
                    logger.debug(f"Loaded {len(self._devices_cache)} devices from API")
                else:
                    logger.warning("No device data received from API")
                    self._devices_cache = []
                    self._devices_cache_time = time.time()
            except Exception as e:
                logger.error(f"Failed to fetch devices data: {e}")
                self._devices_cache = []
                self._devices_cache_time = time.time()
        return self._devices_cache

    def get_hosts(self, force_refresh: bool = False) -> Optional[List[Dict]]:
        """Get all hosts data with caching and expiration."""
        import time
        
        if (self._hosts_cache is None or 
            force_refresh or 
            self._is_cache_expired(self._hosts_cache_time)):
            try:
                response_data = make_sync_request(Config.HOSTS_ENDPOINT)
                if response_data and "data" in response_data:
                    self._hosts_cache = response_data["data"]
                    self._hosts_cache_time = time.time()
                    logger.debug(f"Loaded {len(self._hosts_cache)} hosts from API")
                else:
                    logger.warning("No host data received from API")
                    self._hosts_cache = []
                    self._hosts_cache_time = time.time()
            except Exception as e:
                logger.error(f"Failed to fetch hosts data: {e}")
                self._hosts_cache = []
                self._hosts_cache_time = time.time()
        return self._hosts_cache
    
    def clear_cache(self) -> None:
        """Clear all cached data to free memory."""
        self._devices_cache = None
        self._hosts_cache = None
        self._devices_cache_time = 0
        self._hosts_cache_time = 0


class DeviceEnhancer:
    """Enhances device data with additional information."""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def enhance_device_info(self, device: Dict) -> Dict:
        """Enhance device with additional data."""
        enhanced = device.copy()
        
        # Add host alias
        hostname = device.get("hostname")
        if hostname:
            hosts = self.data_manager.get_hosts()
            host = HostFilter.find_exact_match(hosts or [], hostname)
            if host and host.get("alias"):
                enhanced["hostname"] = host["alias"]
                enhanced["host_ip"] = hostname
        
        # Add IP:Port for Android
        if device.get("platform") == "android" and device.get("adb_port"):
            enhanced["ip_port"] = f"{hostname}:{device['adb_port']}"
        
        return enhanced


class ConnectionManager:
    """Handles SSH and ADB connections."""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.ssh_timeout = 30  # SSH connection timeout
        self.adb_timeout = 15  # ADB connection timeout
    
    def connect_ssh(self, query: str) -> None:
        """Connect via SSH with improved error handling and keep-alive."""
        typer.echo(f"\n🔍 Looking up host...")
        typer.echo(f"   Query: '{query}'")
        
        hosts = self.data_manager.get_hosts()
        if not hosts:
            typer.echo(f"   ❌ Unable to fetch host information")
            raise typer.Exit(1)
            
        host_ip = HostFilter.get_single_host_ip(hosts, query)
        
        if host_ip == "not_found":
            typer.echo(f"   ❌ No host found matching '{query}'")
            raise typer.Exit(1)
        elif not self._is_valid_ip(host_ip):
            typer.echo(f"   ❌ Invalid host IP: {host_ip}")
            raise typer.Exit(1)
        
        typer.echo(f"   ✅ Found host IP: {host_ip}")
        typer.echo(f"\n🔗 Connecting via SSH...")
        typer.echo(f"   💡 Tips:")
        typer.echo(f"      - Connection will auto-disconnect after 30 minutes of inactivity")
        typer.echo(f"      - Use 'exit' or Ctrl+D to disconnect manually")
        typer.echo(f"      - Keep-alive is enabled to prevent early timeouts")
        
        try:
            # Use SSH config if available, fallback to default credentials
            from my_cli_utilities_common.system_helpers import SSHConfig
            ssh_config = SSHConfig()
            user, password, _ = ssh_config.get_ssh_credentials(host_ip)
            
            cmd = [
                "sshpass", "-p", password, "ssh", 
                "-o", "StrictHostKeyChecking=no", 
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "ServerAliveInterval=60", 
                "-o", "ServerAliveCountMax=30",
                "-o", "TCPKeepAlive=yes",
                "-o", f"ConnectTimeout={self.ssh_timeout}",
                f"{user}@{host_ip}"
            ]
            
            # Remove the timeout from subprocess.run to allow indefinite connection
            result = subprocess.run(cmd, check=False)
            
            # Check exit code for different scenarios
            if result.returncode == 0:
                typer.echo(f"\n   ✅ SSH session ended normally")
            elif result.returncode == 130:  # Ctrl+C
                typer.echo(f"\n   ⚠️  SSH session interrupted by user")
            elif result.returncode == 255:  # SSH connection error
                typer.echo(f"\n   ❌ SSH connection error (exit code: {result.returncode})")
                typer.echo(f"   💡 This might be due to:")
                typer.echo(f"      - Network connectivity issues")
                typer.echo(f"      - Host is down or unreachable")
                typer.echo(f"      - SSH service not running on host")
                raise typer.Exit(1)
            else:
                typer.echo(f"\n   ⏱️  SSH connection ended (exit code: {result.returncode})")
                
        except subprocess.TimeoutExpired:
            typer.echo(f"   ⏱️  SSH connection timeout after {self.ssh_timeout}s")
            raise typer.Exit(1)
        except subprocess.CalledProcessError as e:
            typer.echo(f"   ❌ SSH connection failed: {e}")
            raise typer.Exit(1)
        except FileNotFoundError:
            typer.echo(f"   ❌ sshpass not found. Install: brew install sshpass")
            raise typer.Exit(1)
        except KeyboardInterrupt:
            typer.echo(f"\n   ⚠️  Connection interrupted by user")
            raise typer.Exit(0)
    
    def connect_adb(self, udid: str) -> None:
        """Connect via ADB with improved error handling."""
        typer.echo(f"\n🔍 Looking up Android device...")
        typer.echo(f"   UDID: {udid}")
        
        devices = self.data_manager.get_devices()
        if not devices:
            typer.echo(f"   ❌ Unable to fetch device information")
            raise typer.Exit(1)
            
        device = DeviceFilter.find_by_udid(devices, udid)
        
        if not device:
            typer.echo(f"   ❌ Device {udid} not found")
            raise typer.Exit(1)
        
        if device.get("is_locked"):
            typer.echo(f"   🔒 Device {udid} is locked")
            raise typer.Exit(1)
        
        if device.get("platform") != "android" or not device.get("adb_port"):
            typer.echo(f"   ❌ Device is not Android or has no ADB port")
            raise typer.Exit(1)
        
        ip_port = f"{device['hostname']}:{device['adb_port']}"
        typer.echo(f"   ✅ Found Android device")
        typer.echo(f"   🌐 Connection: {ip_port}")
        typer.echo(f"\n🔗 Connecting via ADB...")
        
        try:
            # First try to disconnect if already connected
            disconnect_cmd = ["adb", "disconnect", ip_port]
            subprocess.run(disconnect_cmd, capture_output=True, timeout=5)
            
            # Then connect
            connect_cmd = ["adb", "connect", ip_port]
            result = subprocess.run(
                connect_cmd, 
                capture_output=True, 
                text=True, 
                check=False, 
                timeout=self.adb_timeout
            )
            
            if result.returncode == 0:
                typer.echo(f"   ✅ ADB connection successful")
                if result.stdout.strip():
                    typer.echo(f"   📄 Output: {result.stdout.strip()}")
            else:
                typer.echo(f"   ❌ ADB connection failed")
                if result.stderr.strip():
                    typer.echo(f"   📄 Error: {result.stderr.strip()}")
                raise typer.Exit(1)
        except subprocess.TimeoutExpired:
            typer.echo(f"   ⏱️  ADB connection timeout after {self.adb_timeout}s")
            raise typer.Exit(1)
        except FileNotFoundError:
            typer.echo(f"   ❌ adb not found. Install Android SDK Platform Tools")
            raise typer.Exit(1)
    
    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        """Validate IP address format."""
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(pattern, ip))


# Global instances
data_manager = DataManager()
device_enhancer = DeviceEnhancer(data_manager)
connection_manager = ConnectionManager(data_manager)


# CLI Commands
@app.command("udid")
def get_device_info(udid: str = typer.Argument(..., help="Device UDID to lookup")):
    """📱 Display detailed information for a specific device"""
    udid = udid.strip()
    if not udid:
        typer.echo("❌ UDID cannot be empty")
        raise typer.Exit(1)
    
    typer.echo(f"\n🔍 Looking up device information...")
    typer.echo(f"   UDID: {udid}")
    
    devices = data_manager.get_devices()
    if not devices:
        typer.echo(f"   ❌ Unable to fetch device information from server")
        raise typer.Exit(1)
        
    device = DeviceFilter.find_by_udid(devices, udid)
    
    if not device:
        typer.echo(f"   ❌ Device with UDID '{udid}' not found")
        typer.echo(f"   💡 Tip: Use 'ds devices android' or 'ds devices ios' to see available devices")
        raise typer.Exit(1)
    
    typer.echo(f"   ✅ Device found")
    enhanced_device = device_enhancer.enhance_device_info(device)
    DeviceDisplayManager.display_device_info(enhanced_device)


@app.command("devices")
def list_available_devices(platform: str = typer.Argument(..., help="Platform: android or ios")):
    """📋 List available devices for a platform"""
    platform = platform.lower().strip()
    if platform not in ["android", "ios"]:
        typer.echo("❌ Platform must be 'android' or 'ios'")
        raise typer.Exit(1)
    
    typer.echo(f"\n🔍 Finding available devices...")
    typer.echo(f"   Platform: {platform}")
    
    devices = data_manager.get_devices()
    if not devices:
        typer.echo(f"   ❌ Unable to fetch device information from server")
        raise typer.Exit(1)
        
    available_devices = DeviceFilter.get_available_devices(devices, platform)
    
    typer.echo(f"   ✅ Found {len(available_devices)} available {platform} devices")
    
    if available_devices:
        title = f"📱 Available {platform.capitalize()} Devices"
        DeviceDisplayManager.display_device_list(available_devices, title)
    else:
        typer.echo(f"\n   ℹ️  No available {platform} devices found")
        typer.echo(f"   💡 Tip: Try 'ds host <hostname> --detailed' to see all devices on a specific host")


@app.command("host")
def find_host_info(
    query: str = typer.Argument(..., help="Host query string (hostname or alias)"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed host information")
):
    """🖥️  Find host information by query"""
    query = query.strip()
    if not query:
        typer.echo("❌ Host query cannot be empty")
        raise typer.Exit(1)
    
    typer.echo(f"\n🔍 Searching for hosts...")
    typer.echo(f"   Query: '{query}'")
    
    hosts = data_manager.get_hosts()
    if not hosts:
        typer.echo(f"   ❌ Unable to fetch host information from server")
        raise typer.Exit(1)
        
    found_hosts = HostFilter.by_query(hosts, query)
    
    if not found_hosts:
        typer.echo(f"   ❌ No hosts found matching '{query}'")
        typer.echo(f"   💡 Tip: Try a partial hostname or alias (e.g., 'XMNA' or '106')")
        raise typer.Exit(1)
    
    typer.echo(f"   ✅ Found {len(found_hosts)} matching host(s)")
    
    if detailed and len(found_hosts) == 1:
        host = found_hosts[0]
        hostname = host.get("hostname", "")
        devices = data_manager.get_devices()
        if devices:
            host_devices = DeviceFilter.by_host(devices, hostname)
            HostDisplayManager.display_detailed_host_info(host, host_devices)
        else:
            typer.echo(f"   ⚠️  Unable to fetch device information for detailed view")
            HostDisplayManager.display_host_results(found_hosts, query)
    elif detailed and len(found_hosts) > 1:
        typer.echo(f"   ⚠️  Multiple hosts found. Please be more specific for detailed view:")
        HostDisplayManager.display_host_results(found_hosts, query)
    else:
        HostDisplayManager.display_host_results(found_hosts, query)
        if len(found_hosts) == 1:
            typer.echo(f"\n💡 Use 'ds host {query} --detailed' for comprehensive host information")


@app.command("ssh")
def ssh_connect(query: str = typer.Argument(..., help="Host query string to connect via SSH")):
    """🔗 Connect to a host via SSH"""
    query = query.strip()
    if not query:
        typer.echo("❌ Host query cannot be empty")
        raise typer.Exit(1)
    
    connection_manager.connect_ssh(query)


@app.command("connect")
def adb_connect(udid: str = typer.Argument(..., help="Android device UDID to connect via ADB")):
    """🤖 Connect to Android device via ADB"""
    udid = udid.strip()
    if not udid:
        typer.echo("❌ UDID cannot be empty")
        raise typer.Exit(1)
    
    connection_manager.connect_adb(udid)


@app.command("android-ip")
def get_android_connection(udid: str = typer.Argument(..., help="Android device UDID")):
    """🤖 Get Android device IP:Port for ADB connection"""
    devices = data_manager.get_devices()
    device = DeviceFilter.find_by_udid(devices or [], udid)
    
    if not device:
        typer.echo("not_found")
        return "not_found"
    
    if device.get("is_locked"):
        typer.echo("locked")
        return "locked"
    elif device.get("platform") == "android" and device.get("adb_port"):
        ip_port = f"{device.get('hostname')}:{device.get('adb_port')}"
        typer.echo(ip_port)
        return ip_port
    else:
        typer.echo("not_android")
        return "not_android"


@app.command("host-ip")
def get_host_ip_for_script(query: str = typer.Argument(..., help="Host query string")):
    """🌐 Get host IP address for script usage"""
    hosts = data_manager.get_hosts()
    result = HostFilter.get_single_host_ip(hosts or [], query)
    typer.echo(result)
    return result


@app.command("status")
def show_system_status():
    """📊 Show system status and cache information"""
    typer.echo(f"\n📊 Device Spy CLI Status")
    typer.echo("=" * Config.DISPLAY_WIDTH)
    
    # API connectivity
    typer.echo(f"🌐 API Connectivity:")
    typer.echo(f"   Base URL:     {Config.BASE_URL}")
    
    # Cache status
    devices_cached = data_manager._devices_cache is not None
    hosts_cached = data_manager._hosts_cache is not None
    
    typer.echo(f"\n💾 Cache Status:")
    typer.echo(f"   Devices:      {'✅ Cached' if devices_cached else '❌ Not cached'}")
    typer.echo(f"   Hosts:        {'✅ Cached' if hosts_cached else '❌ Not cached'}")
    
    if devices_cached:
        device_count = len(data_manager._devices_cache)
        typer.echo(f"   Device Count: {device_count}")
        
        if device_count > 0:
            summary = DeviceFilter.get_device_summary(data_manager._devices_cache)
            typer.echo(f"   Android:      {summary['android']}")
            typer.echo(f"   iOS:          {summary['ios']}")
            typer.echo(f"   Available:    {summary['available']}")
            typer.echo(f"   Locked:       {summary['locked']}")
    
    if hosts_cached:
        host_count = len(data_manager._hosts_cache)
        typer.echo(f"   Host Count:   {host_count}")
    
    # Quick connectivity test
    typer.echo(f"\n🔍 Quick Connectivity Test:")
    try:
        devices = data_manager.get_devices(force_refresh=True)
        hosts = data_manager.get_hosts(force_refresh=True)
        
        if devices is not None and hosts is not None:
            typer.echo(f"   Status:       ✅ Connected")
            typer.echo(f"   Devices:      {len(devices)} found")
            typer.echo(f"   Hosts:        {len(hosts)} found")
        else:
            typer.echo(f"   Status:       ❌ Connection failed")
    except Exception as e:
        typer.echo(f"   Status:       ❌ Error: {e}")
    
    typer.echo("=" * Config.DISPLAY_WIDTH)


@app.command("refresh")
def refresh_cache():
    """🔄 Refresh cached data from server"""
    typer.echo(f"\n🔄 Refreshing cached data...")
    
    try:
        devices = data_manager.get_devices(force_refresh=True)
        hosts = data_manager.get_hosts(force_refresh=True)
        
        if devices is not None and hosts is not None:
            typer.echo(f"   ✅ Cache refreshed successfully")
            typer.echo(f"   📱 Devices: {len(devices)}")
            typer.echo(f"   🖥️  Hosts:   {len(hosts)}")
        else:
            typer.echo(f"   ❌ Failed to refresh cache")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"   ❌ Error refreshing cache: {e}")
        raise typer.Exit(1)


# Legacy compatibility class
class DeviceSpyCli:
    """Legacy class for backward compatibility with .startup.sh"""
    
    def __init__(self):
        self.data_manager = data_manager
    
    def get_android_ip_port(self, udid: str) -> str:
        """Legacy method for getting Android IP:Port."""
        devices = self.data_manager.get_devices()
        device = DeviceFilter.find_by_udid(devices or [], udid)
        
        if not device:
            return "not_found"
        if device.get("is_locked"):
            return "locked"
        elif device.get("platform") == "android" and device.get("adb_port"):
            return f"{device.get('hostname')}:{device.get('adb_port')}"
        else:
            return "not_android"
    
    def get_host_ip_for_script(self, query_string: str) -> str:
        """Legacy method for getting host IP."""
        hosts = self.data_manager.get_hosts()
        return HostFilter.get_single_host_ip(hosts or [], query_string)


def main_ds_function():
    """Main entry point for Device Spy CLI"""
    app()


if __name__ == "__main__":
    main_ds_function()
