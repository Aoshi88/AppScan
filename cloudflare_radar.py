#!/usr/bin/env python3
"""
Cloudflare URL Scanner API Client

This script allows you to submit URLs for scanning to Cloudflare Radar.
Requires a Cloudflare API token with URL Scanner permissions and your account ID.

Documentation: https://developers.cloudflare.com/radar/investigate/url-scanner/
"""

import requests
import json
import time
import keyring
from typing import Optional, Dict, List, Any
from dataclasses import dataclass


@dataclass
class ScanConfig:
    """Configuration for URL scan"""
    url: str
    screenshots_resolutions: Optional[List[str]] = None  # desktop, mobile, tablet
    custom_agent: Optional[str] = None
    referer: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    visibility: str = "Public"  # Public or Unlisted


class CloudflareURLScanner:
    """Client for Cloudflare URL Scanner API"""

    BASE_URL = "https://api.cloudflare.com/client/v4/accounts"

    def __init__(self, api_token: str, account_id: str):
        """
        Initialize the scanner client.

        Args:
            api_token: Cloudflare API token with URL Scanner permissions
            account_id: Cloudflare account ID
        """
        self.api_token = api_token
        self.account_id = account_id
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def _build_scan_payload(self, config: ScanConfig) -> Dict[str, Any]:
        """Build the request payload for a URL scan."""
        payload = {"url": config.url}

        if config.screenshots_resolutions:
            payload["screenshotsResolutions"] = config.screenshots_resolutions

        if config.custom_agent:
            payload["customagent"] = config.custom_agent

        if config.referer:
            payload["referer"] = config.referer

        if config.custom_headers:
            payload["customHeaders"] = config.custom_headers

        if config.visibility:
            payload["visibility"] = config.visibility

        return payload

    def submit_url(self, config: ScanConfig) -> Dict[str, Any]:
        """
        Submit a single URL for scanning.

        Args:
            config: ScanConfig object with URL and optional parameters

        Returns:
            Response dictionary with scan details including uuid

        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.BASE_URL}/{self.account_id}/urlscanner/v2/scan"
        payload = self._build_scan_payload(config)

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        response_data = response.json()
        if isinstance(response_data, dict):
            return response_data.get("result", response_data)
        return response_data

    def submit_urls_bulk(self, urls: List[str]) -> Dict[str, Any]:
        """
        Submit multiple URLs for scanning (up to 100).

        Args:
            urls: List of URLs to scan (max 100)

        Returns:
            Response dictionary with scan details

        Raises:
            ValueError: If more than 100 URLs provided
            requests.RequestException: If the API request fails
        """
        if len(urls) > 100:
            raise ValueError("Maximum 100 URLs can be submitted at once")

        url = f"{self.BASE_URL}/{self.account_id}/urlscanner/v2/scans"
        payload = {"scans": [{"url": u} for u in urls]}

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        response_data = response.json()
        if isinstance(response_data, dict):
            return response_data.get("result", response_data)
        return response_data

    def get_scan_result(self, scan_id: str, poll: bool = False, 
                       poll_interval: int = 10, max_polls: int = 180) -> Dict[str, Any]:
        """
        Retrieve scan results.

        Args:
            scan_id: UUID of the scan
            poll: Whether to continuously poll until completion
            poll_interval: Interval in seconds between polls (default: 10)
            max_polls: Maximum number of polls (default: 180 = 30 minutes)

        Returns:
            Response dictionary with scan results

        Raises:
            requests.RequestException: If the API request fails
            TimeoutError: If max_polls reached without completion
        """
        url = f"{self.BASE_URL}/{self.account_id}/urlscanner/v2/result/{scan_id}"

        if not poll:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            response_data = response.json()
            if isinstance(response_data, dict):
                return response_data.get("result", response_data)
            return response_data

        # Polling mode
        for poll_count in range(max_polls):
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                print(f"Scan completed after {poll_count} polls")
                response_data = response.json()
                if isinstance(response_data, dict):
                    return response_data.get("result", response_data)
                return response_data

            if response.status_code == 404:
                print(f"Poll {poll_count + 1}/{max_polls}: Scan in progress...")
                if poll_count < max_polls - 1:
                    time.sleep(poll_interval)
                continue

            response.raise_for_status()

        raise TimeoutError(
            f"Scan did not complete after {max_polls} polls "
            f"({max_polls * poll_interval} seconds)"
        )

    def search_scans(self, query: str) -> Dict[str, Any]:
        """
        Search for scans using ElasticSearch Query syntax.

        Args:
            query: Search query (e.g., 'page.domain:"google.com"')

        Returns:
            Response dictionary with search results

        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.BASE_URL}/{self.account_id}/urlscanner/v2/search"
        params = {"q": query}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        response_data = response.json()
        if isinstance(response_data, dict):
            return response_data.get("result", response_data)
        return response_data


