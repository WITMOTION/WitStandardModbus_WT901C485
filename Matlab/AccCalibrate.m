clear all;
close all;
instrreset;
devNo=1;                                           %根据实际串联的个数，修改该数量   Device Number
disp('Press Ctrl+C to stop collecting data!');      %按Ctrl+C 可以终止运行
s=serial('com3','baudrate',9600) ;fopen(s);       %Open Com Port   请将COM37换成电脑识别到的COM口，波特率9600换成传感器对应的波特率   

fid = fopen('20210812E.txt','wt'); %根据实际需求，可将文件“20210812E”的名称修改   According to actual needs, the name of the file "20210812E" can be modified
%文件数据格式：加速度X 加速度Y 加速度Z 角速度X 角速度Y 角速度Z 角度X 角度Y 角度Z 无效0 设备ID   File Data Format: Acceleration X, Acceleration Y, Acceleration Z, Angular Velocity X, Angular Velocity Y, Angular Velocity Z, Angle X, Angle Y, Angle Z, Invalid 0, Device ID
DataTxt=zeros(1,10);
f = 20;
NumCnt=1;
BuffIndex1=0;
BuffIndex2=0;
BuffIndex3=0;
DisplayIndex=1;
aa=zeros(1,devNo*3); %每个设备的加速度有3个轴，1，2，3为1号设备，4，5，6为2号设备，......34,35,36为12号设备   There are 3 axes acceleration of each device,  device 1 is 1, 2, 3, device 2 is 4, 5, 6 ... device 12 is 34, 35, 36 
ww=zeros(1,devNo*3);
AA=zeros(1,devNo*3);
tt=zeros(1,1);
a=zeros(1,devNo*3);  %每个设备的加速度有3个轴，1，2，3为1号设备，4，5，6为2号设备，......34,35,36为12号设备
w=zeros(1,devNo*3);
A=zeros(1,devNo*3);
Temp=zeros(1,24);

UnLockCmd=[80 06 0 105 181 136 34 161]';  %0x50 0x06 0x00 0x69 0xB5 0x88 0x22 0xA1
CaliCmd=[80 06 0 1 0 1 20 75]';  %0x50 0x06 0x00 0x01 0x00 0x01 0x14 0x4B
SaveCmd=[80 06 0 0 0 0 132 75]';  %0x50 0x06 0x00 0x00 0x00 0x00 0x84 0x4B

StartCali='CALI';
CalFlag=0;

D1=[                      %如果修改devNo的数量，则需要往下面添加指令，目前为1个设备   If modify the number of devNo, need to add instructions below, currently 1 devices
    80 3 0 52 0 12 9 128  %0x50 0x03 0x00 0x34 0x00 0x0C 0x09 0x80
%     81 3 0 52 0 12 8 81   %0x51 0x03 0x00 0x34 0x00 0x0C 0x08 0x51
%     82 3 0 52 0 12 8 98   %0x52 0x03 0x00 0x34 0x00 0x0C 0x08 0x62
%     83 3 0 52 0 12 9 179  %0x53 0x03 0x00 0x34 0x00 0x0C 0x09 0xB3
%     84 3 0 52 0 12 8 4    %0x54 0x03 0x00 0x34 0x00 0x0C 0x08 0x04
%     85 3 0 52 0 12 9 213  %0x55 0x03 0x00 0x34 0x00 0x0C 0x09 0xD5
%     86 3 0 52 0 12 9 230  %0x56 0x03 0x00 0x34 0x00 0x0C 0x09 0xE6
%     87 3 0 52 0 12 8 55   %0x57 0x03 0x00 0x34 0x00 0x0C 0x08 0x37
%     88 3 0 52 0 12 8 200  %0x58 0x03 0x00 0x34 0x00 0x0C 0x08 0xC8
%     89 3 0 52 0 12 9 25   %0x59 0x03 0x00 0x34 0x00 0x0C 0x09 0x19
%     90 3 0 52 0 12 9 42   %0x5A 0x03 0x00 0x34 0x00 0x0C 0x09 0x2A
%     91 3 0 52 0 12 8 251  %0x5B 0x03 0x00 0x34 0x00 0x0C 0x08 0xFB
   ];
D0 = D1';

StartTime=cputime;

