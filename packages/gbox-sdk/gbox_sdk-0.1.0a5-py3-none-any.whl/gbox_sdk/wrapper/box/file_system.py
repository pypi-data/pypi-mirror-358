from typing import List, Union, Optional

from gbox_sdk._client import GboxClient
from gbox_sdk.types.v1.boxes.f_info_params import FInfoParams
from gbox_sdk.types.v1.boxes.f_list_params import FListParams
from gbox_sdk.types.v1.boxes.f_read_params import FReadParams
from gbox_sdk.types.v1.boxes.f_write_params import WriteFile, WriteFileByBinary
from gbox_sdk.types.v1.boxes.f_exists_params import FExistsParams
from gbox_sdk.types.v1.boxes.f_list_response import Data, DataDir, DataFile, FListResponse
from gbox_sdk.types.v1.boxes.f_read_response import FReadResponse
from gbox_sdk.types.v1.boxes.f_remove_params import FRemoveParams
from gbox_sdk.types.v1.boxes.f_rename_params import FRenameParams
from gbox_sdk.types.v1.boxes.f_write_response import FWriteResponse
from gbox_sdk.types.v1.boxes.f_exists_response import FExistsResponse
from gbox_sdk.types.v1.boxes.f_rename_response import FRenameResponse


class FileSystemOperator:
    def __init__(self, client: GboxClient, box_id: str):
        self.client = client
        self.box_id = box_id

    def list_info(self, body: Union[FListParams, str]) -> FListResponse:
        if isinstance(body, str):
            return self.client.v1.boxes.fs.list(box_id=self.box_id, path=body)
        else:
            return self.client.v1.boxes.fs.list(box_id=self.box_id, **body)

    def list(self, body: Union[FListParams, str]) -> List[Union["FileOperator", "DirectoryOperator"]]:
        res = self.list_info(body)
        return [self.data_to_operator(r) for r in res.data]

    def read(self, body: FReadParams) -> FReadResponse:
        return self.client.v1.boxes.fs.read(box_id=self.box_id, **body)

    def write_text(self, body: WriteFile) -> FWriteResponse:
        return self.client.v1.boxes.fs.write(box_id=self.box_id, **body)

    def write_binary(self, body: WriteFileByBinary) -> FWriteResponse:
        return self.client.v1.boxes.fs.write(box_id=self.box_id, **body)

    def remove(self, body: FRemoveParams) -> None:
        self.client.v1.boxes.fs.remove(box_id=self.box_id, **body)
        return

    def exists(self, body: FExistsParams) -> FExistsResponse:
        return self.client.v1.boxes.fs.exists(box_id=self.box_id, **body)

    def rename(self, body: FRenameParams) -> FRenameResponse:
        return self.client.v1.boxes.fs.rename(box_id=self.box_id, **body)

    def get(self, body: FInfoParams) -> Union["FileOperator", "DirectoryOperator"]:
        res = self.client.v1.boxes.fs.info(box_id=self.box_id, **body)
        if res.type == "file":
            data_file = DataFile(
                path=res.path, type="file", mode=res.mode, name=res.name, size=res.size, lastModified=res.last_modified
            )
            return FileOperator(self.client, self.box_id, data_file)
        else:
            data_dir = DataDir(path=res.path, type="dir", mode=res.mode, name=res.name, lastModified=res.last_modified)
            return DirectoryOperator(self.client, self.box_id, data_dir)

    def data_to_operator(self, data: Optional[Data]) -> Union["FileOperator", "DirectoryOperator"]:
        if data is None:
            raise ValueError("data is None")
        if data.type == "file":
            return FileOperator(self.client, self.box_id, data)
        else:
            return DirectoryOperator(self.client, self.box_id, data)


class FileOperator:
    def __init__(self, client: GboxClient, box_id: str, data: DataFile):
        self.client = client
        self.box_id = box_id
        self.data = data

    def write_text(self, body: WriteFile) -> FWriteResponse:
        params = WriteFile(
            path=self.data.path, content=body.get("content", ""), working_dir=body.get("working_dir") or ""
        )
        return self.client.v1.boxes.fs.write(box_id=self.box_id, **params)

    def write_binary(self, body: WriteFileByBinary) -> FWriteResponse:
        params = WriteFileByBinary(
            path=self.data.path, content=body.get("content", b""), working_dir=body.get("working_dir") or ""
        )
        return self.client.v1.boxes.fs.write(box_id=self.box_id, **params)

    def read(self, body: Optional[FReadParams] = None) -> FReadResponse:
        if body is None:
            body = FReadParams(path=self.data.path, working_dir="")
        return self.client.v1.boxes.fs.read(box_id=self.box_id, **body)

    def rename(self, body: FRenameParams) -> FRenameResponse:
        params = FRenameParams(
            old_path=self.data.path, new_path=body.get("new_path", ""), working_dir=body.get("working_dir") or ""
        )
        return self.client.v1.boxes.fs.rename(box_id=self.box_id, **params)


class DirectoryOperator:
    def __init__(self, client: GboxClient, box_id: str, data: DataDir):
        self.client = client
        self.box_id = box_id
        self.data = data

    def list_info(self, body: Optional[FListParams] = None) -> FListResponse:
        if body is None:
            body = FListParams(path=self.data.path)
        return self.client.v1.boxes.fs.list(box_id=self.box_id, **body)

    def list(self, body: Optional[FListParams] = None) -> List[Union["FileOperator", "DirectoryOperator"]]:
        res = self.list_info(body)
        result: List[Union["FileOperator", "DirectoryOperator"]] = []
        for r in res.data:
            if r.type == "file":
                file = DataFile(
                    path=r.path, type=r.type, mode=r.mode, name=r.name, size=r.size, lastModified=r.last_modified
                )
                result.append(FileOperator(self.client, self.box_id, file))
            else:
                dir = DataDir(path=r.path, type=r.type, mode=r.mode, name=r.name, lastModified=r.last_modified)
                result.append(DirectoryOperator(self.client, self.box_id, dir))
        return result

    def rename(self, body: FRenameParams) -> FRenameResponse:
        params = FRenameParams(
            old_path=self.data.path, new_path=body.get("new_path", ""), working_dir=body.get("working_dir") or ""
        )
        return self.client.v1.boxes.fs.rename(box_id=self.box_id, **params)