def get_api_credentials_from_keyring(service_name: str = "svc_cloudflare_urlscanner") -> tuple[str, str]:
    """
    Retrieve Cloudflare API credentials from keyring.
    
    Args:
        service_name: The service name in keyring (default: "svc_cloudflare_urlscanner")
    
    Returns:
        Tuple of (api_token, account_id)
    
    Raises:
        ValueError: If credentials are not found in keyring
    """
    api_token = keyring.get_password(service_name, "api_token")
    account_id = keyring.get_password(service_name, "account_id")
    
    if not api_token:
        raise ValueError(
            "Cloudflare API Token not found in keyring.\n"
            "Please run 'Set API.py' to configure your credentials."
        )
    
    if not account_id:
        raise ValueError(
            "Cloudflare Account ID not found in keyring.\n"
            "Please run 'Set API.py' to configure your credentials."
        )
    
    return api_token, account_id


def print_header():
    """Print script header and information"""
    print("\n" + "="*80)
    print("Cloudflare URL Scanner - Interactive Mode")
    print("="*80 + "\n")
    print("This script allows you to submit URLs for scanning to Cloudflare Radar.")
    print("Scans will analyze websites for security threats, technologies, and metadata.\n")


def get_screenshot_options() -> Optional[List[str]]:
    """Get screenshot resolution options from user"""
    return ["desktop"]


def get_advanced_options() -> Dict[str, Any]:
    """Get advanced scan options from user"""
    options = {}
    
    print("\nAdvanced Options (press Enter to skip defaults):")
    
    custom_agent = input("Custom User-Agent (press Enter to skip): ").strip() or None
    if custom_agent:
        options["custom_agent"] = custom_agent
    
    referer = input("Custom Referer header (press Enter to skip): ").strip() or None
    if referer:
        options["referer"] = referer
    
    visibility = input("Visibility level - 'Public' or 'Unlisted' [default: Public]: ").strip() or "Public"
    if visibility in ["Public", "Unlisted"]:
        options["visibility"] = visibility
    else:
        print("Invalid visibility. Using default: Public")
        options["visibility"] = "Public"
    
    return options


