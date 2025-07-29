import aiohttp
from typing import Dict, Any, Literal
from .entity import (
    MoveMouseRequest,
    ClickMouseRequest,
    PressMouseRequest,
    ReleaseMouseRequest,
    DragMouseRequest,
    ScrollRequest,
    PressKeyRequest,
    TypeTextRequest,
    WaitRequest,
    TakeScreenshotRequest,
    GetCursorPositionRequest,
    GetScreenSizeRequest,
    ChangePasswordRequest,
    BaseResponse,
    CursorPositionResponse,
    ScreenSizeResponse,
    ScreenshotResponse,
)


class AsyncComputerUseClient:
    """
    Asynchronous version of Computer Use Tool Server Client SDK
    """

    def __init__(self, base_url: str = "http://localhost:8102", api_version: str = "2020-04-01", auth_key: str = ""):
        """
        Initialize the asynchronous Computer Use SDK client
        
        Args:
            base_url: Base URL of the Computer Use Tool Server
            api_version: API version to use
            auth_key: Authentication key
        """
        self.base_url = base_url
        self.api_version = api_version
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Key": auth_key,
        }
        self._session = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def _make_request(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an asynchronous request to the Computer Use Tool Server
        
        Args:
            action: Action to perform
            params: Parameters for the action
            
        Returns:
            Response from the server
        """
        if not self._session:
            self._session = aiohttp.ClientSession()
            
        url = self.base_url
        # Convert all parameters to strings
        str_params = {k: str(v).lower() if isinstance(v, bool) else str(v) for k, v in params.items()}
        str_params.update({
            "Version": self.api_version,
            "Action": action
        })
        
        async with self._session.get(
            url,
            params=str_params,
            headers=self.headers
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def move_mouse(self, x: int, y: int) -> BaseResponse:
        """Move the mouse to the specified position"""
        request = MoveMouseRequest(PositionX=x, PositionY=y)
        response_data = await self._make_request("MoveMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def click_mouse(
            self,
            x: int,
            y: int,
            button: Literal["left", "right", "middle", "double_click", "double_left"] = "left",
            press: bool = False,
            release: bool = False
    ) -> BaseResponse:
        """Click the mouse at the specified position"""
        request = ClickMouseRequest(
            PositionX=x,
            PositionY=y,
            button=button,
            press=press,
            release=release
        )
        response_data = await self._make_request("ClickMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def press_mouse(
            self,
            x: int,
            y: int,
            button: Literal["left", "right", "middle"] = "left"
    ) -> BaseResponse:
        """Press the mouse button at the specified position"""
        request = PressMouseRequest(
            PositionX=x,
            PositionY=y,
            button=button
        )
        response_data = await self._make_request("PressMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def release_mouse(
            self,
            x: int,
            y: int,
            button: Literal["left", "right", "middle"] = "left"
    ) -> BaseResponse:
        """Release the mouse button at the specified position"""
        request = ReleaseMouseRequest(
            PositionX=x,
            PositionY=y,
            button=button
        )
        response_data = await self._make_request("ReleaseMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def drag_mouse(
            self,
            source_x: int,
            source_y: int,
            target_x: int,
            target_y: int
    ) -> BaseResponse:
        """Drag the mouse from source to target position"""
        request = DragMouseRequest(
            source_x=source_x,
            source_y=source_y,
            target_x=target_x,
            target_y=target_y
        )
        response_data = await self._make_request("DragMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def scroll(
            self,
            x: int,
            y: int,
            scroll_direction: Literal["up", "down", "left", "right"] = "up",
            scroll_amount: int = 1
    ) -> BaseResponse:
        """Scroll at the specified position"""
        request = ScrollRequest(
            PositionX=x,
            PositionY=y,
            scroll_direction=scroll_direction,
            scroll_amount=scroll_amount
        )
        response_data = await self._make_request("Scroll", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def press_key(self, key: str) -> BaseResponse:
        """Press the specified key"""
        request = PressKeyRequest(key=key)
        response_data = await self._make_request("PressKey", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def type_text(self, text: str) -> BaseResponse:
        """Type the specified text"""
        request = TypeTextRequest(text=text)
        response_data = await self._make_request("TypeText", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def wait(self, duration: int) -> BaseResponse:
        """Wait for the specified duration in milliseconds"""
        request = WaitRequest(duration=duration)
        response_data = await self._make_request("Wait", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    async def take_screenshot(self) -> ScreenshotResponse:
        """Take a screenshot"""
        request = TakeScreenshotRequest()
        response_data = await self._make_request("TakeScreenshot", request.model_dump(by_alias=True))
        return ScreenshotResponse(**response_data)

    async def get_cursor_position(self) -> CursorPositionResponse:
        """Get the current cursor position"""
        request = GetCursorPositionRequest()
        response_data = await self._make_request("GetCursorPosition", request.model_dump(by_alias=True))
        return CursorPositionResponse(**response_data)

    async def get_screen_size(self) -> ScreenSizeResponse:
        """Get the screen size"""
        request = GetScreenSizeRequest()
        response_data = await self._make_request("GetScreenSize", request.model_dump(by_alias=True))
        return ScreenSizeResponse(**response_data)

    async def change_password(self, username: str, new_password: str) -> BaseResponse:
        """Change the password for the specified user"""
        request = ChangePasswordRequest(
            Username=username,
            NewPassword=new_password
        )
        response_data = await self._make_request("ChangePassword", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)


async def new_async_computer_use_client(endpoint: str, auth_key: str = "") -> AsyncComputerUseClient:
    """Create a new asynchronous Computer Use client instance"""
    client = AsyncComputerUseClient(base_url=endpoint, auth_key=auth_key)
    await client.__aenter__()
    return client 