
from  gj_kingstar_api.entity.gtick import GTick

class MarketListener():
    def on_subscribe_tick_data(self,flow_no):
        """订阅返回触发"""
        pass

    def on_tick(self,flow_no,ticks:[GTick]):
        """行情tick返回触发"""
        pass

    def on_unsubscribe_tick_data(self,flow_no):
        """取消订阅返回触发"""
        pass


