#!/usr/bin/env python3
"""
VirusTotal API v3 - URL Scanning and Report Retrieval Script
Submits URLs for scanning and retrieves analysis reports from previously scanned URLs.

This script provides the following functionality:
  1. Submit URLs for scanning (public scanning)
  2. Retrieve reports for URLs that have been scanned before
  3. Request URL rescan (re-analysis)
  4. Display detailed threat analysis

Requirements:
  - requests library: pip install requests
  - keyring library: pip install keyring
  - VirusTotal API key (stored in system keyring)

API Documentation: https://docs.virustotal.com/reference/
"""

import requests
import time
import json
import keyring
import urllib.parse
from datetime import datetime


def get_api_key():
    """
    Retrieve the VirusTotal API key from system keyring.
    Falls back to user input if not stored.
    """
    service_name = "svc_gti_enterprise"
    account_name = "gti_api_account"
    
    try:
        api_key = keyring.get_password(service_name, account_name)
        if api_key:
            return api_key
    except Exception:
        pass
    
    print("\n❌ VirusTotal API key not found in keyring.")
    print(f"   Please run 'Set API.py' to configure credentials.")
    print(f"   (Service: {service_name}, Account: {account_name})")
    return None


def get_headers(api_key):
    """Create request headers with authentication"""
    return {
        "accept": "application/json",
        "x-apikey": api_key,
        "content-type": "application/x-www-form-urlencoded"
    }


def encode_url_for_analysis(url):
    """
    Encode URL for VirusTotal API submission.
    VirusTotal expects URL encoded format for the 'url' parameter.
    """
    return url


