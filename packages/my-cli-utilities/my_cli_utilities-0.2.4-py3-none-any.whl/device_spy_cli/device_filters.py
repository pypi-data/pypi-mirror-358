# -*- coding: utf-8 -*-

from typing import List, Dict, Optional


class DeviceFilter:
    """Utility class for filtering devices based on various criteria."""
    
    @staticmethod
    def by_platform(devices: List[Dict], platform: str) -> List[Dict]:
        """Filter devices by platform."""
        return [device for device in devices if device.get("platform") == platform.lower()]
    
    @staticmethod
    def by_availability(devices: List[Dict], available_only: bool = True) -> List[Dict]:
        """Filter devices by availability status."""
        if available_only:
            return [device for device in devices if not device.get("is_locked", False)]
        return [device for device in devices if device.get("is_locked", False)]
    
    @staticmethod
    def by_host(devices: List[Dict], hostname: str) -> List[Dict]:
        """Filter devices by hostname."""
        if not hostname:
            return []
        return [device for device in devices if device.get("hostname") == hostname]
    
    @staticmethod
    def exclude_simulators(devices: List[Dict]) -> List[Dict]:
        """Exclude simulator devices."""
        return [device for device in devices if not device.get("is_simulator", False)]
    
    @staticmethod
    def by_model(devices: List[Dict], model_pattern: str) -> List[Dict]:
        """Filter devices by model name pattern (case-insensitive)."""
        if not model_pattern:
            return []
        pattern = model_pattern.lower()
        return [device for device in devices 
                if pattern in device.get("model", "").lower()]
    
    @staticmethod
    def by_os_version(devices: List[Dict], min_version: str = None, max_version: str = None) -> List[Dict]:
        """Filter devices by OS version range."""
        filtered = devices
        if min_version:
            filtered = [d for d in filtered if d.get("platform_version", "0") >= min_version]
        if max_version:
            filtered = [d for d in filtered if d.get("platform_version", "999") <= max_version]
        
        return filtered
    
    @staticmethod
    def get_available_devices(devices: List[Dict], platform: str) -> List[Dict]:
        """Get available devices for a specific platform (non-locked, non-simulator)."""
        filtered = DeviceFilter.by_platform(devices, platform)
        filtered = DeviceFilter.exclude_simulators(filtered)
        filtered = DeviceFilter.by_availability(filtered, available_only=True)
        
        return filtered
    
    @staticmethod
    def find_by_udid(devices: List[Dict], udid: str) -> Optional[Dict]:
        """Find a device by UDID with partial matching support."""
        if not devices or not udid:
            return None
        
        # First try exact match
        for device in devices:
            if device.get("udid") == udid:
                return device
        
        # If no exact match, try partial match (useful for shortened UDIDs)
        if len(udid) >= 8:  # Only allow partial matching for reasonable length UDIDs
            for device in devices:
                device_udid = device.get("udid", "")
                if device_udid.startswith(udid):
                    return device
        
        return None
    
    @staticmethod
    def get_android_with_adb(devices: List[Dict]) -> List[Dict]:
        """Get Android devices that have ADB port configured."""
        android_devices = DeviceFilter.by_platform(devices, "android")
        return [device for device in android_devices if device.get("adb_port")]
    
    @staticmethod
    def get_device_summary(devices: List[Dict]) -> Dict[str, int]:
        """Get summary statistics for devices."""
        if not devices:
            return {"total": 0, "android": 0, "ios": 0, "available": 0, "locked": 0}
        
        android_count = len(DeviceFilter.by_platform(devices, "android"))
        ios_count = len(DeviceFilter.by_platform(devices, "ios"))
        available_count = len(DeviceFilter.by_availability(devices, available_only=True))
        locked_count = len(DeviceFilter.by_availability(devices, available_only=False))
        
        return {
            "total": len(devices),
            "android": android_count,
            "ios": ios_count,
            "available": available_count,
            "locked": locked_count
        }

 