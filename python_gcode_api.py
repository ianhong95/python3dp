import serial
import logging
import time
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(filename="api_logs.log", level=logging.INFO)

'''
Python API for controlling 3D printers.
Compatible with any printer that uses Marlin-based firmware.
'''

class Printer:
    def __init__(self, serial_port):

        # Constants
        self.SERIAL_PORT = serial_port  # example: /dev/ttyACM0
        self.BAUDRATE = 115200
        self.TIMEOUT = 3
        self.REL_POS_GCODE = "G91"
        self.DELAY = 0.1

        self.conn = None    # serial connection
        self.ok = None

        # Attempt to connect to the device upon object initialization
        self.connect()
        

    def connect(self):
        print(f"Connecting to {self.SERIAL_PORT}")
        try:
            self.conn = serial.Serial(self.SERIAL_PORT, self.BAUDRATE)
            time.sleep(2)
        except Exception as e:
            print("Could not connect")
            logger.log(0, "Could not connect to serial device.")
            exit()

        if self.conn:
            logger.log(0, f"Successfully connected to serial device {self.SERIAL_PORT}!")
            print("Connection successful!")


    '''
    READ COMMANDS
    '''
    def getPrinterInfo(self):
        '''
        Send M115 to read the printer's information.
            - Firmware name and version
            - Source code URL
            - Prototcol version
            - Machine type
            - Extruder count
            - UUID
        '''
        response = None
        self.write("M115")

        while response==None:
            if self.conn.in_waiting:
                response = self.conn.readline().decode("utf-8")
                print(f"> {response}")
            else:
                time.sleep(0.1)

        return response
    

    def check_ok(self):
        ok_response = False
        response = None

        while ok_response==False:
            if self.conn.in_waiting:
                response = self.conn.readline().decode("utf-8")
                print(f"response: {response}")
                if "ok" in response:
                    print("Command complete")
                    ok_response = True
                    self.ok = ok_response
                else:
                    pass
    

    '''
    MANUAL COMMANDS
        - G21 ; set units to mm
        - G28 ; auto home
        - G90 ; use absolute coordinates

        - M17 ; enable steppers
        - M18 ; disable steppers
        - M84 ; disable steppers with optional timeout and motor selection
    '''
    def disable_all(self):
        self.write("M84")
        self.check_ok()


    '''
    HOMING COMMANDS
    '''
    def homeX(self):
        pass


    def homeY(self):
        pass


    def homeZ(self):
        pass


    def homeXYZ(self):
        self.write("G28")
        self.disable_all()
        self.check_ok()


        time.sleep(self.DELAY)

    def homeXY(self):
        pass


    '''
    LINEAR MOVE COMMANDS
    '''
    def relMoveX(self, steps, speed=500):

        move_gcode = f"G0 X{steps} F{speed}"
        self.write(self.REL_POS_GCODE)
        self.write(move_gcode)
        # self.disable_all()
        self.check_ok()


        time.sleep(self.DELAY)


    def relMoveY(self, steps, speed=500):

        move_gcode = f"G0 Y{steps} F{speed}"
        self.write(self.REL_POS_GCODE)
        self.write(move_gcode)
        # self.disable_all()
        self.check_ok()


        time.sleep(self.DELAY)


    def relMoveZ(self, steps, speed=500):

        move_gcode = f"G0 Z{steps} F{speed}"
        self.write(self.REL_POS_GCODE)
        self.write(move_gcode)
        # self.disable_all()
        self.check_ok()


        time.sleep(self.DELAY)


    '''
    NONLINEAR MOVE COMMANDS
    '''
    def relMoveCircle(self, radius, speed):
        move_gcode = f"G2 I{radius} J{radius} F{speed}"
        self.write(self.REL_POS_GCODE)
        self.write(move_gcode)
        # self.disable_all()
        self.check_ok()


        time.sleep(self.DELAY)


    '''
    UTILITY FUNCTIONS
    '''
    def write(self, gcode):
        gcode += "\n"
        gcode_to_bytes = gcode.encode("utf-8")
        print(f"Writing gcode {gcode_to_bytes}")
        self.conn.write(gcode_to_bytes)
        self.conn.write(b'M84\n')

        self.check_ok()


    # if __name__=="__main__":
    #     print("test")