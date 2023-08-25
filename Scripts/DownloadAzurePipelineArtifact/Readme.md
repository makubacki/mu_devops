# Download Azure Pipeline Arifact

[DownloadAzurePipelineArtifact.py](./DownloadAzurePipelineArtifact.py) is a script used in pipelines to download
artifacts from other pipelines.

## Overview

This script is intended to be a lightweight implementation of CI-specific tasks like [`DownloadPipelineArtifact@2`](https://learn.microsoft.com/azure/devops/pipelines/tasks/reference/download-pipeline-artifact-v2?view=azure-pipelines)
and [`DownloadBuildArtifacts@1`](https://learn.microsoft.com/azure/devops/pipelines/tasks/reference/download-build-artifacts-v1?view=azure-pipelines).

The primary reason the script is used is that those tasks have failed to reliably download artifacts under certain
conditions. In particular, accessing artifacts in an Azure Pipeline from a pull requests triggered over a GitHub
service connection.

To reduce complexity, the script intentionally has some fixed behavior.

- The script can only access public resources
- The script always flattens files when copying to the destination

## Inputs

Because this script is only intended to run in pipelines, it does not present a user-facing command-line parameter
interface and accepts its input as environment variables that are expected to be passed in the environment variable
section of the task that invokes the script.

The environment variables are (name and example value):

- `ARTIFACT_NAME` - `Binaries`
- `AZURE_ORG_NAME` - `projectmu`
- `AZURE_PROJ_NAME` - `mu`
- `AZURE_PIPELINE_DEF_ID` - `123`
- `FILE_PATTERN` - `**/application.exe`
- `TARGET_DIR` - `$(Build.ArtifactStagingDirectory)`
- `WORK_DIR` - `$(Agent.TempDirectory)`
