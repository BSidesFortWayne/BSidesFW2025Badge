from machine import Pin, I2C
import lis3dh

i2c = I2C(sda=Pin(17), scl=Pin(25))
imu = lis3dh.LIS3DH_I2C(i2c)
