import pandas,numpy,pyads,time
import numpy as np
import pandas as pd
import os
global plc,py_id,global_identifiers,datas,shu,value_ov
global data_0,data_1,data_2,data_3,data_4,data_5,data_6,data_7,data_8,data_9,data_10
global data_11,data_12,data_13,data_14,data_15,data_16,data_17,data_18,data_19,data_20,data_21,data_22,data_23,data_24,data_25,data_26
data_0 = None
data_1 = None
data_2 = None
data_3 = None
data_4 = None
data_5 = None
data_6 = None
data_7 = None
data_8 = None
data_9 = None
data_10 = None
data_11 = None
data_12 = None
data_13 = None
data_14 = None
data_15 = None
data_16 = None
data_17 = None
data_18 = None
data_19 = None
data_20 = None
data_21 = None
data_22 = None
data_23 = None
data_24 = None
data_25 = None
data_26 = None
global_identifiers = []
datas = []
shu = 0

#Pyads连接
def pyads_connection(ams_net_id,ams_port):
    global plc
    plc = pyads.Connection(ams_net_id, ams_port)
    if plc:
        print("通讯已连接")
    else:
         print("通讯连接失败")
    return plc

def fifo_power():
    global plc
    plc.open()
    plc.write_by_name('MAIN.power_do', True, pyads.PLCTYPE_BOOL)
    plc_value = plc.read_by_name('MAIN.power_do',  pyads.PLCTYPE_BOOL)
    if plc_value:
        print("机器人上使能")
    else:
         print("机器人使能失败")

def speed(speed_value):
    global plc
    plc.open()
    plc.write_by_name('MAIN.ov', speed_value, pyads.PLCTYPE_UDINT)



def stop_do():
    global plc
    plc.open()
    plc.write_by_name('MAIN.power_do', True, pyads.PLCTYPE_BOOL)
    print("机器人下使能")

def fifostop(plc):
        global shu
        plc.open()
        if plc:
            plc.open()
            plc.write_by_name('MAIN.fifo_stop_do', True,pyads.PLCTYPE_BOOL)
            

            safentries_1 = plc.read_by_name('MAIN.axis3.NcToPlc.SafEntries',pyads.PLCTYPE_DINT)

            new_ov = plc.read_by_name('MAIN.new_ov',pyads.PLCTYPE_DINT)

            time.sleep(0.6)

            plc.write_by_name('MAIN.dis_do', False, pyads.PLCTYPE_BOOL)
            plc.write_by_name('MAIN.dis_do', True, pyads.PLCTYPE_BOOL)
            time.sleep(0.2)
            plc.write_by_name('MAIN.dis_do', False, pyads.PLCTYPE_BOOL)
            time.sleep(0.2)
            plc.write_by_name('MAIN.integrate_do', False, pyads.PLCTYPE_BOOL)
            plc.write_by_name('MAIN.integrate_do', True, pyads.PLCTYPE_BOOL)
            time.sleep(0.2)
            plc.write_by_name('MAIN.integrate_do', False, pyads.PLCTYPE_BOOL)
            
            plc.open()
            value_0 = plc.read_by_name('MAIN.integrate_do', pyads.PLCTYPE_BOOL)
            value_1 = plc.read_by_name('MAIN.dis_do', pyads.PLCTYPE_BOOL)


            jogq1 = plc.read_by_name('MAIN.jogq1',pyads.PLCTYPE_ARR_LREAL(new_ov))
            jogq2 = plc.read_by_name('MAIN.jogq2',pyads.PLCTYPE_ARR_LREAL(new_ov))
            jogq3 = plc.read_by_name('MAIN.jogq3',pyads.PLCTYPE_ARR_LREAL(new_ov))
            jogq4 = plc.read_by_name('MAIN.jogq4',pyads.PLCTYPE_ARR_LREAL(new_ov))
            jogq5 = plc.read_by_name('MAIN.jogq5',pyads.PLCTYPE_ARR_LREAL(new_ov))

            # 获取初始数据         
            q_chart = new_ov - safentries_1 -1
            q_chart1 = q_chart+1

            jogq1_chart = jogq1[q_chart]
            jogq1_chart1 = jogq1[q_chart1+1]
            jogq2_chart = jogq2[q_chart]
            jogq2_chart1 = jogq2[q_chart1+1]
            jogq3_chart = jogq3[q_chart]
            jogq3_chart1 = jogq3[q_chart1+1]
            jogq4_chart = jogq4[q_chart]
            jogq4_chart1 = jogq4[q_chart1+1]
            jogq5_chart = jogq5[q_chart]
            jogq5_chart1 = jogq5[q_chart1+1]

            jogq1_home = plc.read_by_name('MAIN.axis1.NcToPlc.ActPos',pyads.PLCTYPE_LREAL)
            jogq2_home = plc.read_by_name('MAIN.axis2.NcToPlc.ActPos',pyads.PLCTYPE_LREAL)
            jogq3_home = plc.read_by_name('MAIN.axis3.NcToPlc.ActPos',pyads.PLCTYPE_LREAL)
            jogq4_home = plc.read_by_name('MAIN.axis4.NcToPlc.ActPos',pyads.PLCTYPE_LREAL)
            jogq5_home = plc.read_by_name('MAIN.axis5.NcToPlc.ActPos',pyads.PLCTYPE_LREAL)

            jogq1_remain = jogq1[q_chart1+1:]
            jogq2_remain = jogq2[q_chart1+1:]
            jogq3_remain = jogq3[q_chart1+1:]
            jogq4_remain = jogq4[q_chart1+1:]
            jogq5_remain = jogq5[q_chart1+1:]

            delt1 = jogq1_chart1 - jogq1_home
            delt2 = jogq2_chart1 - jogq2_home
            delt3 = jogq3_chart1 - jogq3_home
            delt4 = jogq4_chart1 - jogq4_home
            delt5 = jogq5_chart1 - jogq5_home
            
            r = 2  # 公比
            n = 10  # 大份数量
            d1 =  delt1 / (-2 * (1 - r**n))
            d2 =  delt2 / (-2 * (1 - r**n))
            d3 =  delt3 / (-2 * (1 - r**n))
            d4 =  delt4 / (-2 * (1 - r**n))
            d5 =  delt5 / (-2 * (1 - r**n))
            lengths1 = [d1 * (r ** (i - 1)) for i in range(1, 11)]
            lengths2 = [d2 * (r ** (i - 1)) for i in range(1, 11)]
            lengths3 = [d3 * (r ** (i - 1)) for i in range(1, 11)]
            lengths4 = [d4 * (r ** (i - 1)) for i in range(1, 11)]
            lengths5 = [d5 * (r ** (i - 1)) for i in range(1, 11)]
            
            a1 = 0
            a2 = 0
            a3 = 0
            a4 = 0
            a5 = 0
            # 初始化插值数组
            q1_in = np.zeros((10, 1), 'float')
            q2_in = np.zeros((10, 1), 'float')
            q3_in = np.zeros((10, 1), 'float')
            q4_in = np.zeros((10, 1), 'float')
            q5_in = np.zeros((10, 1), 'float')

            # 如果有差值，则进行插值计算
            if any(abs(delt) != 0 for delt in [delt1, delt2, delt3, delt4, delt5]):
                        


                for i in range(10):
                                
                        a1 += lengths1[i]
                        a2 += lengths2[i]
                        a3 += lengths3[i]
                        a4 += lengths4[i]
                        a5 += lengths5[i]
                        q1_in[i] = jogq1_home + a1
                        q2_in[i] = jogq2_home + a2
                        q3_in[i] = jogq3_home + a3
                        q4_in[i] = jogq4_home + a4
                        q5_in[i] = jogq5_home + a5

                            # 拼接新数组
                jogq1_new = np.concatenate((q1_in.flatten(), jogq1_remain))
                jogq2_new = np.concatenate((q2_in.flatten(), jogq2_remain))
                jogq3_new = np.concatenate((q3_in.flatten(), jogq3_remain))
                jogq4_new = np.concatenate((q4_in.flatten(), jogq4_remain))
                jogq5_new = np.concatenate((q5_in.flatten(), jogq5_remain))


                plc.write_by_name('MAIN.jogq1', jogq1_new, pyads.PLCTYPE_ARR_LREAL(len(jogq1_new)))
                plc.write_by_name('MAIN.jogq2', jogq2_new, pyads.PLCTYPE_ARR_LREAL(len(jogq2_new)))
                plc.write_by_name('MAIN.jogq3', jogq3_new, pyads.PLCTYPE_ARR_LREAL(len(jogq3_new)))
                plc.write_by_name('MAIN.jogq4', jogq4_new, pyads.PLCTYPE_ARR_LREAL(len(jogq4_new)))
                plc.write_by_name('MAIN.jogq5', jogq5_new, pyads.PLCTYPE_ARR_LREAL(len(jogq5_new)))

                        # 设置标志位
                
                plc.write_by_name('MAIN.new_ov', len(jogq1_new), pyads.PLCTYPE_UDINT)
            else:
                jogq1_new = jogq1_remain
                jogq2_new = jogq2_remain
                jogq3_new = jogq3_remain
                jogq4_new = jogq4_remain
                jogq5_new = jogq5_remain

                plc.write_by_name('MAIN.jogq1', jogq1_new, pyads.PLCTYPE_ARR_LREAL(len(jogq1_new)))
                plc.write_by_name('MAIN.jogq2', jogq2_new, pyads.PLCTYPE_ARR_LREAL(len(jogq2_new)))
                plc.write_by_name('MAIN.jogq3', jogq3_new, pyads.PLCTYPE_ARR_LREAL(len(jogq3_new)))
                plc.write_by_name('MAIN.jogq4', jogq4_new, pyads.PLCTYPE_ARR_LREAL(len(jogq4_new)))
                plc.write_by_name('MAIN.jogq5', jogq5_new, pyads.PLCTYPE_ARR_LREAL(len(jogq5_new)))

                # 设置标志位
                plc.write_by_name('MAIN.fifo_stop_do', False,pyads.PLCTYPE_BOOL)
                plc.write_by_name('MAIN.new_ov', len(jogq1_new), pyads.PLCTYPE_UDINT)
                print("机器人暂停")

            plc.close()
            shu = 0