def submit_url_for_scanning(url, api_key):
    """
    Submit a URL for scanning.
    
    Args:
        url: The URL to scan
        api_key: VirusTotal API key
        
    Returns:
        dict: Response containing analysis ID or error
    """
    submit_url = "https://www.virustotal.com/api/v3/urls"
    headers = get_headers(api_key)
    
    payload = {"url": url}
    
    try:
        print(f"\n📤 Submitting URL for scanning: {url}")
        response = requests.post(submit_url, data=payload, headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            analysis_id = result.get("data", {}).get("id")
            if analysis_id:
                print(f"✓ URL submitted successfully")
                print(f"  Analysis ID: {analysis_id}")
                return {"success": True, "analysis_id": analysis_id, "response": result}
            else:
                print(f"⚠️  No analysis ID in response")
                return {"success": False, "response": result}
        else:
            print(f"✗ Submission failed (Status {response.status_code}): {result}")
            return {"success": False, "response": result}
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Request error: {e}")
        return {"success": False, "error": str(e)}


def get_url_report(url, api_key):
    """
    Retrieve analysis report for a URL (if it exists).
    
    Args:
        url: The URL to get report for
        api_key: VirusTotal API key
        
    Returns:
        dict: Analysis report or error
    """
    # URL encoding for the API query
    url_id = urllib.parse.quote(url, safe='')
    report_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    headers = get_headers(api_key)
    
    try:
        print(f"\n🔍 Retrieving report for: {url}")
        response = requests.get(report_url, headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            print(f"✓ Report retrieved successfully")
            return {"success": True, "response": result}
        elif response.status_code == 404:
            print(f"⚠️  URL not found in VirusTotal database")
            print(f"   Consider submitting it for scanning first.")
            return {"success": False, "error": "URL not in database", "response": result}
        else:
            print(f"✗ Report retrieval failed (Status {response.status_code}): {result}")
            return {"success": False, "response": result}
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Request error: {e}")
        return {"success": False, "error": str(e)}


def get_analysis_report(analysis_id, api_key):
    """
    Retrieve analysis report using analysis ID.
    
    Args:
        analysis_id: The analysis ID returned from submission
        api_key: VirusTotal API key
        
    Returns:
        dict: Analysis report or error
    """
    report_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
    headers = get_headers(api_key)
    
    try:
        print(f"\n🔍 Retrieving analysis report: {analysis_id}")
        response = requests.get(report_url, headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            print(f"✓ Analysis report retrieved")
            return {"success": True, "response": result}
        elif response.status_code == 404:
            print(f"⚠️  Analysis not found")
            return {"success": False, "error": "Analysis not found", "response": result}
        else:
            print(f"✗ Report retrieval failed (Status {response.status_code}): {result}")
            return {"success": False, "response": result}
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Request error: {e}")
        return {"success": False, "error": str(e)}


def request_url_rescan(url, api_key):
    """
    Request a rescan (re-analysis) of a previously scanned URL.
    
    Args:
        url: The URL to rescan
        api_key: VirusTotal API key
        
    Returns:
        dict: Response containing new analysis ID or error
    """
    url_id = urllib.parse.quote(url, safe='')
    rescan_url = f"https://www.virustotal.com/api/v3/urls/{url_id}/analyse"
    headers = get_headers(api_key)
    
    try:
        print(f"\n🔄 Requesting URL rescan: {url}")
        response = requests.post(rescan_url, headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            analysis_id = result.get("data", {}).get("id")
            if analysis_id:
                print(f"✓ Rescan requested successfully")
                print(f"  New Analysis ID: {analysis_id}")
                return {"success": True, "analysis_id": analysis_id, "response": result}
            else:
                print(f"⚠️  No analysis ID in response")
                return {"success": False, "response": result}
        else:
            print(f"✗ Rescan request failed (Status {response.status_code}): {result}")
            return {"success": False, "response": result}
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Request error: {e}")
        return {"success": False, "error": str(e)}


def display_analysis_summary(analysis_data):
    """
    Display a formatted summary of the analysis results.
    
    Args:
        analysis_data: The analysis data from the API response
    """
    if not analysis_data or "data" not in analysis_data:
        print("⚠️  No analysis data available")
        return
    
    data = analysis_data.get("data", {})
    attributes = data.get("attributes", {})
    
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)
    
    # Basic information
    print(f"\n📋 Analysis Details:")
    print(f"  Status: {attributes.get('status', 'Unknown')}")
    print(f"  Type: {data.get('type', 'Unknown')}")
    
    # URL analysis specific
    if "url" in attributes:
        print(f"  URL: {attributes.get('url')}")
    if "last_analysis_date" in attributes:
        timestamp = attributes.get("last_analysis_date")
        if timestamp:
            dt = datetime.fromtimestamp(timestamp)
            print(f"  Last Analysis: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Threat statistics
    if "last_analysis_stats" in attributes:
        stats = attributes.get("last_analysis_stats", {})
        print(f"\n⚠️  Threat Statistics:")
        print(f"  Malicious: {stats.get('malicious', 0)}")
        print(f"  Suspicious: {stats.get('suspicious', 0)}")
        print(f"  Undetected: {stats.get('undetected', 0)}")
        print(f"  Timeout: {stats.get('timeout', 0)}")
        print(f"  Total Vendors: {stats.get('malicious', 0) + stats.get('suspicious', 0) + stats.get('undetected', 0) + stats.get('timeout', 0)}")
    
    # Categories
    if "categories" in attributes:
        categories = attributes.get("categories", {})
        if categories:
            print(f"\n🏷️  Categories:")
            for category, value in categories.items():
                print(f"  - {category}: {value}")
    
    # Last analysis results (vendors)
    if "last_analysis_results" in attributes:
        results = attributes.get("last_analysis_results", {})
        malicious_vendors = [
            vendor for vendor, result in results.items() 
            if result.get("category") == "malicious"
        ]
        
        if malicious_vendors:
            print(f"\n🚨 Malicious Detections ({len(malicious_vendors)}):")
            for vendor in malicious_vendors[:5]:  # Show first 5
                result = results[vendor]
                print(f"  - {vendor}: {result.get('result', 'Detection found')}")
            if len(malicious_vendors) > 5:
                print(f"  ... and {len(malicious_vendors) - 5} more")


def display_full_report(analysis_data, pretty_print=False):
    """
    Display the full analysis report.
    
    Args:
        analysis_data: The full analysis data
        pretty_print: Whether to pretty print the JSON
    """
    if pretty_print:
        print("\n" + "="*80)
        print("FULL ANALYSIS REPORT (JSON)")
        print("="*80)
        print(json.dumps(analysis_data, indent=2))
    else:
        return analysis_data


def interactive_menu(api_key):
    """
    Display interactive menu for URL scanning operations.
    
    Args:
        api_key: VirusTotal API key
    """
    while True:
        print("\n" + "="*80)
        print("VIRUSTOTAL URL SCANNING - MAIN MENU")
        print("="*80)
        print("""
Options:
  1 - Submit URL for scanning
  2 - Get URL report (if previously scanned)
  3 - Rescan a URL
  4 - Get analysis report by ID
  5 - Batch process URLs from file
  6 - Exit
        """)
        
        choice = input("Select option (1-6): ").strip()
        
        if choice == "1":
            url = input("\nEnter URL to scan: ").strip()
            if url:
                result = submit_url_for_scanning(url, api_key)
                if result.get("success"):
                    print(f"\n⏳ Wait a moment before checking report...")
                    time.sleep(5)
                    report = get_analysis_report(result.get("analysis_id"), api_key)
                    if report.get("success"):
                        display_analysis_summary(report.get("response"))
                        show_full = input("\n📄 Display full report? (y/n): ").strip().lower()
                        if show_full == 'y':
                            display_full_report(report.get("response"), pretty_print=True)
        
        elif choice == "2":
            url = input("\nEnter URL to get report for: ").strip()
            if url:
                report = get_url_report(url, api_key)
                if report.get("success"):
                    display_analysis_summary(report.get("response"))
                    show_full = input("\n📄 Display full report? (y/n): ").strip().lower()
                    if show_full == 'y':
                        display_full_report(report.get("response"), pretty_print=True)
        
        elif choice == "3":
            url = input("\nEnter URL to rescan: ").strip()
            if url:
                result = request_url_rescan(url, api_key)
                if result.get("success"):
                    print(f"\n⏳ Wait a moment before checking report...")
                    time.sleep(5)
                    report = get_analysis_report(result.get("analysis_id"), api_key)
                    if report.get("success"):
                        display_analysis_summary(report.get("response"))
        
        elif choice == "4":
            analysis_id = input("\nEnter Analysis ID: ").strip()
            if analysis_id:
                report = get_analysis_report(analysis_id, api_key)
                if report.get("success"):
                    display_analysis_summary(report.get("response"))
                    show_full = input("\n📄 Display full report? (y/n): ").strip().lower()
                    if show_full == 'y':
                        display_full_report(report.get("response"), pretty_print=True)
        
        elif choice == "5":
            batch_process_urls(api_key)
        
        elif choice == "6":
            print("\n👋 Exiting...")
            break
        
        else:
            print("\n❌ Invalid option. Please select 1-6.")


def batch_process_urls(api_key):
    """
    Process multiple URLs from a file.
    
    Args:
        api_key: VirusTotal API key
    """
    file_path = input("\nEnter path to file with URLs (one per line): ").strip()
    
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    if not urls:
        print("⚠️  No URLs found in file")
        return
    
    print(f"\n📋 Found {len(urls)} URLs to process")
    operation = input("Select operation: (1) Submit for scanning, (2) Get reports: ").strip()
    
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        
        if operation == "1":
            result = submit_url_for_scanning(url, api_key)
            results.append({"url": url, "analysis_id": result.get("analysis_id"), "success": result.get("success")})
        elif operation == "2":
            result = get_url_report(url, api_key)
            results.append({"url": url, "success": result.get("success"), "status": result.get("response", {}).get("data", {}).get("attributes", {}).get("status")})
        
        # Add delay to avoid rate limiting
        if i < len(urls):
            time.sleep(2)
    
    # Display summary
    print("\n" + "="*80)
    print("BATCH PROCESSING SUMMARY")
    print("="*80)
    for result in results:
        status = "✓" if result.get("success") else "✗"
        print(f"{status} {result.get('url')}")
        if result.get("analysis_id"):
            print(f"   Analysis ID: {result.get('analysis_id')}")
    
    # Save results
    save_option = input("\nSave results to file? (y/n): ").strip().lower()
    if save_option == 'y':
        output_file = "scan_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Results saved to {output_file}")


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("VIRUSTOTAL API v3 - URL SCANNING & REPORTING")
    print("="*80)
    print("\nDocumentation: https://docs.virustotal.com/reference/analysis")
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("❌ No API key provided. Exiting.")
        exit(1)
    
    # Show interactive menu
    interactive_menu(api_key)


if __name__ == "__main__":
    main()