def submit_single_url(scanner: CloudflareURLScanner):
    """Submit a single URL for scanning"""
    print("\n" + "-"*80)
    print("SUBMIT SINGLE URL FOR SCANNING")
    print("-"*80 + "\n")
    
    url = input("Enter URL to scan: ").strip()
    if not url:
        print("Error: URL cannot be empty")
        return
    
    # Ensure URL has a scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    screenshots = get_screenshot_options()
    advanced = get_advanced_options()
    
    config = ScanConfig(
        url=url,
        screenshots_resolutions=screenshots,
        custom_agent=advanced.get("custom_agent"),
        referer=advanced.get("referer"),
        visibility=advanced.get("visibility", "Public")
    )
    
    try:
        print(f"\nSubmitting '{url}' for scanning...")
        result = scanner.submit_url(config)
        
        print("\n✓ URL submitted successfully!")
        if isinstance(result, dict):
            print(f"  Scan ID: {result.get('id', result.get('uuid', 'N/A'))}")
            if result.get('visibility'):
                print(f"  Visibility: {result.get('visibility')}")
            if result.get('job_priority'):
                print(f"  Priority: {result.get('job_priority')}")
        else:
            print(f"  Response: {result}")
        
    except requests.RequestException as e:
        print(f"\n✗ API Error: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"  Response: {e.response.text}")


def get_scan_result(scanner: CloudflareURLScanner):
    """Retrieve scan results"""
    print("\n" + "-"*80)
    print("RETRIEVE SCAN RESULT")
    print("-"*80 + "\n")
    
    scan_id = input("Enter scan UUID: ").strip()
    if not scan_id:
        print("Error: Scan UUID cannot be empty")
        return
    
    poll = input("Poll until complete? (yes/no) [default: no]: ").strip().lower() in ["yes", "y"]
    
    try:
        result = scanner.get_scan_result(
            scan_id,
            poll=poll,
            poll_interval=10
        )
        
        print("\n✓ Scan result retrieved!")
        if isinstance(result, dict):
            task = result.get('task', {})
            print(f"  Status: {task.get('status')}")
            print(f"  Success: {task.get('success')}")
            print(f"  URL: {task.get('url')}")
            
            # Display verdict
            verdicts = result.get('verdicts', {})
            if verdicts:
                print(f"\n  Verdict:")
                if verdicts.get('overall'):
                    print(f"    Overall: {verdicts['overall'].get('verdict', 'N/A')}")
                    if verdicts['overall'].get('score') is not None:
                        print(f"    Score: {verdicts['overall'].get('score')}")
                
                malicious = verdicts.get('malicious')
                if malicious is not None:
                    print(f"    Malicious: {malicious}")
                
                phishing = verdicts.get('phishing')
                if phishing is not None:
                    print(f"    Phishing: {phishing}")
            
            # Show additional details if scan is complete
            if task.get('success'):
                page = result.get('page', {})
                meta = result.get('meta', {})
                print(f"\n  Page Details:")
                print(f"    Page URL: {page.get('url')}")
                print(f"    Country: {page.get('country')}")
                print(f"    IP Address: {page.get('ip')}")
                
                if meta.get('processors'):
                    print(f"    Technologies: {len(meta['processors'].get('wappa', []))} detected")
            
            # Write full result to JSON file
            json_filename = f"cloudflare_scan_result_{scan_id}.json"
            try:
                with open(json_filename, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n✓ Full result saved to: {json_filename}")
            except IOError as io_err:
                print(f"\n⚠ Warning: Could not save JSON file: {io_err}")
        else:
            print(f"  Response: {result}")
        
    except requests.RequestException as e:
        print(f"\n✗ API Error: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"  Response: {e.response.text}")


def search_scans(scanner: CloudflareURLScanner):
    """Search for previous scans"""
    print("\n" + "-"*80)
    print("SEARCH SCANS")
    print("-"*80 + "\n")
    
    print("ElasticSearch Query Examples:")
    print('  page.domain:"google.com"')
    print('  verdicts.malicious:true')
    print('  date:[2024-01 TO 2024-10]')
    print('  page.asn:AS24940\n')
    
    query = input("Enter search query: ").strip()
    if not query:
        print("Error: Search query cannot be empty")
        return
    
    try:
        print(f"\nSearching for scans: {query}...")
        result = scanner.search_scans(query)
        
        print("\n✓ Search completed!")
        if isinstance(result, (dict, list)):
            print(json.dumps(result, indent=2))
        else:
            print(result)
        
    except requests.RequestException as e:
        print(f"\n✗ API Error: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"  Response: {e.response.text}")


def main():
    """Main entry point with interactive menu"""
    print_header()
    
    try:
        api_token, account_id = get_api_credentials_from_keyring()
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    # Initialize scanner with retrieved credentials
    scanner = CloudflareURLScanner(api_token, account_id)
    
    while True:
        print("\n" + "="*80)
        print("SELECT AN OPTION:")
        print("="*80)
        print("  1 - Submit a single URL for scanning")
        print("  2 - Retrieve scan results")
        print("  3 - Search scans")
        print("  4 - Exit")
        print()
        
        choice = input("Enter selection (1-4): ").strip()
        
        if choice == "1":
            submit_single_url(scanner)
        elif choice == "2":
            get_scan_result(scanner)
        elif choice == "3":
            search_scans(scanner)
        elif choice == "4":
            print("\n✓ Exiting...\n")
            break
        else:
            print("Invalid option. Please enter a number between 1-4.")
    
    return 0


if __name__ == "__main__":
    exit(main())
