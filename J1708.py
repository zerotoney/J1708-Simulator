import tkinter as tk
import serial  # import the module
import time
import sys, select
import threading

Computer_COM_PortName = "COM3"


MAX_RoadSpeed = 205
MAX_ExhaustBackPressure = 441
MAX_EngineOilPressure = 879
MAX_EngineSpeed = 16383
MAX_InjectionControlPressure = 256

RoadSpeed = 0.0
ExhaustBackPressure = 0.0
EngineOilPressure = 0.0
EngineSpeed = 0.0
InjectionControlPressure = 0.0
############################### Simple Window ######################################

def GetRoadSpeed(v):
    global RoadSpeed
    RoadSpeed = float(v)

def GetExhaustBackPressure(v):
    global ExhaustBackPressure
    ExhaustBackPressure = float(v)

def GetEngineOilPressure(v):
    global EngineOilPressure
    EngineOilPressure = float(v)

def GetEngineSpeed(v):
    global EngineSpeed
    EngineSpeed = float(v)

def GetInjectionControlPressure (v):
    global InjectionControlPressure
    InjectionControlPressure = float(v)


window = tk.Tk()
# 设置窗口大小
winWidth = 800
winHeight = 600
# 获取屏幕分辨率
screenWidth = window.winfo_screenwidth()
screenHeight = window.winfo_screenheight()
 
x = int((screenWidth - winWidth) / 2)
y = int((screenHeight - winHeight) / 2)
 
# 设置主窗口标题
window.title("Scale参数说明")
# 设置窗口初始位置在屏幕居中
window.geometry("%sx%s+%s+%s" % (winWidth, winHeight, x, y))
# 设置窗口宽高固定
window.resizable(0, 0)
 
"""scale参数.
 
        Valid resource names: activebackground, background, bigincrement, bd,
        bg, borderwidth, command, cursor, digits, fg, font, foreground, from,
        highlightbackground, highlightcolor, highlightthickness, label,
        length, orient, relief, repeatdelay, repeatinterval, resolution,
        showvalue, sliderlength, sliderrelief, state, takefocus,
        tickinterval, to, troughcolor, variable, width."""

# 创建一个1到100的滑块， 精度为0.01， 显示的最大位数为8
scale_RoadSpeed = tk.Scale(window, label="RoadSpeed", length = 400, from_=0, to = MAX_RoadSpeed, bg="#bbb", fg = "#f00", orient = tk.HORIZONTAL, command=GetRoadSpeed, resolution=0.01, digits = 8)
scale_RoadSpeed.pack()

scale_ExhaustBackPressure = tk.Scale(window, label="Exhaust Back Pressure", length = 400, from_=0, to = MAX_ExhaustBackPressure, bg="#bbb", fg = "#f00", orient = tk.HORIZONTAL, command=GetExhaustBackPressure, resolution=0.01, digits = 8)
scale_ExhaustBackPressure.pack()
 
scale_EngineOilPressure = tk.Scale(window, label="Engine Oil Pressure", length = 400, from_=0, to = MAX_EngineOilPressure, bg="#bbb", fg = "#f00", orient = tk.HORIZONTAL, command=GetEngineOilPressure, resolution=0.01, digits = 8)
scale_EngineOilPressure.pack()

scale_EngineSpeed = tk.Scale(window, label="Engine Speed", length = 400, from_=0, to = MAX_EngineSpeed, bg="#bbb", fg = "#f00", orient = tk.HORIZONTAL, command=GetEngineSpeed, resolution=0.01, digits = 8)
scale_EngineSpeed.pack()

scale_InjectionControlPressure = tk.Scale(window, label="Injection Control Pressure", length = 400, from_=0, to = MAX_InjectionControlPressure, bg="#bbb", fg = "#f00", orient = tk.HORIZONTAL, command=GetInjectionControlPressure, resolution=0.01, digits = 8)
scale_InjectionControlPressure.pack()

text_info=tk.Text(x=10, width=400, height=200)
text_info.pack()






############################### J1708 Simulate ######################################

J1708_PID_84_VEHICLE_SPEED = 84
J1708_PID_89_PTO_STATUS = 89
J1708_PID_100_OIL_PRESSURE = 100
J1708_PID_110_COOLANT_TEMPERATURE = 110
J1708_PID_190_ENGINE_RPM = 190
J1708_PID_175_ENGINE_OIL_TEMPERATURE = 175
J1708_PID_182_FUEL_CONSUMPTION = 182

J1708_REQUEST_ONLY_PID_237_VIN = 237
J1708_REQUEST_ONLY_PID_246_VEHICLE_HOURS = 246
J1708_REQUEST_ONLY_PID_247_ENGINE_HOURS = 247


VEHICLE_SPEED_SCALE = 0.805
OIL_PRESSURE_SCALE = 3.45
TEMP_SCALE = 1.8
TEMP_OFFSET = 32.0
RPM_SCALE = 0.25
ENGINE_HOURS_SCALE = 0.05
FUEL_CONSUMP_SCALE = 0.473


