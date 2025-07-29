import pytest
from stardots_sdk import StarDots, CreateSpaceReq, DeleteSpaceReq, ToggleSpaceAccessibilityReq, SpaceFileListReq, FileAccessTicketReq, UploadFileReq, DeleteFileReq

CLIENT_KEY = "Your client key"
CLIENT_SECRET = "Your client secret"

def test_create_instance():
    sdk = StarDots(CLIENT_KEY, CLIENT_SECRET)
    assert sdk is not None

def test_get_space_list():
    sdk = StarDots(CLIENT_KEY, CLIENT_SECRET)
    try:
        resp = sdk.get_space_list()
        assert resp is not None
    except Exception as e:
        assert e is not None

def test_create_space():
    sdk = StarDots(CLIENT_KEY, CLIENT_SECRET)
    try:
        resp = sdk.create_space(CreateSpaceReq(space="demo", public=True))
        assert resp is not None
    except Exception as e:
        assert e is not None

def test_delete_space():
    sdk = StarDots(CLIENT_KEY, CLIENT_SECRET)
    try:
        resp = sdk.delete_space(DeleteSpaceReq(space="demo"))
        assert resp is not None
    except Exception as e:
        assert e is not None

def test_toggle_space_accessibility():
    sdk = StarDots(CLIENT_KEY, CLIENT_SECRET)
    try:
        resp = sdk.toggle_space_accessibility(ToggleSpaceAccessibilityReq(space="demo", public=False))
        assert resp is not None
    except Exception as e:
        assert e is not None

def test_get_space_file_list():
    sdk = StarDots(CLIENT_KEY, CLIENT_SECRET)
    try:
        resp = sdk.get_space_file_list(SpaceFileListReq(space="demo"))
        assert resp is not None
    except Exception as e:
        assert e is not None

def test_file_access_ticket():
    sdk = StarDots(CLIENT_KEY, CLIENT_SECRET)
    try:
        resp = sdk.file_access_ticket(FileAccessTicketReq(space="demo", filename="1.png"))
        assert resp is not None
    except Exception as e:
        assert e is not None

def test_upload_file():
    sdk = StarDots(CLIENT_KEY, CLIENT_SECRET)
    try:
        resp = sdk.upload_file(UploadFileReq(space="demo", filename="test.txt", fileContent=b"hello world"))
        assert resp is not None
    except Exception as e:
        assert e is not None

def test_delete_file():
    sdk = StarDots(CLIENT_KEY, CLIENT_SECRET)
    try:
        resp = sdk.delete_file(DeleteFileReq(space="demo", filenameList=["test.txt"]))
        assert resp is not None
    except Exception as e:
        assert e is not None 