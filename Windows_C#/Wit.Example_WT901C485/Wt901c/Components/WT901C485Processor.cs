using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading;
using Wit.SDK.Device.Device.Device.DKey;
using Wit.SDK.Modular.Sensor.Device;
using Wit.SDK.Modular.Sensor.Device.Entity;
using Wit.SDK.Modular.Sensor.Modular.DataProcessor.Constant;
using Wit.SDK.Modular.Sensor.Modular.DataProcessor.Context;
using Wit.SDK.Modular.Sensor.Modular.DataProcessor.Interface;
using Wit.SDK.Modular.Sensor.Modular.DataProcessor.Utils;
using Wit.SDK.Modular.Sensor.Utils;
using Wit.SDK.Utils;

namespace Wit.SDK.Modular.Sensor.Modular.DataProcessor.Role
{
    /// <summary>
    /// WT901C485数据处理器
    /// </summary>
    public class WT901C485Processor : IDataProcessor
    {
        /// <summary>
        /// 设备模型
        /// </summary>
        public DeviceModel DeviceModel { get; private set; }

        /// <summary>
        /// 控制读取数据线程是否运行
        /// </summary>
        bool ReadDataThreadRuning = false;

        /// <summary>
        /// 记录key值切换器
        /// </summary>
        private RecordKeySwitch RecordKeySwitch = new RecordKeySwitch();

        /// <summary>
        /// 数据刷新的key值
        /// </summary>
        List<string> UpdateKeys = new List<string>() {};

        /// <summary>
        /// 当传感器打开时
        /// </summary>
        /// <param name="deviceModel"></param>
        public override void OnOpen(DeviceModel deviceModel)
        {
            for (int i = 0x30; i < 0x30 + 0x30; i++)
            {
                UpdateKeys.Add(string.Format("{0:X2}", i));
            }
            // 传入刷新数据的key值
            RecordKeySwitch.Open(deviceModel, UpdateKeys);

            this.DeviceModel = deviceModel;
            Thread thread = new Thread(ReadDataThread) { IsBackground = true };
            ReadDataThreadRuning = true;
            thread.Start();
        }

        /// <summary>
        /// 自动读取线程
        /// </summary>
        private void ReadDataThread()
        {

            while (ReadDataThreadRuning) {

                try
                {
                    // 暂停读取
                    while (DataProcessorContext.AutoReadPause) { Thread.Sleep(1000);  }

                    //// 发送读取命令
                    //DeviceModel.SendProtocolData(
                    //    Modbus16Utils.GetRead(byte.Parse(DeviceModel.GetDeviceData("ADDR")), 0x30, 0x30),
                    //    DataProcessorContext.AutoReadInterval);

                    for (int i = 0; i < DataProcessorContext.ReadCmdList.Count; i++)
                    {
                        CmdBean cmdBean = DataProcessorContext.ReadCmdList[i];
                        byte[] cmd = CmdUtils.GenerationCmd(cmdBean.sendData, cmdBean.sendHex, cmdBean.sendNewLine, DeviceModel.DeviceData);
                        // 发送读取命令
                        DeviceModel.ReadData(cmd, DataProcessorContext.AutoReadInterval);
                    }

                    // 读取版本号寄存器
                    ReadVersionNumberReg(DeviceModel);
                    // 读取磁场类型寄存器
                    ReadMagType(DeviceModel);
                    // 读取序列号寄存器
                    ReadSerialNumberReg(DeviceModel);
                }
                catch (Exception e)
                {
                    Debug.WriteLine("自动读取失败：" + e.Message);
                }
            }
            // throw new NotImplementedException();
        }

        /// <summary>
        /// 读取版本号寄存器
        /// </summary>
        /// <param name="deviceModel"></param>
        private void ReadVersionNumberReg(DeviceModel deviceModel)
        {
            // 读版本号
            if (deviceModel.GetDeviceData("2E") == null)
            {
                // 读版本号
                deviceModel.ReadData(Modbus16Utils.GetRead(byte.Parse(deviceModel.GetDeviceData("ADDR")), 0x2e, 2));
                Thread.Sleep(20);
            }
        }