while(1)
    
    if CalFlag==0
        CalFlag=input('请放置水平，输入CALI进行校准','s');
        if strcmp(CalFlag,StartCali)==1
            disp('校准中，请稍等')
            fwrite(s,UnLockCmd(1:8),'uint8');                %解锁   Unlock
            pause(1);
            fwrite(s,CaliCmd(1:8),'uint8');                  %解锁完成后，等待1秒，发送进入加计校准   After unlocking, wait for 1 second and send command to enter the acceleration calibration
            pause(4);
            fwrite(s,SaveCmd(1:8),'uint8');                  %等待4秒，校准完成后，保存校准参数   Wait 4 second to save the calibration parameters
            pause(1);
        end
    end
    
    t=cputime-StartTime; %获取CPU时间减去初始时间
    
    for NumCnt=1:devNo 
        fwrite(s,D0((NumCnt-1)*8+1:NumCnt*8),'uint8');  %串口发送读取指令    Serial sends the read command
        PHead=D0((NumCnt-1)*8+1);                       %取ID用于判断回来的数据是否符合ID    Get the ID to determine whether the returned data conforms to the ID

        Head = fread(s,3,'uint8');                      %先读取3个字节，判断是否符合Modbus协议头   First read 3 bytes, and then judge whether it conforms to the Modbus protocol header

        if (Head(1)~=uint8(PHead))
            pause(0.05);
            continue;                                   %如果不通过，则不执行以下程序，立马执行下一个读取   If it does not pass, the following procedure is not executed, and the next read is executed immediately
        end  
        if (Head(2)~=uint8(3))
            pause(0.05);
            continue;
        end  
        if (Head(3)~=uint8(24))
            pause(0.05);
            continue;
        end 

        for i=1:24                                      %连续读取数据24个  加速度*3   角速度*3   磁场*3   角度*3   Read 24 data continuously, acceleration*3, angular velocity*3, magnetic field*3, angle*3
            if(mod(i,2)==0)
               Temp(i)=fread(s,1,'uint8');              %低字节为无符号   The low byte is unsigned
            end
            if(mod(i,2)~=0)
               Temp(i)=fread(s,1,'int8');               %高字节为有符号   The high byte is signed
            end
        end
        End=fread(s,1,'uint16');                         %读取最后两个字节，不需要处理   Read the last two bytes, no processing required

        BuffIndex1=3*(NumCnt)-2;                         
        BuffIndex2=3*(NumCnt)-1;
        BuffIndex3=3*(NumCnt);
        a(BuffIndex1)=single(int16(Temp(1)*256+Temp(2)))/32768*16;%取加速度X    Get acceleration X
        a(BuffIndex2)=single(int16(Temp(3)*256+Temp(4)))/32768*16;%取加速度Y    Get acceleration Y
        a(BuffIndex3)=single(int16(Temp(5)*256+Temp(6)))/32768*16;%取加速度Z    Get acceleration Z
        w(BuffIndex1)=single(int16(Temp(7)*256+Temp(8)))/32768*2000;%取角速度X    Get angular velocity X
        w(BuffIndex2)=single(int16(Temp(9)*256+Temp(10)))/32768*2000;%取角速度Y    Get angular velocity Y
        w(BuffIndex3)=single(int16(Temp(11)*256+Temp(12)))/32768*2000;%取角速度Z    Get angular velocity Z
        A(BuffIndex1)=single(int16(Temp(19)*256+Temp(20)))/32768*180;%取角度X    Get angle X
        A(BuffIndex2)=single(int16(Temp(21)*256+Temp(22)))/32768*180;%取角度Y    Get angle Y
        A(BuffIndex3)=single(int16(Temp(23)*256+Temp(24)))/32768*180;%取角度Z    Get angle Z
    end                                                              
    %以上程序为读取传感器数据部分   The above program is to read part of the sensor data
      
    %以下程序为显示及存储数据部分   The following program is to display and store part of data
    aa = [aa;a];
    ww = [ww;w];
    AA = [AA;A];
    tt = [tt;t];
    for NumCnt=1:devNo
        BuffIndex1=3*NumCnt-2; %例如，NumCnt=5，则当前要刷新显示的为第5个设备的数据，则3*5-2=13，则第5个设备的数据存放在数组的第13~15的位置   For example, NumCnt=5, which means that the current data to be refreshed and displayed is the data of the fifth device, that is, 3*5-2=13, so the data of the fifth device is stored in the 13th~15th position of the array
        BuffIndex2=3*NumCnt-1;
        BuffIndex3=3*NumCnt;
        PlotTemp1=aa(:,BuffIndex1:BuffIndex3);%如果不需要Figure显示，则注释，可以加快程序运行时间   If don't need Figure display, then comment, which can speed up the program running time
        PlotTemp2=ww(:,BuffIndex1:BuffIndex3);%如果不需要Figure显示，则注释，可以加快程序运行时间
        PlotTemp3=AA(:,BuffIndex1:BuffIndex3);%如果不需要Figure显示，则注释，可以加快程序运行时间
%第一种显示方式        
        subplot(6,6,3*NumCnt-2);plot(tt,PlotTemp1);title(['Acc = ' num2str(a(BuffIndex1:BuffIndex3)) 'm2/s']);ylabel('m2/s'); %如果不需要Figure显示，则注释，可以加快程序运行时间
        subplot(6,6,3*NumCnt-1);plot(tt,PlotTemp2);title(['Gyro = ' num2str(w(BuffIndex1:BuffIndex3)) '°/s']);ylabel('°/s'); %如果不需要Figure显示，则注释，可以加快程序运行时间
        subplot(6,6,3*NumCnt-0);plot(tt,PlotTemp3);title(['Angle = ' num2str(A(BuffIndex1:BuffIndex3)) '°']);ylabel('°');    %如果不需要Figure显示，则注释，可以加快程序运行时间
%第二种显示方式
%         subplot(12,3,3*NumCnt-2);plot(tt,PlotTemp1);title(['Acc = ' num2str(a(BuffIndex1:BuffIndex3)) 'm2/s']);ylabel('m2/s');
%         subplot(12,3,3*NumCnt-1);plot(tt,PlotTemp2);title(['Gyro = ' num2str(w(BuffIndex1:BuffIndex3)) '°/s']);ylabel('°/s'); 
%         subplot(12,3,3*NumCnt-0);plot(tt,PlotTemp3);title(['Angle = ' num2str(A(BuffIndex1:BuffIndex3)) '°']);ylabel('°');   

        drawnow;     
        
        DataTxt(:,1:3)=a(:,BuffIndex1:BuffIndex3);%数据存储部分   Data storage part
        DataTxt(:,4:6)=w(:,BuffIndex1:BuffIndex3);
        DataTxt(:,7:9)=A(:,BuffIndex1:BuffIndex3);
        fprintf(fid,'%g\t',DataTxt');
        PHead=D0((NumCnt-1)*8+1);
        fprintf(fid,'%g\n',PHead);%数据存储部分
    end
    if (size(aa,1)>5*f)%clear history data
        aa = aa(f:5*f,:);
        ww = ww(f:5*f,:);
        AA = AA(f:5*f,:);
        tt = tt(f:5*f,:);
    end
end
fclose(s);
