# @file DownloadAzurePipelineArtifact.py
#
# A script used in pipelines to download artifacts from an Azure Pipeline.
#
# Will always download latest without authentication. Copies all files in the
# artifact to the target dir. Always does flat copy.
#
# See the accompanying script readme for more details.
#
# The environment variables are (name and example value):
# - `ARTIFACT_NAME` - `Binaries`
# - `AZURE_ORG_NAME` - `projectmu`
# - `AZURE_PROJ_NAME` - `mu`
# - `AZURE_PIPELINE_DEF_ID` - `123`
# - `FILE_PATTERN` - `**/application.exe`
# - `TARGET_DIR` - `$(Build.ArtifactStagingDirectory)`
# - `WORK_DIR` - `$(Agent.TempDirectory)`
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause-Patent
##

import os
import requests
import shutil
import zipfile
from pathlib import Path

ARTIFACT_NAME = os.environ["ARTIFACT_NAME"]
AZURE_ORG_NAME = os.environ["AZURE_ORG_NAME"]
AZURE_PROJ_NAME = os.environ["AZURE_PROJ_NAME"]
AZURE_PIPELINE_DEF_ID = os.environ["AZURE_PIPELINE_DEF_ID"]
FILE_PATTERN = os.environ["FILE_PATTERN"]
TARGET_DIR = Path(os.environ["TARGET_DIR"])
WORK_DIR = os.environ["WORK_DIR"]

build_id_url = f"https://dev.azure.com/{AZURE_ORG_NAME}/{AZURE_PROJ_NAME}/_apis/build/builds?definitions={AZURE_PIPELINE_DEF_ID}&$top=1&api-version=6.0"

# Fetch the list of assets from the GitHub releases
response = requests.get(build_id_url)
response.raise_for_status()
latest_build_id = response.json()["value"][0]["id"]

artifact_url = f"https://dev.azure.com/{AZURE_ORG_NAME}/{AZURE_PROJ_NAME}/_apis/build/builds/{latest_build_id}/artifacts?artifactName={ARTIFACT_NAME}&api-version=6.0"
response = requests.get(artifact_url)
response.raise_for_status()
download_url = response.json()["resource"]["downloadUrl"]

print(f"Latest Build ID: {latest_build_id}")
print(f"Artifact Download URL: {download_url}")

download_path = Path(WORK_DIR, "artifact_download", ARTIFACT_NAME).with_suffix(".zip")
download_path.parent.mkdir(parents=True)
with requests.get(download_url, stream=True) as r:
    with download_path.open('wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

with zipfile.ZipFile(download_path, 'r') as zip_ref:
    zip_ref.extractall(download_path.parent)

unzip_path = download_path.parent / ARTIFACT_NAME


def flatten_copy(src: Path, dst: Path, pattern: str):
    if not dst.exists():
        dst.mkdir(parents=True)

    for item in src.rglob(pattern):
        print(f"Current item is {item}")
        if item.is_dir():
            flatten_copy(item, dst, pattern)
        else:
            shutil.copy2(item, dst)


TARGET_DIR.mkdir(parents=True, exist_ok=True)
flatten_copy(unzip_path, TARGET_DIR, FILE_PATTERN)
shutil.rmtree(download_path.parent)
