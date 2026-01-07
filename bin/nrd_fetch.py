#!/usr/bin/env python

import csv
import json
import tarfile
import os
import sys
import requests

import configparser

# --- Setup Paths ---
splunk_home = os.environ.get("SPLUNK_HOME")

if not splunk_home:
    splunk_home = "/tmp/splunk"  # Default path for testing

app_name = "stamus_for_splunk"
app_root = os.path.join(splunk_home, "etc", "apps", app_name)
lookup_dir = os.path.join(app_root, "lookups")
config_file = os.path.join(app_root, "local", "ssp.conf")
default_config_file = os.path.join(app_root, "default", "ssp.conf")

# --- Constants for Internal Files ---
TARGET_JSON_FILENAME = os.path.join("rules", "nrd-30day.ndjson")  # File inside the tar
LOOKUP_OUTPUT_NAME = "nrd-30day.csv"  # Final CSV name


def get_config():
    config = configparser.ConfigParser()
    # Read default first, then local (local overrides default)
    config.read([default_config_file, config_file])

    if "config" not in config or "license_key" not in config["config"]:
        raise NotImplementedError("License key not found in ssp.conf")

    return config["config"]


def fetch_and_update():
    try:
        # 1. Get Configuration
        settings = get_config()
        license_key = settings["license_key"]
        full_url = f"https://ti.stamus-networks.io/{license_key}/sti-domains-json-nrd-30.tar.gz"

        print(f"INFO: Fetching from {full_url}...")

        # 3. Download the tar file
        response = requests.get(full_url, stream=True)
        response.raise_for_status()

        tar_path = os.path.join(lookup_dir, "temp_download.tar.gz")

        with open(tar_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # 4. Extract and Convert
        with tarfile.open(tar_path, "r:*") as tar:
            try:
                member = tar.getmember(TARGET_JSON_FILENAME)
            except KeyError:
                print(f"ERROR: {TARGET_JSON_FILENAME} not found in archive")
                sys.exit(1)

            extracted_f = tar.extractfile(member)
            if extracted_f is None:
                raise FileNotFoundError(
                    "Failed to extract the target JSON file from the tar archive"
                )

            # Parse JSON lines
            data = []
            for line in extracted_f:
                data.append(json.loads(line))

            # Convert to CSV for Splunk Lookup
            csv_path = os.path.join(lookup_dir, LOOKUP_OUTPUT_NAME)
            with open(csv_path, "w", newline="") as csvfile:
                # Assuming data is a list of dicts: [{"id":1, "val":"a"}]
                if isinstance(data, list) and len(data) > 0:
                    writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    print("WARNING: JSON data format unexpected or empty")

        # 5. Cleanup
        os.remove(tar_path)
        print(f"SUCCESS: Updated {csv_path}")

    except NotImplementedError:
        # config is not complete so we just exit silently.
        print("INFO: License key not configured, skipping NRD fetch.")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    fetch_and_update()
