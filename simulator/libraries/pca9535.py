import emulator

I2C_ADDR = 0x20

class PCA9535:
    def __init__(self, i2c):
        pass

    def read_all_pca9535_inputs(self):
        return emulator.send_command('pca9535', 'get_inputs')['resp']
