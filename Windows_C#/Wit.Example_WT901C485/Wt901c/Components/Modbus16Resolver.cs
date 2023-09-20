using System;
using System.Diagnostics;
using System.Linq;
using Wit.SDK.Device.Device.Device.DKey;
using Wit.SDK.Modular.Sensor.Device;
using Wit.SDK.Modular.Sensor.Modular.ProtocolResolver.Interface;
using Wit.SDK.Modular.Sensor.Modular.Resolver.Utils;
using Wit.SDK.Modular.Sensor.Utils;
using Wit.SDK.Utils;

namespace Wit.SDK.Modular.Sensor.Modular.ProtocolResolver.Roles
{

    /// <summary>
    /// ModbusCRC16协议解析器
    /// </summary>
    public class Modbus16Resolver : IProtocolResolver
    {
        /// <summary>
        /// 解析主动回传的数据
        /// </summary>
        /// <param name="data"></param>
        /// <param name="baseDevice"></param>
        public override void OnReceiveData(DeviceModel baseDevice, byte[] data)
        {

        }

        /// <summary>
        /// 发送数据
        /// </summary>
        /// <param name="sendData"></param>
        /// <param name="deviceModel"></param>
        public override void OnReadData(DeviceModel deviceModel, byte[] sendData, int delay = -1)
        {
            try
            {
                delay = AutoDelayUtils.GetModbusAutoDelay(delay, deviceModel);

                byte[] returnData;
         
                // 发送数据
                deviceModel.SendData(sendData, out returnData, true, delay);

                // 如果返回了正确的数据
                byte[] modbusBytes;
                if (sendData != null && returnData != null && returnData.Length >= 7
                    && Modbus16Utils.FindModbus(sendData, returnData, out modbusBytes))
                {
                    int readReg = sendData[2] << 8 | sendData[3];
                    byte[] regData = modbusBytes.Skip(3).Take(modbusBytes.Length - 5).ToArray(); 

                    for (int j = 0; regData != null &&
                        j < regData.Length - 1; j += 2)
                    {
                        string key = string.Format("{0:X2}", readReg++);
                        short value = (short)(regData[j] << 8 | regData[j + 1]);
                        deviceModel.SetDeviceData(new ShortKey(key), value);
                    }
                }
                else {
                    if (returnData != null && returnData.Length > 0) {
                        Debug.WriteLine("数据校验错误");
                        Debug.WriteLine(ByteArrayConvert.ByteArrayToHexString(returnData));
                    }
                }
            }
            catch (Exception ex)
            {

                Console.WriteLine("error:" + ex.Message);
            }

        }
    }
}
