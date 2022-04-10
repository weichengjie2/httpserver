# 1创建套接字
import socket
import threading
import re
import json
from urllib import parse
import serial ,time

import struct
RECV_TIMEOUT = 10            #串口接收，超时时间以10毫秒为一个单位。共10*10 =100毫秒

x = serial.Serial('com3', 230400, timeout=1)

#x = serial.Serial('/dev/ttuUSB0', 230400, timeout=1)



def checksettingpara(para):
    if '=' not in para:             #请求的数据如果没有 “=”，则认为非法
        return False
    Tmpdata = para.split("=")       #以 “=” 拆分为两部分
    Tmpdata[1].replace(' ', '')     #把空格去掉，以防请求的数据写法不规范，有空格导致的异常。
    dict = json.loads(Tmpdata[1])  # 把{} 数据化为字典。
    keyname ={"x_speed","y_speed","z_speed"}    #检查要判断的字段名是否存在。
    for i in keyname:
        if i not in dict.keys():
            return False
    return dict                             #合法，则返回字典

def float2byte(f):
    return [hex(i) for i in struct.pack('f', f)]

def jieShou(TimeOut):  # 接收函数
    while True: # 循环接收数据
        while x.inWaiting()>0:  # 当接收缓冲区中的数据不为零时，执行下面的代码
            myout=x.read(x.inWaiting()) # 提取接收缓冲区中所有字节数
            print(myout)
            if myout[0] != 0xFE or myout[1] != 0xEF:        ## if myout[0]==0xFE and myout[1]==0xEF:
                return False
            N = len(myout)
            BCC =0
            i =0
            while i<(N-1):
                BCC +=myout[i]
                i+=1
            BCC &=0XFF
            if BCC!=myout[N-1]:
                return False
            return True
        time.sleep(0.01)  # 延时0.1秒，免得CPU出问题
        if TimeOut>0:
            TimeOut -=1
        else:
            print('timeout')
            return False


def faSong():  # 发送函数
    # while True: # 循环发送数据
    print('Send Data to Com')
    #   time.sleep(1)   # 设置发送间隔时间
    Sendbuff = [0X01, 0X03, 0X00, 0X00, 0X00, 0X01, 0X84, 0X09]

    myinput = bytes(Sendbuff)  # 需要发送的十六进制数据
    x.write(myinput)  # 用write函数向串口发送数据
    jieShou(50)
#设置车子的速度



#  Sendbuff = bytearray([0xFE,0xEF,0x0D,0x01,0x3E,0x4C,0xCC,0xCC,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x1d])
def setspeed(xspeed,yspeed,zspeed):  # 发送函数

    Sendbuff = bytearray([0XFE, 0XEF, 0x0D, 0X01])
    if type(xspeed) is str:
        tmp =float(xspeed)
        x_v = float2byte(tmp)
    else:
        x_v =float2byte(xspeed)
    Sendbuff.append(int(x_v[3],16))
    Sendbuff.append(int(x_v[2],16))
    Sendbuff.append(int(x_v[1],16))
    Sendbuff.append(int(x_v[0],16))

    if type(yspeed) is str:
        tmp = float(yspeed)
        y_v = float2byte(tmp)
    else:
        y_v = float2byte(yspeed)
    Sendbuff.append(int(y_v[3], 16))
    Sendbuff.append(int(y_v[2], 16))
    Sendbuff.append(int(y_v[1], 16))
    Sendbuff.append(int(y_v[0], 16))

    if type(zspeed) is str:
        tmp = float(zspeed)
        z_v = float2byte(tmp)
    else:
        z_v = float2byte(zspeed)
    Sendbuff.append(int(z_v[3], 16))
    Sendbuff.append(int(z_v[2], 16))
    Sendbuff.append(int(z_v[1], 16))
    Sendbuff.append(int(z_v[0], 16))
    BCC =0
    for i in Sendbuff:
        BCC +=i
    BCC &= 0xFF  # 强制截断
    print(BCC,type(BCC))
    Sendbuff.append(BCC)
    myinput = bytes(Sendbuff)  # 需要发送的十六进制数据
    x.write(myinput)  # 用write函数向串口发送数据
    status =jieShou(RECV_TIMEOUT)
    return status

def recv_msg(new_tcp_socket, ip_port):
    """
    接受信息的函数
    :return:w
    """
    # 这个while可以不间断的接收客户端信息
    print(ip_port)
    while True:
        # 7.接受客户端发送的信息
        recv_data = new_tcp_socket.recv(1024)
        if recv_data:

            recv_data = recv_data.decode('utf-8')
