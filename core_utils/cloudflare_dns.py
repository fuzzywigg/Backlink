"""
Cloudflare DNS Management Utility

This utility provides functions to manage DNS records via the Cloudflare API.
Requires CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID environment variables.

Usage:
    python -m core_utils.cloudflare_dns list
    python -m core_utils.cloudflare_dns add A www 192.168.1.1
    python -m core_utils.cloudflare_dns update RECORD_ID A www 192.168.1.2
    python -m core_utils.cloudflare_dns delete RECORD_ID
"""

import os
import sys
from typing import Any

try:
    import requests
except ImportError:
    print("Error: 'requests' library not installed. Run: pip install requests")
    sys.exit(1)


class CloudflareClient:
    """Client for interacting with Cloudflare API."""

    def __init__(self, api_token: str, zone_id: str):
        """Initialize Cloudflare client.

        Args:
            api_token: Cloudflare API token with DNS edit permissions
            zone_id: Zone ID for the target domain
        """
        self.api_token = api_token
        self.zone_id = zone_id
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def list_dns_records(self) -> list[dict[str, Any]]:
        """List all DNS records for the zone.

        Returns:
            List of DNS record dictionaries
        """
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["result"]

    def get_dns_record(self, record_id: str) -> dict[str, Any]:
        """Get details of a specific DNS record.

        Args:
            record_id: DNS record ID

        Returns:
            DNS record dictionary
        """
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records/{record_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["result"]

    def create_dns_record(
        self,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 1,
        proxied: bool = True,
    ) -> dict[str, Any]:
        """Create a new DNS record.

        Args:
            record_type: DNS record type (A, CNAME, TXT, etc.)
            name: Record name (e.g., 'www', '@', 'api')
            content: Record content (IP address, domain, etc.)
            ttl: Time to live (1 = automatic)
            proxied: Whether to proxy through Cloudflare (orange cloud)

        Returns:
            Created DNS record dictionary
        """
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records"
        data = {
            "type": record_type,
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": proxied,
        }
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()["result"]

    def update_dns_record(
        self,
        record_id: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 1,
        proxied: bool = True,
    ) -> dict[str, Any]:
        """Update an existing DNS record.

        Args:
            record_id: DNS record ID to update
            record_type: DNS record type
            name: Record name
            content: Record content
            ttl: Time to live
            proxied: Whether to proxy through Cloudflare

        Returns:
            Updated DNS record dictionary
        """
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records/{record_id}"
        data = {
            "type": record_type,
            "name": name,
            "content": content,
            "ttl": ttl,
            "proxied": proxied,
        }
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()["result"]

    def delete_dns_record(self, record_id: str) -> dict[str, Any]:
        """Delete a DNS record.

        Args:
            record_id: DNS record ID to delete

        Returns:
            Deletion confirmation dictionary
        """
        url = f"{self.base_url}/zones/{self.zone_id}/dns_records/{record_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["result"]


def main():
    """CLI entry point for Cloudflare DNS management."""
    # Load credentials from environment
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    zone_id = os.getenv("CLOUDFLARE_ZONE_ID")

    if not api_token or not zone_id:
        print("Error: Missing credentials!")
        print("Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID environment variables.")
        print("See docs/QUICK_START_EXTERNAL_SERVICES.md for setup instructions.")
        sys.exit(1)

    # Initialize client
    client = CloudflareClient(api_token, zone_id)

    # Parse command
    if len(sys.argv) < 2:
        print("Usage: python -m core_utils.cloudflare_dns <command> [args]")
        print("Commands:")
        print("  list                          - List all DNS records")
        print("  add TYPE NAME CONTENT         - Add new DNS record")
        print("  update ID TYPE NAME CONTENT   - Update existing record")
        print("  delete ID                     - Delete record")
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "list":
            records = client.list_dns_records()
            print(f"\nFound {len(records)} DNS records:\n")
            for record in records:
                proxied = "🟠 Proxied" if record.get("proxied") else "⚪ DNS only"
                print(
                    f"  {record['type']:6} {record['name']:30} → {record['content']:40} {proxied}"
                )
                print(f"         ID: {record['id']}")
                print()

        elif command == "add":
            if len(sys.argv) < 5:
                print("Usage: python -m core_utils.cloudflare_dns add TYPE NAME CONTENT")
                sys.exit(1)
            record_type = sys.argv[2]
            name = sys.argv[3]
            content = sys.argv[4]
            result = client.create_dns_record(record_type, name, content)
            print(f"✅ Created {record_type} record:")
            print(f"   {result['name']} → {result['content']}")
            print(f"   ID: {result['id']}")

        elif command == "update":
            if len(sys.argv) < 6:
                print("Usage: python -m core_utils.cloudflare_dns update ID TYPE NAME CONTENT")
                sys.exit(1)
            record_id = sys.argv[2]
            record_type = sys.argv[3]
            name = sys.argv[4]
            content = sys.argv[5]
            result = client.update_dns_record(record_id, record_type, name, content)
            print(f"✅ Updated {record_type} record:")
            print(f"   {result['name']} → {result['content']}")

        elif command == "delete":
            if len(sys.argv) < 3:
                print("Usage: python -m core_utils.cloudflare_dns delete ID")
                sys.exit(1)
            record_id = sys.argv[2]
            client.delete_dns_record(record_id)
            print(f"✅ Deleted record {record_id}")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
        print(f"   Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
