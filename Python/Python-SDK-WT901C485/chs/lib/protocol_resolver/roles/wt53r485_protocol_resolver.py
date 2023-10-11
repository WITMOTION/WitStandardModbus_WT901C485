# coding:UTF-8
import time
import datetime
from lib.protocol_resolver.interface.i_protocol_resolver import IProtocolResolver

"""
    WT53R485协议解析器 WT53R485 protocol resolver
"""


class WT53RProtocol485Resolver(IProtocolResolver):
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
    TempBytes = []          # 临时数据列表 Temporary Data List
    PackSize = 9            # 一包数据大小 Size of a packet of data

    TempFindValues = []     # 读取指定寄存器返回的数据 Read the data returned by the specified register
    TempReadRegCount = 0    # 读取寄存器个数 Read the number of registers

    def get_crc(self, datas, dlen):
        """
        获取CRC校验  Obtain CRC verification
        :param datas:数据
        :param dlen:校验数据长度
        :return:
        """
        tempH = 0xff  # 高 CRC 字节初始化 High CRC byte initialization
        tempL = 0xff  # 低 CRC 字节初始化 Low CRC byte initialization
        for i in range(0, dlen):
            tempIndex = (tempH ^ datas[i]) & 0xff
            tempH = (tempL ^ self.auchCRCHi[tempIndex]) & 0xff
            tempL = self.auchCRCLo[tempIndex]
        return (tempH << 8) | tempL
        pass

    def setConfig(self, deviceModel):
        pass

    def sendData(self, sendData, deviceModel):
        success_bytes = deviceModel.serialPort.write(sendData)

    def passiveReceiveData(self, data, deviceModel):
        global TempBytes
        tempdata = bytes.fromhex(data.hex())            # 将收到的数据转为16进制数组 Convert the received data into a hexadecimal array
        for val in tempdata:
            self.TempBytes.append(val)
            if self.TempBytes[0] != deviceModel.ADDR:   # 如果第一个位不是设备ID（0x50）去除 If the first bit is not the device ID (0x50), remove it
                del self.TempBytes[0]
                continue
            if len(self.TempBytes) > 2:
                if not (self.TempBytes[1] == 0x03):     # 第三个字节数值不是读取标识 0x03 去除 The third byte value is not a read identifier 0x03 removed
                    del self.TempBytes[0]
                    continue
                tlen = len(self.TempBytes)              # 当前临时数组的长度 The length of the current temporary array
                if tlen == self.TempBytes[2] + 5:       # 比较当前临时数组是否是9个字节（根据发送指令可以得知接收完整是9字节） Compare whether the current temporary array is 9 bytes (according to the sending instruction, it can be determined that the received complete array is 9 bytes)
                    tempCrc = self.get_crc(self.TempBytes, tlen - 2)        # 拿到CRC校验 Obtain CRC verification
                    if (tempCrc >> 8) == self.TempBytes[tlen - 2] and (tempCrc & 0xff) == self.TempBytes[tlen - 1]:  # CRC校验通过 CRC verification passed
                        if self.PackSize == tlen:
                            self.get_data(self.TempBytes, deviceModel)       # 结算数据 Settlement data
                            deviceModel.dataProcessor.onUpdate(deviceModel)  # 触发数据更新事件 Trigger data update event
                        self.get_find(self.TempBytes, deviceModel)           # 如果字节数不是9，则到这个方法 If the number of bytes is not 9, then go to this method
                        self.TempBytes = []
                    else:
                        del self.TempBytes[0]

    def get_readbytes(self, devid, regAddr, regCount):
        """
        获取读取的指令
        :param devid: 设备ID
        :param regAddr: 寄存器地址
        :param regCount: 寄存器个数
        :return:
        """
        tempBytes = [None] * 8
        tempBytes[0] = devid  # 设备ID Device ID
        tempBytes[1] = 0x03   # 读取指令 Read command
        tempBytes[2] = regAddr >> 8     # 寄存器起始位——高位 Register start bit - high bit
        tempBytes[3] = regAddr & 0xff   # 寄存器起始位——低位 Register start bit - low bit
        tempBytes[4] = regCount >> 8    # 寄存器个数——高位 Number of registers - high bit
        tempBytes[5] = regCount & 0xff  # 寄存器个数——低位 Number of registers - low bit
        tempCrc = self.get_crc(tempBytes, len(tempBytes) - 2)  # 获取CRC校验 Obtain CRC verification
        tempBytes[6] = tempCrc >> 8    # CRC校验——高位 CRC verification - high bit
        tempBytes[7] = tempCrc & 0xff  # CRC校验——低位 CRC verification - low bit
        return tempBytes

    def get_writebytes(self, devid, regAddr, sValue):
        """
        获取写入的指令
        :param devid: 设备ID
        :param regAddr: 寄存器地址
        :param sValue: 写入的值
        :return:
        """
        tempBytes = [None] * 8
        tempBytes[0] = devid   # 设备ID Device ID
        tempBytes[1] = 0x06    # 写入指令 Read command
        tempBytes[2] = regAddr >> 8    # 寄存器起始位——高位 Register start bit - high bit
        tempBytes[3] = regAddr & 0xff  # 寄存器起始位——低位 Register start bit - low bit
        tempBytes[4] = sValue >> 8     # 寄存器数值——高位 Register Value - High Bit
        tempBytes[5] = sValue & 0xff   # 寄存器数值——低位 Register Value - low Bit
        tempCrc = self.get_crc(tempBytes, len(tempBytes) - 2)  # 获取CRC校验 Obtain CRC verification
        tempBytes[6] = tempCrc >> 8
        tempBytes[7] = tempCrc & 0xff
        return tempBytes

    def get_data(self, datahex, deviceModel):
        """
        结算数据
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        tempReg = 0x34              # 起始寄存器 Start register
        dlen = int(datahex[2] / 2)  # 寄存器个数 Number of registers
        tempVals = []               # 临时数组 Temp array
        for i in range(0, dlen):
            tempIndex = 3 + i * 2   # 获取当前数据索引 Get current data index
            tempVal = datahex[tempIndex] << 8 | datahex[tempIndex + 1]
            if tempReg == 0x34:     # 解算距离数据 Calculate distance data
                deviceModel.setDeviceData("distance", str(tempVal))
            elif tempReg == 0x35:
                if tempVal == 0:    # 解算状态数据 Solve state data
                    deviceModel.setDeviceData("status", "数据正常")
                else:
                    deviceModel.setDeviceData("status", "数据异常")
            tempReg += 1            # 下一个寄存器 Next reg

    def readReg(self, regAddr, regCount, deviceModel):
        """
        读取寄存器
        :param regAddr: 寄存器地址
        :param regCount: 寄存器个数
        :param deviceModel: 设备模型
        :return:
        """
        self.TempFindValues = []    # 清除数据 Clear data
        self.TempReadRegCount = regCount
        tempBytes = self.get_readbytes(deviceModel.ADDR, regAddr, regCount)   # 获取读取的指令 Get cmd
        success_bytes = deviceModel.serialPort.write(tempBytes)               # 写入数据 Write data
        for i in range(0, 15):      # 设置超时1秒 Set timeout of 1 second
            time.sleep(0.01)        # 休眠10毫秒  Sleep 10ms
            if len(self.TempFindValues) > 0:    # 已返回所找查的寄存器的值 The value of the searched register has been returned
                break
        return self.TempFindValues

    def writeReg(self, regAddr, sValue, deviceModel):
        """
        写入寄存器
        :param regAddr: 寄存器地址
        :param sValue: 写入值
        :param deviceModel: 设备模型
        :return:
        """
        tempBytes = self.get_writebytes(deviceModel.ADDR, regAddr, sValue)  # 获取写入指令 Get cmd
        success_bytes = deviceModel.serialPort.write(tempBytes)             # 写入寄存器 Write reg

    def get_find(self, datahex, deviceModel):
        """
        读取指定寄存器结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        tempArr = []                    # 临时存储 Temporary Storage
        dlen = int(datahex[2] / 2)      # 寄存器个数 Number of registers
        for i in range(0, dlen):
            tempIndex = 3 + i * 2       # 获取当前数据索引 Get current data index
            tempVal = datahex[tempIndex] << 8 | datahex[tempIndex + 1]  # 数据转换 data conversion
            tempArr.append(tempVal)     # 将数据添加到列表中 Add data to the list

        self.TempFindValues.extend(tempArr)

    def unlock(self, deviceModel):
        """
        解锁
        :return:
        """
        tempBytes = self.get_writebytes(deviceModel.ADDR, 0x69, 0xb588)  # 获取写入指令 Get cmd
        success_bytes = deviceModel.serialPort.write(tempBytes)          # 写入寄存器 Write reg

    def save(self, deviceModel):
        """
        保存
        :return:
        """
        tempBytes = self.get_writebytes(deviceModel.ADDR, 0x00, 0x00)  # 获取写入指令 Get cmd
        success_bytes = deviceModel.serialPort.write(tempBytes)        # 写入寄存器 Write reg
