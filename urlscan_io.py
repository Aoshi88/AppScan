#!/usr/bin/env python3
"""
URLSCAN.io URL Submission and Result Retrieval Script

This script submits URLs to urlscan.io for scanning and retrieves the scan results.
The API key is retrieved from the system keyring as configured by "Set API - URLScan.py"

Features:
  - Submit single URLs for scanning
  - Poll for scan completion
  - Display formatted scan results
  - Export results to JSON file

Requirements:
  - requests library: pip install requests
  - keyring library: pip install keyring
  - URLSCAN.io API key configured via "Set API - URLScan.py"

Usage:
  python "URLscanIO - URL Scan.py"
"""

import requests
import time
import json
import sys
import keyring
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path


class URLScanIOScanner:
    """Client for URLSCAN.io URL submission and result retrieval"""
    
    BASE_URL = "https://urlscan.io"
    SERVICE_NAME = "svc_urlscan_io"
    API_KEY_NAME = "api_key"
    
    def __init__(self, timeout: int = 30, max_wait: int = 600, poll_interval: int = 10):
        """
        Initialize URLSCAN.io scanner client
        
        Args:
            timeout: Request timeout in seconds (default: 30)
            max_wait: Maximum time to wait for scan completion in seconds (default: 600)
            poll_interval: Interval between polls in seconds (default: 10)
        """
        self.timeout = timeout
        self.max_wait = max_wait
        self.poll_interval = poll_interval
        self.api_key = None
        self.session = requests.Session()
        
        # Load API key from keyring
        self._load_api_key()
    
    def _load_api_key(self) -> bool:
        """Load API key from keyring"""
        try:
            self.api_key = keyring.get_password(self.SERVICE_NAME, self.API_KEY_NAME)
            
            if not self.api_key:
                print("❌ Error: No API key found in keyring")
                print("   Please configure your API key using 'Set API - URLScan.py'")
                return False
            
            self.session.headers.update({
                "API-Key": self.api_key,
                "Content-Type": "application/json"
            })
            print("✅ API key loaded from keyring")
            return True
            
        except Exception as e:
            print(f"❌ Error loading API key from keyring: {e}")
            return False
    
    def submit_url(self, url: str, visibility: str = "public", country: Optional[str] = None, 
                   tags: Optional[List[str]] = None, override_safety: bool = False, 
                   referer: Optional[str] = None, custom_agent: Optional[str] = None) -> Optional[str]:
        """
        Submit a URL for scanning
        
        Args:
            url: The URL to scan
            visibility: Visibility of the scan - "public", "unlisted", or "private" (default: "public")
            country: ISO 3166-1 alpha-2 country code for scanning location (optional)
            tags: List of user-defined tags to annotate the scan (max 10, optional)
            override_safety: If True, disables reclassification of URLs with potential PII (default: False)
            referer: Override HTTP referer for this scan (optional)
            custom_agent: Override HTTP User-Agent for this scan (optional)
        
        Returns:
            UUID of the scan if successful, None if failed
        """
        if not self.api_key:
            print("❌ Error: API key not loaded")
            return None
        
        # Validate visibility parameter
        if visibility not in ["public", "unlisted", "private"]:
            print(f"❌ Error: Invalid visibility '{visibility}'. Must be 'public', 'unlisted', or 'private'")
            return None
        
        payload = {
            "url": url,
            "visibility": visibility
        }
        
        if country:
            payload["country"] = country.lower()
        if tags:
            if len(tags) > 10:
                print("⚠️  Warning: Maximum 10 tags allowed, truncating to first 10")
                tags = tags[:10]
            payload["tags"] = tags
        if override_safety:
            payload["overrideSafety"] = True
        if referer:
            payload["referer"] = referer
        if custom_agent:
            payload["customagent"] = custom_agent
        
        try:
            print(f"[*] Submitting URL for scanning: {url}")
            response = self.session.post(f"{self.BASE_URL}/api/v1/scan", json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            uuid = result.get("uuid")
            if uuid:
                print(f"[+] Scan submitted successfully — UUID: {uuid}")
                return uuid
            
            print(f"[-] No UUID in response: {result}")
            return None
                
        except requests.exceptions.RequestException as e:
            print(f"[-] Error submitting URL: {e}")
            resp = getattr(e, 'response', None)
            if resp is not None:
                try:
                    print(f"    Response: {resp.json()}")
                except Exception:
                    print(f"    Response: {resp.text}")
            return None
    
    def get_results(self, uuid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve scan results
        
        Args:
            uuid: The UUID of the scan
        
        Returns:
            Dictionary containing scan results, or None if failed
        """
        if not self.api_key:
            print("❌ Error: API key not loaded")
            return None
        
        try:
            response = self.session.get(f"{self.BASE_URL}/api/v1/result/{uuid}/", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code != 404:
                print(f"[-] Error retrieving results: HTTP {e.response.status_code}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[-] Error retrieving results: {e}")
            return None
    
    def get_scan_report(self, uuid: str, verbose: bool = True) -> Optional[Dict[str, Any]]:
        """
        Retrieve complete scan report by UUID
        
        Args:
            uuid: The UUID of the scan
            verbose: If True, print status messages (default: True)
        
        Returns:
            Dictionary containing the full scan report, or None if failed
        """
        if verbose:
            print(f"[*] Retrieving scan report for UUID: {uuid}")
        
        results = self.get_results(uuid)
        if not results:
            if verbose:
                print(f"[-] Failed to retrieve scan report for UUID: {uuid}")
            return None
        
        if verbose:
            if "page" in results or "data" in results:
                print("[+] Scan report retrieved successfully!")
            else:
                print("[*] Scan is pending or in-progress")
        
        return results
    
    def wait_for_results(self, uuid: str) -> Optional[Dict[str, Any]]:
        """
        Poll for scan results until completion or timeout
        
        Args:
            uuid: The UUID of the scan
        
        Returns:
            Dictionary containing scan results, or None if timeout/failed
        """
        start_time = time.time()
        print(f"\n[*] Waiting for scan to complete (max {self.max_wait}s)...")
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > self.max_wait:
                print(f"[-] Timeout waiting for results (exceeded {self.max_wait} seconds)")
                return None
            
            print(f"[*] Checking results... (elapsed: {int(elapsed)}s)")
            results = self.get_results(uuid)
            if results and ("page" in results or "data" in results):
                print("[+] Scan completed successfully!")
                return results
            
            time.sleep(self.poll_interval)
    
    def scan_url(self, url: str, visibility: str = "public", country: Optional[str] = None,
                tags: Optional[List[str]] = None, referer: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Complete workflow: submit URL and wait for results
        
        Args:
            url: The URL to scan
            visibility: Visibility of the scan - "public", "unlisted", or "private" (default: "public")
            country: ISO 3166-1 alpha-2 country code for scanning location (optional)
            tags: List of user-defined tags to annotate the scan (max 10, optional)
            referer: Override HTTP referer for this scan (optional)
        
        Returns:
            Dictionary containing scan results, or None if failed
        """
        uuid = self.submit_url(url, visibility=visibility, country=country, tags=tags, referer=referer)
        if not uuid:
            return None
        
        results = self.wait_for_results(uuid)
        if results:
            print("\n[+] Scan results retrieved successfully")
        return results
    



def print_summary(results: Dict[str, Any]) -> None:
    """Print a formatted summary of scan results"""
    if not results:
        return
    
    print("\n" + "="*80)
    print("SCAN RESULTS SUMMARY")
    print("="*80)
    
    # Basic info
    page = results.get("page", {})
    print(f"\n📄 URL Information:")
    print(f"   URL: {page.get('url', 'N/A')}")
    print(f"   Title: {page.get('title', 'N/A')}")
    print(f"   Domain: {page.get('domain', 'N/A')}")
    print(f"   IP: {page.get('ip', 'N/A')}")
    print(f"   Country: {page.get('country', 'N/A')}")
    print(f"   ASN: {page.get('asn', 'N/A')}")
    print(f"   Server: {page.get('server', 'N/A')}")
    
    # Verdicts
    verdicts = results.get("verdicts", {})
    print(f"\n🔒 Security Verdicts:")
    overall = verdicts.get('overall', {})
    print(f"   Overall: {overall.get('description', 'N/A')} ({overall.get('score', 'N/A')})")
    print(f"   URL Malicious: {verdicts.get('urlmalicious', {}).get('description', 'N/A')}")
    print(f"   Phishing: {verdicts.get('phishing', {}).get('description', 'N/A')}")
    print(f"   Malware: {verdicts.get('malware', {}).get('description', 'N/A')}")
    
    # Stats
    print(f"\n📊 Page Statistics:")
    stats = results.get("stats", {})
    print(f"   Total Requests: {stats.get('totalRequests', 'N/A')}")
    print(f"   Finished Requests: {stats.get('finishedRequests', 'N/A')}")
    print(f"   Successful Requests: {stats.get('successfulRequests', 'N/A')}")
    print(f"   Failed Requests: {stats.get('failedRequests', 'N/A')}")
    print(f"   Malicious Requests: {stats.get('maliciousRequests', 'N/A')}")
    
    # Links
    links = results.get("links", [])
    print(f"\n🔗 External Links: {len(links)} found")
    if links:
        print("   First 5 links:")
        for link in links[:5]:
            print(f"      - {link}")
    
    # Technologies
    tech = results.get("technologies", [])
    if tech:
        print(f"\n⚙️  Technologies Detected: {len(tech)}")
        for t in tech[:10]:
            print(f"   - {t.get('name', 'Unknown')} {t.get('version', '')}")
    
    print("\n" + "="*80)


def save_results(results: Dict[str, Any], filename: Optional[str] = None) -> bool:
    """Save scan results to JSON file"""
    try:
        if not filename:
            uuid = results.get('uuid')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if uuid:
                filename = f"urlscan_results_{uuid}_{timestamp}.json"
            else:
                filename = f"urlscan_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Full results saved to: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving results to file: {e}")
        return False


def get_urls_from_input() -> List[str]:
    """Get URLs from user input"""
    print("\n📝 Enter URLs (one per line). Submit an empty line to finish:")
    urls: List[str] = []
    while True:
        line = input().strip()
        if not line:
            break
        if not line.startswith(("http://", "https://")):
            line = "https://" + line
        urls.append(line)
    return urls


def retrieve_scan_by_uuid(scanner: 'URLScanIOScanner', uuid: str) -> bool:
    """Retrieve and display scan results by UUID"""
    print(f"\n[*] Retrieving scan results for UUID: {uuid}")
    
    results = scanner.get_results(uuid)
    
    if results:
        if "page" in results or "data" in results:
            print(f"[+] Scan results retrieved successfully!")
            print_summary(results)
            save_results(results)
            return True
        else:
            print(f"[*] Scan is still in progress or pending")
            print(f"   Available fields: {', '.join(results.keys())}")
            return False
    else:
        print(f"[-] Failed to retrieve scan results for UUID: {uuid}")
        return False


def get_urls_from_file(filename: str) -> List[str]:
    """Read URLs from a text file (one URL per line)"""
    path = Path(filename).expanduser()
    if not path.is_file():
        print(f"❌ File not found: {filename}")
        return []
    
    urls: List[str] = []
    try:
        with path.open('r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if not url or url.startswith('#'):
                    continue
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                urls.append(url)
        print(f"✅ Loaded {len(urls)} URL(s) from {filename}")
    except Exception as e:
        print(f"❌ Error reading file {filename}: {e}")
    
    return urls


def get_scan_report_by_uuid(uuid: str, display_summary: bool = True, save_to_file: bool = True) -> Optional[Dict[str, Any]]:
    """
    Retrieve and optionally display a scan report by UUID
    
    Args:
        uuid: The UUID of the scan to retrieve
        display_summary: If True, print formatted summary of results (default: True)
        save_to_file: If True, save results to JSON file (default: True)
    
    Returns:
        Dictionary containing scan results, or None if failed
    """
    # Initialize scanner
    scanner = URLScanIOScanner()
    
    if not scanner.api_key:
        print("❌ Cannot retrieve scan report without API key")
        print("   Please configure your API key using 'Set API - URLScan.py'")
        return None
    
    # Get the report
    report = scanner.get_scan_report(uuid, verbose=True)
    
    if report:
        if display_summary:
            print_summary(report)
        
        if save_to_file:
            save_results(report)
        
        return report
    else:
        return None



def main():
    """Main function"""
    print("\n" + "="*80)
    print("URLSCAN.IO URL SCANNER")
    print("="*80)
    
    # Initialize scanner
    scanner = URLScanIOScanner()
    
    if not scanner.api_key:
        print("\n❌ Cannot proceed without API key")
        print("   Please run 'Set API - URLScan.py' first to configure your URLSCAN.io API key")
        sys.exit(1)
    
    # Main menu
    print("\n" + "-"*80)
    print("Main Menu")
    print("-"*80)
    print("  1 - Submit new URLs for scanning")
    print("  2 - Retrieve existing scan by UUID")
    print("  3 - Exit")
    
    main_choice = input("\nSelect option (1-3): ").strip()
    
    if main_choice == "1":
        # Submit new URLs workflow
        submit_new_urls(scanner)
    elif main_choice == "2":
        # Retrieve single scan
        uuid = input("\nEnter Scan UUID (e.g., 68e26c59-2eae-437b-aeb1-cf750fafe7d7): ").strip()
        if uuid:
            retrieve_scan_by_uuid(scanner, uuid)
        else:
            print("❌ No UUID provided")
            sys.exit(1)
    elif main_choice == "3":
        print("\n✅ Goodbye!\n")
        sys.exit(0)
    else:
        print("❌ Invalid option")
        sys.exit(1)


def submit_new_urls(scanner: 'URLScanIOScanner'):
    """Workflow for submitting new URLs for scanning"""
    print("\n" + "-"*80)
    print("Import Options")
    print("-"*80)
    print("  1 - Enter URLs manually (one per line)")
    print("  2 - Load URLs from a file")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    urls = []
    if choice == "1":
        urls = get_urls_from_input()
    elif choice == "2":
        filename = input("Enter filename (e.g., urls.txt): ").strip()
        urls = get_urls_from_file(filename)
    else:
        print("❌ Invalid option")
        sys.exit(1)
    
    if not urls:
        print("❌ No URLs provided")
        sys.exit(1)
    
    if len(urls) > 1:
        print("⚠️  Only single URL scanning is supported. Using first URL.")
        urls = urls[:1]
    
    print(f"\n✅ Scanning URL: {urls[0]}")
    
    # Ask for visibility option
    print("\nVisibility options:")
    print("  1 - public   (visible to everyone)")
    print("  2 - unlisted (not searchable, but accessible via link)")
    print("  3 - private  (only visible to your account)")
    visibility_choice = input("\nSelect visibility (1-3) [1]: ").strip()
    
    visibility_map = {"1": "public", "2": "unlisted", "3": "private"}
    visibility = visibility_map.get(visibility_choice, "public")
    
    # Ask for country option
    country = input("\nScan from specific country? (e.g., us, de, jp) [random]: ").strip().lower() or None
    
    # Start scanning
    print("\n" + "="*80)
    print("STARTING SCANS")
    print("="*80)
    
    results = scanner.scan_url(urls[0], visibility=visibility, country=country)
    if results:
        print_summary(results)
        save_results(results)
    else:
        print("❌ Scan failed")
        sys.exit(1)
    
    print("\n✅ Scanning completed!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
