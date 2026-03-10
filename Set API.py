import keyring

print("\n" + "="*80)
print("API CREDENTIALS CONFIGURATION")
print("="*80 + "\n")

print("Select which API credentials to configure:")
print("  1 - Cloudflare URL Scanner (API Token + Account ID)")
print("  2 - GTI Enterprise API key")
choice = input("\nEnter selection (1 or 2): ").strip()

if choice not in ("1", "2"):
    print("Invalid option. Please enter correct option.")
    exit(1)

if choice == "1":
    # Cloudflare configuration
    print("\n" + "-"*80)
    print("CLOUDFLARE URL SCANNER CREDENTIALS")
    print("-"*80 + "\n")
    
    systemname_key = input("Please enter the service name [default: svc_urlscanner]: ").strip() or "svc_urlscanner"
    
    print("\nSelect an option:")
    print("  1 - Set API Token and Account ID")
    print("  2 - Remove credentials")
    print("  3 - Retrieve credentials")
    mode = input("Enter selection: ").strip()
    
    if mode not in ("1", "2", "3"):
        print("Invalid option. Please enter correct option.")
        exit(1)
    
    if mode == "1":
        # Set Cloudflare credentials
        api_token = input("Enter Cloudflare API Token: ").strip()
        if not api_token:
            raise ValueError("API Token cannot be empty")
        
        account_id = input("Enter Cloudflare Account ID: ").strip()
        if not account_id:
            raise ValueError("Account ID cannot be empty")
        
        keyring.set_password(systemname_key, "api_token", api_token)
        keyring.set_password(systemname_key, "account_id", account_id)
        print(f"\n✅ Cloudflare credentials saved in keyring:\n")
        print(f"   Service: {systemname_key}\n")
    
    elif mode == "2":
        # Remove Cloudflare credentials
        try:
            keyring.delete_password(systemname_key, "api_token")
            keyring.delete_password(systemname_key, "account_id")
            print(f"\n✅ Cloudflare credentials removed from keyring:\n")
            print(f"   Service: {systemname_key}\n")
        except keyring.errors.PasswordDeleteError:
            print("Error: Credentials not found or cannot be deleted.")
    
    elif mode == "3":
        # Retrieve Cloudflare credentials
        api_token = keyring.get_password(systemname_key, "api_token")
        account_id = keyring.get_password(systemname_key, "account_id")
        if api_token and account_id:
            print(f"\n✅ Cloudflare credentials retrieved from keyring:\n")
            print(f"   Service: {systemname_key}\n")
            print(f"   API Token: {api_token[:10]}...\n")
            print(f"   Account ID: {account_id}\n")
        else:
            print("No credentials found for Cloudflare service.")

elif choice == "2":
    # GTI configuration
    print("\n" + "-"*80)
    print("GTI ENTERPRISE API KEY")
    print("-"*80 + "\n")
    print("Enter the API key below, you may skip configuring the default service account name and system name\n")
    print("DO NOT LEAVE API key field empty!\n")

    # Mode selection
    print("Select an option:")
    print("  1 - Set API key for GTI")
    print("  2 - Remove API key for GTI")
    print("  3 - Retrieve an API key")
    mode = input("Enter selection: ").strip()

    if mode not in ("1", "2", "3"):
        print("Invalid option. Please enter correct option.")
        exit(1)

    if mode == "1":
        # Add API key
        systemname_key = input("Please enter the system name [default: svc_softwareassessment]: ").strip() or "svc_softwareassessment"
        servicename_key = input("Please enter the service account name ([default: svc_softwareassessment]): ").strip() or "svc_softwareassessment"
        api_key = input("Please enter the GTI API key: ").strip()

        if not api_key:
            raise ValueError("API key cannot be empty.")

        # Store the API key using the provided/selected service username
        keyring.set_password(systemname_key, servicename_key, api_key)
        print(f"\n✅ API key saved in keyring:\n")
        print(f"   Service (system name): {systemname_key}\n")
        print(f"   Username (service account): {servicename_key}\n")

    elif mode == "2":
        # Remove API key for GTI
        systemname_key = input("Please enter the system name [default: softwareassessment]: ").strip() or "softwareassessment"
        servicename_key = input("Please enter the service account name ([default: svc_softwareassessment]): ").strip() or "svc_softwareassessment"
        try:
            keyring.delete_password(systemname_key, servicename_key)
            print(f"\n✅ API key removed from keyring:\n")
            print(f"   Service (system name): {systemname_key}\n")
            print(f"   Username (service account): {servicename_key}\n")
        except keyring.errors.PasswordDeleteError:
            print("Error: API key not found or cannot be deleted.")

    elif mode == "3":
        # Retrieve API key
        systemname_key = input("Please enter the system name [default: softwareassessment]: ").strip() or "softwareassessment"
        servicename_key = input("Please enter the service account name ([default: svc_softwareassessment]): ").strip() or "svc_softwareassessment"
        api_key = keyring.get_password(systemname_key, servicename_key)
        if api_key:
            print(f"\n✅ API key retrieved from keyring:\n")
            print(f"   Service (system name): {systemname_key}\n")
            print(f"   Username (service account): {servicename_key}\n")
            print(f"   API Key: {api_key}\n")
        else:
            print("No API key found for the provided service and username.")
