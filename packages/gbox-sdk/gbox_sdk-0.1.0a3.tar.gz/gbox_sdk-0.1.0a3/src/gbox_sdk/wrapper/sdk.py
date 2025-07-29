from typing import List, Union, Mapping, Optional

import httpx

from gbox_sdk import GboxClient
from gbox_sdk._types import NOT_GIVEN, Timeout, NotGiven
from gbox_sdk.wrapper.utils import is_linux_box, is_android_box
from gbox_sdk.wrapper.box.linux import LinuxBoxOperator
from gbox_sdk.types.v1.linux_box import LinuxBox
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.types.v1.box_list_params import BoxListParams
from gbox_sdk.types.v1.box_list_response import BoxListResponse
from gbox_sdk.wrapper.box.android.android import AndroidBoxOperator
from gbox_sdk.types.v1.box_terminate_params import BoxTerminateParams
from gbox_sdk.types.v1.box_retrieve_response import BoxRetrieveResponse
from gbox_sdk.types.v1.box_create_linux_params import BoxCreateLinuxParams
from gbox_sdk.types.v1.box_create_android_params import BoxCreateAndroidParams

BoxOperator = Union[AndroidBoxOperator, LinuxBoxOperator]


class BoxListOperatorResponse:
    def __init__(
        self,
        operators: List[BoxOperator],
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        total: Optional[int] = None,
    ):
        self.operators = operators
        self.page = page
        self.page_size = page_size
        self.total = total


class GboxSDK:
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[Union[str, httpx.URL]] = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: Optional[int] = None,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
        _strict_response_validation: Optional[bool] = None,
    ):
        self.client = GboxClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries if max_retries is not None else 2,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation
            if _strict_response_validation is not None
            else False,
        )

    def create_android(self, body: BoxCreateAndroidParams) -> AndroidBoxOperator:
        res = self.client.v1.boxes.create_android(**body)
        return AndroidBoxOperator(self.client, res)

    def create_linux(self, body: BoxCreateLinuxParams) -> LinuxBoxOperator:
        res = self.client.v1.boxes.create_linux(**body)
        return LinuxBoxOperator(self.client, res)

    def list_info(self, query: Optional[BoxListParams] = None) -> BoxListResponse:
        if query is None:
            query = BoxListParams()
        return self.client.v1.boxes.list(**query)

    def list(self, query: Optional[BoxListParams] = None) -> BoxListOperatorResponse:
        if query is None:
            query = BoxListParams()
        res = self.client.v1.boxes.list(**query)
        data = getattr(res, "data", [])
        operators = [self.data_to_operator(item) for item in data]
        return BoxListOperatorResponse(
            operators=operators,
            page=getattr(res, "page", None),
            page_size=getattr(res, "page_size", None),
            total=getattr(res, "total", None),
        )

    def get_info(self, box_id: str) -> BoxRetrieveResponse:
        return self.client.v1.boxes.retrieve(box_id)

    def get(self, box_id: str) -> BoxOperator:
        res = self.client.v1.boxes.retrieve(box_id)
        return self.data_to_operator(res)

    def terminate(self, box_id: str, body: Optional[BoxTerminateParams] = None) -> None:
        if body is None:
            body = BoxTerminateParams()
        self.client.v1.boxes.terminate(box_id, **body)

    def data_to_operator(self, data: Union[AndroidBox, LinuxBox]) -> BoxOperator:
        if is_android_box(data):
            android_box: AndroidBox = AndroidBox(**data.model_dump())
            return AndroidBoxOperator(self.client, android_box)
        elif is_linux_box(data):
            linux_box: LinuxBox = LinuxBox(**data.model_dump())
            return LinuxBoxOperator(self.client, linux_box)
        else:
            raise ValueError(f"Invalid box type: {data.type}")

    def get_client(self) -> GboxClient:
        return self.client
