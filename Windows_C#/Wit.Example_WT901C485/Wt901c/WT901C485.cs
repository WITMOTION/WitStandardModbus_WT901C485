using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading;
using Wit.SDK.Device.Device.Device.DKey;
using Wit.SDK.Modular.Sensor.Device;
using Wit.SDK.Modular.Sensor.Device.Entity;
using Wit.SDK.Modular.Sensor.Modular.Connector.Entity;
using Wit.SDK.Modular.Sensor.Modular.Connector.Interface;
using Wit.SDK.Modular.Sensor.Modular.Connector.Role;
using Wit.SDK.Modular.Sensor.Modular.DataProcessor.Context;
using Wit.SDK.Modular.Sensor.Modular.DataProcessor.Role;
using Wit.SDK.Modular.Sensor.Modular.ProtocolResolver.Roles;
using Wit.SDK.Modular.Sensor.Utils;
using Wit.SDK.Modular.WitSensorApi.Interface;

namespace Wit.SDK.Modular.WitSensorApi.Modular.WT901C485
{
    /// <summary>
    /// WT901C485连接类
    /// </summary>
    public class WT901C485 : IAttitudeSensorApi
    {
        /// <summary>
        /// 设备模型
        /// </summary>
        private DeviceModel DeviceModel;

        /// <summary>
        /// 连接器
        /// </summary>
        private SPConnector connector = new SPConnector(new SerialPortConfig());

        /// <summary>
        /// 记录数据委托
        /// </summary>
        public delegate void OnRecordHandler(WT901C485 BWT901BLE);

        /// <summary>
        /// 记录数据事件
        /// </summary>
        public event OnRecordHandler OnRecord;

        /// <summary>
        /// 构造方法
        /// </summary>
        /// <param name="portName"></param>
        /// <param name="baudrate"></param>
        public WT901C485()
        {
            // 创建一个连接WT901C485的设备模型
            DeviceModel deviceModel = new DeviceModel($"", $"",
                    new Modbus16Resolver(),
                    new WT901C485Processor(),
                    "34");
            deviceModel.Connector = connector;
            DeviceModel = deviceModel;

            // 自动读取命令
            DataProcessorContext.ReadCmdList = new List<CmdBean>()
            {
                new CmdBean(){
                    sendData = "${ADDR} 03 00 30 00 30 ${CRC16}",
                    sendHex = true
                }
            };
        }

        /// <summary>
        /// 指定串口号
        /// </summary>
        /// <param name="portName"></param>
        public void SetPortName(string portName)
        {
            connector.SerialPortConfig.PortName = portName;
            DeviceModel.DeviceName = $"{portName}";
        }

        /// <summary>
        /// 指定波特率
        /// </summary>
        /// <param name="baudrate"></param>
        public void SetBaudrate(int baudRate)
        {
            connector.SerialPortConfig.BaudRate = baudRate;
        }

        /// <summary>
        /// 打开设备
        /// </summary>
        public void Open()
        {
            DeviceModel.OpenDevice();
            DeviceModel.OnListenKeyUpdate += DeviceModel_OnListenKeyUpdate;
        }

        /// <summary>
        /// 是否打开的
        /// </summary>
        public bool IsOpen()
        {
            return DeviceModel.IsOpen;
        }

        /**
         * 关闭连接
         *
         * @author huangyajun
         * @date 2022/6/28 20:51
         */
        public void Close()
        {
            DeviceModel.CloseDevice();
        }

        /// <summary>
        /// 发送数据
        /// </summary>
        /// <param name="data">需要发送出去的数据</param>
        /// <param name="returnData">传感器返回的数据</param>
        /// <param name="isWaitReturn">是否需要传感器返回数据</param>
        /// <param name="waitTime">等待传感器返回数据时间，单位ms，默认100ms</param>
        /// <param name="repetition">重复发送次数</param>
        public void SendData(byte[] data, out byte[] returnData, bool isWaitReturn = false, int waitTime = 100, int repetition = 1)
        {
            DeviceModel.SendData(data, out returnData, isWaitReturn, waitTime, repetition);
        }

        /// <summary>
        /// 发送带协议的数据，使用默认等待时长
        /// </summary>
        /// <param name="data">数据</param>
        public void SendProtocolData(byte[] data)
        {
            DeviceModel.ReadData(data);
        }

        /// <summary>
        /// 发送带协议的数据,并且指定等待时长
        /// </summary>
        /// <param name="data">数据</param>
        /// <param name="waitTime">等待时间</param>
        public void SendProtocolData(byte[] data, int waitTime)
        {
            DeviceModel.ReadData(data, waitTime);
        }

