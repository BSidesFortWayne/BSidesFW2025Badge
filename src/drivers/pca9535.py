from drivers.base import Driver

I2C_ADDR = 0x20  # PCA9535 address
class PCA9535(Driver):
    def __init__(self, i2c):
        super().__init__()
        # Initialize I2C on an ESP32 
        self.i2c = i2c

        I2C_ADDR = 0x20  # PCA9535 address

        # 1) Configure all Port 0 pins as inputs (0xFF = all bits are inputs)
        self.i2c.writeto_mem(I2C_ADDR, 0x06, b'\xFF')

        # 2) Configure all Port 1 pins as inputs (0xFF = all bits are inputs)
        self.i2c.writeto_mem(I2C_ADDR, 0x07, b'\xFF')

    def read_pca9535_input(self, port: int):
        # Read one byte from the specified port (register 0x00 or 0x01)
        port_data = self.i2c.readfrom_mem(I2C_ADDR, port, 1)[0]
    
        # Return the value of the specified pin
        return port_data
                
    def read_all_pca9535_inputs(self):
        # Read one byte from Input Port 0 (register 0x00)
        port0_data = self.read_pca9535_input(0x00)
    
        # Read one byte from Input Port 1 (register 0x01)
        port1_data = self.read_pca9535_input(0x01)
    
        # bit mask the two bytes together
        return port0_data | (port1_data << 8)