MID_RoadSpeed = 144
PID_RoadSpeed = 84
Length_RoadSpeed = 1

MID_ExhaustBackPressure = 128
PID_ExhaustBackPressure = 131
Length_ExhaustBackPressure = 2

MID_EngineOilPressure = 128
PID_EngineOilPressure = 100
Length_EngineOilPressure = 1

MID_EngineSpeed = 128
PID_EngineSpeed = 190
Length_EngineSpeed = 2

MID_InjectionControlPressure = 128
PID_InjectionControlPressure = 164
Length_InjectionControlPressure = 2


MID_DUMMY = 0xff
PID_DUMMY = 0Xff
Length_DUMMY = 2
DATA_DUMMY = 0Xffff


MID = 128
BUS_CHASSIS_MID = 210
RPM_PID = 190
VIN_PID = 237
ENGINE_HOURS_PID = 247
COOLANT_PID = 110
FUEL_ECO_PID = 184
engine_speed : int = (600/RPM_SCALE)  # 190, 2 bytes, x 0.25
coolant_temperature = 50.0  # 110, 1 byte, x 1
fuel_eco = 1.0  # 184, 2 bytes  , x 0.0016672
simulated_vin: bytearray = bytearray(b"Vin_from_Rs485")
vin_message : bytearray = bytearray([BUS_CHASSIS_MID, VIN_PID, 0x00]) + bytearray(b"Vin_from_Rs485") + bytearray([0])
engine_hours_message = bytearray([MID, ENGINE_HOURS_PID, 4, 0, 0, 0, 0, 0])
rpm_message = bytearray([MID, RPM_PID, 0, 0, 0])
speed_message = bytearray([MID, J1708_PID_84_VEHICLE_SPEED, 0, 0])
engine_hours : int = int(10000.0 / ENGINE_HOURS_SCALE)
exit_console = False
vehicle_speed :int = int(115.00 / VEHICLE_SPEED_SCALE)

hb_start : bool = False




def calculate_checksum(frame_data: bytearray) -> int:
    checksum = 0
    for x in range(len(frame_data) - 1):
        checksum += frame_data[x]
    checksum &= 255
    checksum = 256 - checksum
    return checksum

def wait_read(comport: serial.Serial) -> bytearray:
    global engine_hours
    comport.setRTS(1)  # RTS=1,~RTS=0 so ~RE=0,Receive mode enabled for MAX485
    comport.setDTR(1)  # DTR=1,~DTR=0 so  DE=0,(In FT232 RTS and DTR pins are inverted)
    # ~RE and DE LED's on USB2SERIAL board will be off
    # print('\n    DTR = 1,~DTR = 0 so  DE = 0')
    # print('    RTS = 1,~RTS = 0 so ~RE = 0,Receive mode enabled for MAX485')
    RxedData: bytearray = bytearray()
    comport.timeout = 0.100
    previous_length: int = 0
    while True:
        RxedData.extend(comport.read(1))
        if len(RxedData) > 0:
            if previous_length != len(RxedData):
                previous_length = len(RxedData)
            else:
                text_info.insert("end","\n--- Looks bus is idle");text_info.see("end")
                break
        else:
            break

    if len(RxedData) >= 3:
        text_info.insert("end","\nReceived J1708 Frame: " + "".join(format(x, "02x") for x in RxedData) + " <<")
        if RxedData[1] == 0x00:
            if RxedData[2] == 0xED:
                text_info.insert("end","\nsending VIN reponse");text_info.see("end")
                vin_message[2] = len(simulated_vin)
                vin_message[17] = 0x00
                msgchecksum = calculate_checksum(vin_message) & 0xFF
                vin_message[17] = msgchecksum
                return vin_message
            elif RxedData[2] == 0xF7:
                text_info.insert("end","\nsending Engine Hours reponse");text_info.see("end")
                engine_hours_message[7] = 0x00
                engine_hours_message[3] = engine_hours & 0xFF
                engine_hours_message[4] = (engine_hours >> 8) & 0xFF
                engine_hours_message[5] = (engine_hours >> 16) & 0xFF
                engine_hours_message[6] = (engine_hours >> 24) & 0xFF
                msgchecksum = calculate_checksum(engine_hours_message) & 0xFF
                engine_hours_message[7] = msgchecksum
                engine_hours += 1
                return engine_hours_message
    else:
        return None

def COM_Send_Message(COM_Port, MID, PID, Data, DataLength):
    if DataLength == 2:
        message = bytearray([MID, PID, 0, 0, 0])
        message[2] = int(Data) & 0xFF
        message[3] = (int(Data) >> 8) & 0xFF
        calculated_checksum = calculate_checksum(message)
        message[4] = calculated_checksum & 0xFF
    else:
        message = bytearray([MID, PID, 0, 0])
        message[2] = int(Data) & 0xFF
        calculated_checksum = calculate_checksum(message)
        message[3] = calculated_checksum & 0xFF

    NoOfBytes = COM_Port.write(message)  # Write data to serial port
    text_info.insert("end","\nJ1708 Broadcast Frame: " + "".join(format(x, "02x") for x in message) + "(" + str(NoOfBytes) + ")");text_info.see("end")

