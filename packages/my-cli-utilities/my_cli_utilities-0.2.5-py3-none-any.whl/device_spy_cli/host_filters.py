# -*- coding: utf-8 -*-

from typing import List, Dict, Optional


class HostFilter:
    """Utility class for filtering hosts based on various criteria."""
    
    @staticmethod
    def by_query(hosts: List[Dict], query: str) -> List[Dict]:
        """Filter hosts by query string (hostname or alias)."""
        query_lower = query.lower()
        return [host for host in hosts 
                if query_lower in host.get("hostname", "").lower() or 
                   query_lower in host.get("alias", "").lower()]
    
    @staticmethod
    def find_exact_match(hosts: List[Dict], query: str) -> Optional[Dict]:
        """Find exact match for hostname or alias."""
        query_lower = query.lower()
        
        for host in hosts:
            hostname = host.get("hostname", "").lower()
            alias = host.get("alias", "").lower()
            
            if hostname == query_lower or alias == query_lower:
                return host
        
        return None
    
    @staticmethod
    def get_single_host_ip(hosts: List[Dict], query: str) -> str:
        """Get single host IP for script usage with intelligent matching."""
        found_hosts = HostFilter.by_query(hosts, query)
        
        if not found_hosts:
            return "not_found"
        elif len(found_hosts) == 1:
            return found_hosts[0].get("hostname", "error")
        else:
            # Multiple results, try exact match first
            exact_match = HostFilter.find_exact_match(found_hosts, query)
            if exact_match:
                return exact_match.get("hostname", "error")
            # No exact match, return first result
            return found_hosts[0].get("hostname", "error") 