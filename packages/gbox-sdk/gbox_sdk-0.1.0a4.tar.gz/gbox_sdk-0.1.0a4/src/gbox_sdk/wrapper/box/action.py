import os
import base64
from typing import Optional

from gbox_sdk._client import GboxClient
from gbox_sdk.types.v1.boxes.action_drag_params import ActionDragParams
from gbox_sdk.types.v1.boxes.action_move_params import ActionMoveParams
from gbox_sdk.types.v1.boxes.action_type_params import ActionTypeParams
from gbox_sdk.types.v1.boxes.action_click_params import ActionClickParams
from gbox_sdk.types.v1.boxes.action_swipe_params import SwipeSimple, SwipeAdvanced
from gbox_sdk.types.v1.boxes.action_touch_params import ActionTouchParams
from gbox_sdk.types.v1.boxes.action_drag_response import ActionDragResponse
from gbox_sdk.types.v1.boxes.action_move_response import ActionMoveResponse
from gbox_sdk.types.v1.boxes.action_scroll_params import ActionScrollParams
from gbox_sdk.types.v1.boxes.action_type_response import ActionTypeResponse
from gbox_sdk.types.v1.boxes.action_click_response import ActionClickResponse
from gbox_sdk.types.v1.boxes.action_swipe_response import ActionSwipeResponse
from gbox_sdk.types.v1.boxes.action_touch_response import ActionTouchResponse
from gbox_sdk.types.v1.boxes.action_scroll_response import ActionScrollResponse
from gbox_sdk.types.v1.boxes.action_press_key_params import ActionPressKeyParams
from gbox_sdk.types.v1.boxes.action_screenshot_params import ActionScreenshotParams
from gbox_sdk.types.v1.boxes.action_press_key_response import ActionPressKeyResponse
from gbox_sdk.types.v1.boxes.action_press_button_params import ActionPressButtonParams
from gbox_sdk.types.v1.boxes.action_screenshot_response import ActionScreenshotResponse
from gbox_sdk.types.v1.boxes.action_press_button_response import ActionPressButtonResponse
from gbox_sdk.types.v1.boxes.action_screen_rotation_params import ActionScreenRotationParams
from gbox_sdk.types.v1.boxes.action_screen_rotation_response import ActionScreenRotationResponse


class ActionScreenshot(ActionScreenshotParams, total=False):
    path: Optional[str]


class ActionOperator:
    def __init__(self, client: GboxClient, box_id: str):
        self.client = client
        self.box_id = box_id

    def click(self, body: ActionClickParams) -> ActionClickResponse:
        return self.client.v1.boxes.actions.click(box_id=self.box_id, **body)

    def drag(self, body: ActionDragParams) -> ActionDragResponse:
        return self.client.v1.boxes.actions.drag(box_id=self.box_id, **body)

    def swipe_simple(self, body: SwipeSimple) -> ActionSwipeResponse:
        return self.client.v1.boxes.actions.swipe(box_id=self.box_id, **body)

    def swipe_advanced(self, body: SwipeAdvanced) -> ActionSwipeResponse:
        return self.client.v1.boxes.actions.swipe(box_id=self.box_id, **body)

    def press_key(self, body: ActionPressKeyParams) -> ActionPressKeyResponse:
        return self.client.v1.boxes.actions.press_key(box_id=self.box_id, **body)

    def press_button(self, body: ActionPressButtonParams) -> ActionPressButtonResponse:
        return self.client.v1.boxes.actions.press_button(box_id=self.box_id, **body)

    def move(self, body: ActionMoveParams) -> ActionMoveResponse:
        return self.client.v1.boxes.actions.move(box_id=self.box_id, **body)

    def scroll(self, body: ActionScrollParams) -> ActionScrollResponse:
        return self.client.v1.boxes.actions.scroll(box_id=self.box_id, **body)

    def touch(self, body: ActionTouchParams) -> ActionTouchResponse:
        return self.client.v1.boxes.actions.touch(box_id=self.box_id, **body)

    def type(self, body: ActionTypeParams) -> ActionTypeResponse:
        return self.client.v1.boxes.actions.type(box_id=self.box_id, **body)

    def screenshot(self, body: ActionScreenshotParams) -> ActionScreenshotResponse:
        if body.get("output_format") is None:
            body["output_format"] = "base64"
        return self.client.v1.boxes.actions.screenshot(box_id=self.box_id, **body)

    def screen_rotation(self, body: ActionScreenRotationParams) -> ActionScreenRotationResponse:
        return self.client.v1.boxes.actions.screen_rotation(box_id=self.box_id, **body)

    def save_data_url_to_file(self, data_url: str, file_path: str) -> None:
        if not data_url.startswith("data:"):
            raise ValueError("Invalid data URL format")
        parts = data_url.split(",")
        if len(parts) != 2:
            raise ValueError("Invalid data URL format")
        base64_data = parts[1]

        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(base64.b64decode(base64_data))