        /// <summary>
        /// 发送读取寄存器的命令
        /// </summary>
        /// <param name="reg"></param>
        /// <param name="waitTime"></param>
        public void SendReadReg(byte reg, int waitTime)
        {
            var read03Bytes = Modbus16Utils.GetRead(byte.Parse(DeviceModel.GetDeviceData("ADDR")), reg, 0x1);
            DeviceModel.ReadData(read03Bytes);
        }

        /// <summary>
        ///  解锁寄存器
        /// </summary>
        public void UnlockReg()
        {
            byte addr = GetModbusId();
            byte[] setting = Modbus16Utils.GetWrite(addr, 0x69, 0xB588);
            SendProtocolData(setting);
        }

        /// <summary>
        /// 保存寄存器
        /// </summary>
        public void SaveReg()
        {
            byte addr = GetModbusId();
            byte[] setting = Modbus16Utils.GetWrite(addr, 0x00, 0x0000);
            SendProtocolData(setting);
        }

        /// <summary>
        /// 加计校准
        /// </summary>
        public void AppliedCalibration()
        {
            byte addr = GetModbusId();
            byte[] setting = Modbus16Utils.GetWrite(addr, 0x01, 0x01);
            SendProtocolData(setting);
        }

        /// <summary>
        /// 开始磁场校准
        /// </summary>
        public void StartFieldCalibration()
        {
            byte addr = GetModbusId();
            byte[] setting = Modbus16Utils.GetWrite(addr, 0x01, 0x07);
            SendProtocolData(setting);
        }

        /// <summary>
        /// 结束磁场校准
        /// </summary>
        public void EndFieldCalibration()
        {
            byte addr = GetModbusId();
            byte[] setting = Modbus16Utils.GetWrite(addr, 0x01, 0x00);
            SendProtocolData(setting);
        }

        /// <summary>
        /// 设置带宽
        /// </summary>
        /// <param name="rate"></param>
        public void SetBandWidth(byte band)
        {
            byte addr = GetModbusId();
            byte[] setting = Modbus16Utils.GetWrite(addr, 0x1F, band);
            SendProtocolData(setting);
        }

        /// <summary>
        /// 指定ModbusId
        /// </summary>
        /// <param name="modbusId"></param>
        public void SetModbusId(byte modbusId)
        {
            if (DeviceModel.IsOpen)
            {
                try
                {
                    byte addr = GetModbusId();
                    byte[] setting = Modbus16Utils.GetWrite(addr, 0x1A, modbusId);
                    SendProtocolData(setting);
                }
                catch (Exception)
                {
                    //Debug.WriteLine(e.Message);
                    //Debug.WriteLine(e.StackTrace);
                }
            }

            // 更改上位机地址
            DeviceModel.SetAddr(modbusId.ToString());
        }

        /// <summary>
        /// 获得设备地址
        /// </summary>
        /// <returns></returns>
        public byte GetModbusId()
        {

            byte addr = 0;

            try
            {
                addr = byte.Parse(DeviceModel.GetAddr());
            }
            catch (Exception e)
            {
                Debug.WriteLine(e.Message);
                Debug.WriteLine(e.StackTrace);
            }

            return addr;
        }

        /// <summary>
        /// 获得设备名称
        /// </summary>
        /// <returns></returns>
        public string GetDeviceName()
        {
            return DeviceModel.DeviceName;
        }


        /// <summary>
        /// 获得数据
        /// </summary>
        /// <param name="key">数据键值</param>
        /// <returns></returns>
        public string GetDeviceData(string key)
        {
            return DeviceModel.GetDeviceData(key);
        }

        /// <summary>
        /// 获得数据
        /// </summary>
        /// <param name="key">数据键值</param>
        /// <returns></returns>
        public short? GetDeviceData(ShortKey key)
        {
            return DeviceModel.GetDeviceData(key);
        }

        /// <summary>
        /// 获得数据
        /// </summary>
        /// <param name="key">数据键值</param>
        /// <returns></returns>
        public string GetDeviceData(StringKey key)
        {
            return DeviceModel.GetDeviceData(key);
        }

        /// <summary>
        /// 获得数据
        /// </summary>
        /// <param name="key">数据键值</param>
        /// <returns></returns>
        public double? GetDeviceData(DoubleKey key)
        {
            return DeviceModel.GetDeviceData(key);
        }

        /// <summary>
        /// 传感器数据更新时
        /// </summary>
        /// <param name="deviceModel"></param>
        public void DeviceModel_OnListenKeyUpdate(DeviceModel deviceModel)
        {
            OnRecord?.Invoke(this);
        }

        /// <summary>
        /// 无设置回传速率
        /// </summary>
        /// <param name="rate"></param>
        public void SetReturnRate(byte rate)
        {
            // 无设置回传速率
        }
    }
}
