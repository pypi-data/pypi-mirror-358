import os
from typing import List

from gbox_sdk._client import GboxClient
from gbox_sdk._response import BinaryAPIResponse
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.wrapper.box.android.types import AndroidInstall
from gbox_sdk.wrapper.box.android.app_operator import AndroidAppOperator
from gbox_sdk.types.v1.boxes.android_get_response import AndroidGetResponse
from gbox_sdk.types.v1.boxes.android_install_response import AndroidInstallResponse
from gbox_sdk.types.v1.boxes.android_uninstall_params import AndroidUninstallParams
from gbox_sdk.types.v1.boxes.android_list_app_response import AndroidListAppResponse


class AndroidPkgManager:
    def __init__(self, client: GboxClient, box: AndroidBox):
        self.client = client
        self.box = box

    def install(self, body: AndroidInstall) -> AndroidInstallResponse:
        apk = body["apk"]
        if isinstance(apk, str) and not apk.startswith("http"):
            if not os.path.exists(apk):
                raise FileNotFoundError(f"File {apk} does not exist")
            with open(apk, "rb") as apk_file:
                return self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk_file)
        elif isinstance(apk, str) and apk.startswith("http"):
            return self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk)

        return self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk)

    def uninstall(self, package_name: str, params: AndroidUninstallParams) -> None:
        keep_data = bool(params.get("keepData", False))
        return self.client.v1.boxes.android.uninstall(package_name, box_id=self.box.id, keep_data=keep_data)

    def list(self) -> List[AndroidAppOperator]:
        res = self.client.v1.boxes.android.list_app(box_id=self.box.id)
        return [AndroidAppOperator(self.client, self.box, app) for app in res.data]

    def list_info(self) -> AndroidListAppResponse:
        return self.client.v1.boxes.android.list_app(box_id=self.box.id)

    def get(self, package_name: str) -> AndroidAppOperator:
        res = self.client.v1.boxes.android.get_app(package_name, box_id=self.box.id)
        return AndroidAppOperator(self.client, self.box, res)

    def get_info(self, package_name: str) -> AndroidGetResponse:
        res = self.client.v1.boxes.android.get(package_name, box_id=self.box.id)
        return res

    def close_all(self) -> None:
        return self.client.v1.boxes.android.close_all(box_id=self.box.id)

    def backup_all(self) -> BinaryAPIResponse:
        return self.client.v1.boxes.android.backup_all(box_id=self.box.id)
