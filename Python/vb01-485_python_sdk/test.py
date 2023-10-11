import time

import device_model

"""
    WTVB01-485示例 Example
"""

# region 常用寄存器地址对照表  Common Register Address Comparison Table
"""

hex    dec      describe        describe en

0x00    0       保存/重启/恢复       SAVE
0x04    4       串口波特率          BAUD

0x1A    26      设备地址            IICADDR

0x3A    58      振动速度x           VX
0x3B    59      振动速度y           VY
0x3C    60      振动速度z           VZ

0x3D    61      振动角度x           ADX
0x3E    62      振动角度y           ADY
0x3F    63      振动角度z           ADZ

0x40    64      温度               TEMP

0x41    65      振动位移x           DX
0x42    66      振动位移y           DY
0x43    67      振动位移z           DZ    

0x44    68      振动频率x           HZX                
0x45    69      振动频率y           HZY
0x46    70      振动频率z           HZZ

0x63    99      截止频率            CUTOFFFREQI
0x64    100     截止频率            CUTOFFFREQF
0x65    101     检测周期            SAMPLEFREQ

"""
# endregion

# 拿到设备模型 Get the device model
device = device_model.DeviceModel("测试设备", "COM50", 9600, 0x50)
# 开启设备 Turn on the device
device.openDevice()
# 开启轮询 Enable loop reading
device.startLoopRead()
time.sleep(0.5)

# 数据展示 Data display
while True:
    # v：振动速度 a：振动角度 t：温度 s：振动位移 f：振动频率
    print("vx:{} vy:{} vz:{} ax:{} ay:{} az:{} t:{} sx:{} sy:{} sz:{} fx:{} fy:{} fz:{}".format(device.get("58"),device.get("59"),device.get("60"),device.get("61"),device.get("62"),device.get("63"),device.get("64"),device.get("65"),device.get("66"),device.get("67"),device.get("68"),device.get("69"),device.get("70")))
    time.sleep(0.2)


# 读取寄存器 从0x3a读取1个寄存器 Read Register Read 1 register from 0x3a
# device.readReg(0x3a, 1)
# 获得读取结果 Obtaining read results
# device.get(str(0x3a))

# 写入寄存器 向0x65写入50 即修改检测周期为50hz Write a register to 0x65 and write 50 to modify the detection cycle to 50Hz
# device.writeReg(0x65, 50)
