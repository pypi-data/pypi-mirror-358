from gbox_sdk._client import GboxClient
from gbox_sdk.wrapper.box.base import BaseBox
from gbox_sdk.types.v1.linux_box import LinuxBox


class LinuxBoxOperator(BaseBox):
    def __init__(self, client: GboxClient, data: LinuxBox):
        super().__init__(client, data)
