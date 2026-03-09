import keyring

print("This script will set the GTI Enterprise API key\n")
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
#declare variables for keyring
    systemname_key = input("Please enter the system name [default: softwareassessment]: ").strip() or "softwareassessment"
    servicename_key = input("Please enter the service account name ([default: svc_synsoftwareassessment]): ").strip() or "svc_synsoftwareassessment"
    api_key = input("Please enter the GTI API key: ").strip()

    if not api_key:
        raise ValueError("API key cannot be empty.")

#Store the API key using the provided/selected service  username
    keyring.set_password(systemname_key, servicename_key, api_key)
    print(f"\n✅ API key saved in keyring:\n")
    print(f"   Service (system name): {systemname_key}\n")
    print(f"   Username (service account): {servicename_key}\n")

elif mode == "2":
    # Remove API key for GTI
    systemname_key = input("Please enter the system name [default: softwareassessment]: ").strip() or "softwareassessment"
    servicename_key = input("Please enter the service account name ([default: svc_synsoftwareassessment]): ").strip() or "svc_synsoftwareassessment"
    try:
        keyring.delete_password(systemname_key, servicename_key)
        print(f"\n✅ API key removed from keyring:\n")
        print(f"   Service (system name): {systemname_key}\n")
        print(f"   Username (service account): {servicename_key}\n")
    except keyring.errors.PasswordDeleteError:
        print("Error: API key not found or cannot be deleted.")

elif mode == "3":
    # Retrieve API key for GTI
    systemname_key = input("Please enter the system name [default: softwareassessment]: ").strip() or "softwareassessment"
    servicename_key = input("Please enter the service account name ([default: svc_synsoftwareassessment]): ").strip() or "svc_synsoftwareassessment"
    api_key = keyring.get_password(systemname_key, servicename_key)
    if api_key:
        print(f"\n✅ API key retrieved from keyring:\n")
        print(f"   Service (system name): {systemname_key}\n")
        print(f"   Username (service account): {servicename_key}\n")
        print(f"   API Key: {api_key}\n")
    else:
        print("No API key found for the provided service and username.")
