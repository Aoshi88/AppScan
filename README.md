# AppScan — Scanners & Credential Manager (DEV)

Collection of Python tools for submitting URLs and files to scanning services and managing API credentials securely.

## Files

- `GTI Public.py` — Upload files to VirusTotal (public GTI) for malware scanning; supports standard and large-file workflows and retrieves analysis reports.
- `GTI Private.py` — Upload files to VirusTotal private GTI / sandbox with additional sandbox options and detailed verdict retrieval.
- `GTI URL.py` — Submit URLs to VirusTotal (GTI) for scanning, retrieve URL analysis reports, request rescans, and run batch URL processing.
- `Set API.py` — Interactive credential manager. Configures credentials for:
  - Cloudflare URL Scanner (`svc_cloudflare_urlscanner`)
  - URLSCAN.io (`svc_urlscan_io`)
  - GTI Enterprise (`svc_gti_enterprise`)
- `urlscan_io.py` — Submit URLs to URLSCAN.io, poll for completion, retrieve full reports, and save results to JSON.
- `cloudflare_radar.py` — Client for Cloudflare URL Scanner API: submit individual or bulk URL scans, and retrieve results.

## Key Features

- Centralized credential storage via the `keyring` library (no hardcoded keys).
- Interactive CLI flows for setting, retrieving, and deleting API credentials.
- URL scanning and result retrieval for URLSCAN.io and Cloudflare URL Scanner.
- File submission workflows for VirusTotal GTI (public and private), with report retrieval and optional SHA256 hash verification.
- Save full scan reports to JSON/text files for offline analysis.

## Usage

1. Configure API credentials first by running:

   python "Set API.py"

   Follow the prompts to set keys for URLSCAN.io, Cloudflare, and GTI. Credentials are stored in the OS keyring under the service names listed above.

2. Use the desired scanner:

   - URLSCAN.io interactive submit/retrieve: `python urlscan_io.py`
   - Cloudflare URL Scanner client: import and use `cloudflare_radar.py` or run any wrapper you have that integrates it.
   - GTI file scans: `python GTI Public.py` or `python GTI Private.py`
   - GTI URL scans (submit URLs / retrieve reports): `python "GTI URL.py"`

3. Reports are saved to files (JSON or text) by the individual scripts after retrieval.

## Requirements

- Python 3.8+
- `requests` (HTTP client)
- `keyring` (secure credential storage)

Install requirements with:

```bash
pip install requests keyring
```

## Notes & Security
- The script depends on `requests` and `keyring` (see Requirements section).  
- Saved results from batch runs are written to `scan_results.json` when you choose to save them.
- Do not share your API keys or commit them into version control.
- `GTI Public.py` is intended for public VirusTotal submissions — do not use it for internal-only or sensitive builds.
- Filenames and paths are case-sensitive on some platforms; run scripts from the directory containing target files when prompted.

## License & Disclaimer
Use these tools only in authorized environments and in accordance with the respective services' terms of use. The repository is provided "as-is" with no warranty.