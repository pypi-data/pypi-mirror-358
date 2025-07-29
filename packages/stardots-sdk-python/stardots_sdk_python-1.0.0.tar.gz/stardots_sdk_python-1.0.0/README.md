<div align="center">
    <h1><img src="logo.png" alt="logo.png" title="logo.png" width="300" /></h1>
</div> 

# StarDots-SDK-Python

[![Python](https://img.shields.io/badge/Python-3.7+-green.svg)](https://www.python.org/)
[![PIP](https://img.shields.io/badge/PIP-latest-orange.svg)](https://pypi.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  

## Introduction

This project is used to help developers quickly access the StarDots platform and is written in Python 3.

## Requirement
- Python >= 3.7

## Installation
```bash
pip install stardots-sdk-python
# 或者本地开发：
pip install -r requirements.txt
```

## Example
```python
from stardots_sdk import StarDots, CreateSpaceReq, UploadFileReq

client_key = "Your client key"
client_secret = "Your client secret"
sdk = StarDots(client_key, client_secret)

# Get space list
space_list = sdk.get_space_list()

# Create a new space
create_result = sdk.create_space(CreateSpaceReq(space="my-space", public=True))

# Upload a file
with open("example.txt", "rb") as f:
    upload_result = sdk.upload_file(UploadFileReq(space="my-space", filename="example.txt", fileContent=f.read()))
```

## API Reference
- `StarDots.get_space_list(params: SpaceListReq) -> SpaceListResp`
- `StarDots.create_space(params: CreateSpaceReq) -> CreateSpaceResp`
- `StarDots.delete_space(params: DeleteSpaceReq) -> DeleteSpaceResp`
- `StarDots.toggle_space_accessibility(params: ToggleSpaceAccessibilityReq) -> ToggleSpaceAccessibilityResp`
- `StarDots.get_space_file_list(params: SpaceFileListReq) -> SpaceFileListResp`
- `StarDots.file_access_ticket(params: FileAccessTicketReq) -> FileAccessTicketResp`
- `StarDots.upload_file(params: UploadFileReq) -> UploadFileResp`
- `StarDots.delete_file(params: DeleteFileReq) -> DeleteFileResp`

## Documentation
[https://stardots.io/en/documentation/openapi](https://stardots.io/en/documentation/openapi)

## Homepage
[https://stardots.io](https://stardots.io) 