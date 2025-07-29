from gbox_sdk._client import GboxClient
from gbox_sdk.wrapper.box.base import BaseBox
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.wrapper.box.android.app_manager import AndroidAppManager
from gbox_sdk.wrapper.box.android.pkg_manager import AndroidPkgManager


class AndroidBoxOperator(BaseBox):
    def __init__(self, client: GboxClient, data: AndroidBox):
        super().__init__(client, data)
        self.app = AndroidAppManager(client, data)
        self.pkg = AndroidPkgManager(client, data)
