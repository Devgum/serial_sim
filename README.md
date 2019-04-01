# serial_sim

这是一个通过串口操作SIM卡的类，方便发送AT指令和接受串口消息。
本人的使用场景在于监听短信接收，用以同步短信。其中包含了短信常用方法。

## 依赖

* 支持AT指令的串口SIM卡设备
* python >= 3.6
* pyserial
* smspdudecoder

## 示例

发送'AT+CSQ'到设备/dev/ttyS0，并打印结果
```
with serial.Serial('/dev/ttyS0', baudrate=115200, timeout=10) as serial_obj:
    sim = SIM(serial_obj)
    print(sim.send('AT+CSQ'))
```

打印
```
['+CSQ: 20,99', 'OK']
```
