# coding:UTF-8
import time
from lib.protocol_resolver.interface.i_protocol_resolver import IProtocolResolver

"""
    维特协议解析器
"""

class WitProtocolResolver(IProtocolResolver):
    TempBytes = []          # 临时数据列表 Temporary Data List
    PackSize = 11           # 一包数据大小 Size of a packet of data
    gyroRange = 2000.0      # 角速度量程 Angular velocity range
    accRange = 16.0         # 加速度量程 Acceleration range
    angleRange = 180.0      # 角度量程  Angle range
    TempFindValues = []     # 读取指定寄存器返回的数据  Read the data returned by the specified register

    def setConfig(self, deviceModel):
        pass

    def sendData(self, sendData, deviceModel):
        success_bytes = deviceModel.serialPort.write(sendData)
    def passiveReceiveData(self, data, deviceModel):
        """
        接收数据处理
        :param data: 串口数据
        :param deviceModel: 设备模型
        :return:
        """
        global TempBytes
        for val in data:
            self.TempBytes.append(val)
            if (self.TempBytes[0]!=0x55):                   #非标识符0x55开头的 Not starting with identifier 0x55
                del self.TempBytes[0]                       #去除第一个字节 Remove the first byte
                continue
            if (len(self.TempBytes)>1):
                if (((self.TempBytes[1] - 0x50 >=0 and self.TempBytes[1] - 0x50 <=11) or self.TempBytes[1]==0x5f)==False):   # 第二个字节数值不在0x50~0x5a范围或者不等于0x5f  The second byte value is not in the range of 0x50~0x5a or is not equal to 0x5f
                    del self.TempBytes[0]                   #去除第一个字节 Remove the first byte
                    continue
            if (len(self.TempBytes) == self.PackSize):      #表示一个包的数据大小 Represents the data size of a package
                CheckSum = 0                                #求和校验位 Sum check bit
                for i in range(0,self.PackSize-1):
                    CheckSum+=self.TempBytes[i]
                if (CheckSum&0xff==self.TempBytes[self.PackSize-1]):    # 校验和通过  Checksum passed
                    if (self.TempBytes[1] == 0x50):                     # 芯片时间包 Chip Time Packet
                        self.get_chiptime(self.TempBytes, deviceModel)  # 结算芯片时间数据 Settlement chip time data
                    elif (self.TempBytes[1]==0x51):                     # 加速度包 Acceleration package
                        self.get_acc(self.TempBytes,deviceModel)        # 结算加速度数据 Settlement acceleration data
                    elif(self.TempBytes[1]==0x52):                      # 角速度包 Angular velocity package
                        self.get_gyro(self.TempBytes,deviceModel)       # 结算角速度数据 Settlement angular velocity data
                    elif(self.TempBytes[1]==0x53):                      # 角度包 Angle package
                        self.get_angle(self.TempBytes,deviceModel)      # 结算角度数据 Settlement angle data
                    elif(self.TempBytes[1]==0x54):                      # 磁场包 Magnetic field package
                        self.get_mag(self.TempBytes, deviceModel)       # 结算磁场数据 Settlement of magnetic field data
                        deviceModel.dataProcessor.onUpdate(deviceModel) # 触发数据更新事件 Trigger data update event
                    elif(self.TempBytes[1]==0x57):                      # 经纬度包 Latitude and longitude package
                        self.get_lonlat(self.TempBytes, deviceModel)    # 结算经纬度数据 Settlement longitude and latitude data
                        deviceModel.dataProcessor.onUpdate(deviceModel) # 触发数据更新事件 Trigger data update event
                    elif(self.TempBytes[1]==0x58):                      # gps包 GPS package
                        self.get_gps(self.TempBytes, deviceModel)       # 结算gps数据 Settlement of GPS data
                        deviceModel.dataProcessor.onUpdate(deviceModel) # 触发数据更新事件 Trigger data update event
                    elif(self.TempBytes[1]==0x59):                      # 四元素包 Four Element Package
                        self.get_four_elements(self.TempBytes, deviceModel)    # 结算四元素数据 Settlement Four Element Data
                        deviceModel.dataProcessor.onUpdate(deviceModel) # 触发数据更新事件 Trigger data update event
                    elif(self.TempBytes[1]==0x5f):           # 返回读取指定的寄存器 Returns reading the specified register
                        self.get_find(self.TempBytes,deviceModel)
                    self.TempBytes=[]                        # 清除数据 Clear data
                else:                                        # 校验和未通过 Checksum failed
                    del self.TempBytes[0]                    # 去除第一个字节 Remove the first byte

    def get_readbytes(self,regAddr):
        """
        获取读取的指令
        :param regAddr: 寄存器地址
        :return:
        """
        return [0xff, 0xaa,0x27, regAddr & 0xff, regAddr >> 8]

    def get_writebytes(self,regAddr,sValue):
        """
        获取写入的指令
        :param regAddr: 寄存器地址
        :param sValue: 写入的值
        :return:
        """
        return [0xff, 0xaa, regAddr, sValue & 0xff, sValue >> 8]

    def get_acc(self,datahex, deviceModel):
        """
        加速度、温度结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        axl = datahex[2]
        axh = datahex[3]
        ayl = datahex[4]
        ayh = datahex[5]
        azl = datahex[6]
        azh = datahex[7]

        tempVal = (datahex[9] << 8 | datahex[8])
        acc_x = (axh << 8 | axl) / 32768.0 * self.accRange
        acc_y = (ayh << 8 | ayl) / 32768.0 * self.accRange
        acc_z = (azh << 8 | azl) / 32768.0 * self.accRange
        if acc_x >= self.accRange:
            acc_x -= 2 * self.accRange
        if acc_y >= self.accRange:
            acc_y -= 2 * self.accRange
        if acc_z >= self.accRange:
            acc_z -= 2 * self.accRange

        deviceModel.setDeviceData("accX", round(acc_x, 4))     # 设备模型加速度X赋值 Equipment model acceleration X assignment
        deviceModel.setDeviceData("accY", round(acc_y, 4))     # 设备模型加速度Y赋值 Equipment model acceleration Y assignment
        deviceModel.setDeviceData("accZ", round(acc_z, 4))     # 设备模型加速度Z赋值 Equipment model acceleration Z assignment
        temperature = round(tempVal / 100.0, 2)                     # 温度结算,并保留两位小数 Temperature settlement with two decimal places retained
        deviceModel.setDeviceData("temperature", temperature)       # 设备模型温度赋值 Equipment model temperature assignment

    def get_gyro(self,datahex, deviceModel):
        """
        角速度结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        wxl = datahex[2]
        wxh = datahex[3]
        wyl = datahex[4]
        wyh = datahex[5]
        wzl = datahex[6]
        wzh = datahex[7]

        gyro_x = (wxh << 8 | wxl) / 32768.0 * self.gyroRange
        gyro_y = (wyh << 8 | wyl) / 32768.0 * self.gyroRange
        gyro_z = (wzh << 8 | wzl) / 32768.0 * self.gyroRange
        if gyro_x >= self.gyroRange:
            gyro_x -= 2 * self.gyroRange
        if gyro_y >= self.gyroRange:
            gyro_y -= 2 * self.gyroRange
        if gyro_z >= self.gyroRange:
            gyro_z -= 2 * self.gyroRange

        deviceModel.setDeviceData("gyroX", round(gyro_x, 4))  # 设备模型角速度X赋值 Equipment model angular velocity X assignment
        deviceModel.setDeviceData("gyroY", round(gyro_y, 4))  # 设备模型角速度Y赋值 Equipment model angular velocity Y assignment
        deviceModel.setDeviceData("gyroZ", round(gyro_z, 4))  # 设备模型角速度Z赋值 Equipment model angular velocity Z assignment

    def get_angle(self,datahex, deviceModel):
        """
        角度结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        rxl = datahex[2]
        rxh = datahex[3]
        ryl = datahex[4]
        ryh = datahex[5]
        rzl = datahex[6]
        rzh = datahex[7]

        angle_x = (rxh << 8 | rxl) / 32768.0 * self.angleRange
        angle_y = (ryh << 8 | ryl) / 32768.0 * self.angleRange
        angle_z = (rzh << 8 | rzl) / 32768.0 * self.angleRange
        if angle_x >= self.angleRange:
            angle_x -= 2 * self.angleRange
        if angle_y >= self.angleRange:
            angle_y -= 2 * self.angleRange
        if angle_z >= self.angleRange:
            angle_z -= 2 * self.angleRange

        deviceModel.setDeviceData("angleX", round(angle_x, 3))  # 设备模型角度X赋值 Equipment model angle X assignment
        deviceModel.setDeviceData("angleY", round(angle_y, 3))  # 设备模型角度Y赋值 Equipment model angle Y assignment
        deviceModel.setDeviceData("angleZ", round(angle_z, 3))  # 设备模型角度Z赋值 Equipment model angle Z assignment

    def get_mag(self,datahex, deviceModel):
        """
        磁场结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        _x = deviceModel.get_int(bytes([datahex[2],datahex[3]]))
        _y = deviceModel.get_int(bytes([datahex[4],datahex[5]]))
        _z = deviceModel.get_int(bytes([datahex[6],datahex[7]]))

        deviceModel.setDeviceData("magX", round(_x, 0))   # 设备模型磁场X赋值 Equipment model magnetic field X assignment
        deviceModel.setDeviceData("magY", round(_y, 0))   # 设备模型磁场Y赋值 Equipment model magnetic field Y assignment
        deviceModel.setDeviceData("magZ", round(_z, 0))   # 设备模型磁场Z赋值 Equipment model magnetic field Z assignment

    def get_lonlat(self,datahex, deviceModel):
        """
        经纬度结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """

        lon = deviceModel.get_unint(bytes([datahex[2],datahex[3],datahex[4],datahex[5]]))
        lat = deviceModel.get_unint(bytes([datahex[6],datahex[7],datahex[8],datahex[9]]))
        #(lon / 10000000 + ((double)(lon % 10000000) / 1e5 / 60.0)).ToString("f8")
        tlon = lon / 10000000.0
        tlat = lat / 10000000.0
        deviceModel.setDeviceData("lon", round(tlon, 8))   # 设备模型经度赋值 Equipment model longitude assignment
        deviceModel.setDeviceData("lat", round(tlat, 8))   # 设备模型纬度赋值 Equipment model latitude assignment

    def get_gps(self,datahex, deviceModel):
        """
        GPS结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        Height = deviceModel.get_int(bytes([datahex[2],datahex[3]])) / 10.0   # 高度 Height
        Yaw = deviceModel.get_int(bytes([datahex[4],datahex[5]])) / 100.0     # 航向角 Heading angle
        Speed = deviceModel.get_unint(bytes([datahex[6],datahex[7],datahex[8],datahex[9]])) / 1e3   # 海里 Nautical mile

        deviceModel.setDeviceData("Height", round(Height, 3))   # 设备模型高度赋值 Equipment model height assignment
        deviceModel.setDeviceData("Yaw", round(Yaw, 2))         # 设备模型航向角赋值 Equipment model heading angle assignment
        deviceModel.setDeviceData("Speed", round(Speed, 3))     # 设备模型速度赋值 Device model speed assignment

    def get_four_elements(self,datahex, deviceModel):
        """
        四元素结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        q1 = deviceModel.get_int(bytes([datahex[2],datahex[3]])) / 32768.0
        q2 = deviceModel.get_int(bytes([datahex[4],datahex[5]])) / 32768.0
        q3 = deviceModel.get_int(bytes([datahex[6],datahex[7]])) / 32768.0
        q4 = deviceModel.get_int(bytes([datahex[8],datahex[9]])) / 32768.0

        deviceModel.setDeviceData("q1", round(q1, 5))   # 设备模型元素1赋值 Device Model Element 1 Assignment
        deviceModel.setDeviceData("q2", round(q2, 5))   # 设备模型元素2赋值 Device Model Element 2 Assignment
        deviceModel.setDeviceData("q3", round(q3, 5))   # 设备模型元素3赋值 Device Model Element 3 Assignment
        deviceModel.setDeviceData("q4", round(q4, 5))   # 设备模型元素4赋值 Device Model Element 4 Assignment

    def get_chiptime(self,datahex, deviceModel):
        """
        芯片时间结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        tempVals = []      #临时结算数据
        for i in range(0,4):
            tIndex = 2 + i * 2
            tempVals.append(datahex[tIndex+1] << 8 | datahex[tIndex])

        _year = 2000 + (tempVals[0] & 0xff)      # 年 Year
        _moth = ((tempVals[0] >> 8) & 0xff)      # 月 Month
        _day = (tempVals[1] & 0xff)              # 日 Day
        _hour = ((tempVals[1] >> 8) & 0xff)      # 时 Hour
        _minute = (tempVals[2] & 0xff)           # 分 Minute
        _second = ((tempVals[2] >> 8) & 0xff)    # 秒 Second
        _millisecond = tempVals[3]               # 毫秒 Millisecond
        deviceModel.setDeviceData("Chiptime",
                                  str(_year) + "-" + str(_moth) + "-" + str(_day) + " " + str(_hour) + ":" + str(
                                      _minute) + ":" + str(_second) + "." + str(_millisecond))  # 设备模型芯片时间赋值 Device model chip time assignment

    def readReg(self, regAddr,regCount, deviceModel):
        """
        读取寄存器
        :param regAddr: 寄存器地址
        :param regCount: 寄存器个数
        :param deviceModel: 设备模型
        :return:
        """
        tempResults = []                      # 返回数据 Return data
        readCount = int(regCount/4)           # 根据寄存器个数获取读取次数 Obtain the number of reads based on the number of registers
        if (regCount % 4>0):
            readCount+=1
        for n in range(0,readCount):
            self.TempFindValues = []  # 清除数据 Clear data
            tempBytes = self.get_readbytes(regAddr + n * 4)             # 获取读取的指令 Get read instructions
            success_bytes = deviceModel.serialPort.write(tempBytes)     # 写入数据 Write data
            for i in range(0,20):   # 设置超时1秒 Set timeout of 1 second
                time.sleep(0.05)    # 休眠50毫秒 Sleep for 50 milliseconds
                if (len(self.TempFindValues)>0):    # 已返回所找查的寄存器的值 The value of the searched register has been returned
                    for j in range(0,len(self.TempFindValues)):
                        if (len(tempResults) < regCount):
                            tempResults.append(self.TempFindValues[j])
                        else:
                            break
                    break
        return tempResults

    def writeReg(self, regAddr,sValue, deviceModel):
        """
        写入寄存器
        :param regAddr: 寄存器地址
        :param sValue: 写入值
        :param deviceModel: 设备模型
        :return:
        """
        tempBytes = self.get_writebytes(regAddr,sValue)                  # 获取写入指令 Get Write Instructions
        success_bytes = deviceModel.serialPort.write(tempBytes)          # 写入寄存器 Write Register
    def unlock(self, deviceModel):
        """
        解锁
        :return:
        """
        tempBytes = self.get_writebytes(0x69, 0xb588)                    # 获取写入指令 Get Write Instructions
        success_bytes = deviceModel.serialPort.write(tempBytes)          # 写入寄存器 Write Register

    def save(self, deviceModel):
        """
        保存
        :param deviceModel: 设备模型
        :return:
        """
        tempBytes = self.get_writebytes(0x00, 0x00)                      # 获取写入指令 Get Write Instructions
        success_bytes = deviceModel.serialPort.write(tempBytes)          # 写入寄存器 Write Register

    def AccelerationCalibration(self,deviceModel):
        """
        加计校准
        :param deviceModel: 设备模型
        :return:
        """
        self.unlock(deviceModel)                                         # 解锁 Unlock
        time.sleep(0.1)                                                  # 休眠100毫秒 Sleep for 100 milliseconds
        tempBytes = self.get_writebytes(0x01, 0x01)                      # 获取写入指令 Get Write Instructions
        success_bytes = deviceModel.serialPort.write(tempBytes)          # 写入寄存器 Write Register
        time.sleep(5.5)                                                  # 休眠5500毫秒 Sleep for 5500 milliseconds

    def BeginFiledCalibration(self,deviceModel):
        """
        开始磁场校准
        :param deviceModel: 设备模型
        :return:
        """
        self.unlock(deviceModel)                                         # 解锁 Unlock
        time.sleep(0.1)                                                  # 休眠100毫秒 Sleep for 100 milliseconds
        tempBytes = self.get_writebytes(0x01, 0x07)                      # 获取写入指令 磁场校准 Obtain write command magnetic field calibration
        success_bytes = deviceModel.serialPort.write(tempBytes)          # 写入寄存器 Write Register


    def EndFiledCalibration(self,deviceModel):
        """
        结束磁场校准
        :param deviceModel: 设备模型
        :return:
        """
        self.unlock(deviceModel)                                         # 解锁 Unlock
        time.sleep(0.1)                                                  # 休眠100毫秒  Sleep for 100 milliseconds
        self.save(deviceModel)                                           # 保存 Save

    def get_find(self,datahex, deviceModel):
        """
        读取指定寄存器结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        t0l = datahex[2]
        t0h = datahex[3]
        t1l = datahex[4]
        t1h = datahex[5]
        t2l = datahex[6]
        t2h = datahex[7]
        t3l = datahex[8]
        t3h = datahex[9]

        val0 = (t0h << 8 | t0l)
        val1 = (t1h << 8 | t1l)
        val2 = (t2h << 8 | t2l)
        val3 = (t3h << 8 | t3l)
        self.TempFindValues.extend([val0,val1,val2,val3])