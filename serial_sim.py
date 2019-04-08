# coding:utf-8

from smspdu.easy import easy_sms
import serial
import re


class SIM:

    def __init__(self, serial_obj):
        self.serial = serial_obj
        self.init_sim()

    def init_sim(self):
        self.send('ATE0')
        self.send('AT+CSDH=0')

    def send(self, message):
        if isinstance(message, str):
            message = message.encode('utf-8')
        if not message.endswith(b'\r\n'):
            message += b'\r\n'
        self.serial.write(message)
        return self.recieve()

    def recieve(self, eof_regex=[r'OK', r'ERROR']):
        result = []
        while True:
            line = self.serial.readline()
            if not line:
                return result
            line = line.replace(b'\r\n', b'')
            if line:
                line = str(line, 'utf-8')
                result.append(line)
                for regex in eof_regex:
                    if re.match(regex, line):
                        return result
        return result

    def get_msg(self, index):
        msg = []
        result = self.send(f'AT+CMGR={index}')
        for item in result:
            if self.is_pdu_like(item):
                msg.append(str(easy_sms(item)))
        return '\n'.join(msg)

    def is_pdu_like(self, msg):
        regex = r'^[a-fA-F0-9]+$'
        if re.match(regex, msg):
            return True
        return False

    def del_msg(self, index):
        result = self.send(f'AT+CMGD={index}')
        return result[-1] == 'OK'

    def list_msg(self):
        result = self.send(f'AT+CMGL=1')
        if not result:
            return ['No response']
        if result[-1] == 'OK':
            return list(
                map(
                    lambda x: easy_sms(x) if self.is_pdu_like(x) else x,
                    result[:-1]
                )
            )
        return result[-1]

    def listen_msg(self, callback=None, del_after_call=False):
        try:
            while True:
                recv = self.recieve(
                    eof_regex=[r'OK', r'ERROR', r'\+CMTI: "SM",\d+'])
                for item in recv:
                    m = re.match(r'\+CMTI: "SM",(\d+)', item)
                    if m:
                        msg_index = m.group(1)
                        msg = self.get_msg(msg_index)
                        if callable(callback):
                            if callback(msg) and del_after_call:
                                self.del_msg(msg_index)
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    with serial.Serial('/dev/ttyS0', baudrate=115200, timeout=10) as serial_obj:
        sim = SIM(serial_obj)
        print(sim.send('AT+CSQ'))
