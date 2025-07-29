from gbox_sdk._client import GboxClient


class BrowserOperator:
    def __init__(self, client: GboxClient, box_id: str):
        self.client = client
        self.box_id = box_id

    def cdpUrl(self) -> str:
        return self.client.v1.boxes.browser.cdp_url(box_id=self.box_id)
