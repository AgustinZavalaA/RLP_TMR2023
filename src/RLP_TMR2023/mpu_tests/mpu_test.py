# Delete when we don't need it anymore

import time

import numpy as np
from mpu9250_jmdev.mpu_9250 import MPU9250
from mpu9250_jmdev.registers import \
    AK8963_ADDRESS, MPU9050_ADDRESS_68, GFS_1000, AFS_8G, AK8963_BIT_16, AK8963_MODE_C100HZ

mpu = MPU9250(
    address_ak=AK8963_ADDRESS,
    address_mpu_master=MPU9050_ADDRESS_68,  # In 0x68 Address
    address_mpu_slave=None,
    bus=1,
    gfs=GFS_1000,
    afs=AFS_8G,
    mfs=AK8963_BIT_16,
    mode=AK8963_MODE_C100HZ)

mpu.configure()

var = 100
data_accel = np.zeros([var, 3])
data_mag = np.zeros([var, 3])
data_gyro = np.zeros([var, 3])

for i in range(var):
    accel = mpu.readAccelerometerMaster()
    mag = mpu.readMagnetometerMaster()
    gyro = mpu.readGyroscopeMaster()
    print(f" {i}"
          f"Accelerometer:      {accel}\n"
          f"Magnetometer:       {mag}\n"
          f"Gyroscope:          {gyro}")
    data_accel[i] = accel
    data_mag[i] = mag
    data_gyro[i] = gyro
    
# save a numpy array in csv file
np.save("data_accel.csv", data_accel)
np.save("data_mag.csv", data_mag)
np.save("data_gyro.csv", data_gyro)
