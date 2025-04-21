import serial
import logging
import time
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(filename="api_logs.log", level=logging.INFO)

'''
Python API for controlling 3D printers via serial connection.
Compatible with any printer that uses Marlin-based firmware. This firmware only supports sequential commands, so there's no live control or feedback.
'''

class Printer:
    def __init__(self, serial_port):

        # Constants
        self.SERIAL_PORT = serial_port  # example: /dev/ttyACM0
        self.BAUDRATE = 115200
        self.TIMEOUT = 5
        self.ABS_POS_GCODE = "G90"
        self.REL_POS_GCODE = "G91"
        self.DELAY = 0.1

        # Initialize some variables
        self.conn = None    # serial connection
        self.ok = None

        # Initialize queues
        self.cmd_queue = []

        # Attempt to connect to the device upon object initialization
        connected = self.connect()

        # On successful connection, print printer information
        if connected:
            self.PRINTER_INFO = self.getPrinterInfo()
        

    def connect(self):
        print(f"Connecting to {self.SERIAL_PORT}")
        try:
            self.conn = serial.Serial(self.SERIAL_PORT, self.BAUDRATE, self.TIMEOUT)
            time.sleep(2)
        except Exception as e:
            print("Could not connect")
            logger.log(20, "Could not connect to serial device.")
            exit()

        if self.conn:
            logger.log(20, f"Successfully connected to serial device {self.SERIAL_PORT}!")
            print("Connection successful!")

        return True


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
                logger.log(20, f"{response}!")
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
        logger.log(20, f"Disabling all steppers")
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
        logger.log(20, f"Auto-homing with G28")
        self.write("G28")
        self.disable_all()
        self.check_ok()

        time.sleep(self.DELAY)

    def homeXY(self):
        pass


    '''
    LINEAR MOVE COMMANDS
    '''
    def relMoveX(self, dist, speed=500):
        logger.log(20, f"Linear relative X move, dist {dist}, speed {speed}")

        move_gcode = f"G0 X{dist} F{speed}"
        self.write(self.REL_POS_GCODE)
        self.write(move_gcode)
        # self.disable_all()
        self.check_ok()

        time.sleep(self.DELAY)

        return self


    def relMoveY(self, dist, speed=500):
        logger.log(20, f"Linear relative Y move, dist {dist}, speed {speed}")
        move_gcode = f"G0 Y{dist} F{speed}"
        self.write(self.REL_POS_GCODE)
        self.write(move_gcode)
        # self.disable_all()
        self.check_ok()

        time.sleep(self.DELAY)

        return self


    def relMoveZ(self, dist, speed=500):
        logger.log(20, f"Linear relative Z move, dist {dist}, speed {speed}")
        move_gcode = f"G0 Z{dist} F{speed}"
        self.write(self.REL_POS_GCODE)
        self.write(move_gcode)
        # self.disable_all()
        self.check_ok()

        time.sleep(self.DELAY)

        return self
    

    def relMoveXYZ(self, coords: list, dist, speed=500):
        pass


    '''
    NONLINEAR MOVE COMMANDS
    '''
    def relMoveCircle(self, radius, speed):
        logger.log(20, f"Full circle move, radius {radius}, speed {speed}")
        move_gcode = f"G2 I{radius} J{radius} F{speed}"
        self.write(self.REL_POS_GCODE)
        self.write(move_gcode)
        self.check_ok()

        time.sleep(self.DELAY)

        return self


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