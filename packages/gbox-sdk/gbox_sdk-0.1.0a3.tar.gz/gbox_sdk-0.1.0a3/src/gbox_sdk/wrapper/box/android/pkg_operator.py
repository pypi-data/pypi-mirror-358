from typing import Union

from gbox_sdk._client import GboxClient
from gbox_sdk._response import BinaryAPIResponse
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.types.v1.boxes.android_open_params import AndroidOpenParams
from gbox_sdk.types.v1.boxes.android_get_response import AndroidGetResponse
from gbox_sdk.types.v1.boxes.android_restart_params import AndroidRestartParams
from gbox_sdk.types.v1.boxes.android_list_activities_response import AndroidListActivitiesResponse


class AndroidPkgOperator:
    def __init__(self, client: GboxClient, box: AndroidBox, data: AndroidGetResponse):
        self.client = client
        self.box = box
        self.data = data

    def open(self, activity_name: Union[str, None] = None) -> None:
        params = AndroidOpenParams(box_id=self.box.id)
        if activity_name is not None:
            params["activity_name"] = activity_name
        return self.client.v1.boxes.android.open(self.data.package_name, **params)

    def close(self) -> None:
        return self.client.v1.boxes.android.close(self.data.package_name, box_id=self.box.id)

    def restart(self, activity_name: Union[str, None] = None) -> None:
        params = AndroidRestartParams(box_id=self.box.id)
        if activity_name is not None:
            params["activity_name"] = activity_name
        return self.client.v1.boxes.android.restart(self.data.package_name, **params)

    def list_activities(self) -> AndroidListActivitiesResponse:
        return self.client.v1.boxes.android.list_activities(self.data.package_name, box_id=self.box.id)

    def backup(self) -> BinaryAPIResponse:
        return self.client.v1.boxes.android.backup(self.data.package_name, box_id=self.box.id)
