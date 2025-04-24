import time
import serial
from python_gcode_api import Printer
import asyncio




def test_motion(p: Printer):
    p.home()
    p.moveZ(20)
    p.moveX(60).moveY(60)
    p.setZXPlane()
    p.moveArcCW(100, 100, 100, 2)
    p.moveArcCW(120, 60, 20, 50)
    p.disableMotors()


def main():
    p = Printer("/dev/ttyACM0")
    test_motion(p)
    # pass


if __name__=="__main__":
    # asyncio.run(main())
    main()
