import device_model
import time


# 数据更新事件  Data update event
def updateData(DeviceModel):
    print(DeviceModel.deviceData)
    # 获得加速度x的值
    # print(DeviceModel.get("AccX"))


if __name__ == "__main__":
    # 读取的modbus地址列表 List of Modbus addresses read
    addrLis = [0x50]
    # 拿到设备模型 Get the device model
    device = device_model.DeviceModel("测试设备1", "COM52", 115200, addrLis, updateData)
    # 开启设备 Turn on the device
    device.openDevice()
    # 开启轮询 Enable loop reading
    device.startLoopRead()