#print('来自[%s]的信息：\r\n%s' % (str(ip_port), recv_text))
#把：#jsondata=%7B%22machine_id%22%3A%2218AA520A%22%2C%22machine_ip%22%3A%22192.168.0.200%22%2C%22machine_mac%22%3A%2240204AFF18AA%22%2C%22sign%22%3A%2276A061BCA3E649C1F94A84F14FD82AFC%22%7D
#变为：jsondata={"machine_id":"18AA520A","sign":"76A061BCA3E649C1F94A84F14FD82AFC"}
            real_data = parse.unquote(recv_data)       # 8.解码数据并输出
            # print(real_data)
            ''' 
            POSTNAM 发送的数据，服务端接收到的数据如下：
            POST /robot/getstatus HTTP/1.1
            User-Agent: PostmanRuntime/7.29.0
            Accept: */*
            Postman-Token: 50f43234-6190-4d2d-baad-5b1a1071c5b6
            Host: 192.168.5.6:60009
            Accept-Encoding: gzip, deflate, br
            Connection: keep-alive
            Content-Type: application/x-www-form-urlencoded
            Content-Length: 66
            jsondata={"machine":123,"time":"2020-12-11"}
            '''

            ret = re.match(r"[^/]+([^?]*)",real_data)       #拆分请求的URL
            print(ret)
            if ret:
                url_name = ret.group(1)
                print("*"*50, url_name)     #取到请求的 URL: /robot/speedsetting?
                if "/robot/speedsetting" in url_name:
                        paramdict = checksettingpara(real_data)         #判断字段是否存在
                        if type(paramdict) is bool:
                            break
                        print(paramdict)                    #打印X,Y,Z的速度。
                        x_speed =paramdict["x_speed"]
                        y_speed =paramdict["y_speed"]
                        z_speed = paramdict["z_speed"]
                        st =setspeed(x_speed,y_speed,z_speed)   #发送设置数据到串口
                        jsondata ={}
                        if st==True:
                            jsondata["return_code"] = "SUCCESS"
                        else:
                            jsondata["return_code"] = "FALSE"

                        jsondata["out_sign"] = "null"
                        response_body = json.dumps(jsondata, separators=(',', ':'))   #字典化为jsondata
                        # 构造响应数据
                        response_start_line = "HTTP/1.1 200 OK\r\n"
                        response_headers = "Server: My server\r\n"
                        response = response_start_line + response_headers + "\r\n" + response_body
                        print(response)
                        new_tcp_socket.send(bytes(response.encode("utf-8")))
                if "/robot/getspeed" in url_name:
                    jsondata = {
                                "return_code": "SUCCESS",
                                "x_speed": 0,
                                "y_speed": 0,
                                "z_speed": 0,
                                "out_sign": "null"
                                }
                    res = json.dumps(jsondata, separators=(',', ':'))
                    print(res)
                    response_start_line = "HTTP/1.1 200 OK\r\n"
                    response_headers = "Server: My server\r\n"
                    response_body = res
                    response = response_start_line + response_headers + "\r\n" + response_body
                    new_tcp_socket.send(bytes(response.encode("utf-8")))
                if "/robot/getstatus" in url_name:
                    jsondata = {
                                "return_code": "SUCCESS",
                                "front_disc": 100,
                                "behind_disc": 0,
                                "left_disc": 0,
                                "right_disc": 100,
                                "Current": 0,
                                "deg": 0,
                                "voltage": 24.01,
                                "battery": 60,
                                "out_sign": "null"
                                }
                    res = json.dumps(jsondata, separators=(',', ':'))
                    print(res)
                    response_start_line = "HTTP/1.1 200 OK\r\n"
                    response_headers = "Server: My server\r\n"
                    response_body = res
                    response = response_start_line + response_headers + "\r\n" + response_body
                    new_tcp_socket.send(bytes(response.encode("utf-8")))
       #     new_tcp_socket.send(response.encode("utf-8"))
            break
        else:
            break
    # 关闭客户端连接
    new_tcp_socket.close()


def ReadKeyboard():
    while True:
        seng_data = input('请输入要发送的：')
        if seng_data:
            print(seng_data.encode('gbk'))

def main():
    tcp_socket_host = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # 服务器端口回收操作（释放端口）
    tcp_socket_host.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,True)
    # 2绑定端口
    tcp_socket_host.bind(('',60009))            #ip 不需要绑定，因为一台电脑可能有多个网卡。随便哪个网卡，都允许做服务。

    # 3监听  变为被动套接字
    tcp_socket_host.listen(128)    #128可以监听的最大数量，最大链接数

    # 4等待客户端连接
    print("服务已开启,允许多个客户端的连接")
    while True:
        new_tcp_socket,ip_port=tcp_socket_host.accept()  #accept(new_socket,addr)
  #      print('新用户[%s]连接' % str(ip_port))
        # 创建线程
        thread_msg = threading.Thread(target=recv_msg, args=(new_tcp_socket, ip_port))
        t2 = threading.Thread(target=ReadKeyboard)
        # 子线程守护主线程
      #  thread_msg.setDaemon().setDaemon(True)
    #    self.thread_msg.setDaemon(True)
        # 启动线程
        thread_msg.start()
        t2.start()

    #6服务套接字关闭
    # socket_fuwu.close()    #服务器一般不关闭   此时服务端口因为需要一直执行所以也不能关闭

if __name__ == '__main__':
    main()