def Poly_O(identifier,value):
    global global_identifiers,shu,data_0
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_O"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_0 = read_and_repeat_data(now_sl_0, value) 
            print("肩关节上举运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_P(identifier,value):
    global global_identifiers,shu,data_1
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_P"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_1 = read_and_repeat_data(now_sl_0, value) 
            print("肩关节左右")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_Q(identifier,value):
    global global_identifiers,shu,data_2
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_Q"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_2 = read_and_repeat_data(now_sl_0, value) 
            print("摇肩运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")


def Poly_R(identifier,value):
    global global_identifiers,shu,data_3
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_R"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_3 = read_and_repeat_data(now_sl_0, value) 
            print("肘关节屈曲运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_S(identifier,value):
    global global_identifiers,shu,data_4
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_S"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_4 = read_and_repeat_data(now_sl_0, value) 
            print("左右翻手运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_T(identifier,value):
    global global_identifiers,shu,data_5
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_T"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_5 = read_and_repeat_data(now_sl_0, value) 
            print("肩关节外旋内旋运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_U(identifier,value):
    global global_identifiers,shu,data_6
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_U"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_6 = read_and_repeat_data(now_sl_0, value) 
            print("肩关节外展内收运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_V(identifier,value):
    global global_identifiers,shu,data_7
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_V"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_7 = read_and_repeat_data(now_sl_0, value) 
            print("肘关节屈曲伸展运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")
                                             
def Poly_B(identifier,value):
    global global_identifiers,shu,data_8
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_B"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_8 = read_and_repeat_data(now_sl_0, value)
            print("擦嘴运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_C(identifier,value):
    global global_identifiers,shu,data_9
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_C"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_9 = read_and_repeat_data(now_sl_0, value) 
            print("系安全带运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_D(identifier,value):
    global global_identifiers,shu,data_10
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_D"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_10 = read_and_repeat_data(now_sl_0, value) 
            print("喝水运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_E(identifier,value):
    global global_identifiers,shu,data_11
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_E"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_11 = read_and_repeat_data(now_sl_0, value) 
            print("擦窗户运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")


def Poly_G(identifier,value):
    global global_identifiers,shu,data_12
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_G"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_12 = read_and_repeat_data(now_sl_0, value) 
            print("向前挥拳运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_H(identifier,value):
    global global_identifiers,shu,data_13
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_H"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_13 = read_and_repeat_data(now_sl_0, value) 
            print("低手传球运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_I(identifier,value):
    global global_identifiers,shu,data_14
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_I"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_14 = read_and_repeat_data(now_sl_0, value) 
            print("戴眼镜运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_M(identifier,value):
    global global_identifiers,shu,data_15
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_M"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_15 = read_and_repeat_data(now_sl_0, value) 
            print("吃东西运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_N(identifier,value):
    global global_identifiers,shu,data_16
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_N"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_16 = read_and_repeat_data(now_sl_0, value) 
            print("扣扣子运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_NEW1(identifier,value):
    global global_identifiers,shu,data_17
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_NEW1"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_17 = read_and_repeat_data(now_sl_0, value) 
            print("新轨迹1运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_NEW2(identifier,value):
    global global_identifiers,shu,data_18
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_NEW2"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_18 = read_and_repeat_data(now_sl_0, value) 
            print("新轨迹2运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_NEW3(identifier,value):
    global global_identifiers,shu,data_19
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_NEW3"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_19 = read_and_repeat_data(now_sl_0, value) 
            print("新轨迹3运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_NEW4(identifier,value):
    global global_identifiers,shu,data_20
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_NEW4"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_20 = read_and_repeat_data(now_sl_0, value) 
            print("新轨迹4运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_NEW5(identifier,value):
    global global_identifiers,shu,data_21
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_NEW5"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_21 = read_and_repeat_data(now_sl_0, value) 
            print("新轨迹5运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_NEW6(identifier,value):
    global global_identifiers,shu,data_22
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_NEW6"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_22 = read_and_repeat_data(now_sl_0, value) 
            print("新轨迹6运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_NEW7(identifier,value):
    global global_identifiers,shu,data_23
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_NEW7"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_23 = read_and_repeat_data(now_sl_0, value) 
            print("新轨迹7运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_NEW8(identifier,value):
    global global_identifiers,shu,data_24
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_NEW8"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_24 = read_and_repeat_data(now_sl_0, value)
            print("新轨迹8运动") 
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")
                                    
def Poly_NEW9(identifier,value):
    global global_identifiers,shu,data_25
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_NEW9"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_25 = read_and_repeat_data(now_sl_0, value) 
            print("新轨迹9运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def Poly_NEW10(identifier,value):
    global global_identifiers,shu,data_26
    identifier=identifier
    value = value
    if identifier not in global_identifiers:
        global_identifiers.append(identifier)
        now_sl_0 = "7Poly_NEW10"
    if identifier in global_identifiers and int(value) != 0:
            value= int(value)
            data_26 = read_and_repeat_data(now_sl_0, value) 
            print("新轨迹10运动")
            shu = value+shu
            if shu > 41:
                shu = 0
                global_identifiers = []
                print("轨迹超过41条，本条轨迹轨迹作废，请重选轨迹")

def read_and_repeat_data(file_identifier, repeat_times):
                data_folder = "./data/"
                for file_name in os.listdir(data_folder):
                    if file_identifier in file_name and file_name.endswith(".xlsx"):
                        file_path = os.path.join(data_folder, file_name)
                        data = pd.read_excel(file_path, sheet_name="Sheet1", header=0)
                        # 重复数据行
                        repeated_data_0 = pd.concat([data] * repeat_times, ignore_index=True)
                        return repeated_data_0
                        
                return None

def chazhi(q1,q2,number):
        # 如果通过定义点读入
        n = 2  # 控制点的数量
        dim = 1  # 轨迹的维度
        q = np.zeros((n, dim))  # 控制点矩阵
        v = np.zeros_like(q)  # 控制点速度矩阵
        a = np.zeros_like(q)  # 控制点加速度矩阵
        j = np.zeros_like(q)  # 控制点急动度矩阵
        t = np.zeros(n)  # 控制点时间矩阵
        # 设置控制点
        # 关节5
        q[0, 0] ,q[1, 0] = q1,q2
        # 设置控制点速度
        v[0, 0], v[1, 0] = 0, 0
        # 设置控制点加速度
        a[0, 0], a[1, 0] = 0, 0
        # 设置控制点急动度
        j[0, 0], j[1, 0] = 0, 0
        # 设置控制点时间
        t[0], t[1] = 0, 10
        time_step_n = number # 每段多项式的插值数量
        time = np.linspace(t[0], t[-1], (time_step_n * (n - 1) - (n - 2)))#t[0]表示数组t的第一个元素即0，t[-1]表示数组t的最后一个元素即10
        time_step = [[] for _ in range(n-1)]
        traj = [[] for _ in range(n-1)] # 存放每段多项式轨迹的容器
        vel = [[] for _ in range(n-1)]
        acc = [[] for _ in range(n-1)]
        jer = [[] for _ in range(n-1)]

        for i in range(n-1):
            step = np.linspace(0, t[i+1]-t[i], time_step_n)
            for p in range(time_step_n):
                time_step[i].append(step[p])
            for k in range(dim):
                traj[i].append([])
                vel[i].append([])
                acc[i].append([])
                jer[i].append([])

        # 定义多项式系数
        a0 = np.zeros((n-1, dim)) # 每一段、每一个维度
        a1 = np.zeros_like(a0)
        a2 = np.zeros_like(a0)
        a3 = np.zeros_like(a0)
        a4 = np.zeros_like(a0)
        a5 = np.zeros_like(a0)
        a6 = np.zeros_like(a0)
        a7 = np.zeros_like(a0)

        for k in range(dim):
            for i in range(n-1):  # 5个点4个五次多项式
                t_delta = t[i + 1] - t[i]
                h = q[i + 1][k] - q[i][k]
                # 计算各项系数
                a0[i][k] = q[i][k]
                a1[i][k] = v[i][k]
                a2[i][k] = a[i][k] / 2
                a3[i][k] = j[i][k] / 6
                a4[i][k] = 1.0 / (6 * t_delta ** 4) * (210 * h - t_delta * ((30 * a[i][k] - 15 * a[i + 1][k]) * t_delta + (4 * j[i][k] + j[i+1][k]) * t_delta ** 2 + 120 * v[i][k] + 90 * v[i+1][k]))
                a5[i][k] = 1.0 / (2 * t_delta ** 5) * (-168 * h + t_delta * ((20 * a[i][k] - 14 * a[i + 1][k]) * t_delta + (2 * j[i][k] + j[i+1][k]) * t_delta ** 2 + 90 * v[i][k] + 78 * v[i+1][k]))
                a6[i][k] = 1.0 / (6 * t_delta ** 6) * (420 * h - t_delta * ((45 * a[i][k] - 39 * a[i + 1][k]) * t_delta + (4 * j[i][k] + 3 * j[i+1][k]) * t_delta**2 + 216 * v[i][k] + 204 * v[i+1][k]))
                a7[i][k] = 1.0 / (6 * t_delta ** 7) * (-120 * h + t_delta * ((12 * a[i][k] - 12 * a[i + 1][k]) * t_delta + (j[i][k] + j[i+1][k]) * t_delta**2 + 60 * v[i][k] + 60 * v[i+1][k]))

        for i in range(n-1):
            for k in range(dim):
                for p in range(time_step_n):
                    ts = a0[i][k] + a1[i][k] * time_step[i][p] + a2[i][k] * (time_step[i][p] ** 2) + a3[i][k] * (time_step[i][p] ** 3) + a4[i][k] * (time_step[i][p] ** 4) + a5[i][k] * (time_step[i][p] ** 5) + a6[i][k] * (time_step[i][p] ** 6) + a7[i][k] * (time_step[i][p] ** 7)
                    traj[i][k].append(ts)
                    tv = a1[i][k] + 2 * a2[i][k] * time_step[i][p] + 3 * a3[i][k] * (time_step[i][p] ** 2) + 4 * a4[i][k] * (time_step[i][p] ** 3) + 5 * a5[i][k] * (time_step[i][p] ** 4) + 6 * a6[i][k] * (time_step[i][p] ** 5) + 7 * a7[i][k] * (time_step[i][p] ** 6)
                    vel[i][k].append(tv)
                    ta = 2 * a2[i][k] + 2 * 3 * a3[i][k] * time_step[i][p] + 3 * 4 * a4[i][k] * (time_step[i][p] ** 2) + 4 * 5 * a5[i][k] * (time_step[i][p] ** 3) + 5 * 6 * a6[i][k] * (time_step[i][p] ** 4) + 6 * 7 * a7[i][k] * (time_step[i][p] ** 5)
                    acc[i][k].append(ta)
                    tj = 2 * 3 * a3[i][k] + 2 * 3 * 4 * a4[i][k] * time_step[i][p] + 3 * 4 * 5 * a5[i][k] * (time_step[i][p] ** 2) + 4 * 5 * 6 * a6[i][k] * (time_step[i][p] ** 3) + 5 * 6 * 7 * a7[i][k] * (time_step[i][p] ** 4)
                    jer[i][k].append(tj)

        Trajs = [[] for _ in range(dim)]
        Trajv = [[] for _ in range(dim)]
        Traja = [[] for _ in range(dim)]
        Trajj = [[] for _ in range(dim)]

        for i in range(n-1):
            for k in range(dim):
                for p in range(time_step_n-1):
                    Trajs[k].append(traj[i][k][p])
                    Trajv[k].append(vel[i][k][p])
                    Traja[k].append(acc[i][k][p])
                    Trajj[k].append(jer[i][k][p])
        for k in range(dim):
            Trajs[k].append(traj[-1][k][-1])
            Trajv[k].append(vel[-1][k][-1])
            Traja[k].append(acc[-1][k][-1])
            Trajj[k].append(jer[-1][k][-1])

        trajectory = np.zeros((time_step_n * (n - 1) - (n - 2), dim*3 + 1))
        trajectory[:, 0] = time[:]

        for k in range(dim):
            for i in range(time_step_n * (n - 1) - (n - 2)):
                trajectory[i, k + 1] = Trajs[k][i]
                trajectory[i, dim + k + 1] = Trajv[k][i]
                trajectory[i, 2 * dim + k + 1] = Traja[k][i]

    
        if dim == 1: # 针对单维轨迹输出

            data =  trajectory[:, 1]
            data = data.flatten()[:number] 
            data = data.reshape(-1, 1)
            
            return data            

def fifoinsert_ex(concatenated_data,point): 
    global plc
    data = concatenated_data
    # 数据转换为numpy数组
    q1, q2, q3, q4, q5 = [np.array(data.iloc[:, i]) for i in range(5)]
    q3, q5 = -q3, -q5  # 取反，根据原始需求
    q1_in = np.zeros((50, 1), 'float')
    q2_in = np.zeros((50, 1), 'float')
    q3_in = np.zeros((50, 1), 'float')
    q4_in = np.zeros((50, 1), 'float')
    q5_in = np.zeros((50, 1), 'float')

    plc.open()
    # 读取当前PLC位置
    # 读取当前位置
    actpos1 = plc.read_by_name('MAIN.axis1.NcToPlc.ActPos', pyads.PLCTYPE_LREAL)
    actpos2 = plc.read_by_name('MAIN.axis2.NcToPlc.ActPos', pyads.PLCTYPE_LREAL)
    actpos3 = plc.read_by_name('MAIN.axis3.NcToPlc.ActPos', pyads.PLCTYPE_LREAL)
    actpos4 = plc.read_by_name('MAIN.axis4.NcToPlc.ActPos', pyads.PLCTYPE_LREAL)
    actpos5 = plc.read_by_name('MAIN.axis5.NcToPlc.ActPos', pyads.PLCTYPE_LREAL)
    delt1 = q1[0] - actpos1
    delt2 = q2[0] - actpos2
    delt3 = q3[0] - actpos3
    delt4 = q4[0] - actpos4
    delt5 = q5[0] - actpos5
    max_delt = max(abs(delt1),abs(delt2),abs(delt3),abs(delt4),abs(delt5))


    if abs(delt1) > 0.005 or abs(delt2) > 0.005 or abs(delt3) > 0.005 or abs(delt4) > 0.005 or abs(delt5) > 0.005:

        if 0 <abs(max_delt) < 10:
                    q1_in = np.zeros((25, 1), 'float')
                    q2_in = np.zeros((25, 1), 'float')
                    q3_in = np.zeros((25, 1), 'float')
                    q4_in = np.zeros((25, 1), 'float')
                    q5_in = np.zeros((25, 1), 'float')

                    q1_in = chazhi(actpos1,-2,25)
                    q2_in = chazhi(actpos2,0,25)
                    q3_in = chazhi(actpos3,0,25)
                    q4_in = chazhi(actpos4,2,25)
                    q5_in = chazhi(actpos5,0,25)

                
        elif 10 <= abs(max_delt) < 20:
                    q1_in = np.zeros((50, 1), 'float')
                    q2_in = np.zeros((50, 1), 'float')
                    q3_in = np.zeros((50, 1), 'float')
                    q4_in = np.zeros((50, 1), 'float')
                    q5_in = np.zeros((50, 1), 'float')

                    q1_in = chazhi(actpos1,-2,50)
                    q2_in = chazhi(actpos2,0,50)
                    q3_in = chazhi(actpos3,0,50)
                    q4_in = chazhi(actpos4,2,50)
                    q5_in = chazhi(actpos5,0,50)



        elif 20 <= abs(max_delt) < 30:
                    q1_in = np.zeros((75, 1), 'float')
                    q2_in = np.zeros((75, 1), 'float')
                    q3_in = np.zeros((75, 1), 'float')
                    q4_in = np.zeros((75, 1), 'float')
                    q5_in = np.zeros((75, 1), 'float')

                    q1_in = chazhi(actpos1,-2,75)
                    q2_in = chazhi(actpos2,0,75)
                    q3_in = chazhi(actpos3,0,75)
                    q4_in = chazhi(actpos4,2,75)
                    q5_in = chazhi(actpos5,0,75)



        elif 30 <= abs(max_delt) < 40:
                    q1_in = np.zeros((100, 1), 'float')
                    q2_in = np.zeros((100, 1), 'float')
                    q3_in = np.zeros((100, 1), 'float')
                    q4_in = np.zeros((100, 1), 'float')
                    q5_in = np.zeros((100, 1), 'float')

                    q1_in = chazhi(actpos1,-2,100)
                    q2_in = chazhi(actpos2,0,100)
                    q3_in = chazhi(actpos3,0,100)
                    q4_in = chazhi(actpos4,2,100)
                    q5_in = chazhi(actpos5,0,100)   

        else:
                
                    q1_in = np.zeros((125, 1), 'float')
                    q2_in = np.zeros((125, 1), 'float')
                    q3_in = np.zeros((125, 1), 'float')
                    q4_in = np.zeros((125, 1), 'float')
                    q5_in = np.zeros((125, 1), 'float')

                    q1_in = chazhi(actpos1,-2,125)
                    q2_in = chazhi(actpos2,0,125)
                    q3_in = chazhi(actpos3,0,125)
                    q4_in = chazhi(actpos4,2,125)
                    q5_in = chazhi(actpos5,0,125)  
                

        # 插值点写入plc
    if np.all(q1_in==0) and np.all(q2_in==0) and np.all(q3_in==0) and np.all(q4_in==0) and np.all(q5_in==0):
            jogq1_new = q1
            jogq2_new = q2
            jogq3_new = q3
            jogq4_new = q4
            jogq5_new = q5
    else:
            jogq1_new = np.concatenate((q1_in.flatten(), q1))
            jogq2_new = np.concatenate((q2_in.flatten(), q2))
            jogq3_new = np.concatenate((q3_in.flatten(), q3))
            jogq4_new = np.concatenate((q4_in.flatten(), q4))
            jogq5_new = np.concatenate((q5_in.flatten(), q5))
    


    plc.write_by_name('MAIN.jogq1', jogq1_new, pyads.PLCTYPE_ARR_LREAL(len(jogq1_new)))
    plc.write_by_name('MAIN.jogq2', jogq2_new, pyads.PLCTYPE_ARR_LREAL(len(jogq2_new)))
    plc.write_by_name('MAIN.jogq3', jogq3_new, pyads.PLCTYPE_ARR_LREAL(len(jogq3_new)))
    plc.write_by_name('MAIN.jogq4', jogq4_new, pyads.PLCTYPE_ARR_LREAL(len(jogq4_new)))
    plc.write_by_name('MAIN.jogq5', jogq5_new, pyads.PLCTYPE_ARR_LREAL(len(jogq5_new)))
    plc.write_by_name("MAIN.need_in", True, pyads.PLCTYPE_BOOL)
    plc.write_by_name("MAIN.need1_in", True, pyads.PLCTYPE_BOOL)
    plc.write_by_name("MAIN.adsflag", True, pyads.PLCTYPE_BOOL)
    plc.write_by_name("MAIN.new_ov", len(jogq1_new), pyads.PLCTYPE_DINT)

    plc.close()   
            

            #轨迹导入

def fifo_insert():
    global global_identifiers,shu,data_0,data_1,data_2,data_3, data_4,data_5, data_6,data_7,shu1,plc
    plc.open()
    if  shu != 0:
        point = shu
        shu1 = shu
        plc.open()
        safentries= plc.read_by_name('MAIN.axis3.NcToPlc.SafEntries', pyads.PLCTYPE_UDINT)
        if safentries == 0:
            plc.write_by_name('MAIN.dis_do', False, pyads.PLCTYPE_BOOL)
            plc.write_by_name('MAIN.integrate_do', False, pyads.PLCTYPE_BOOL)
            plc.write_by_name('MAIN.integrate_do', True, pyads.PLCTYPE_BOOL)
            time.sleep(0.2)
            plc.write_by_name('MAIN.integrate_do', False, pyads.PLCTYPE_BOOL)
            global_identifier = ["7Poly_O", "7Poly_P","7Poly_Q","7Poly_R", "7Poly_S","7Poly_T", "7Poly_U","7Poly_V"
                                ,"7Poly_B", "7Poly_C","7Poly_D","7Poly_E", "7Poly_G","7Poly_H","7Poly_I", "7Poly_M","7Poly_N","7Poly_NEW1","7Poly_NEW2","7Poly_NEW3","7Poly_NEW4","7Poly_NEW5","7Poly_NEW6",
                                "7Poly_NEW7","7Poly_NEW8","7Poly_NEW9","7Poly_NEW10"]
            data_list = [data_0, data_1,data_2,data_3, data_4,data_5, data_6,data_7,data_8, data_9,data_10,
                        data_11, data_12,data_13,data_14, data_15,data_16,data_17,data_18,data_19,data_20,data_21,
                        data_22,data_23,data_24,data_25,data_26]
            order_mapping = {identifier: data for identifier, data in zip(global_identifier, data_list)}
            # 更新映射关系
            new_order_mapping = {identifier: order_mapping.get(identifier, None) for identifier in global_identifiers}
            new_data_list = [data for data in new_order_mapping.values() if data is not None]
            concatenated_data = pd.concat(new_data_list, ignore_index=True)
            fifoinsert_ex(concatenated_data,point)
            print("轨迹已插入")
            shu = 0 
            global_identifiers = []
#运动
def fifostart(plc):
        plc.open()
        safentries = plc.read_by_name('MAIN.axis3.NcToPlc.SafEntries',pyads.PLCTYPE_DINT)       
        if safentries == 0:
            jogq1_now = plc.read_by_name('MAIN.jogq1',pyads.PLCTYPE_ARR_LREAL(13))
            jogq2_now = plc.read_by_name('MAIN.jogq2',pyads.PLCTYPE_ARR_LREAL(13))
            jogq3_now = plc.read_by_name('MAIN.jogq3',pyads.PLCTYPE_ARR_LREAL(13))
            jogq4_now = plc.read_by_name('MAIN.jogq4',pyads.PLCTYPE_ARR_LREAL(13))
            jogq5_now = plc.read_by_name('MAIN.jogq5',pyads.PLCTYPE_ARR_LREAL(13))
            jogq1_home = plc.read_by_name('MAIN.axis1.NcToPlc.ActPos',pyads.PLCTYPE_LREAL)
            jogq2_home = plc.read_by_name('MAIN.axis2.NcToPlc.ActPos',pyads.PLCTYPE_LREAL)
            jogq3_home = plc.read_by_name('MAIN.axis3.NcToPlc.ActPos',pyads.PLCTYPE_LREAL)
            jogq4_home = plc.read_by_name('MAIN.axis4.NcToPlc.ActPos',pyads.PLCTYPE_LREAL)
            jogq5_home = plc.read_by_name('MAIN.axis5.NcToPlc.ActPos',pyads.PLCTYPE_LREAL)
            a1 = jogq1_now[0]
            b1 = jogq2_now[0]
            c1 = jogq3_now[0]
            d1 = jogq4_now[0]
            e1 = jogq5_now[0]
            a2 = jogq1_home
            b2 = jogq2_home
            c2 = jogq3_home
            d2 = jogq4_home
            e2 = jogq5_home
            f1 =  abs(a2-a1)
            f2 =  abs(b2-b1)
            f3 =  abs(c2-c1)
            f4 =  abs(d2-d1)
            f5 =  abs(e2-e1)

            if f1 <= 0.5 and f2 <= 0.5 and f3 <= 0.5 and f4 <= 0.5 and f5 <= 0.5:                  
                plc.write_by_name('MAIN.fifo_start_do', True, pyads.PLCTYPE_BOOL)
                print("机器人运动")
                time.sleep(0.2)
                plc.write_by_name('MAIN.fifo_start_do', False, pyads.PLCTYPE_BOOL)
            
#回零
def back_to_zero(plc):
    global value_ov,diff1,diff2,diff3,diff4,diff5
    if plc:
        plc.open()
        # bool型
        plc.write_by_name('MAIN.dis_do', False, pyads.PLCTYPE_BOOL)
        plc.write_by_name('MAIN.dis_do', True, pyads.PLCTYPE_BOOL)
        time.sleep(0.2)
        plc.write_by_name('MAIN.dis_do', False, pyads.PLCTYPE_BOOL)
        time.sleep(0.2)
        plc.write_by_name('MAIN.integrate_do', False, pyads.PLCTYPE_BOOL)
        plc.write_by_name('MAIN.integrate_do', True, pyads.PLCTYPE_BOOL)
        time.sleep(0.2)
        plc.write_by_name('MAIN.integrate_do', False, pyads.PLCTYPE_BOOL)
        plc.write_by_name('MAIN.adsflag', True, pyads.PLCTYPE_BOOL)
        plc.write_by_name("MAIN.need_in", True, pyads.PLCTYPE_BOOL)
        plc.close()
        
        # 读取当前位置
        plc.open()
        actpos1 = plc.read_by_name('MAIN.axis1.NcToPlc.ActPos', pyads.PLCTYPE_LREAL)
        actpos2 = plc.read_by_name('MAIN.axis2.NcToPlc.ActPos', pyads.PLCTYPE_LREAL)
        actpos3 = plc.read_by_name('MAIN.axis3.NcToPlc.ActPos', pyads.PLCTYPE_LREAL)
        actpos4 = plc.read_by_name('MAIN.axis4.NcToPlc.ActPos', pyads.PLCTYPE_LREAL)
        actpos5 = plc.read_by_name('MAIN.axis5.NcToPlc.ActPos', pyads.PLCTYPE_LREAL)
        delt1 =  -2- actpos1 
        delt2 =  - actpos2
        delt3 =  - actpos3
        delt4 =  2- actpos4 
        delt5 =  - actpos5
        max_delt = max(abs(delt1),abs(delt2),abs(delt3),abs(delt4),abs(delt5))
                  
        if abs(delt1) > 0.005 or abs(delt2) > 0.005 or abs(delt3) > 0.005 or abs(delt4) > 0.005 or abs(delt5) > 0.005:

            if 0 <abs(max_delt) < 10:
                plc.write_by_name('MAIN.new_ov', 25, pyads.PLCTYPE_UDINT)
                q1_in = np.zeros((25, 1), 'float')
                q2_in = np.zeros((25, 1), 'float')
                q3_in = np.zeros((25, 1), 'float')
                q4_in = np.zeros((25, 1), 'float')
                q5_in = np.zeros((25, 1 ), 'float')

                q1_in = chazhi(actpos1,-2,25) 
                q2_in = chazhi(actpos2,0,25)
                q3_in = chazhi(actpos3,0,25)
                q4_in = chazhi(actpos4,2,25)
                q5_in = chazhi(actpos5,0,25)

                plc.write_by_name('MAIN.jogq1', q1_in, pyads.PLCTYPE_ARR_LREAL(len(q1_in)))
                plc.write_by_name('MAIN.jogq2', q2_in, pyads.PLCTYPE_ARR_LREAL(len(q2_in)))
                plc.write_by_name('MAIN.jogq3', q3_in, pyads.PLCTYPE_ARR_LREAL(len(q3_in)))
                plc.write_by_name('MAIN.jogq4', q4_in, pyads.PLCTYPE_ARR_LREAL(len(q4_in)))
                plc.write_by_name('MAIN.jogq5', q5_in, pyads.PLCTYPE_ARR_LREAL(len(q5_in)))
                plc.write_by_name("MAIN.need_in", True, pyads.PLCTYPE_BOOL)
                plc.write_by_name("MAIN.need1_in", True, pyads.PLCTYPE_BOOL)
            
            elif 10 <= abs(max_delt) < 20:
                plc.write_by_name('MAIN.new_ov', 50, pyads.PLCTYPE_UDINT)
                q1_in = np.zeros((50, 1), 'float')
                q2_in = np.zeros((50, 1), 'float')
                q3_in = np.zeros((50, 1), 'float')
                q4_in = np.zeros((50, 1), 'float')
                q5_in = np.zeros((50, 1), 'float')

                q1_in = chazhi(actpos1,-2,50)
                q2_in = chazhi(actpos2,0,50)
                q3_in = chazhi(actpos3,0,50)
                q4_in = chazhi(actpos4,2,50)
                q5_in = chazhi(actpos5,0,50)

                plc.write_by_name('MAIN.jogq1', q1_in, pyads.PLCTYPE_ARR_LREAL(len(q1_in)))
                plc.write_by_name('MAIN.jogq2', q2_in, pyads.PLCTYPE_ARR_LREAL(len(q2_in)))
                plc.write_by_name('MAIN.jogq3', q3_in, pyads.PLCTYPE_ARR_LREAL(len(q3_in)))
                plc.write_by_name('MAIN.jogq4', q4_in, pyads.PLCTYPE_ARR_LREAL(len(q4_in)))
                plc.write_by_name('MAIN.jogq5', q5_in, pyads.PLCTYPE_ARR_LREAL(len(q5_in)))
                plc.write_by_name("MAIN.need_in", True, pyads.PLCTYPE_BOOL)
                plc.write_by_name("MAIN.need1_in", True, pyads.PLCTYPE_BOOL)
                
            elif 20 <= abs(max_delt) < 30:
                plc.write_by_name('MAIN.new_ov', 75, pyads.PLCTYPE_UDINT)
                q1_in = np.zeros((75, 1), 'float')
                q2_in = np.zeros((75, 1), 'float')
                q3_in = np.zeros((75, 1), 'float')
                q4_in = np.zeros((75, 1), 'float')
                q5_in = np.zeros((75, 1), 'float')

                q1_in = chazhi(actpos1,-2,75)
                q2_in = chazhi(actpos2,0,75)
                q3_in = chazhi(actpos3,0,75)
                q4_in = chazhi(actpos4,2,75)
                q5_in = chazhi(actpos5,0,75)

                plc.write_by_name('MAIN.jogq1', q1_in, pyads.PLCTYPE_ARR_LREAL(len(q1_in)))
                plc.write_by_name('MAIN.jogq2', q2_in, pyads.PLCTYPE_ARR_LREAL(len(q2_in)))
                plc.write_by_name('MAIN.jogq3', q3_in, pyads.PLCTYPE_ARR_LREAL(len(q3_in)))
                plc.write_by_name('MAIN.jogq4', q4_in, pyads.PLCTYPE_ARR_LREAL(len(q4_in)))
                plc.write_by_name('MAIN.jogq5', q5_in, pyads.PLCTYPE_ARR_LREAL(len(q5_in)))
                plc.write_by_name("MAIN.need_in", True, pyads.PLCTYPE_BOOL)
                plc.write_by_name("MAIN.need1_in", True, pyads.PLCTYPE_BOOL)
            
            elif 30 <= abs(max_delt) < 40:
                plc.write_by_name('MAIN.new_ov', 100, pyads.PLCTYPE_UDINT)
                q1_in = np.zeros((100, 1), 'float')
                q2_in = np.zeros((100, 1), 'float')
                q3_in = np.zeros((100, 1), 'float')
                q4_in = np.zeros((100, 1), 'float')
                q5_in = np.zeros((100, 1), 'float')

                q1_in = chazhi(actpos1,-2,100)
                q2_in = chazhi(actpos2,0,100)
                q3_in = chazhi(actpos3,0,100)
                q4_in = chazhi(actpos4,2,100)
                q5_in = chazhi(actpos5,0,100)   

                plc.write_by_name('MAIN.jogq1', q1_in, pyads.PLCTYPE_ARR_LREAL(len(q1_in)))
                plc.write_by_name('MAIN.jogq2', q2_in, pyads.PLCTYPE_ARR_LREAL(len(q2_in)))
                plc.write_by_name('MAIN.jogq3', q3_in, pyads.PLCTYPE_ARR_LREAL(len(q3_in)))
                plc.write_by_name('MAIN.jogq4', q4_in, pyads.PLCTYPE_ARR_LREAL(len(q4_in)))
                plc.write_by_name('MAIN.jogq5', q5_in, pyads.PLCTYPE_ARR_LREAL(len(q5_in)))
                plc.write_by_name("MAIN.need_in", True, pyads.PLCTYPE_BOOL)
                plc.write_by_name("MAIN.need1_in", True, pyads.PLCTYPE_BOOL)
                
            else:
                plc.write_by_name('MAIN.new_ov', 125, pyads.PLCTYPE_UDINT)
                q1_in = np.zeros((125, 1), 'float')
                q2_in = np.zeros((125, 1), 'float')
                q3_in = np.zeros((125, 1), 'float')
                q4_in = np.zeros((125, 1), 'float')
                q5_in = np.zeros((125, 1), 'float')

                q1_in = chazhi(actpos1,-2,125)
                q2_in = chazhi(actpos2,0,125)
                q3_in = chazhi(actpos3,0,125)
                q4_in = chazhi(actpos4,2,125)
                q5_in = chazhi(actpos5,0,125)   

                plc.write_by_name('MAIN.jogq1', q1_in, pyads.PLCTYPE_ARR_LREAL(len(q1_in)))
                plc.write_by_name('MAIN.jogq2', q2_in, pyads.PLCTYPE_ARR_LREAL(len(q2_in)))
                plc.write_by_name('MAIN.jogq3', q3_in, pyads.PLCTYPE_ARR_LREAL(len(q3_in)))
                plc.write_by_name('MAIN.jogq4', q4_in, pyads.PLCTYPE_ARR_LREAL(len(q4_in)))
                plc.write_by_name('MAIN.jogq5', q5_in, pyads.PLCTYPE_ARR_LREAL(len(q5_in)))
                plc.write_by_name("MAIN.need_in", True, pyads.PLCTYPE_BOOL)
                plc.write_by_name("MAIN.need1_in", True, pyads.PLCTYPE_BOOL)
                print("机器人已回零")

def Traject_planning(arry,vel):
    # 如果通过定义点读入
    n = 16  # 控制点的数量
    dim = 1  # 轨迹的维度
    q = np.zeros((n, dim))  # 控制点矩阵
    v = np.zeros_like(q)  # 控制点速度矩阵
    a = np.zeros_like(q)  # 控制点加速度矩阵
    j = np.zeros_like(q)  # 控制点急动度矩阵
    t = np.zeros(n)  # 控制点时间矩阵
    # 设置控制点
   
    # 关节2
    q[0, 0], q[1, 0], q[2, 0], q[3, 0], q[4, 0], q[5, 0], q[6, 0], q[7, 0], q[8, 0], q[9, 0], q[10, 0], q[11, 0], q[12, 0], q[13, 0], q[14, 0], q[15, 0] = arry[0], arry[1], arry[2], arry[3], arry[4], arry[5], arry[6], arry[7], arry[8], arry[9], arry[10], arry[11], arry[12], arry[13], arry[14], arry[15]
    # 设置控制点速度
    v[0, 0], v[1, 0], v[2, 0], v[3, 0], v[4, 0], v[5, 0], v[6, 0], v[7, 0], v[8, 0], v[9, 0], v[10, 0], v[11, 0], v[12, 0], v[13, 0], v[14, 0], v[15, 0] = vel[0], vel[1], vel[2], vel[3], vel[4], vel[5], vel[6], vel[7], vel[8], vel[9], vel[10], vel[11], vel[12], vel[13], vel[14], vel[15]
    # 设置控制点加速度
    a[0, 0], a[1, 0], a[2, 0], a[3, 0], a[4, 0], a[5, 0], a[6, 0], a[7, 0], a[8, 0], a[9, 0], a[10, 0], a[11, 0], a[12, 0], a[13, 0], a[14, 0], a[15, 0] = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    # 设置控制点急动度
    j[0, 0], j[1, 0], j[2, 0], j[3, 0], j[4, 0], j[5, 0], j[6, 0], j[7, 0], j[8, 0], j[9, 0], j[10, 0], j[11, 0], j[12, 0], j[13, 0], j[14, 0], j[15, 0] = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    # 设置控制点时间
    t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9], t[10], t[11], t[12], t[13], t[14], t[15]= 0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45

    time_step_n = 15 # 每段多项式的插值数量
    time = np.linspace(t[0], t[-1], (time_step_n * (n - 1) - (n - 2)))#t[0]表示数组t的第一个元素即0，t[-1]表示数组t的最后一个元素即10
    time_step = [[] for _ in range(n-1)]
    traj = [[] for _ in range(n-1)] # 存放每段多项式轨迹的容器
    vel = [[] for _ in range(n-1)]
    acc = [[] for _ in range(n-1)]
    jer = [[] for _ in range(n-1)]

    for i in range(n-1):
        step = np.linspace(0, t[i+1]-t[i], time_step_n)
        for p in range(time_step_n):
            time_step[i].append(step[p])
        for k in range(dim):
            traj[i].append([])
            vel[i].append([])
            acc[i].append([])
            jer[i].append([])

    # 定义多项式系数
    a0 = np.zeros((n-1, dim)) # 每一段、每一个维度
    a1 = np.zeros_like(a0)
    a2 = np.zeros_like(a0)
    a3 = np.zeros_like(a0)
    a4 = np.zeros_like(a0)
    a5 = np.zeros_like(a0)
    a6 = np.zeros_like(a0)
    a7 = np.zeros_like(a0)

    for k in range(dim):
        for i in range(n-1):  # 5个点4个五次多项式
            t_delta = t[i + 1] - t[i]
            h = q[i + 1][k] - q[i][k]
            # 计算各项系数
            a0[i][k] = q[i][k]
            a1[i][k] = v[i][k]
            a2[i][k] = a[i][k] / 2
            a3[i][k] = j[i][k] / 6
            a4[i][k] = 1.0 / (6 * t_delta ** 4) * (210 * h - t_delta * ((30 * a[i][k] - 15 * a[i + 1][k]) * t_delta + (4 * j[i][k] + j[i+1][k]) * t_delta ** 2 + 120 * v[i][k] + 90 * v[i+1][k]))
            a5[i][k] = 1.0 / (2 * t_delta ** 5) * (-168 * h + t_delta * ((20 * a[i][k] - 14 * a[i + 1][k]) * t_delta + (2 * j[i][k] + j[i+1][k]) * t_delta ** 2 + 90 * v[i][k] + 78 * v[i+1][k]))
            a6[i][k] = 1.0 / (6 * t_delta ** 6) * (420 * h - t_delta * ((45 * a[i][k] - 39 * a[i + 1][k]) * t_delta + (4 * j[i][k] + 3 * j[i+1][k]) * t_delta**2 + 216 * v[i][k] + 204 * v[i+1][k]))
            a7[i][k] = 1.0 / (6 * t_delta ** 7) * (-120 * h + t_delta * ((12 * a[i][k] - 12 * a[i + 1][k]) * t_delta + (j[i][k] + j[i+1][k]) * t_delta**2 + 60 * v[i][k] + 60 * v[i+1][k]))

    for i in range(n-1):
        for k in range(dim):
            for p in range(time_step_n):
                ts = a0[i][k] + a1[i][k] * time_step[i][p] + a2[i][k] * (time_step[i][p] ** 2) + a3[i][k] * (time_step[i][p] ** 3) + a4[i][k] * (time_step[i][p] ** 4) + a5[i][k] * (time_step[i][p] ** 5) + a6[i][k] * (time_step[i][p] ** 6) + a7[i][k] * (time_step[i][p] ** 7)
                traj[i][k].append(ts)
                tv = a1[i][k] + 2 * a2[i][k] * time_step[i][p] + 3 * a3[i][k] * (time_step[i][p] ** 2) + 4 * a4[i][k] * (time_step[i][p] ** 3) + 5 * a5[i][k] * (time_step[i][p] ** 4) + 6 * a6[i][k] * (time_step[i][p] ** 5) + 7 * a7[i][k] * (time_step[i][p] ** 6)
                vel[i][k].append(tv)
                ta = 2 * a2[i][k] + 2 * 3 * a3[i][k] * time_step[i][p] + 3 * 4 * a4[i][k] * (time_step[i][p] ** 2) + 4 * 5 * a5[i][k] * (time_step[i][p] ** 3) + 5 * 6 * a6[i][k] * (time_step[i][p] ** 4) + 6 * 7 * a7[i][k] * (time_step[i][p] ** 5)
                acc[i][k].append(ta)
                tj = 2 * 3 * a3[i][k] + 2 * 3 * 4 * a4[i][k] * time_step[i][p] + 3 * 4 * 5 * a5[i][k] * (time_step[i][p] ** 2) + 4 * 5 * 6 * a6[i][k] * (time_step[i][p] ** 3) + 5 * 6 * 7 * a7[i][k] * (time_step[i][p] ** 4)
                jer[i][k].append(tj)

    Trajs = [[] for _ in range(dim)]
    Trajv = [[] for _ in range(dim)]
    Traja = [[] for _ in range(dim)]
    Trajj = [[] for _ in range(dim)]

    for i in range(n-1):
        for k in range(dim):
            for p in range(time_step_n-1):
                Trajs[k].append(traj[i][k][p])
                Trajv[k].append(vel[i][k][p])
                Traja[k].append(acc[i][k][p])
                Trajj[k].append(jer[i][k][p])
    for k in range(dim):
        Trajs[k].append(traj[-1][k][-1])
        Trajv[k].append(vel[-1][k][-1])
        Traja[k].append(acc[-1][k][-1])
        Trajj[k].append(jer[-1][k][-1])

    trajectory = np.zeros((time_step_n * (n - 1) - (n - 2), dim*3 + 1))
    trajectory[:, 0] = time[:]

    for k in range(dim):
        for i in range(time_step_n * (n - 1) - (n - 2)):
            trajectory[i, k + 1] = Trajs[k][i]
            trajectory[i, dim + k + 1] = Trajv[k][i]
            trajectory[i, 2 * dim + k + 1] = Traja[k][i]

    # 输出图像
    if dim == 1: # 针对单维轨迹输出

        data = {
            '位移 q2/°': trajectory[:, 1]
        }
        df = pd.DataFrame(data)
        print("轨迹生成成功")
        return data
        
# arr=[0,-4,-8,-8,-8,-8,-8,-8,-8,-8,-8,-8,-8,-8,-4,0]
# vel=[0, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0]
# data=Traject_planning(arr,vel)
# df = pd.DataFrame(data)
# df.to_excel(r'D:/7Poly_NEW1_2.xlsx', index=False)