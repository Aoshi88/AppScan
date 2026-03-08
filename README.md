# GTI Public & Private Scanner Scripts (Dev Branch)

This repository contains two Python scripts for submitting files to VirusTotal's GTI (Global Threat Intelligence) public and private scanning APIs, retrieving scan reports, and verifying file integrity via SHA256 hash.

## Files

- **GTI Public.py**: Uploads files to VirusTotal's public GTI API for malware scanning. Supports files of any size, retrieves scan reports, and compares the file's hash to a vendor-provided value.
- **GTI Private.py**: Uploads files to VirusTotal's private GTI API with additional sandboxing options (e.g., internet access, locale, TLS interception). Retrieves detailed sandbox verdicts and confidence levels.

## Features

- Secure API key management using the `keyring` library.
- Interactive prompts for file selection, hash verification, and scan/report options.
- Supports both standard and large file uploads.
- Saves full scan reports as `virustotal_report.txt`.
- Hash verification to ensure file integrity.
- Private scan script allows advanced sandbox configuration.

## Usage

1. Place the script(s) and the file to be scanned in the same directory.
2. Run the desired script:
   - For public scan: `python GTI Public.py`
   - For private scan: `python GTI Private.py`
3. Follow the prompts to select scan mode, enter file name, and (optionally) provide a SHA256 hash.
4. For private scans, configure sandbox options as needed.
5. Retrieve and review the scan report. The full JSON report is saved as `virustotal_report.txt`.

## Requirements

- Python 3.x
- `requests` library
- `keyring` library

## Notes
- Do **not** use the public scan script for in-house or custom software.
- Filenames are case-sensitive.
- For large files (>200MB), select the appropriate mode when prompted.

## Disclaimer
These scripts are for authorized use only. Ensure you comply with your organization's security policies and VirusTotal's terms of service.
