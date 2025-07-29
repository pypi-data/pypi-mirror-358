from typing import Any, List, Optional
from pydantic import BaseModel, Field

class CommonResponse(BaseModel):
    code: int = Field(..., description="Service response code.")
    message: str = Field(..., description="Message prompt of the operation result.")
    requestId: str = Field(..., description="A unique number for the request, which can be used for troubleshooting.")
    success: bool = Field(..., alias="bool", description="Indicates whether the business operation is successful.")
    ts: int = Field(..., description="Server millisecond timestamp.")
    data: Any = Field(..., description="Business data field. This field can be of any data type.")

class PaginationReq(BaseModel):
    page: Optional[int] = Field(1, description="Page number, default value is 1.")
    pageSize: Optional[int] = Field(20, description="The number of entries per page ranges from 1 to 100, and the default value is 20.")

class PaginationResp(BaseModel):
    page: int
    pageSize: int
    totalCount: int

class SpaceInfo(BaseModel):
    name: str
    public: bool
    createdAt: int
    fileCount: int

class SpaceListReq(PaginationReq):
    pass

class SpaceListResp(CommonResponse):
    data: List[SpaceInfo]

class CreateSpaceReq(BaseModel):
    space: str
    public: Optional[bool] = False

class CreateSpaceResp(CommonResponse):
    pass

class DeleteSpaceReq(BaseModel):
    space: str

class DeleteSpaceResp(CommonResponse):
    pass

class ToggleSpaceAccessibilityReq(BaseModel):
    space: str
    public: bool

class ToggleSpaceAccessibilityResp(CommonResponse):
    pass

class SpaceFileListReq(PaginationReq):
    space: str

class FileInfo(BaseModel):
    name: str
    byteSize: int
    size: str
    uploadedAt: int
    url: str

class SpaceFileListResp(CommonResponse):
    class DataModel(BaseModel):
        list: List[FileInfo]
    data: DataModel

class FileAccessTicketReq(BaseModel):
    filename: str
    space: str

class FileAccessTicketResp(CommonResponse):
    class DataModel(BaseModel):
        ticket: str
    data: DataModel

class UploadFileReq(BaseModel):
    filename: str
    space: str
    fileContent: bytes

class UploadFileResp(CommonResponse):
    class DataModel(BaseModel):
        space: str
        filename: str
        url: str
    data: DataModel

class DeleteFileReq(BaseModel):
    filenameList: List[str]
    space: str

class DeleteFileResp(CommonResponse):
    pass 