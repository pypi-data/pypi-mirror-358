import asyncio
import inspect
import websockets
import logging
import json
import threading

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
        self._task = None
        self._running = False

    def event(self, func):
        self.handlers.register(func.__name__, func)
        return func

    async def _connect(self):
        async with websockets.connect(self.url, logger=logger) as ws:
            # on_readyハンドラーが存在する場合のみ呼び出し
            on_ready_handler = self.handlers.get("on_ready")
            if on_ready_handler:
                if inspect.iscoroutinefunction(on_ready_handler):
                    await on_ready_handler()
                else:
                    on_ready_handler()
            
            async for message in ws:
                await self.handlers.dispatch(message)
    
    
    def __get_url__(self):
        if self.isEQL:
            return "wss://ws-api.wolfx.jp/jma_eqlist"
        return "wss://ws-api.wolfx.jp/jma_eew"

    @property
    def is_connected(self):
        return self._running and self._task and not self._task.done()

    async def start(self):
        """WebSocket接続を開始します（discord.pyとの統合用）"""
        if self._running:
            print("既に実行中です")
            return
            
        self._running = True
        try:
            await self._connect()
        except Exception as e:
            print(f"WebSocket接続エラー: {e}")
        finally:
            self._running = False

    def run(self, loop=None):
        """WebSocket接続を開始します（非同期でバックグラウンド実行）"""
        if self._running:
            print("既に実行中です")
            return self._task
            
        # 現在のイベントループを取得（discord.pyのループを使用）
        if loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # イベントループが実行中でない場合は新しく作成
                return self.run_sync()
        
        self._task = loop.create_task(self.start())
        return self._task
            
    def run_sync(self):
        """WebSocket接続を開始します（同期実行、ブロッキング）"""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            pass
            
    async def stop(self):
        """WebSocket接続を停止します"""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._running = False
