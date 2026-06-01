#!/usr/bin/env python3
"""
Unified API Credentials Configuration Script
Securely stores and manages API credentials for multiple services using the system keyring.

This script allows you to configure and manage:
  - Cloudflare URL Scanner (API Token + Account ID)
  - URLSCAN.io API key
  - GTI Enterprise API key

Requirements:
  - keyring library: pip install keyring
  - requests library (optional): pip install requests (for URLSCAN.io testing)
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
# CLOUDFLARE Functions
# ============================================================================

def cloudflare_set_credentials(service_name):
    """Set Cloudflare API credentials in keyring"""
    print_section("SET CLOUDFLARE URL SCANNER CREDENTIALS")
    
    print(f"ℹ️  Get your credentials from: https://dash.cloudflare.com/")
    print(f"Service name: {service_name}\n")
    
    api_token = input("Enter Cloudflare API Token: ").strip()
    if not api_token:
        print("❌ Error: API Token cannot be empty")
        return False
    
    account_id = input("Enter Cloudflare Account ID: ").strip()
    if not account_id:
        print("❌ Error: Account ID cannot be empty")
        return False
    
    try:
        keyring.set_password(service_name, "api_token", api_token)
        keyring.set_password(service_name, "account_id", account_id)
        print(f"\n✅ Cloudflare credentials saved successfully!\n")
        print(f"   Service: {service_name}\n")
        return True
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")
        return False


def cloudflare_get_credentials(service_name):
    """Retrieve Cloudflare API credentials from keyring"""
    print_section("RETRIEVE CLOUDFLARE URL SCANNER CREDENTIALS")
    
    try:
        api_token = keyring.get_password(service_name, "api_token")
        account_id = keyring.get_password(service_name, "account_id")
        
        if api_token and account_id:
            print(f"✅ Cloudflare credentials retrieved successfully!\n")
            print(f"   Service: {service_name}")
            print(f"   API Token: {api_token[:10]}...{api_token[-5:]}")
            print(f"   Account ID: {account_id}\n")
            return True
        else:
            print(f"❌ No credentials found for service: {service_name}\n")
            return False
    except Exception as e:
        print(f"❌ Error retrieving credentials: {e}")
        return False


def cloudflare_delete_credentials(service_name):
    """Delete Cloudflare API credentials from keyring"""
    print_section("DELETE CLOUDFLARE URL SCANNER CREDENTIALS")
    
    confirm = input(f"Are you sure you want to delete credentials for '{service_name}'? (y/n) [n]: ").strip().lower()
    if confirm != 'y':
        print("Deletion cancelled.\n")
        return False
    
    try:
        keyring.delete_password(service_name, "api_token")
        keyring.delete_password(service_name, "account_id")
        print(f"\n✅ Cloudflare credentials deleted successfully!\n")
        print(f"   Service: {service_name}\n")
        return True
    except PasswordDeleteError:
        print(f"❌ Error: Credentials not found or cannot be deleted.\n")
        return False
    except Exception as e:
        print(f"❌ Error deleting credentials: {e}")
        return False


def cloudflare_menu():
    """Cloudflare configuration menu"""
    service_name = "svc_cloudflare_urlscanner"
    
    while True:
        print_header("CLOUDFLARE URL SCANNER CREDENTIALS MANAGER")
        
        print(f"Current Service ID: {service_name}\n")
        print("Select an option:")
        print("  1 - Set credentials")
        print("  2 - Retrieve credentials")
        print("  3 - Delete credentials")
        print("  4 - Back to main menu")
        
        choice = input("\nEnter selection (1-4): ").strip()
        
        if choice == "1":
            cloudflare_set_credentials(service_name)
        elif choice == "2":
            cloudflare_get_credentials(service_name)
        elif choice == "3":
            cloudflare_delete_credentials(service_name)
        elif choice == "4":
            return
        else:
            print("❌ Invalid option. Please enter 1-4.\n")
            input("Press Enter to continue...")
            continue
        
        input("Press Enter to continue...")


# ============================================================================
# URLSCAN.io Functions
# ============================================================================

def urlscan_set_api_key(service_name, api_key_name):
    """Set the URLSCAN.io API key in keyring"""
    print_section("SET URLSCAN.IO API KEY")
    
    print(f"ℹ️  Get your API key from: https://urlscan.io/user/profile/")
    print(f"Service name: {service_name}\n")
    
    api_key = input("Enter your URLSCAN.io API Key: ").strip()
    
    if not api_key:
        print("❌ Error: API Key cannot be empty")
        return False
    
    if len(api_key) < 10:
        print("❌ Error: API Key appears to be too short. Please verify.")
        return False
    
    try:
        keyring.set_password(service_name, api_key_name, api_key)
        print(f"\n✅ API Key saved successfully!\n")
        print(f"   Service: {service_name}")
        print(f"   Username: {api_key_name}\n")
        return True
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        return False


def urlscan_get_api_key(service_name, api_key_name):
    """Retrieve the URLSCAN.io API key from keyring"""
    print_section("RETRIEVE URLSCAN.IO API KEY")
    
    try:
        api_key = keyring.get_password(service_name, api_key_name)
        
        if api_key:
            print(f"✅ API Key retrieved successfully!\n")
            print(f"   Service: {service_name}")
            print(f"   Username: {api_key_name}")
            print(f"   API Key: {api_key[:8]}***{'*' * (len(api_key) - 11)}{api_key[-3:]}\n")
            
            show_full = input("Show full API key? (y/n) [n]: ").strip().lower()
            if show_full == 'y':
                print(f"   Full API Key: {api_key}\n")
            
            return api_key
        else:
            print(f"❌ No API key found for service: {service_name}\n")
            return None
    except Exception as e:
        print(f"❌ Error retrieving API key: {e}")
        return None


def urlscan_delete_api_key(service_name, api_key_name):
    """Delete the URLSCAN.io API key from keyring"""
    print_section("DELETE URLSCAN.IO API KEY")
    
    confirm = input(f"Are you sure you want to delete the API key for '{service_name}'? (y/n) [n]: ").strip().lower()
    if confirm != 'y':
        print("Deletion cancelled.\n")
        return False
    
    try:
        keyring.delete_password(service_name, api_key_name)
        print(f"\n✅ API Key deleted successfully!\n")
        print(f"   Service: {service_name}\n")
        return True
    except PasswordDeleteError:
        print(f"❌ Error: No API key found for service '{service_name}'")
        print("   The credentials may have already been deleted or don't exist.\n")
        return False
    except Exception as e:
        print(f"❌ Error deleting API key: {e}")
        return False





def urlscan_menu():
    """URLSCAN.io configuration menu"""
    service_name = "svc_urlscan_io"
    api_key_name = "api_key"
    
    while True:
        print_header("URLSCAN.IO API KEY MANAGER")
        
        print(f"Current Service ID: {service_name}\n")
        print("Select an option:")
        print("  1 - Set API Key")
        print("  2 - Retrieve API Key")
        print("  3 - Delete API Key")
        print("  4 - Back to main menu")
        
        choice = input("\nEnter selection (1-4): ").strip()
        
        if choice == "1":
            urlscan_set_api_key(service_name, api_key_name)
        elif choice == "2":
            urlscan_get_api_key(service_name, api_key_name)
        elif choice == "3":
            urlscan_delete_api_key(service_name, api_key_name)
        elif choice == "4":
            return
        else:
            print("❌ Invalid option. Please enter 1-4.\n")
            input("Press Enter to continue...")
            continue
        
        input("Press Enter to continue...")


# ============================================================================
# GTI Enterprise Functions
# ============================================================================

def gti_set_api_key():
    """Set the GTI Enterprise API key in keyring"""
    print_section("SET GTI ENTERPRISE API KEY")
    
    service_name = "svc_gti_enterprise"
    account_name = "gti_api_account"
    
    print(f"Service ID: {service_name}")
    print(f"Account Name: {account_name}\n")
    print("DO NOT LEAVE API key field empty!\n")
    
    api_key = input("Please enter the GTI API key: ").strip()

    if not api_key:
        print("❌ Error: API key cannot be empty")
        return False

    try:
        keyring.set_password(service_name, account_name, api_key)
        print(f"\n✅ API key saved in keyring:\n")
        print(f"   Service: {service_name}")
        print(f"   Account: {account_name}\n")
        return True
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        return False


def gti_get_api_key():
    """Retrieve the GTI Enterprise API key from keyring"""
    print_section("RETRIEVE GTI ENTERPRISE API KEY")
    
    service_name = "svc_gti_enterprise"
    account_name = "gti_api_account"
    
    try:
        api_key = keyring.get_password(service_name, account_name)
        if api_key:
            print(f"✅ API key retrieved from keyring:\n")
            print(f"   Service: {service_name}")
            print(f"   Account: {account_name}")
            print(f"   API Key: {api_key[:10]}...\n")
            return True
        else:
            print(f"❌ No API key found for service: {service_name}\n")
            return False
    except Exception as e:
        print(f"❌ Error retrieving API key: {e}")
        return False


def gti_delete_api_key():
    """Delete the GTI Enterprise API key from keyring"""
    print_section("DELETE GTI ENTERPRISE API KEY")
    
    service_name = "svc_gti_enterprise"
    account_name = "gti_api_account"
    
    confirm = input(f"Are you sure you want to delete the API key for '{service_name}'? (y/n) [n]: ").strip().lower()
    if confirm != 'y':
        print("Deletion cancelled.\n")
        return False
    
    try:
        keyring.delete_password(service_name, account_name)
        print(f"\n✅ API key deleted from keyring:\n")
        print(f"   Service: {service_name}")
        print(f"   Account: {account_name}\n")
        return True
    except PasswordDeleteError:
        print(f"❌ Error: API key not found or cannot be deleted.\n")
        return False
    except Exception as e:
        print(f"❌ Error deleting API key: {e}")
        return False


def gti_menu():
    """GTI Enterprise configuration menu"""
    while True:
        print_header("GTI ENTERPRISE API KEY MANAGER")
        
        print("Current Service ID: svc_gti_enterprise\n")
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


# ============================================================================
# Main Menu
# ============================================================================

def main():
    """Main menu"""
    while True:
        print_header("UNIFIED API CREDENTIALS CONFIGURATION MANAGER")
        
        print("Select which API credentials to configure:")
        print("  1 - Cloudflare URL Scanner")
        print("  2 - URLSCAN.io")
        print("  3 - GTI Enterprise")
        print("  4 - Exit")
        
        choice = input("\nEnter selection (1-4): ").strip()
        
        if choice == "1":
            cloudflare_menu()
        elif choice == "2":
            urlscan_menu()
        elif choice == "3":
            gti_menu()
        elif choice == "4":
            print("\n✅ Goodbye!\n")
            sys.exit(0)
        else:
            print("❌ Invalid option. Please enter 1-4.\n")
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