class J1708_Simulate(threading.Thread):
    def run(self):
        COM_PortName = Computer_COM_PortName
        COM_Port = serial.Serial(COM_PortName)  # open the COM port
        text_info.insert("end",COM_PortName + "Opened");text_info.see("end")
        #print("\n   ", COM_PortName, "Opened")

        COM_Port.baudrate = 9600  # set Baud rate
        COM_Port.bytesize = 8  # Number of data bits = 8
        COM_Port.parity = "N"  # No parity
        COM_Port.stopbits = 1  # Number of Stop bits = 1

        text_info.insert("end","\nBaud rate = " + str(COM_Port.baudrate));text_info.see("end")
        text_info.insert("end","\nData bits = " + str(COM_Port.bytesize));text_info.see("end")
        text_info.insert("end","\nParity    = " + str(COM_Port.parity));text_info.see("end")
        text_info.insert("end","\nStop bits = " + str(COM_Port.stopbits));text_info.see("end")
        text_info.insert("end","\nStarting J1708 Bus")

        text_info.insert("end","\nRoadSpeed = ", str(RoadSpeed));text_info.see("end")
        text_info.insert("end","\nRoadSpeed = ", str(engine_speed));text_info.see("end")

        try:
            hundred_msec_count = 0 
            loop_count: int = 0

            while not exit_console:
                # Controlling DTR and RTS pins to put USB2SERIAL in transmit mode
                text_info.insert("end","\nwaiting for bus idle.....")

                response_to_request = wait_read(COM_Port)

                # Write to the bus.
                COM_Port.setDTR(0)  # DTR=0,~DTR=1 so DE = 1,Transmit mode enabled
                COM_Port.setRTS(0)  # RTS=0,~RTS=1 (In FT232 RTS and DTR pins are inverted)            

                if response_to_request is not None:
                    NoOfBytes = COM_Port.write(response_to_request)
                    text_info.insert("end","Sent J1708 Response: " + "".join(format(x, "02x") for x in response_to_request) + "(" + str(NoOfBytes) + ")");text_info.see("end")
                else:
                    if loop_count == 0: # Road Speed
                        text_info.insert("end","\n\n0.RoadSpeed : " + "(" + str(RoadSpeed) + ")");text_info.see("end")
                        COM_Send_Message(COM_Port, MID_RoadSpeed, PID_RoadSpeed, int(RoadSpeed*0xFF/MAX_RoadSpeed), Length_RoadSpeed)
                    elif loop_count == 1: # ExhaustBackPressure
                        text_info.insert("end","\n\n1.ExhaustBackPressure : " + "(" + str(ExhaustBackPressure) + ")");text_info.see("end")
                        COM_Send_Message(COM_Port, MID_ExhaustBackPressure, PID_ExhaustBackPressure, int(ExhaustBackPressure*0xFFFF/MAX_ExhaustBackPressure), Length_ExhaustBackPressure)
                    elif loop_count == 2: # EngineOilPressure
                        text_info.insert("end","\n\n2.EngineOilPressure : " + "(" + str(EngineOilPressure) + ")");text_info.see("end")
                        COM_Send_Message(COM_Port, MID_EngineOilPressure, PID_EngineOilPressure, int(EngineOilPressure*0xFF/MAX_EngineOilPressure), Length_EngineOilPressure)
                    elif loop_count == 3: # EngineSpeed
                        text_info.insert("end","\n\n3.EngineSpeed : " + "(" + str(EngineSpeed) + ")");text_info.see("end")
                        COM_Send_Message(COM_Port, MID_EngineSpeed, PID_EngineSpeed, int(EngineSpeed*0xFFFF/MAX_EngineSpeed), Length_EngineSpeed)
                    elif loop_count == 4:
                        text_info.insert("end","\n\n4.InjectionControlPressure : " + "(" + str(InjectionControlPressure) + ")");text_info.see("end")
                        COM_Send_Message(COM_Port, MID_InjectionControlPressure, PID_InjectionControlPressure, int(InjectionControlPressure*0xFFFF/MAX_InjectionControlPressure), Length_InjectionControlPressure)
                    elif loop_count == 5:
                        text_info.insert("end","\n\n5.DUMMYDATA : " + "(" + str(DATA_DUMMY) + ")");text_info.see("end")
                        COM_Send_Message(COM_Port, MID_DUMMY, PID_DUMMY, DATA_DUMMY, Length_DUMMY)


                    time.sleep(0.25)
                    
                    if loop_count == 5:
                        loop_count = 0
                    else:
                        loop_count += 1
                    #time.sleep(1)

        finally:
            text_info.insert("end","\nTest finished ");text_info.see("end")


################### Start Thread #################
simulator = J1708_Simulate()
simulator.setDaemon(True) 
simulator.start()



window.mainloop()
