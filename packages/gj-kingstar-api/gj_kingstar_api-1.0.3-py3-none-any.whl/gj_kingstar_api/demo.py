
def print_demo():
    print("""\
from gj_kingstar_api import MarketListener
from gj_kingstar_api import KingstarClient
import time

class MyMarketListener(MarketListener): #继承监听器
    def on_subscribe_tick_data(self,flow_no):
        print('成功订阅了行情！')
    def on_unsubscribe_tick_data(self,flow_no):
        print('取消订阅了行情！')
    def on_tick(self,flow_no,ticks): #返回的tick,是个对象数组
        for tick in  ticks: #type: gj_kingstar_api.entity.gtick.GTick
            print(flow_no,tick) # 实体类
            print(flow_no, tick.gtick2json()) #提供了转json的方法


if __name__ == "__main__":
    client = KingstarClient("ws://ip:port", "user", "pwd") #初始化
    client.add_listener(MyMarketListener()) #注册获取数据的回调类
    client.connect()  # 登陆

    client.subscribe_tick('SHFE','Future',['ag2506','ag2508']) # 订阅，入参为这3项必填，合约代码可传数组
    # client.subscribe_tick('SHFE', 'Future', 'ag2508')
    # client.subscribe_tick('SH', 'CS', '601211')
    time.sleep(10)
    # client.close()
    client.unsubscribe_tick('SHFE','Future',['ag2506','ag2508'])
    while True: # 整个订阅机制都是子线程运行，如果需要持续接收tick，主线程需要手动维持运行
        time.sleep(1)
    """)

