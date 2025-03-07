from machine import Pin, I2C
import lis3dh

i2c = I2C(sda=Pin(21), scl=Pin(22))
imu = lis3dh.LIS3DH_I2C(i2c)
