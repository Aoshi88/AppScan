#!/usr/bin/env python3
"""
API Key Configuration Script
Securely stores and manages API credentials for multiple services using the system keyring.

This script allows you to configure and manage:
  - URLSCAN.io API key
  - GTI Enterprise API key

Features for each API:
  - Set credentials securely
  - Retrieve stored credentials
  - Delete credentials
  - Test API connectivity (URLSCAN.io only)

Requirements:
  - keyring library: pip install keyring
  - For URLSCAN.io: https://urlscan.io/
  - For GTI Enterprise: Contact your GTI administrator
"""

import keyring
import sys
from keyring.errors import PasswordDeleteError


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(title)
    print("="*80 + "\n")


def print_section(title):
    """Print a formatted section header"""
    print("-"*80)
    print(title)
    print("-"*80 + "\n")


# ============================================================================
# URLSCAN.io Functions
# ============================================================================

def urlscan_set_api_key(service_name, api_key_name):
    """Set the URLSCAN.io API key in keyring"""
    print_section("SET URLSCAN.IO API KEY")
    
    # Get service name
    custom_service = input(f"Enter service name [{service_name}]: ").strip() or service_name
    
    # Get API key
    print("\nℹ️  You can get your API key from: https://urlscan.io/user/profile/")
    api_key = input("Enter your URLSCAN.io API Key: ").strip()
    
    if not api_key:
        print("❌ Error: API Key cannot be empty")
        return False
    
    if len(api_key) < 10:
        print("❌ Error: API Key appears to be too short. Please verify.")
        return False
    
    try:
        keyring.set_password(custom_service, api_key_name, api_key)
        print(f"\n✅ API Key saved successfully!\n")
        print(f"   Service: {custom_service}")
        print(f"   Username: {api_key_name}\n")
        return True
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        return False


def urlscan_get_api_key(service_name, api_key_name):
    """Retrieve the URLSCAN.io API key from keyring"""
    print_section("RETRIEVE URLSCAN.IO API KEY")
    
    # Get service name
    custom_service = input(f"Enter service name [{service_name}]: ").strip() or service_name
    
    try:
        api_key = keyring.get_password(custom_service, api_key_name)
        
        if api_key:
            print(f"✅ API Key retrieved successfully!\n")
            print(f"   Service: {custom_service}")
            print(f"   Username: {api_key_name}")
            print(f"   API Key: {api_key[:8]}***{'*' * (len(api_key) - 11)}{api_key[-3:]}\n")
            
            # Ask if user wants to see full key
            show_full = input("Show full API key? (y/n) [n]: ").strip().lower()
            if show_full == 'y':
                print(f"   Full API Key: {api_key}\n")
            
            return api_key
        else:
            print(f"❌ No API key found for service: {custom_service}\n")
            return None
    except Exception as e:
        print(f"❌ Error retrieving API key: {e}")
        return None


def urlscan_delete_api_key(service_name, api_key_name):
    """Delete the URLSCAN.io API key from keyring"""
    print_section("DELETE URLSCAN.IO API KEY")
    
    # Get service name
    custom_service = input(f"Enter service name [{service_name}]: ").strip() or service_name
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete the API key for '{custom_service}'? (y/n) [n]: ").strip().lower()
    if confirm != 'y':
        print("Deletion cancelled.\n")
        return False
    
    try:
        keyring.delete_password(custom_service, api_key_name)
        print(f"\n✅ API Key deleted successfully!\n")
        print(f"   Service: {custom_service}\n")
        return True
    except PasswordDeleteError:
        print(f"\n❌ Error: No API key found for service '{custom_service}'")
        print("   The credentials may have already been deleted or don't exist.\n")
        return False
    except Exception as e:
        print(f"❌ Error deleting API key: {e}")
        return False


