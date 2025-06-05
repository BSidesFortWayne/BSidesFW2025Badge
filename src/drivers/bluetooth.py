import bluetooth, machine, micropython, time, errno
from micropython import const

SENDER_ID   = bytes([0xA2, 0x3F, 0x51])
ADV_INT_MS  = 50
ON_TIME_MS  = 10_000

class Bluetooth:
    def __init__(self):
        self.last_counter  = -1
        self.rebroadcasted = False
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble_callbacks = []

        self.ble.irq(self.irq)
        self.ble.gap_scan(0, 30_000, 30_000)
        
    def manuf_data(self, adv: bytes) -> bytes | None:
        i = 0
        while i < len(adv):
            ln = adv[i]
            if ln == 0:
                break
            typ = adv[i+1]
            if typ == 0xFF:
                return adv[i+2 : i+1+ln]
            i += ln + 1
        return None

    def make_adv(self, blob: bytes) -> bytes:
        return b"\x02\x01\x06" + bytes([len(blob)+1, 0xFF]) + blob

    def irq(self, event, data):
        try:
            if event == const(5):                         # _IRQ_SCAN_RESULT
                _, _, _, _, adv = data
                md = self.manuf_data(adv)
                if md and len(md) >= 5:
                    md_bytes = bytes(md)                  # convert once
                    if not md_bytes.startswith(SENDER_ID):
                        return                            # not our network

                    counter = (md_bytes[3] << 8) | md_bytes[4]

                    if counter > self.last_counter:
                        self.last_counter  = counter
                        self.rebroadcasted = False

                        try:
                            payload = md_bytes[5:].decode()
                        except:
                            payload = md_bytes[5:]
                        
                        print('BLE message')
                        print('----')
                        print('counter', counter)
                        print('payload:', payload)
                        print('----')
                        for callback in self.ble_callbacks:
                            micropython.schedule(lambda _, c=callback: c(payload), 0)

                    if not self.rebroadcasted and counter == self.last_counter:
                        self.ble.gap_advertise(ADV_INT_MS,
                                        self.make_adv(md_bytes),
                                        connectable=False)
                        self.rebroadcasted = True
        except Exception as e:
            print('BLE failed: ' + str(e))
