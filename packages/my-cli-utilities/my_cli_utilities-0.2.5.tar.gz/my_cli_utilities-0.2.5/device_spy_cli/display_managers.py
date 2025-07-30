# -*- coding: utf-8 -*-

import logging
from typing import Dict, List

import typer
from my_cli_utilities_common.pagination import paginated_display
from my_cli_utilities_common.config import BaseConfig

logger = logging.getLogger(__name__)


class Config(BaseConfig):
    pass


class BaseDisplayManager:
    """Base class for display managers with common utilities."""
    
    @staticmethod
    def get_safe_value(data: Dict, key: str, default: str = "N/A") -> str:
        """Safely get value from dictionary with default."""
        return str(data.get(key, default) or default)
    
    @staticmethod
    def format_percentage(current: int, total: int) -> str:
        """Format percentage with proper handling of division by zero."""
        if total == 0:
            return "N/A"
        return f"{round((current / total) * 100, 1)}%"
    
    @staticmethod
    def truncate_udid(udid: str, length: int = 8) -> str:
        """Truncate UDID for better readability."""
        return f"{udid[:length]}..." if len(udid) > length else udid


class DeviceDisplayManager(BaseDisplayManager):
    """Handles device information display."""
    
    @staticmethod
    def display_device_info(device: Dict) -> None:
        """Display device information in a user-friendly format."""
        typer.echo(f"\n📱 Device Information")
        typer.echo("=" * Config.DISPLAY_WIDTH)
        
        # Extract key information using safe getter
        fields = [
            ("📋 UDID:", "udid"),
            ("🔧 Platform:", "platform"),
            ("📟 Model:", "model"),
            ("🎯 OS Version:", "platform_version"),
            ("🖥️  Host:", "hostname"),
        ]
        
        for label, key in fields:
            value = BaseDisplayManager.get_safe_value(device, key)
            typer.echo(f"{label:<18} {value}")
        
        # Optional fields
        optional_fields = [
            ("🌐 Host IP:", "host_ip"),
            ("📍 Location:", "location"),
            ("🌐 IP:Port:", "ip_port"),
        ]
        
        for label, key in optional_fields:
            value = device.get(key)
            if value and value != "N/A":
                typer.echo(f"{label:<18} {value}")
        
        # Status
        is_locked = device.get("is_locked", False)
        status = "🔒 Locked" if is_locked else "✅ Available"
        typer.echo(f"{'🔐 Status:':<18} {status}")
        typer.echo("=" * Config.DISPLAY_WIDTH)

    @staticmethod
    def display_device_list(devices: List[Dict], title: str) -> None:
        """Display a list of devices with pagination."""
        def display_device(device: Dict, index: int) -> None:
            model = BaseDisplayManager.get_safe_value(device, "model")
            os_version = BaseDisplayManager.get_safe_value(device, "platform_version")
            udid = BaseDisplayManager.get_safe_value(device, "udid")
            hostname = BaseDisplayManager.get_safe_value(device, "hostname")
            
            typer.echo(f"\n{index}. {model} ({os_version})")
            typer.echo(f"   UDID: {udid}")
            typer.echo(f"   Host: {hostname}")
        
        paginated_display(devices, display_device, title, Config.PAGE_SIZE, Config.DISPLAY_WIDTH)
        
        typer.echo("\n" + "=" * Config.DISPLAY_WIDTH)
        typer.echo(f"💡 Use 'ds udid <udid>' to get detailed information")
        typer.echo("=" * Config.DISPLAY_WIDTH) 