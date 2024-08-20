# coding:UTF-8
import threading
import time
import serial
from serial import SerialException


# 串口配置 Serial Port Configuration
class SerialConfig:
    # 串口号
    portName = ''

    # 波特率
    baud = 9600


# 设备实例 Device instance
class DeviceModel:
    # region 属性 attribute

    # 设备名称 deviceName
    deviceName = "我的设备"

    # 设备modbus ID列表
    addrLis = []

    # 设备数据字典 Device Data Dictionary
    deviceData = {}

    # 设备是否开启
    isOpen = False

    # 是否循环读取 Whether to loop read
    loop = False

    # 串口 Serial port
    serialPort = None

    # 串口配置 Serial Port Configuration
    serialConfig = SerialConfig()

    # 临时数组 Temporary array
    TempBytes = []

    # 起始寄存器 Start register
    statReg = None

    # endregion

    # region   计算CRC Calculate CRC
    auchCRCHi = [
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
        0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
        0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81,
        0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
        0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
        0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
        0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
        0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
        0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
        0x40]

    auchCRCLo = [
        0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7, 0x05, 0xC5, 0xC4,
        0x04, 0xCC, 0x0C, 0x0D, 0xCD, 0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
        0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A, 0x1E, 0xDE, 0xDF, 0x1F, 0xDD,
        0x1D, 0x1C, 0xDC, 0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
        0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32, 0x36, 0xF6, 0xF7,
        0x37, 0xF5, 0x35, 0x34, 0xF4, 0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
        0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29, 0xEB, 0x2B, 0x2A, 0xEA, 0xEE,
        0x2E, 0x2F, 0xEF, 0x2D, 0xED, 0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
        0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61, 0xA1, 0x63, 0xA3, 0xA2,
        0x62, 0x66, 0xA6, 0xA7, 0x67, 0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
        0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68, 0x78, 0xB8, 0xB9, 0x79, 0xBB,
        0x7B, 0x7A, 0xBA, 0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
        0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0, 0x50, 0x90, 0x91,
        0x51, 0x93, 0x53, 0x52, 0x92, 0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
        0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B, 0x99, 0x59, 0x58, 0x98, 0x88,
        0x48, 0x49, 0x89, 0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
        0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83, 0x41, 0x81, 0x80,
        0x40]

    # endregion  计算CRC

    def __init__(self, deviceName, portName, baud, addrLis, callback_method):
        print("初始化设备模型")
        # 设备名称（自定义） Device Name
        self.deviceName = deviceName
        # 串口号 Serial port number
        self.serialConfig.portName = portName
        # 串口波特率 baud
        self.serialConfig.baud = baud
        # modbus ID 设备地址
        self.addrLis = addrLis
        self.deviceData = {}
        # 数据回调方法 Data callback method
        self.callback_method = callback_method
        # 初始化设备数据字典 Initialize device data dictionary
        for addr in addrLis:
            self.deviceData[addr] = {}

    # 获得CRC校验 Obtain CRC verification
    def get_crc(self, datas, dlen):
        tempH = 0xff  # 高 CRC 字节初始化 High CRC byte initialization
        tempL = 0xff  # 低 CRC 字节初始化 Low CRC byte initialization
        for i in range(0, dlen):
            tempIndex = (tempH ^ datas[i]) & 0xff
            tempH = (tempL ^ self.auchCRCHi[tempIndex]) & 0xff
            tempL = self.auchCRCLo[tempIndex]
        return (tempH << 8) | tempL
        pass

    # region 获取设备数据 Obtain device data

    # 设置设备数据 Set device data
    def set(self, ADDR, key, value):
        # 将设备数据存到键值 Saving device data to key values
        self.deviceData[ADDR][key] = value

    # 获得设备数据 Obtain device data
    def get(self, ADDR, key):
        # 从键值中获取数据，没有则返回None Obtaining data from key values
        if ADDR in self.deviceData:
            if key in self.deviceData[ADDR]:
                return self.deviceData[ADDR][key]
            else:
                return None
        else:
            return None

    # 删除设备数据 Delete device data
    def remove(self, ADDR, key):
        # 删除设备键值
        if ADDR in self.deviceData:
            if key in self.deviceData[ADDR]:
                del self.deviceData[ADDR][key]

    # endregion

    # 打开设备 open Device
    def openDevice(self):
        # 先关闭端口 Turn off the device first
        self.closeDevice()
        try:
            self.serialPort = serial.Serial(self.serialConfig.portName, self.serialConfig.baud, timeout=0.5)
            self.isOpen = True
            print("{}已打开".format(self.serialConfig.portName))
            # 开启一个线程持续监听串口数据 Start a thread to continuously listen to serial port data
            t = threading.Thread(target=self.readDataTh, args=("Data-Received-Thread", 10,))
            t.start()
            print("设备打开成功")
        except SerialException:
            print("打开" + self.serialConfig.portName + "失败")

    # 监听串口数据线程 Listening to serial data threads
    def readDataTh(self, threadName, delay):
        print("启动" + threadName)
        while True:
            # 如果串口打开了
            if self.isOpen:
                try:
                    tLen = self.serialPort.inWaiting()
                    if tLen > 0:
                        data = self.serialPort.read(tLen)
                        self.onDataReceived(data)
                except Exception as ex:
                    print(ex)
            else:
                time.sleep(0.1)
                print("串口未打开")
                break

    # 关闭设备  close Device
    def closeDevice(self):
        if self.serialPort is not None:
            self.serialPort.close()
            print("端口关闭了")
        self.isOpen = False
        print("设备关闭了")
    
    # region 数据解析 data analysis

    # 串口数据处理  Serial port data processing
    def onDataReceived(self, data):
        tempdata = bytes.fromhex(data.hex())
        for val in tempdata:
            self.TempBytes.append(val)
            # 判断ID是否正确 Determine if the ID is correct
            if self.TempBytes[0] not in self.addrLis:
                del self.TempBytes[0]
                continue
            # 判断是否是03读取功能码 Determine whether it is 03 to read the function code
            if len(self.TempBytes) > 2:
                if not (self.TempBytes[1] == 0x03):
                    del self.TempBytes[0]
                    continue
                tLen = len(self.TempBytes)
                # 拿到一包完整协议数据 Get a complete package of protocol data
                if tLen == self.TempBytes[2] + 5:
                    # CRC校验
                    tempCrc = self.get_crc(self.TempBytes, tLen - 2)
                    if (tempCrc >> 8) == self.TempBytes[tLen - 2] and (tempCrc & 0xff) == self.TempBytes[tLen - 1]:
                        self.processData(self.TempBytes[2])
                    else:
                        del self.TempBytes[0]

    # 数据解析 data analysis
    def processData(self, length):
        # 　数据解析
        ADDR = self.TempBytes[0]
        if length == 24:
            AccX = self.getSignInt16(self.TempBytes[3] << 8 | self.TempBytes[4]) / 32768 * 16
            AccY = self.getSignInt16(self.TempBytes[5] << 8 | self.TempBytes[6]) / 32768 * 16
            AccZ = self.getSignInt16(self.TempBytes[7] << 8 | self.TempBytes[8]) / 32768 * 16
            self.set(ADDR, "AccX", round(AccX, 3))
            self.set(ADDR, "AccY", round(AccY, 3))
            self.set(ADDR, "AccZ", round(AccZ, 3))

            AsX = self.getSignInt16(self.TempBytes[9] << 8 | self.TempBytes[10]) / 32768 * 2000
            AsY = self.getSignInt16(self.TempBytes[11] << 8 | self.TempBytes[12]) / 32768 * 2000
            AsZ = self.getSignInt16(self.TempBytes[13] << 8 | self.TempBytes[14]) / 32768 * 2000
            self.set(ADDR, "AsX", round(AsX, 3))
            self.set(ADDR, "AsY", round(AsY, 3))
            self.set(ADDR, "AsZ", round(AsZ, 3))

            HX = self.getSignInt16(self.TempBytes[15] << 8 | self.TempBytes[16]) * 13 / 1000
            HY = self.getSignInt16(self.TempBytes[17] << 8 | self.TempBytes[18]) * 13 / 1000
            HZ = self.getSignInt16(self.TempBytes[19] << 8 | self.TempBytes[20]) * 13 / 1000
            self.set(ADDR, "HX", round(HX, 3))
            self.set(ADDR, "HY", round(HY, 3))
            self.set(ADDR, "HZ", round(HZ, 3))

            AngX = self.getSignInt16(self.TempBytes[21] << 8 | self.TempBytes[22]) / 32768 * 180
            AngY = self.getSignInt16(self.TempBytes[23] << 8 | self.TempBytes[24]) / 32768 * 180
            AngZ = self.getSignInt16(self.TempBytes[25] << 8 | self.TempBytes[26]) / 32768 * 180
            self.set(ADDR, "AngX", round(AngX, 3))
            self.set(ADDR, "AngY", round(AngY, 3))
            self.set(ADDR, "AngZ", round(AngZ, 3))
            self.callback_method(self)
        else:
            if self.statReg is not None:
                for i in range(int(length / 2)):
                    value = self.getSignInt16(self.TempBytes[2 * i + 3] << 8 | self.TempBytes[2 * i + 4])
                    value = value / 32768
                    self.set(ADDR, str(self.statReg), round(value, 3))
                    self.statReg += 1
        self.TempBytes.clear()

    # endregion

    @staticmethod
    def getSignInt16(num):
        if num >= pow(2, 15):
            num -= pow(2, 16)
        return num

    @staticmethod
    def getSignInt32(num):
        if num >= pow(2, 31):
            num -= pow(2, 32)
        return num

    # 发送串口数据 Sending serial port data
    def sendData(self, data):
        try:
            self.serialPort.write(data)
        except Exception as ex:
            print(ex)

    # 读取寄存器 read register
    def readReg(self, ADDR, regAddr, regCount):
        # 从指令中获取起始寄存器 （处理回传数据需要用到） Get start register from instruction
        self.statReg = regAddr
        # 封装读取指令并向串口发送数据 Encapsulate read instructions and send data to the serial port
        self.sendData(self.get_readBytes(ADDR, regAddr, regCount))

    # 写入寄存器 Write Register
    def writeReg(self, ADDR, regAddr, sValue):
        # 解锁 unlock
        self.unlock(ADDR)
        # 延迟100ms Delay 100ms
        time.sleep(0.1)
        # 封装写入指令并向串口发送数据
        self.sendData(self.get_writeBytes(ADDR, regAddr, sValue))
        # 延迟100ms Delay 100ms
        time.sleep(0.1)
        # 保存 save
        self.save(ADDR)

    # 发送读取指令封装 Send read instruction encapsulation
    def get_readBytes(self, devid, regAddr, regCount):
        # 初始化
        tempBytes = [None] * 8
        # 设备modbus地址
        tempBytes[0] = devid
        # 读取功能码
        tempBytes[1] = 0x03
        # 寄存器高8位
        tempBytes[2] = regAddr >> 8
        # 寄存器低8位
        tempBytes[3] = regAddr & 0xff
        # 读取寄存器个数高8位
        tempBytes[4] = regCount >> 8
        # 读取寄存器个数低8位
        tempBytes[5] = regCount & 0xff
        # 获得CRC校验
        tempCrc = self.get_crc(tempBytes, len(tempBytes) - 2)
        # CRC校验高8位
        tempBytes[6] = tempCrc >> 8
        # CRC校验低8位
        tempBytes[7] = tempCrc & 0xff
        return tempBytes

    # 发送写入指令封装 Send write instruction encapsulation
    def get_writeBytes(self, devid, regAddr, sValue):
        # 初始化
        tempBytes = [None] * 8
        # 设备modbus地址
        tempBytes[0] = devid
        # 写入功能码
        tempBytes[1] = 0x06
        # 寄存器高8位
        tempBytes[2] = regAddr >> 8
        # 寄存器低8位
        tempBytes[3] = regAddr & 0xff
        # 寄存器值高8位
        tempBytes[4] = sValue >> 8
        # 寄存器值低8位
        tempBytes[5] = sValue & 0xff
        # 获得CRC校验
        tempCrc = self.get_crc(tempBytes, len(tempBytes) - 2)
        # CRC校验高8位
        tempBytes[6] = tempCrc >> 8
        # CRC校验低8位
        tempBytes[7] = tempCrc & 0xff
        return tempBytes

    # 开始循环读取 Start loop reading
    def startLoopRead(self):
        # 循环读取控制
        self.loop = True
        # 开启读取线程 Enable read thread
        t = threading.Thread(target=self.loopRead, args=())
        t.start()

    # 循环读取线程 Loop reading data
    def loopRead(self):
        print("循环读取开始")
        while self.loop:
            for addr in self.addrLis:
                self.readReg(addr, 0x34, 12)
                time.sleep(0.2)
        print("循环读取结束")

    # 关闭循环读取 Close loop reading
    def stopLoopRead(self):
        self.loop = False

    # 解锁
    def unlock(self, ADDR):
        cmd = self.get_writeBytes(ADDR, 0x69, 0xb588)
        self.sendData(cmd)

    # 保存
    def save(self, ADDR):
        cmd = self.get_writeBytes(ADDR, 0x00, 0x0000)
        self.sendData(cmd)