def urlscan_test_api_key(service_name, api_key_name):
    """Test the URLSCAN.io API key connectivity"""
    print_section("TEST URLSCAN.IO API KEY")
    
    try:
        import requests
    except ImportError:
        print("❌ Error: 'requests' library is required to test API connectivity")
        print("   Install it with: pip install requests\n")
        return False
    
    # Get service name
    custom_service = input(f"Enter service name [{service_name}]: ").strip() or service_name
    
    # Retrieve API key from keyring
    api_key = keyring.get_password(custom_service, api_key_name)
    
    if not api_key:
        print(f"❌ No API key found for service: {custom_service}\n")
        return False
    
    print(f"Testing API key for service: {custom_service}...")
    print("Connecting to URLSCAN.io API...\n")
    
    try:
        headers = {
            "API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        # Test API connectivity with a simple quota request
        response = requests.get(
            "https://urlscan.io/api/v3/quota/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            quota_data = response.json()
            print(f"✅ API Key is valid!\n")
            print(f"   Service: {custom_service}")
            print(f"   API Status: Connected")
            
            # Display quota information if available
            if "quota" in quota_data:
                quota = quota_data.get("quota", {})
                print(f"\n   Quota Information:")
                print(f"   - Limit: {quota.get('limit', 'N/A')}")
                print(f"   - Remaining: {quota.get('remaining', 'N/A')}")
                print(f"   - Reset: {quota.get('resetTime', 'N/A')}\n")
            
            return True
        elif response.status_code == 401:
            print(f"❌ Unauthorized: Invalid or expired API key\n")
            print(f"   Status Code: {response.status_code}")
            print(f"   Please verify your API key and try again.\n")
            return False
        else:
            print(f"❌ API returned status code: {response.status_code}\n")
            print(f"   Response: {response.text}\n")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Error: Request timeout. Please check your internet connection.\n")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to URLSCAN.io API.\n")
        print(f"   Please check your internet connection or try again later.\n")
        return False
    except Exception as e:
        print(f"❌ Error testing API key: {e}\n")
        return False


# ============================================================================
# GTI Enterprise Functions
# ============================================================================

def gti_set_api_key():
    """Set the GTI Enterprise API key in keyring"""
    print_section("SET GTI ENTERPRISE API KEY")
    
    print("Enter the API key below, you may skip configuring the default service account name and system name\n")
    print("DO NOT LEAVE API key field empty!\n")
    
    systemname_key = input("Please enter the system name [default: svc_softwareassessment]: ").strip() or "svc_softwareassessment"
    servicename_key = input("Please enter the service account name [default: svc_softwareassessment]: ").strip() or "svc_softwareassessment"
    api_key = input("Please enter the GTI API key: ").strip()

    if not api_key:
        print("❌ Error: API key cannot be empty")
        return False

    try:
        keyring.set_password(systemname_key, servicename_key, api_key)
        print(f"\n✅ API key saved in keyring:\n")
        print(f"   Service (system name): {systemname_key}")
        print(f"   Username (service account): {servicename_key}\n")
        return True
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        return False


def gti_get_api_key():
    """Retrieve the GTI Enterprise API key from keyring"""
    print_section("RETRIEVE GTI ENTERPRISE API KEY")
    
    systemname_key = input("Please enter the system name [default: svc_softwareassessment]: ").strip() or "svc_softwareassessment"
    servicename_key = input("Please enter the service account name [default: svc_softwareassessment]: ").strip() or "svc_softwareassessment"
    
    try:
        api_key = keyring.get_password(systemname_key, servicename_key)
        if api_key:
            print(f"\n✅ API key retrieved from keyring:\n")
            print(f"   Service (system name): {systemname_key}")
            print(f"   Username (service account): {servicename_key}")
            print(f"   API Key: {api_key[:10]}...\n")
            return True
        else:
            print(f"❌ No API key found for the provided service and username.\n")
            return False
    except Exception as e:
        print(f"❌ Error retrieving API key: {e}")
        return False


def gti_delete_api_key():
    """Delete the GTI Enterprise API key from keyring"""
    print_section("DELETE GTI ENTERPRISE API KEY")
    
    systemname_key = input("Please enter the system name [default: svc_softwareassessment]: ").strip() or "svc_softwareassessment"
    servicename_key = input("Please enter the service account name [default: svc_softwareassessment]: ").strip() or "svc_softwareassessment"
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete the API key for '{systemname_key}'? (y/n) [n]: ").strip().lower()
    if confirm != 'y':
        print("Deletion cancelled.\n")
        return False
    
    try:
        keyring.delete_password(systemname_key, servicename_key)
        print(f"\n✅ API key removed from keyring:\n")
        print(f"   Service (system name): {systemname_key}")
        print(f"   Username (service account): {servicename_key}\n")
        return True
    except PasswordDeleteError:
        print(f"❌ Error: API key not found or cannot be deleted.\n")
        return False
    except Exception as e:
        print(f"❌ Error deleting API key: {e}")
        return False


# ============================================================================
# Menu Functions
# ============================================================================

def urlscan_menu():
    """URLSCAN.io configuration menu"""
    service_name = "svc_urlscan"
    api_key_name = "api_key"
    
    while True:
        print_header("URLSCAN.IO API KEY MANAGER")
        
        print("Select an option:")
        print("  1 - Set API Key")
        print("  2 - Retrieve API Key")
        print("  3 - Delete API Key")
        print("  4 - Test API Key")
        print("  5 - Back to main menu")
        
        choice = input("\nEnter selection (1-5): ").strip()
        
        if choice == "1":
            urlscan_set_api_key(service_name, api_key_name)
        elif choice == "2":
            urlscan_get_api_key(service_name, api_key_name)
        elif choice == "3":
            urlscan_delete_api_key(service_name, api_key_name)
        elif choice == "4":
            urlscan_test_api_key(service_name, api_key_name)
        elif choice == "5":
            return
        else:
            print("❌ Invalid option. Please enter 1-5.\n")
            input("Press Enter to continue...")
            continue
        
        input("Press Enter to continue...")


def gti_menu():
    """GTI Enterprise configuration menu"""
    while True:
        print_header("GTI ENTERPRISE API KEY MANAGER")
        
        print("Select an option:")
        print("  1 - Set API Key")
        print("  2 - Retrieve API Key")
        print("  3 - Delete API Key")
        print("  4 - Back to main menu")
        
        choice = input("\nEnter selection (1-4): ").strip()
        
        if choice == "1":
            gti_set_api_key()
        elif choice == "2":
            gti_get_api_key()
        elif choice == "3":
            gti_delete_api_key()
        elif choice == "4":
            return
        else:
            print("❌ Invalid option. Please enter 1-4.\n")
            input("Press Enter to continue...")
            continue
        
        input("Press Enter to continue...")


def main():
    """Main menu"""
    while True:
        print_header("API CREDENTIALS CONFIGURATION")
        
        print("Select which API credentials to configure:")
        print("  1 - URLSCAN.io")
        print("  2 - GTI Enterprise")
        print("  3 - Exit")
        
        choice = input("\nEnter selection (1-3): ").strip()
        
        if choice == "1":
            urlscan_menu()
        elif choice == "2":
            gti_menu()
        elif choice == "3":
            print("\n✅ Goodbye!\n")
            sys.exit(0)
        else:
            print("❌ Invalid option. Please enter 1-3.\n")
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)
