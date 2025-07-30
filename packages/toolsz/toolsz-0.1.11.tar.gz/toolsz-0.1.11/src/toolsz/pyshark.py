"""抓包和反编译 pyshark"""

import time
import pyshark

# !pip install pyshark
# 使用过滤器捕获 HTTP 流量
capture = pyshark.LiveCapture(interface="Wi-Fi", display_filter="http")

# 捕获流量，设置超时时间为50秒
capture.sniff(timeout=5)

# 打印捕获到的 HTTP 数据包
print("start")
for packet in capture:
    print(packet)
    # print('Packet Number:', packet.number)
    # print('Timestamp:', packet.sniff_time)
    # print('Source IP:', packet.ip.src)
    # print('Destination IP:', packet.ip.dst)
    time.sleep(0.1)


# 捕获网络接口上的流量
capture = pyshark.LiveCapture(interface="eth0")

# 捕获流量，设置超时时间为50秒
capture.sniff(timeout=50)

# 访问数据包内容
for packet in capture:
    print("Packet Number:", packet.number)
    print("Timestamp:", packet.sniff_time)
    print("Source IP:", packet.ip.src)
    print("Destination IP:", packet.ip.dst)
    if "http" in packet:
        print("HTTP Method:", packet.http.request_method)
        print("HTTP Host:", packet.http.host)
