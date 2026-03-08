import requests
import time
import json
import keyring

#keyring.delete_password("softwareassessment","svc_synsoftwareassessment")
keyring.set_password("softwareassessment","svc_synsoftwareassessment","929b4f5227bf3348bb5aa18cf531986b5a8f1abf2eb667ce502d276598dec260")

print(f"\nThis scan will upload the file to public GTI, do not use for Synapxe or custom software installers!\n")
print(f"All software must be in the same location from where this Python script is run\n")
print(f"Filenames are case-sensitive\n")

#API_KEY = input("Please enter the GTI API Key to authenticate for file scan upload:").strip()
API_KEY = keyring.get_password("softwareassessment","svc_synsoftwareassessment").strip()
FILE_PATH = input("Please enter the filename for file scan upload:").strip()
EXPECTED_HASH = input("Enter SHA256 hash provided by the vendor to verify filehash (or press Enter to skip): ").strip().lower()

# Sandbox options
print("\nSandbox options (press Enter to accept defaults):")
disable_sandbox = input("Disable sandbox? (true/false) [default: false]: ").strip().lower() or "false"
enable_internet = input("Enable internet in sandbox? (true/false) [default: false]: ").strip().lower() or "false"
intercept_tls = input("Intercept TLS? (true/false) [default: false]: ").strip().lower() or "false"
locale = input("Locale? [default: EN_US]: ").strip() or "EN_US"

# Mode selection
print("Select an option:")
print("  1 - Submit a file for GTI private scanning")
print("  2 - Submit a file >200MB for GTI private scanning")
print("  3 - Retrieve an existing report using a file ID")
mode = input("Enter selection: ").strip()

if mode not in ("1", "2", "3"):
    print("Invalid option. Please enter correct option.")
    exit(1)

headers = {
    "accept": "application/json",
    "x-apikey": API_KEY
}

if mode == "1":
    # Submit file for private scanning
    print(f"\nUploading '{FILE_PATH}' to GTI Private Scan")

    post_url = "https://www.virustotal.com/api/v3/private/files"

    with open(FILE_PATH, "rb") as f:
        files = {"file": (FILE_PATH, f, "application/octet-stream")}
        data = {
            "disable_sandbox": disable_sandbox,
            "enable_internet": enable_internet,
            "intercept_tls": intercept_tls,
            "locale": locale
        }
        response = requests.post(post_url, files=files, data=data, headers=headers)

    upload_result = response.json()

    if response.status_code != 200:
        print(f"Upload failed: {upload_result}")
        exit(1)

    file_id = upload_result.get("data", {}).get("id")
    if not file_id:
        print("Could not retrieve file ID from upload response.")
        exit(1)

    print(f"File submitted successfully. Analysis ID: {file_id}\n")
    print("You may need to wait up to 5 minutes before retrieving the results of the report")
    exit(0)

elif mode == "2":
    # Submit large file for private scanning
    print(f"\nUploading '{FILE_PATH}' to GTI Private Scan For Large Files")

    post_url = "https://www.virustotal.com/api/v3/private/files/upload_url"

    with open(FILE_PATH, "rb") as f:
        files = {"file": (FILE_PATH, f, "application/octet-stream")}
        data = {
            "disable_sandbox": disable_sandbox,
            "enable_internet": enable_internet,
            "intercept_tls": intercept_tls,
            "locale": locale
        }
        response = requests.post(post_url, files=files, data=data, headers=headers)

    upload_result = response.json()

    if response.status_code != 200:
        print(f"Upload failed: {upload_result}")
        exit(1)

    file_id = upload_result.get("data", {}).get("id")
    if not file_id:
        print("Could not retrieve file ID from upload response.")
        exit(1)

    print(f"File submitted successfully. Analysis ID: {file_id}\n")
    print("You may need to wait up to 5 minutes before retrieving the results of the report")
    exit(0)

elif mode == "3":
    # Accept a file ID directly
    file_id = input("Enter the Analysis ID to retrieve: ").strip()
    if not file_id:
        print("No file ID provided.")
        exit(1)

# Retrieve the scan report
print("\nFetching scan report...")

get_url = f"https://www.virustotal.com/api/v3/private/analyses/{file_id}/item"
report_response = requests.get(get_url, headers=headers)
report = report_response.json()

if report_response.status_code != 200:
    print(f"Failed to retrieve report: {report}")
    exit(1)

# Display a summary of the results
status = report.get("data", {}).get("attributes", {}).get("sandbox_verdicts", {}).get("Zenbox", {}).get("malware_classification", {})
confidence = report.get("data", {}).get("attributes", {}).get("sandbox_verdicts", {}).get("Zenbox", {}).get("confidence", {})
#status = report.get("data", {}).get("attributes", {}).get("status", "unknown")
filehash = report.get("data", {}).get("id", {})

# Compare against expected hash if provided
#if EXPECTED_HASH:
#    if filehash and filehash.lower() == EXPECTED_HASH:
#        print(f"\n✅ Hash MATCH — file integrity verified.")
#    else:
#        print(f"\n❌ Hash MISMATCH! Suspect malicious modification to file, submit for further assessment or re-download the file from a trusted source")
#        print(f"   Expected: {EXPECTED_HASH}")
#        print(f"   Got:      {filehash}")

#Status will retrieve whether the file is clean according to Zenbox results
print(f"\n--- Scan Report ---")
print(f"Status: {status}")
print(f"Confidence: {confidence}")
print(f"Filehash (SHA256): {filehash}")

report_filename = "virustotal_report.txt"
with open(report_filename, "w") as f:
    json.dump(report, f, indent=2)

print(f"\nFull report saved to '{report_filename}'")