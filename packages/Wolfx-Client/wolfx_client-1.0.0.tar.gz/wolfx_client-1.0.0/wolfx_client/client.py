import asyncio
import inspect
import websockets
import logging
import json

from .types.EEW import EEW
from .types.EQL import EarthquakeData
from .types.heartbeat import Heartbeat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventHandler:
    def __init__(self, client):
        self._handlers = {}
        self.client = client
        self._type_map = {
            "heartbeat": ("on_heartbeat", Heartbeat),
            "jma_eew": ("on_eew", EEW),
            "jma_eqlist": ("on_eqlist", EarthquakeData),
        }

    def register(self, name, func):
        self._handlers[name] = func

    def get(self, name):
        return self._handlers.get(name)
    
    def resolve_event(self, data_dict: dict):
        event_type = data_dict.get("type")
        return self._type_map.get(event_type, ("on_message", dict))  # デフォルトはon_messageにdict

    async def dispatch(self, raw_data):
        try:
            data_dict = json.loads(raw_data)

            event_name, expected_type = self.resolve_event(data_dict)
            handler = self.get(event_name)
            if not handler:
                return  # ハンドラが登録されていなければ無視

            # 型付きデータクラスに変換
            if expected_type is dict:
                args = (data_dict,)
            elif expected_type is Heartbeat:
                # Heartbeatは単一の引数を期待
                args = (expected_type(data_dict),)
            else:
                args = (expected_type(**data_dict),)

            if inspect.iscoroutinefunction(handler):
                await handler(*args)
            else:
                handler(*args)

        except Exception as e:
            print(f"[DispatchError] {e}")


class Client:
    """
    WebSocketクライアント
    
    :param  isEQL: bool
    地震情報の履歴を取得できます。
    ※このオプションの使用は非推奨です。
        
    """
    def __init__(self, isEQL: bool = False):
        self.isEQL = isEQL
        self.handlers = EventHandler(self)
        self.url = self.__get_url__()
        self._loop = asyncio.get_event_loop()

    def event(self, func):
        self.handlers.register(func.__name__, func)
        return func

    async def _connect(self):
        async with websockets.connect(self.url) as ws:
            await self.handlers.get("on_ready")()
            async for message in ws:
                await self.handlers.dispatch(message)
    
    
    def __get_url__(self):
        if self.isEQL:
            return "wss://ws-api.wolfx.jp/jma_eqlist"
        return "wss://ws-api.wolfx.jp/jma_eew"

    @property
    def is_connected(self):
        return self._loop.is_running()

    def run(self):
        try:
            self._loop.run_until_complete(self._connect())
        except KeyboardInterrupt:
            pass
