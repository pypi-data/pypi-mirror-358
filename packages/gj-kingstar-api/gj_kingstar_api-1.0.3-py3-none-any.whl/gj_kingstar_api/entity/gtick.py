import datetime
import logging

from gj_kingstar_api.proto.market_pb2 import CommodityTickData2,CommodityType
import re
import traceback
from dataclasses import dataclass

@dataclass
class GTick:


    trading_day:str
    """行情时间戳（毫秒）"""
    trade_timestamp:int
    """交易所代码"""
    exchange_id:str
    """CTP合约代码，虚拟合约采用默认金仕达逻辑"""
    instrument_id:str
    """合约代码"""
    unique_instrument_id:str
    """最新价"""
    last_price:float
    """开盘价"""
    open_price:float
    """最高价"""
    highest_price:float
    """最低价"""
    lowest_price:float
    """涨停价"""
    upper_limit_price:float
    """跌停价"""
    lower_limit_price:float
    """昨结算价"""
    pre_settlement_price:float
    """昨收盘价"""
    pre_close_price:float
    """成交量"""
    volume:int
    """成交额"""
    turnover:float
    """持仓量"""
    open_interest:int
    """卖一报盘价"""
    a1:float
    # """卖二报盘价"""
    # a2:float
    # """卖三报盘价"""
    # a3:float
    # """卖四报盘价"""
    # a4:float
    # """卖五报盘价"""
    # a5:float
    """卖一报盘量"""
    a1_v:int
    # """卖二报盘量"""
    # a2_v:int
    # """卖三报盘量"""
    # a3_v:int
    # """卖四报盘量"""
    # a4_v:int
    # """卖五报盘量"""
    # a5_v:int
    """买一报盘价"""
    b1:float
    # """买二报盘价"""
    # b2:float
    # """买三报盘价"""
    # b3:float
    # """买四报盘价"""
    # b4:float
    # """买五报盘价"""
    # b5:float
    """买一报盘量"""
    b1_v:int
    # """买二报盘量"""
    # b2_v
    # """买三报盘量"""
    # b3_v
    # """买四报盘量"""
    # b4_v
    # """买五报盘量"""
    # b5_v
    delta:float
    gamma:float
    vega:float
    theta:float
    rho:float

    insert_time:datetime.datetime
    """程序拉取并解析tick的时间，datetime类型"""


    def __init__(self):
        pass
    def pb2gtick(self,t:CommodityTickData2):
        """装载tick数据，如果是郑商所，则需要额外的最后交割日字段，以实现3位补4位的逻辑"""
        self.trading_day=str(t.trading_day)
        self.trade_timestamp=t.timestamp
        self.exchange_id=t.key.exchange_code
        self.instrument_id=t.key.code
        try:
            if t.key.type==CommodityType.CT_STOCK:
                contract_type='S'
                product_id=self.instrument_id
                self.unique_instrument_id = f"{self.exchange_id}|{contract_type}|{product_id}".upper()
            elif t.key.type==CommodityType.CT_FUTURE:
                contract_type='F'
                product_id = re.search(r'[a-zA-Z]+', self.instrument_id).group()
                suffix = self.instrument_id.replace(product_id, '', 1)
                if self.exchange_id == 'CZCE':  # TODO 简单起见先这么写，留坑后补
                    suffix = '2' + suffix
                self.unique_instrument_id = f"{self.exchange_id}|{contract_type}|{product_id}|{suffix}".upper()

            elif t.key.type == CommodityType.CT_OPTION:
                contract_type = 'O'
                product_id = re.search(r'[a-zA-Z]+', self.instrument_id).group()
                suffix = self.instrument_id.replace(product_id, '', 1).replace('-','')
                self.unique_instrument_id = f"{self.exchange_id}|{contract_type}|{product_id}|{suffix}".upper()


        except Exception as e:
            self.unique_instrument_id=''
            logging.warning(f"GTick装载异常：{traceback.format_exc()}")
        self.last_price=t.last_price
        self.open_price=t.open_price
        self.highest_price=t.highest_price
        self.lowest_price=t.lowest_price
        self.upper_limit_price=t.upper_limit_price
        self.lower_limit_price=t.lower_limit_price
        self.pre_settlement_price=t.pre_settlement_price
        self.pre_close_price=t.pre_close_price
        self.volume=t.volume
        self.turnover=t.turnover
        self.open_interest=t.open_interest
        try:
            self.a1 = t.ask_prices[0]
        except:
            self.a1=0
        try:
            self.a1_v = t.ask_volumes[0]
        except:
            self.a1_v=0
        try:
            self.b1=t.bid_prices[0]
        except:
            self.b1=0
        try:
            self.b1_v=t.bid_volumes[0]
        except:
            self.b1_v=0
        self.delta=t.delta
        self.gamma=t.gamma
        self.vega=t.vega
        self.theta=t.theta
        self.rho=t.rho
        self.insert_time=datetime.datetime.now()


    def gtick2json(self):
        """返回json"""
        return {
            'trading_day': self.trading_day,
            'trade_timestamp': self.trade_timestamp,
            'exchange_id': self.exchange_id,
            'instrument_id': self.instrument_id,
            'unique_instrument_id': self.unique_instrument_id,
            'last_price': self.last_price,
            'open_price': self.open_price,
            'highest_price': self.highest_price,
            'lowest_price': self.lowest_price,
            'upper_limit_price': self.upper_limit_price,
            'lower_limit_price': self.lower_limit_price,
            'pre_settlement_price': self.pre_settlement_price,
            'pre_close_price': self.pre_close_price,
            'volume': self.volume,
            'turnover': self.turnover,
            'open_interest': self.open_interest,
            'a1': self.a1,
            'a1_v': self.a1_v,
            'b1': self.b1,
            'b1_v': self.b1_v,
            'delta': self.delta,
            'gamma': self.gamma,
            'vega': self.vega,
            'theta': self.theta,
            'rho': self.rho
        }

