import keyring

print("This script will set the GTI Enterprise API key\n")
print("Enter the API key below, you may skip configuring the default service account name and system name\n")
print("DO NOT LEAVE API key field empty!\n")

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
