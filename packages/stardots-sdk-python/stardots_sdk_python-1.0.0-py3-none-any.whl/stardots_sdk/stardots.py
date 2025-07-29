from typing import Optional, Dict, Any
from .constants import ENDPOINT, DEFAULT_REQUEST_TIMEOUT
from .types import *
from .helper import request_url, make_headers, send_request
import requests

class StarDots:
    def __init__(self, client_key: str, client_secret: str, endpoint: Optional[str] = None):
        self.endpoint = endpoint or ENDPOINT
        self.client_key = client_key
        self.client_secret = client_secret

    def get_space_list(self, params: SpaceListReq) -> SpaceListResp:
        query = {
            "page": params.page or 1,
            "pageSize": params.pageSize or 20,
        }
        url = request_url(self.endpoint, f"/openapi/space/list")
        resp = send_request(
            "GET", url, headers=make_headers(self.client_key, self.client_secret), timeout=DEFAULT_REQUEST_TIMEOUT, json_payload=query
        )
        return SpaceListResp.parse_raw(resp.text)

    def create_space(self, params: CreateSpaceReq) -> CreateSpaceResp:
        url = request_url(self.endpoint, "/openapi/space/create")
        resp = send_request(
            "PUT", url, headers=make_headers(self.client_key, self.client_secret), timeout=DEFAULT_REQUEST_TIMEOUT, json_payload=params.dict()
        )
        return CreateSpaceResp.parse_raw(resp.text)

    def delete_space(self, params: DeleteSpaceReq) -> DeleteSpaceResp:
        url = request_url(self.endpoint, "/openapi/space/delete")
        resp = send_request(
            "DELETE", url, headers=make_headers(self.client_key, self.client_secret), timeout=DEFAULT_REQUEST_TIMEOUT, json_payload=params.dict()
        )
        return DeleteSpaceResp.parse_raw(resp.text)

    def toggle_space_accessibility(self, params: ToggleSpaceAccessibilityReq) -> ToggleSpaceAccessibilityResp:
        url = request_url(self.endpoint, "/openapi/space/accessibility/toggle")
        resp = send_request(
            "POST", url, headers=make_headers(self.client_key, self.client_secret), timeout=DEFAULT_REQUEST_TIMEOUT, json_payload=params.dict()
        )
        return ToggleSpaceAccessibilityResp.parse_raw(resp.text)

    def get_space_file_list(self, params: SpaceFileListReq) -> SpaceFileListResp:
        query = {
            "page": params.page or 1,
            "pageSize": params.pageSize or 20,
            "space": params.space,
        }
        url = request_url(self.endpoint, f"/openapi/file/list")
        resp = send_request(
            "GET", url, headers=make_headers(self.client_key, self.client_secret), timeout=DEFAULT_REQUEST_TIMEOUT, json_payload=query
        )
        return SpaceFileListResp.parse_raw(resp.text)

    def file_access_ticket(self, params: FileAccessTicketReq) -> FileAccessTicketResp:
        url = request_url(self.endpoint, "/openapi/file/ticket")
        resp = send_request(
            "POST", url, headers=make_headers(self.client_key, self.client_secret), timeout=DEFAULT_REQUEST_TIMEOUT, json_payload=params.dict()
        )
        return FileAccessTicketResp.parse_raw(resp.text)

    def upload_file(self, params: UploadFileReq) -> UploadFileResp:
        url = request_url(self.endpoint, "/openapi/file/upload")
        files = {
            "file": (params.filename, params.fileContent),
            "space": (None, params.space),
        }
        resp = send_request(
            "PUT", url, headers=make_headers(self.client_key, self.client_secret), timeout=DEFAULT_REQUEST_TIMEOUT, files=files
        )
        return UploadFileResp.parse_raw(resp.text)

    def delete_file(self, params: DeleteFileReq) -> DeleteFileResp:
        url = request_url(self.endpoint, "/openapi/file/delete")
        resp = send_request(
            "DELETE", url, headers=make_headers(self.client_key, self.client_secret), timeout=DEFAULT_REQUEST_TIMEOUT, json_payload=params.dict()
        )
        return DeleteFileResp.parse_raw(resp.text) 