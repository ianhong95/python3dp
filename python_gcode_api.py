'''
Python API for controlling 3D printers via serial connection.
Compatible with any printer that uses Marlin-based firmware. This firmware only supports sequential commands, so there's no live control or feedback.

Motion commands can be chained such as Printer.moveX(5).moveY(5).moveZ(5)

In an attempt to optimize the flow of commands, separate methods are used for various options. Shorter commands allow for a larger batch of commands
to be sent in a single buffer. Reducing the amount of argument parsing and loops will generate the batches quicker. These optimizations come at the
expense of a slightly more cumbersome library.
'''

import serial
import logging
import time
import json


logger = logging.getLogger(__name__)
logging.basicConfig(filename="api_logs.log", level=logging.INFO)

DEFAULT_SPEED = 5000

class Printer:
    def __init__(self, serial_port):
        with open("config.json", "r") as config_file:
            config = json.load(config_file)

        # Constants
        self.SERIAL_PORT = serial_port  # example: /dev/ttyACM0
        self.BAUDRATE = config["serial_settings"]["baudrate"]
        self.TIMEOUT = config["serial_settings"]["timeout"]

        self.DELAY = config["run_params"]["delay"]
        self.STEPS = config["run_params"]["steps"]
        self.RESOLUTION = config["run_params"]["resolution"]
        self.BATCH_SIZE = config["run_params"]["batch_size"]

        self.GCODE = config["gcode"]    # Store the whole dictionary in this property

        # Define printer parameters
        self.DIMS = {
            "LENGTH": 200,
            "WIDTH": 220,
            "HEIGHT": 200
        }

        config_file.close()     # Close the config file after reading from it

        # Initialize some variables
        self.conn = None    # serial connection
        self.ok = None

        # Attempt to connect to the device upon object initialization
        connected = self.connect()

        # On successful connection, print machine information and initialize some parameters
        if connected:
            self.PRINTER_INFO = self.getPrinterInfo()

            # Set parameters
            self.speed= DEFAULT_SPEED  # Mutable speed value
            self._write(self.GCODE["SET_ABS"])
            self._write(f"G0 F{DEFAULT_SPEED}")

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
    
    This set of methods is used to get feedback from the printer, such as the device information and responses after executing gcode.
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

        self._write("M115")

        while response==None:
            if self.conn.in_waiting:
                response = self.conn.readline().decode("utf-8")
                logger.log(20, f"{response}!")
                print(f"> {response}")
            else:
                time.sleep(0.1)

        return response
    

    def checkOk(self):
        '''
        WIP. This method will be used to verify that gcode has been executed successfully before proceeding.
        '''

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
    

    def getCurrentPos(self):
        pass

    '''
    MANUAL COMMANDS
    '''
    def enableMotors(self, motors="XYZ"):
        '''Enables specified motors. If no arguments are passed, all motors will be enabled.'''
        gcode = f"{self.GCODE['ENABLE_MOTORS']}"

        for m in motors:
            gcode += f" {m}"

        self._write(gcode)

        logger.log(20, f"Enabling motors {motors}")

    
    def disableMotors(self, motors="XYZ"):
        '''Disables specified motors. If no arguments are passed, all motors will be disabled.'''
        gcode = f"{self.GCODE['DISABLE_MOTORS']}"

        for m in motors:
            gcode += f" {m}"

        self._write(gcode)

        logger.log(20, f"Disabling motors {motors}")


    '''
    HOMING COMMANDS
    '''
    def home(self, axes="XYZ"):
        '''
        Homes specified axes. Pass a string with up to 3 axes Passing no arguments will home all axes by default.
        '''
        match axes:
            case "X":
                self._write(f"{self.GCODE['AUTO_HOME']} X")
            case "Y":
                self._write(f"{self.GCODE['AUTO_HOME']} Y")
            case "Z":
                self._write(f"{self.GCODE['AUTO_HOME']} Z")
            case "XY" | "YX":
                self._write(f"{self.GCODE['AUTO_HOME']} X Y")
            case "XZ" | "ZX":
                self._write(f"{self.GCODE['AUTO_HOME']} X Z")
            case "YZ" | "ZY":
                self._write(f"{self.GCODE['AUTO_HOME']} Y Z")
            case "XYZ":
                self._write(f"{self.GCODE['AUTO_HOME']} X Y Z")
            case _:
                print("Invalid auto-home command.")
                exit()

        time.sleep(self.DELAY)

        logger.log(20, f"Homing axis/axes {axes}.")
        
        return self


    '''
    BASIC LINEAR MOVE COMMANDS

    To reduce computations due to argument parsing at each step, a separate move method is created for each possible direction.
    
    These commands can be chained. For example: Printer.moveX(50).moveY(50).moveXY([50,50])
    '''

    def moveX(self, dist: float):
        '''Linear move in the X direction.'''
        self._write(f"G0 X{dist}")
        time.sleep(self.DELAY)

        return self
    
    
    def moveY(self, dist: float):
        '''Linear move in the Y direction.'''
        self._write(f"G0 Y{dist}")
        time.sleep(self.DELAY)

        return self
    
    
    def moveZ(self, dist: float):
        '''Linear move in the Z direction.'''
        self._write(f"G0 Z{dist}")
        time.sleep(self.DELAY)

        return self
    

    def moveXY(self, dist: tuple):
        '''Linear move diagonally in the XY direction. Pass a tuple of distances in the order (X,Y).'''
        self._write(f"G0 X{dist[0]} Y{dist[1]}")
        time.sleep(self.DELAY)

        return self
    

    def moveXZ(self, dist: tuple):
        '''Linear move diagonally in the XZ direction. Pass a tuple of distances in the order (X,Z).'''
        self._write(f"G0 X{dist[0]} Z{dist[1]}")
        time.sleep(self.DELAY)

        return self
    

    def moveYZ(self, dist: tuple):
        '''Linear move diagonally in the YZ direction. Pass a tuple of distances in the order (Y,Z).'''
        self._write(f"G0 Y{dist[0]} Z{dist[1]}")
        time.sleep(self.DELAY)

        return self
    

    def move(self, dist: tuple):
        '''General linear move command. Pass a tuple of distances in the order (X,Y,Z).'''
        self._write(f"G0 X{dist[0]} Y{dist[1]} Z{dist[2]}")
        time.sleep(self.DELAY)

        return self
    

    '''
    BASIC LINEAR MOVE COMMANDS WITH SPEED PARAMETER
    '''

    def moveSpeedX(self, dist: float, speed: int):
        '''Linear move in the X direction with a speed parameter.'''
        self._write(f"G0 X{dist} F{speed}")
        time.sleep(self.DELAY)

        return self
    

    def moveSpeedY(self, dist: float, speed: int):
        '''Linear move in the Y direction with a speed parameter.'''
        self._write(f"G0 Y{dist} F{speed}")
        time.sleep(self.DELAY)

        return self
    

    def moveSpeedZ(self, dist: float, speed: int):
        '''Linear move in the Z direction with a speed parameter.'''
        self._write(f"G0 Z{dist} F{speed}")
        time.sleep(self.DELAY)

        return self
    

    def moveSpeedXY(self, dist: tuple, speed: int):
        '''Linear move in the XY direction with a speed parameter. Pass a tuple of distances in the order (X,Y).'''
        self._write(f"G0 X{dist} Y{dist} F{speed}")
        time.sleep(self.DELAY)

        return self
    

    def moveSpeedXZ(self, dist: tuple, speed: int):
        '''Linear move in the XZ direction with a speed parameter. Pass a tuple of distances in the order (X,Z).'''
        self._write(f"G0 X{dist} Z{dist} F{speed}")
        time.sleep(self.DELAY)

        return self
    

    def moveSpeedYZ(self, dist: tuple, speed: int):
        '''Linear move in the YZ direction with a speed parameter. Pass a tuple of distances in the order (Y,Z).'''
        self._write(f"G0 Y{dist} Z{dist} F{speed}")
        time.sleep(self.DELAY)

        return self
    

    def moveSpeed(self, dist: tuple, speed: int):
        '''General linear move with a speed parameter. Pass a tuple of distances in the order (X,Y,Z).'''
        self._write(f"G0 X{dist[0]} Y{dist[1]} Z{dist[2]} F{speed}")
        time.sleep(self.DELAY)

        return self
    

    '''
    RELATIVE MOVE COMMANDS

    Relative move commands are not recommended due to rounding errors which stack up over time.
    Relative move commands will always revert back to absolute coordinates after the move is executed.
    '''

    def relMoveX(self, dist, speed=DEFAULT_SPEED):
        '''Performs a linear move in the X direction with relative positioning, then reverts back to absolute positioning.'''
        self._write(self.GCODE["SET_REL"])
        self._write(f"G0 X{dist} F{speed}")
        self._write(self.GCODE["SET_ABS"])

        time.sleep(self.DELAY)

        logger.log(20, f"Linear relative X move, dist {dist}, speed {speed}")

        return self


    def relMoveY(self, dist, speed=DEFAULT_SPEED):
        '''Performs a linear move in the X direction with relative positioning, then reverts back to absolute positioning.'''
        self._write(self.GCODE["SET_REL"])
        self._write(f"G0 Y{dist} F{speed}")
        self._write(self.GCODE["SET_ABS"])

        time.sleep(self.DELAY)

        logger.log(20, f"Linear relative Y move, dist {dist}, speed {speed}")

        return self


    def relMoveZ(self, dist, speed=DEFAULT_SPEED):
        '''Performs a linear move in the X direction with relative positioning, then reverts back to absolute positioning.'''
        self._write(self.GCODE["SET_REL"])
        self._write(f"G0 Z{dist} F{speed}")
        self._write(self.GCODE["SET_ABS"])

        time.sleep(self.DELAY)

        logger.log(20, f"Linear relative Z move, dist {dist}, speed {speed}")

        return self
    

    def relMoveXY(self, coords: list, dist, speed):
        pass
    

    def relMoveXYZ(self, coords: list, dist, speed):
        pass


    '''
    NONLINEAR MOVE COMMANDS
    '''
    def moveArcCW(self, p1, p2, p3, radius):
        self._write(f"G2 X{p1} Y{p2} Z{p3} R{radius}")
        time.sleep(self.DELAY)

        return self


    '''
    COMBO MOVES

    These are convenience motion commands for more complex moves.
    '''
    def linearHop(self, height: float, dist: float, direction: str, speed=DEFAULT_SPEED):
        '''Perform a hop move using only linear motions.'''
        rise = f"G0 Z{height} F{speed}"
        move_xy = f"G0 {direction}{dist} F{speed}"
        lower = f"G0 Z{-height} F{speed}"

        self._write(f"{rise}\n{move_xy}\n{lower}")

        return self


    '''
    UTILITY FUNCTIONS
    '''
    def setSpeed(self, speed):
        '''Sets movement speed. Pass a value in mm/s and this function will convert to mm/min for the printer to understand.'''
        mms_to_mmmin = round(speed*60.0, 2)
        self._write(f"G0 F{mms_to_mmmin}")
        self.speed = mms_to_mmmin
        logger.log(20, f"Speed set to {speed} mm/s.")

        return self


    def setMode(self, mode):
        '''Set either relative or absolute coordinates. By default, set to absolute.'''
        match mode:
            case "rel":
                self._write(self.GCODE["SET_REL"])
            case "abs":
                self._write(self.GCODE["SET_ABS"])
            case _:
                self._write(self.GCODE["SET_ABS"])

        return self
    

    def setXYPlane(self):
        '''Sets workspace plane to the XY plane. Allows G2, G3, G5 to operate in this plane.'''
        self._write(self.GCODE["SET_XY_PLANE"])
        time.sleep(self.DELAY)


    def setZXPlane(self):
        '''Sets workspace plane to the ZX plane. Allows G2, G3, G5 to operate in this plane.'''
        self._write(self.GCODE["SET_ZX_PLANE"])
        time.sleep(self.DELAY)


    def setYZPlane(self):
        '''Sets workspace plane to the YZ plane. Allows G2, G3, G5 to operate in this plane.'''
        self._write(self.GCODE["SET_YZ_PLANE"])
        time.sleep(self.DELAY)


    def checkOutOfBounds(self):
        pass


    '''
    INTERNAL METHODS
    '''

    def _write(self, gcode):
        '''Writes string of gcode to the printer via serial port. Adds a newline character at the end to execute the command.'''
        gcode += "\n"
        gcode_to_bytes = gcode.encode("utf-8")
        print(f"Writing gcode {gcode_to_bytes}")
        self.conn.write(gcode_to_bytes)
        self.conn.write(b'M84\n')


    def _queueWrite(sef, gcode_list: list):
        pass