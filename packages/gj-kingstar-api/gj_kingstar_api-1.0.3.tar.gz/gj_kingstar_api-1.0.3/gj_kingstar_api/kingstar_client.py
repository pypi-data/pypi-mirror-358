import threading
import asyncio
import time
import logging
import websockets
from gj_kingstar_api.proto.common_pb2 import *
from gj_kingstar_api.proto.market_pb2 import *
import hashlib
import struct
from  gj_kingstar_api.entity.gtick import GTick
from gj_kingstar_api.market_listener import MarketListener



logging.basicConfig(level=logging.INFO)


class KingstarClient:
    def __init__(self, url: str, user: str, pwd: str):
        """
        金仕达客户端初始化
        :param url: 金仕达连接地址
        :param user: 用户名
        :param pwd: 密码
        """
        self.url = url
        self.user = user
        self.pwd = pwd
        self.ws = None
        self.listeners = []
        self._loop = asyncio.new_event_loop()
        self._connect_task = None
        self._running = False
        self._heartbeat_interval = 30
        self.flow_no=0
        self.login_flag = False
        self._thread = threading.Thread(target=self._start_loop, daemon=True)
        self._thread.start()

    def _start_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def connect(self):
        """
        启动客户端websocket连接，做登陆行情源、心跳检查等初始化操作
        :return:
        """
        self._running = True
        self._connect_task = asyncio.run_coroutine_threadsafe(self._auto_connect(), self._loop)

    async def _auto_connect(self):
        while self._running:
            try:
                async with websockets.connect(self.url) as ws:
                    self.ws = ws
                    await self._auth_login()
                    # await self._resubscribe()
                    await self._start_heartbeat()
                    await self._message_handler()  # 处理消息
            except Exception as e:
                logging.error(f"连接异常: {e}, 5秒后重连...")
                await asyncio.sleep(5)

    async def _auth_login(self):

        flow_no, command_no, data_part = await self._receive_msg()
        p = PushSessionKey()
        p.ParseFromString(data_part)
        login_request = LoginRequest()
        login_request.username = self.user
        md5_hash = hashlib.md5()
        md5_hash.update((self.user + self.pwd + p.session_key).encode('gbk'))
        access_token = md5_hash.hexdigest()
        login_request.access_token = access_token
        login_request.channel_id = 'diy'
        login_request.product_type = ProductType.PT_PC
        login_request.version_id = '1.0'
        req_str = login_request.SerializeToString()

        await self._send_msg(CommonInterface.CI_LOGIN, req_str)
        flow_no,command_no,data=await self._receive_msg()
        if data!=b'\n\x00':
            raise ConnectionError("登录失败")
        else:
            self.login_flag=True
            print('登陆成功')
        pass

    async def _receive_msg(self):
        response = await self.ws.recv()
        return self._parse_response(response)

    def _parse_response(self,response):
        format = ">2siiiI"
        header_size = struct.calcsize(format)
        header_data = response[:header_size]
        caTag, flow_no, command_no, datatype, unDataLength = struct.unpack(format, header_data)
        data = response[header_size: header_size + unDataLength]
        return flow_no, command_no, data


    async def _send_msg(self,command_no, body):
        self.flow_no=self.flow_no+1
        datalength=len(body)
        header= struct.pack(
            ">2siiiI",
            b'BF',
            self.flow_no,
            command_no,
            0,
            datalength
        )

        await self.ws.send(header +body)



    async def _start_heartbeat(self):
        async def heartbeat_task():
            while True:
                await asyncio.sleep(self._heartbeat_interval)
                await self._send_msg(CommonInterface.CI_HEARTBEAT, b'')

        asyncio.create_task(heartbeat_task())

    async def _message_handler(self):
        try:
            async for response in self.ws:
                flow_no, command_no, data_part=self._parse_response(response)
                if command_no == MarketInterface.MI_SUBSCRIBE_TICK_DATA:
                    for listener in self.listeners:
                        listener.on_subscribe_tick_data(self.flow_no)
                elif command_no == MarketInterface.MI_PUSH_TICK_DATA:
                    pushTickData = PushTickData()
                    pushTickData.ParseFromString(data_part)
                    ticks=[]
                    for tick in pushTickData.ticks:
                        gtick = GTick()
                        gtick.pb2gtick(tick)
                        ticks.append(gtick)
                    for listener in self.listeners:
                        listener.on_tick(self.flow_no,ticks)
                elif command_no == MarketInterface.MI_UNSUBSCRIBE_TICK_DATA:
                    for listener in self.listeners:
                        listener.on_unsubscribe_tick_data(self.flow_no)
        except websockets.ConnectionClosed:
            logging.warning("连接断开，触发重连...")

    # async def _resubscribe(self):
    #     for inst in self._subscribed_instruments:
    #         await self._send_subscribe(inst)

    def add_listener(self, listener: MarketListener):
        """
        注册监听器，用于接收回调数据
        :param listener: MarketListener
        :return:
        """
        self.listeners.append(listener)

    # def query_instrument_info(self, symbol: str):
    #     req = proto.InstrumentInfoRequest(symbol=symbol)
    #     asyncio.run_coroutine_threadsafe(
    #         self.ws.send(req.SerializeToString()),
    #         self._loop
    #     )

    def _wait_login(self):
        while not self.login_flag:
            time.sleep(0.1)

    def unsubscribe_tick(self, exchange_id:str,type,instrument_id):
        """
        取消订阅tick
        :param exchange_id: 交易所代码
        :param type: Future：期货；Option：期权；CS：股票
        :param instrument_id: 合约代码，或合约代码数组
        :return:
        """
        if type=='Future':
            type=CommodityType.CT_FUTURE
        elif type=='Option':
            type=CommodityType.CT_OPTION
        elif type=='CS':
            type=CommodityType.CT_STOCK
        else:
            raise Exception('type格式异常，应为以下3种：Future、Option、CS')
        if isinstance(instrument_id,str):
            commoditykey = CommodityKey()
            commoditykey.type = type
            commoditykey.exchange_code = exchange_id
            commoditykey.code = instrument_id
            commoditys=[commoditykey]
        elif isinstance(instrument_id,list):
            commoditys=[]
            for code in instrument_id:
                commoditykey = CommodityKey()
                commoditykey.type = type
                commoditykey.exchange_code = exchange_id
                commoditykey.code = code
                commoditys.append(commoditykey)
        else:
            raise Exception('instrument_id格式异常，应为字符串或字符串数组')
        self._wait_login()
        unsubscribeTickDataRequest = UnsubscribeTickDataRequest()
        for commodity in commoditys:
            unsubscribeTickDataRequest.keys.append(commodity)
        asyncio.run_coroutine_threadsafe(
            self._send_unsubscribe(unsubscribeTickDataRequest),
            self._loop
        )


    def subscribe_tick(self, exchange_id:str,type,instrument_id):
        """
       订阅tick
       :param exchange_id: 交易所代码
       :param type: Future：期货；Option：期权；CS：股票
       :param instrument_id: 合约代码，或合约代码数组
       :return:
        """
        if type=='Future':
            type=CommodityType.CT_FUTURE
        elif type=='Option':
            type=CommodityType.CT_OPTION
        elif type=='CS':
            type=CommodityType.CT_STOCK
        else:
            raise Exception('type格式异常，应为以下3种：Future、Option、CS')
        if isinstance(instrument_id,str):
            commoditykey = CommodityKey()
            commoditykey.type = type
            commoditykey.exchange_code = exchange_id
            commoditykey.code = instrument_id
            commoditys=[commoditykey]
        elif isinstance(instrument_id,list):
            commoditys=[]
            for code in instrument_id:
                commoditykey = CommodityKey()
                commoditykey.type = type
                commoditykey.exchange_code = exchange_id
                commoditykey.code = code
                commoditys.append(commoditykey)
        else:
            raise Exception('instrument_id格式异常，应为字符串或字符串数组')
        self._wait_login()
        subscribeTickDataRequest = SubscribeTickDataRequest()
        for commodity in commoditys:
            subscribeTickDataRequest.keys.append(commodity)
        subscribeTickDataRequest.is_full_subscribe = False
        subscribeTickDataRequest.compress_type = TickDataCompressType.TDCT_NO_COMPRESS
        subscribeTickDataRequest.fields.append(CommodityListField.CLF_ASK_PRICE1)
        asyncio.run_coroutine_threadsafe(
            self._send_subscribe(subscribeTickDataRequest),
            self._loop
        )
    async def _send_subscribe(self, subscribeTickDataRequest):
        await self._send_msg(221001,subscribeTickDataRequest.SerializeToString())
    async def _send_unsubscribe(self, unsubscribeTickDataRequest):
        await self._send_msg(221002,unsubscribeTickDataRequest.SerializeToString())
    def close(self):
        self._running = False
        if self.ws:
            asyncio.run_coroutine_threadsafe(self.ws.close(), self._loop)