        /// <summary>
        /// 读取序列号寄存器
        /// </summary>
        /// <param name="deviceModel"></param>
        private void ReadSerialNumberReg(DeviceModel deviceModel)
        {
            // 读序列号
            if (deviceModel.GetDeviceData("7F") == null && deviceModel.GetDeviceData("82") == null)
            {
                // 读序列号
                deviceModel.ReadData(Modbus16Utils.GetRead(byte.Parse(deviceModel.GetDeviceData("ADDR")), 0x7F, 3));
                deviceModel.ReadData(Modbus16Utils.GetRead(byte.Parse(deviceModel.GetDeviceData("ADDR")), 0x7F + 3, 3));
            }
        }

        /// <summary>
        /// 当传感器关闭时
        /// </summary>
        public override void OnClose(DeviceModel deviceModel)
        {
            ReadDataThreadRuning = false;
        }

        /// <summary>
        /// 当触发数据更新时
        /// </summary>
        /// <param name="deviceModel"></param>
        public override void OnUpdate(DeviceModel deviceModel)
        {
            // 版本号
            var reg2e = deviceModel.GetDeviceData("2E");// 版本号
            var reg2f = deviceModel.GetDeviceData("2F");// 版本号

            // 如果有版本号
            if (string.IsNullOrEmpty(reg2e) == false &&
                string.IsNullOrEmpty(reg2f) == false)
            {
                var reg2eValue = (ushort)short.Parse(reg2e);
                var vbytes = BitConverter.GetBytes((ushort)short.Parse(reg2e)).Concat(BitConverter.GetBytes((ushort)short.Parse(reg2f))).ToArray();
                UInt32 tempVerSion = BitConverter.ToUInt32(vbytes, 0);
                string sbinary = Convert.ToString(tempVerSion, 2);
                sbinary = ("").PadLeft((32 - sbinary.Length), '0') + sbinary;
                if (sbinary.StartsWith("1"))//新版本号
                {
                    string tempNewVS = Convert.ToUInt32(sbinary.Substring(4 - 3, 14 + 3), 2).ToString();
                    tempNewVS += "." + Convert.ToUInt32(sbinary.Substring(18, 6), 2);
                    tempNewVS += "." + Convert.ToUInt32(sbinary.Substring(24), 2);
                    deviceModel.SetDeviceData(WitSensorKey.VersionNumber, tempNewVS);
                }
                else
                {
                    deviceModel.SetDeviceData(WitSensorKey.VersionNumber, reg2eValue.ToString());
                }
            }

            // 序列号
            var reg7f = deviceModel.GetDeviceData("7F");// 序列号
            var reg80 = deviceModel.GetDeviceData("80");// 序列号
            var reg81 = deviceModel.GetDeviceData("81");// 序列号
            var reg82 = deviceModel.GetDeviceData("82");// 序列号
            var reg83 = deviceModel.GetDeviceData("83");// 序列号
            var reg84 = deviceModel.GetDeviceData("84");// 序列号
            if (string.IsNullOrEmpty(reg7f) == false &&
                string.IsNullOrEmpty(reg80) == false &&
                string.IsNullOrEmpty(reg81) == false &&
                string.IsNullOrEmpty(reg82) == false &&
                string.IsNullOrEmpty(reg83) == false &&
                string.IsNullOrEmpty(reg84) == false)
            {
                var sbytes = BitConverter.GetBytes(short.Parse(reg7f))
                    .Concat(BitConverter.GetBytes(short.Parse(reg80)))
                    .Concat(BitConverter.GetBytes(short.Parse(reg81)))
                    .Concat(BitConverter.GetBytes(short.Parse(reg82)))
                    .Concat(BitConverter.GetBytes(short.Parse(reg83)))
                    .Concat(BitConverter.GetBytes(short.Parse(reg84)))
                    .ToArray();
                string sn = Encoding.Default.GetString(sbytes);
                deviceModel.SetDeviceData(WitSensorKey.SerialNumber, sn);
            }


            // 30代表传感器回传的30寄存器数据,其它的同理
            var reg30 = deviceModel.GetDeviceData("30");// 年月
            var reg31 = deviceModel.GetDeviceData("31");// 日时
            var reg32 = deviceModel.GetDeviceData("32");// 分秒
            var reg33 = deviceModel.GetDeviceData("33");// 毫秒
            // 如果回传了时间数据包就解算时间
            if (!string.IsNullOrEmpty(reg30) &&
                !string.IsNullOrEmpty(reg31) &&
                !string.IsNullOrEmpty(reg32) &&
                !string.IsNullOrEmpty(reg33)
                )
            {
                // 解算数据,并且保存到设备数据里
                var yy = 2000 + (byte)int.Parse(reg30);
                var MM = (byte)(int.Parse(reg30) >> 8);
                var dd = (byte)int.Parse(reg31);
                var hh = (byte)(int.Parse(reg31) >> 8);
                var mm = (byte)int.Parse(reg32);
                var ss = (byte)(int.Parse(reg32) >> 8);
                var ms = int.Parse(reg33).ToString("000");


                deviceModel.SetDeviceData(WitSensorKey.ChipTime, $"{yy}-{MM}-{dd} {hh}:{mm}:{ss}.{ms}");
            }


            var reg34 = deviceModel.GetDeviceData("34");// 加速度X
            var reg35 = deviceModel.GetDeviceData("35");// 加速度X
            var reg36 = deviceModel.GetDeviceData("36");// 加速度X
            // 如果回传了加速度数据包
            if (!string.IsNullOrEmpty(reg34) &&
                !string.IsNullOrEmpty(reg35) &&
                !string.IsNullOrEmpty(reg36)
                )
            {
                // 解算数据,并且保存到设备数据里
                deviceModel.SetDeviceData(WitSensorKey.AccX, Math.Round(double.Parse(reg34) / 32768.0 * 16,3));
                deviceModel.SetDeviceData(WitSensorKey.AccY, Math.Round(double.Parse(reg35) / 32768.0 * 16,3));
                deviceModel.SetDeviceData(WitSensorKey.AccZ, Math.Round(double.Parse(reg36) / 32768.0 * 16,3));
            }

            var reg37 = deviceModel.GetDeviceData("37");// 角速度X
            var reg38 = deviceModel.GetDeviceData("38");// 角速度Y
            var reg39 = deviceModel.GetDeviceData("39");// 角速度Z
            // 如果回传了角速度数据包
            if (!string.IsNullOrEmpty(reg37) &&
                !string.IsNullOrEmpty(reg38) &&
                !string.IsNullOrEmpty(reg39)
                )
            {
                // 解算数据,并且保存到设备数据里
                deviceModel.SetDeviceData(WitSensorKey.AsX, Math.Round(double.Parse(reg37) / 32768.0 * 2000,3));
                deviceModel.SetDeviceData(WitSensorKey.AsY, Math.Round(double.Parse(reg38) / 32768.0 * 2000,3));
                deviceModel.SetDeviceData(WitSensorKey.AsZ, Math.Round(double.Parse(reg39) / 32768.0 * 2000,3));
            }

            var reg3D = deviceModel.GetDeviceData("3D");// 角度X
            var reg3E = deviceModel.GetDeviceData("3E");// 角度Y
            var reg3F = deviceModel.GetDeviceData("3F");// 角度Z
            // 如果回传了角度数据包
            if (!string.IsNullOrEmpty(reg3D) &&
                !string.IsNullOrEmpty(reg3E) &&
                !string.IsNullOrEmpty(reg3F)
                )
            {
                // 解算数据,并且保存到设备数据里
                deviceModel.SetDeviceData(WitSensorKey.AngleX, Math.Round(double.Parse(reg3D) / 32768.0 * 180,3));
                deviceModel.SetDeviceData(WitSensorKey.AngleY, Math.Round(double.Parse(reg3E) / 32768.0 * 180,3));
                deviceModel.SetDeviceData(WitSensorKey.AngleZ, Math.Round(double.Parse(reg3F) / 32768.0 * 180,3));
            }

            var reg3A = deviceModel.GetDeviceData("3A");// 磁场X
            var reg3B = deviceModel.GetDeviceData("3B");// 磁场Y
            var reg3C = deviceModel.GetDeviceData("3C");// 磁场Z
            var magType = deviceModel.GetDeviceData("72");// 磁场类型

            // 如果回传了磁场数据包
            if (!string.IsNullOrEmpty(reg3A) &&
                !string.IsNullOrEmpty(reg3B) &&
                !string.IsNullOrEmpty(reg3C) &&
                !string.IsNullOrEmpty(magType)
                )
            {
                short type = short.Parse(magType);
                // 解算数据,并且保存到设备数据里
                deviceModel.SetDeviceData(WitSensorKey.HX, DipSensorMagHelper.GetMagToUt(type, double.Parse(reg3A)));
                deviceModel.SetDeviceData(WitSensorKey.HY, DipSensorMagHelper.GetMagToUt(type, double.Parse(reg3B)));
                deviceModel.SetDeviceData(WitSensorKey.HZ, DipSensorMagHelper.GetMagToUt(type, double.Parse(reg3C)));
                deviceModel.SetDeviceData(WitSensorKey.HM, Math.Round(Math.Sqrt(Math.Pow(DipSensorMagHelper.GetMagToUt(type, double.Parse(reg3A)), 2) + 
                                                           Math.Pow(DipSensorMagHelper.GetMagToUt(type, double.Parse(reg3B)), 2) + 
                                                           Math.Pow(DipSensorMagHelper.GetMagToUt(type, double.Parse(reg3C)), 2)), 2));
            }

            var reg40 = deviceModel.GetDeviceData("40");// 温度
            // 如果回传了温度数据包
            if (!string.IsNullOrEmpty(reg40))
            {
                deviceModel.SetDeviceData(WitSensorKey.T, Math.Round(double.Parse(reg40) / 100.0, 2));
            }

            var reg41 = deviceModel.GetDeviceData(new ShortKey("41"));// 端口0
            var reg42 = deviceModel.GetDeviceData(new ShortKey("42"));// 端口1
            var reg43 = deviceModel.GetDeviceData(new ShortKey("43"));// 端口2
            var reg44 = deviceModel.GetDeviceData(new ShortKey("44"));// 端口3
            // 如果回传了端口状态数据包
            if (reg41 != null &&
                reg42 != null &&
                reg43 != null &&
                reg44 != null
                )
            {
                deviceModel.SetDeviceData(WitSensorKey.D0, (short)reg41);
                deviceModel.SetDeviceData(WitSensorKey.D1, (short)reg42);
                deviceModel.SetDeviceData(WitSensorKey.D2, (short)reg43);
                deviceModel.SetDeviceData(WitSensorKey.D3, (short)reg44);
            }

            var reg45 = deviceModel.GetDeviceData("45");// 气压低位
            var reg46 = deviceModel.GetDeviceData("46");// 气压高位
            var reg47 = deviceModel.GetDeviceData("47");// 高度低位
            var reg48 = deviceModel.GetDeviceData("48");// 高度高位
            // 如果回传了气压高度数据包
            if (!string.IsNullOrEmpty(reg45) &&
                !string.IsNullOrEmpty(reg46) &&
                !string.IsNullOrEmpty(reg47) &&
                !string.IsNullOrEmpty(reg48)
                ) {

                var pbytes =  BitConverter.GetBytes(short.Parse(reg45)).Concat(BitConverter.GetBytes(short.Parse(reg46))).ToArray();
                var hbytes = BitConverter.GetBytes(short.Parse(reg47)).Concat(BitConverter.GetBytes(short.Parse(reg48))).ToArray();
                deviceModel.SetDeviceData(WitSensorKey.P, BitConverter.ToInt32(pbytes, 0));
                deviceModel.SetDeviceData(WitSensorKey.H, (BitConverter.ToInt32(hbytes, 0) / 100.0));
            }


            var reg49 = deviceModel.GetDeviceData("49");// 经度低位
            var reg4A = deviceModel.GetDeviceData("4A");// 经度高位
            var reg4B = deviceModel.GetDeviceData("4B");// 纬度低位
            var reg4C = deviceModel.GetDeviceData("4C");// 纬度高位
            // 如果有经纬度输出
            if (!string.IsNullOrEmpty(reg49) &&
                !string.IsNullOrEmpty(reg4A) &&
                !string.IsNullOrEmpty(reg4B) &&
                !string.IsNullOrEmpty(reg48)
                )
            {
                var lonbytes = BitConverter.GetBytes(short.Parse(reg49)).Concat(BitConverter.GetBytes(short.Parse(reg4A))).ToArray();
                var lon = BitConverter.ToInt32(lonbytes, 0);
                var latbytes = BitConverter.GetBytes(short.Parse(reg4B)).Concat(BitConverter.GetBytes(short.Parse(reg4C))).ToArray();
                var lat = BitConverter.ToInt32(latbytes, 0);

                double lon_D = GpsUtils.DmsToD((double)lon / 100000.0);
                deviceModel.SetDeviceData(WitSensorKey.Lon, $"{lon_D}°");
                deviceModel.SetDeviceData(WitSensorKey.LonDeg, Math.Round(lon_D,6));
                double lat_D = GpsUtils.DmsToD((double)lat / 100000.0);
                deviceModel.SetDeviceData(WitSensorKey.Lat, $"{lat_D}°");
                deviceModel.SetDeviceData(WitSensorKey.LatDeg, Math.Round(lat_D,6));
            }

            var reg4D = deviceModel.GetDeviceData("4D");// GPS高度
            var reg4E = deviceModel.GetDeviceData("4E");// GPS航向
            var reg4F = deviceModel.GetDeviceData("4F");// 地速低位
            var reg50 = deviceModel.GetDeviceData("50");// 地速高位
            // 如果有地速包输出
            if (!string.IsNullOrEmpty(reg4D) &&
                !string.IsNullOrEmpty(reg4E) &&
                !string.IsNullOrEmpty(reg4F) &&
                !string.IsNullOrEmpty(reg50)
                ) {
                var svbytes = BitConverter.GetBytes(short.Parse(reg4F)).Concat(BitConverter.GetBytes(short.Parse(reg50))).ToArray();

                deviceModel.SetDeviceData(WitSensorKey.GPSHeight, Math.Round(short.Parse(reg4D)/ 10.0,3));
                byte[] temp = BitConverter.GetBytes(short.Parse(reg4E));    // 航向解算不要负数
                uint reg4EValue = BitConverter.ToUInt16(temp, 0);
                deviceModel.SetDeviceData(WitSensorKey.GPSYaw, Math.Round(reg4EValue / 100.0,3));
                deviceModel.SetDeviceData(WitSensorKey.GPSV, Math.Round(BitConverter.ToInt32(svbytes, 0) / 1e3,3));
            }

            var reg51 = deviceModel.GetDeviceData("51");// 四元数0
            var reg52 = deviceModel.GetDeviceData("52");// 四元数1
            var reg53 = deviceModel.GetDeviceData("53");// 四元数2
            var reg54 = deviceModel.GetDeviceData("54");// 四元数3
            // 如果有四元数输出
            if (!string.IsNullOrEmpty(reg51) &&
                !string.IsNullOrEmpty(reg52) &&
                !string.IsNullOrEmpty(reg53) &&
                !string.IsNullOrEmpty(reg54)
                )
            {
                deviceModel.SetDeviceData(WitSensorKey.Q0, Math.Round(short.Parse(reg51) / 32768.0,3));
                deviceModel.SetDeviceData(WitSensorKey.Q1, Math.Round(short.Parse(reg52) / 32768.0,3));
                deviceModel.SetDeviceData(WitSensorKey.Q2, Math.Round(short.Parse(reg53) / 32768.0,3));
                deviceModel.SetDeviceData(WitSensorKey.Q3, Math.Round(short.Parse(reg54) / 32768.0,3));
            }

            var reg55 = deviceModel.GetDeviceData("55");// 卫星数
            var reg56 = deviceModel.GetDeviceData("56");// 位置精度
            var reg57 = deviceModel.GetDeviceData("57");// 位置精度
            var reg58 = deviceModel.GetDeviceData("58");// 位置精度

            // 如果有位置精度输出
            if (!string.IsNullOrEmpty(reg55) &&
                !string.IsNullOrEmpty(reg56) &&
                !string.IsNullOrEmpty(reg57) &&
                !string.IsNullOrEmpty(reg58)
                )
            {
                deviceModel.SetDeviceData(WitSensorKey.SN, short.Parse(reg55));
                deviceModel.SetDeviceData(WitSensorKey.PDOP, Math.Round(short.Parse(reg56) / 100.0,3));
                deviceModel.SetDeviceData(WitSensorKey.HDOP, Math.Round(short.Parse(reg57) / 100.0,3));
                deviceModel.SetDeviceData(WitSensorKey.VDOP, Math.Round(short.Parse(reg58) / 100.0,3));
            }
        }

        /// <summary>
        /// 读取磁场类型寄存器
        /// </summary>
        private void ReadMagType(DeviceModel deviceModel) {
            // 读版本号
            if (deviceModel.GetDeviceData("72") == null)
            {
                // 读取72磁场类型寄存器,后面解析磁场的时候要用到（读三次避免读不上）
                deviceModel.ReadData(Modbus16Utils.GetRead(byte.Parse(deviceModel.GetDeviceData("ADDR")), 0x72, 1));
                Thread.Sleep(20);
            }
        }
    }
}
