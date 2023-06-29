# coding:UTF-8
"""
    测试文件
    Test file
"""
import time
import datetime
import platform
import threading
import lib.device_model as deviceModel
from lib.data_processor.roles.wt53r485_dataProcessor import WT53R485DataProcessor
from lib.protocol_resolver.roles.wt53r485_protocol_resolver import WT53RProtocol485Resolver

welcome = """
欢迎使用维特智能示例程序    Welcome to the Wit-Motoin sample program
"""
_writeF = None      # 写文件  Write file
_IsWriteF = False   # 写文件标识    Write file identification


def readConfig(device):
    """
    读取配置信息示例    Example of reading configuration information
    :param device: 设备模型  Device model
    :return:
    """
    print("***** 正在读取配置 Read configuration *****")

    tVals = device.readReg(0x02, 1)     # 报警阈值 Alarm threshold
    if len(tVals) > 0:
        print("报警阈值：" + str(tVals[0]) + "mm")
    else:
        print("无返回")

    tVals = device.readReg(0x36, 1)     # 测量模式 Measurement mode
    if len(tVals) > 0:
        if tVals[0] == 1:
            print("测量模式：{0}".format("短距离"))
        elif tVals[0] == 2:
            print("测量模式：{0}".format("中距离"))
        elif tVals[0] == 3:
            print("测量模式：{0}".format("长距离"))
    else:
        print("无返回")

    print("***** 读取配置完成 End of reading *****")


def setConfig(device):
    """
    设置配置信息示例    Example setting configuration information
    :param device: 设备模型 Device model
    :return:
    """
    device.unlock()                 # 解锁 unlock
    time.sleep(0.1)                 # 休眠100毫秒    Sleep 100ms
    device.writeReg(0x02, 400)      # 设置报警阈值400mm Set alarm threshold 400mm
    time.sleep(0.1)                 # 休眠100毫秒    Sleep 100ms
    device.writeReg(0x36, 3)        # 设置长距离模式 Set Long Distance Mode
    time.sleep(0.1)                 # 休眠100毫秒    Sleep 100ms
    device.save()                   # 保存 Save


def startRecord():
    """
    开始记录数据  Start recording data
    :return:
    """
    global _writeF
    global _IsWriteF
    _writeF = open(str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + ".txt", "w")     # 新建一个文件 Create a new file
    _IsWriteF = True    # 标记写入标识 Mark Write Identification
    Tempstr = "\distance(mm)\tstatus"
    Tempstr += "\r\n"
    _writeF.write(Tempstr)
    print("开始记录数据")


def endRecord():
    """
    结束记录数据  End record data
    :return:
    """
    global _writeF
    global _IsWriteF
    _IsWriteF = False   # 标记不可写入标识    Tag cannot write the identity
    _writeF.close()     # 关闭文件     Close file
    print("结束记录数据")


def onUpdate(deviceModel):
    """
    数据更新事件  Data update event
    :param deviceModel: 设备模型    Device model
    :return:
    """
    print("距离:" + "  " + deviceModel.getDeviceData("distance") + "mm" + "    " +
          "输出状态：" + "  " + deviceModel.getDeviceData("status"))
    if _IsWriteF:   # 记录数据 Record data
        Tempstr = " " + deviceModel.deviceName
        Tempstr += "\t" + deviceModel.getDeviceData("distance") + "\t" + deviceModel.getDeviceData("status") + "\t"
        Tempstr += "\r\n"
        _writeF.write(Tempstr)


def LoopReadThead(device):
    """
    循环读取数据  Cyclic read data
    :param device:
    :return:
    """
    while True:     # 循环读取数据 Cyclic read data
        device.readReg(0x34, 2)   # 读取距离、状态数据  Reading distance and status data
        time.sleep(0.2)


if __name__ == '__main__':

    print(welcome)
    device = deviceModel.DeviceModel(
        "我的WT53R",
        WT53RProtocol485Resolver(),
        WT53R485DataProcessor(),
        ""
    )
    device.ADDR = 0x50                                  # 设置传感器ID   Setting the Sensor ID
    if platform.system().lower() == 'linux':
        device.serialConfig.portName = "/dev/ttyUSB0"   # 设置串口  Set serial port
    else:
        device.serialConfig.portName = "COM23"          # 设置串口  Set serial port
    device.serialConfig.baud = 115200                   # 设置波特率 Set baud rate
    device.openDevice()                                 # 打开串口  Open serial port
    readConfig(device)                                  # 读取配置信息    Read configuration information
    device.dataProcessor.onVarChanged.append(onUpdate)  # 数据更新事件    Data update event

    startRecord()                                       # 开始记录数据   Start recording data
    t = threading.Thread(target=LoopReadThead, args=(device,))  # 开启一个线程读取数据 Start a thread to read data
    t.start()

    input()
    device.closeDevice()
    endRecord()                                         # 结束记录数据    End record data
