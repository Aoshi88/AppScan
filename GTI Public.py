import requests
import time
import json
import keyring

print(f"\nThis scan will upload the file to public GTI, do not use for Synapxe or custom software installers!\n")
print(f"All software must be in the same location from where this Python script is run\n")
print(f"Filenames are case-sensitive\n")

API_KEY = keyring.get_password("softwareassessment","svc_synsoftwareassessment")
FILE_PATH = input("Please enter the filename for file scan upload:").strip()
EXPECTED_HASH = input("Enter SHA256 hash provided by the vendor to verify filehash (or press Enter to skip): ").strip().lower()

# Mode selection
print("Select an option:")
print("  1 - Submit a file less than 200MBfor GTI public scanning")
print("  2 - Submit a file greater than 200MB for GTI public scanning")
print("  3 - Retrieve a report using an ID")
mode = input("Enter selection: ").strip()

if mode not in ("1", "2", "3"):
    print("Invalid option. Please enter correct option.")
    exit(1)

headers = {
    "accept": "application/json",
    "x-apikey": API_KEY
}

if mode == "1":
    # Step 1: Submit file for scanning
    print(f"\nUploading '{FILE_PATH}' to GTI Public Scan")

    post_url = "https://www.virustotal.com/api/v3/files"

    with open(FILE_PATH, "rb") as f:
        files = {"file": (FILE_PATH, f, "application/octet-stream")}
        response = requests.post(post_url, files=files, headers=headers)

    upload_result = response.json()

    if response.status_code != 200:
        print(f"Upload failed: {upload_result}")
        exit(1)

    # Extract the file ID from the upload response
    file_id = upload_result.get("data", {}).get("id")
    if not file_id:
        print("Could not retrieve file ID from upload response.")
        exit(1)

    print(f"File submitted successfully. Analysis ID: {file_id}")

    # Step 2: Wait for the scan to complete
    print("Waiting 20 seconds for the scan to complete...")
    time.sleep(20)

elif mode == "2":
    # Step 1: Submit file for scanning
    print(f"\nUploading '{FILE_PATH}' to GTI Scan For Large Files")

    post_url = "https://www.virustotal.com/api/v3/files/upload_url"

    with open(FILE_PATH, "rb") as f:
        files = {"file": (FILE_PATH, f, "application/octet-stream")}
        response = requests.post(post_url, files=files, headers=headers)

    upload_result = response.json()

    if response.status_code != 200:
        print(f"Upload failed: {upload_result}")
        exit(1)

    # Extract the  ID from the upload response
    file_id = upload_result.get("data", {}).get("id")
    if not file_id:
        print("Could not retrieve ID from upload response.")
        exit(1)

    print(f"File submitted successfully. Analysis ID: {file_id}")

    # Step 2: Wait for the scan to complete
    print("Waiting 20 seconds for the scan to complete...")
    time.sleep(20)

elif mode == "3":
    # Step 1 (alternate): Accept a file ID directly
    file_id = input("Enter the Analysis ID to retrieve: ").strip()
    if not file_id:
        print("No file ID provided.")
        exit(1)

# Step 3: Retrieve the scan report
print("\nFetching scan report...")

get_url = f"https://www.virustotal.com/api/v3/analyses/{file_id}"
report_response = requests.get(get_url, headers=headers)
report = report_response.json()

if report_response.status_code != 200:
    print(f"Failed to retrieve report: {report}")
    exit(1)

# Display a summary of the results
stats = report.get("data", {}).get("attributes", {}).get("stats", {})
status = report.get("data", {}).get("attributes", {}).get("status", "unknown")
filehash = report.get("meta", {}).get("file_info", {}).get("sha256", {})

# Step 4: Compare against expected hash if provided
if EXPECTED_HASH:
    if filehash and filehash.lower() == EXPECTED_HASH:
        print(f"\n✅ Hash MATCH — file integrity verified.")
    else:
        print(f"\n❌ Hash MISMATCH! Suspect malicious modification to file, submit for further assessment or re-download the file from a trusted source")
        print(f"   Expected: {EXPECTED_HASH}")
        print(f"   Got:      {filehash}")

print(f"\n--- Scan Report ---")
print(f"Status: {status}")
if stats:
    print(f"Malicious:  {stats.get('malicious', 0)}")
    print(f"Suspicious: {stats.get('suspicious', 0)}")
    print(f"Harmless:   {stats.get('harmless', 0)}")
    print(f"Undetected: {stats.get('undetected', 0)}")
print(f"Filehash: {filehash}")


report_filename = "virustotal_report.txt"
with open(report_filename, "w") as f:
    json.dump(report, f, indent=2)

print(f"\nFull report saved to '{report_filename}'")