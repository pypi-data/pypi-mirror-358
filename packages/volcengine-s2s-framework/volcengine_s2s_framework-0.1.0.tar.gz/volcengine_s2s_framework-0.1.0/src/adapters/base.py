import queue
import threading
from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator, Optional
from dataclasses import dataclass

from src.adapters.type import AdapterType
from src.config import WELCOME_MESSAGE


@dataclass
class ChatTTSTextPayload:
    start: bool
    end: bool
    content: str


class AudioAdapter(ABC):
    """音频适配器基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_connected = False
        self.session_id = None

    @abstractmethod
    async def connect(self) -> bool:
        """建立连接"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """断开连接"""
        pass

    @abstractmethod
    async def send_audio(self, audio_data: bytes) -> bool:
        """发送音频数据"""
        pass

    @abstractmethod
    async def receive_audio(self) -> AsyncGenerator[bytes, None]:
        """接收音频数据流"""
        pass

    @abstractmethod
    async def send_text(self, text: str) -> bool:
        """发送文本消息"""
        pass

    async def send_welcome(self):
        return await self.send_text(WELCOME_MESSAGE)

    async def send_chat_tts_text(self, content: str, start: bool = True, end: bool = True) -> bool:
        """发送ChatTTS文本请求"""
        payload = ChatTTSTextPayload(start=start, end=end, content=content)
        return await self.send_text_with_payload(payload)

    async def send_text_with_payload(self, payload: ChatTTSTextPayload) -> bool:
        """发送带payload的文本请求（由子类实现具体协议）"""
        return await self.send_text(payload.content)

    @property
    @abstractmethod
    def adapter_type(self) -> AdapterType:
        """获取适配器类型"""
        pass

    async def setup_audio_devices(self, p, stop_event: threading.Event) -> tuple[
        Optional[threading.Thread], Optional[threading.Thread]]:
        """设置音频设备，返回(recorder_thread, player_thread)"""
        return None, None

    async def run_sender_task(self, send_queue: queue.Queue, stop_event: threading.Event) -> None:
        """运行发送任务"""
        pass

    async def run_receiver_task(self, play_queue: queue.Queue, stop_event: threading.Event) -> None:
        """运行接收任务"""
        pass


class ConnectionConfig:
    """连接配置基类"""

    def __init__(self, **kwargs):
        self.params = kwargs

    def get(self, key: str, default: Any = None) -> Any:
        return self.params.get(key, default)

    def update(self, **kwargs) -> None:
        self.params.update(kwargs)


class LocalConnectionConfig(ConnectionConfig):
    """本地连接配置"""

    def __init__(self, app_id: str, access_token: str, **kwargs):
        super().__init__(
            app_id=app_id,
            access_token=access_token,
            base_url="wss://openspeech.bytedance.com/api/v3/realtime/dialogue",
            **kwargs
            )


class BrowserConnectionConfig(ConnectionConfig):
    """浏览器连接配置（通过代理服务器）"""

    def __init__(self, proxy_url: str, app_id: str, access_token: str, **kwargs):
        super().__init__(
            proxy_url=proxy_url, app_id=app_id, access_token=access_token, **kwargs
            )
