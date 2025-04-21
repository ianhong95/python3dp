import time
import serial
from python_gcode_api import Printer
import asyncio


p = Printer("/dev/ttyACM0")

def test_motion():
    p.homeXYZ()

    p.relMoveZ(10, 5000)

    p.relMoveX(100, 5000).relMoveY(100, 5000)

    p.relMoveCircle(20, 5000)

    p.relMoveX(-100, 5000).relMoveY(-100, 5000)

    p.disable_all()

def main():
    # test_motion()
    pass


if __name__=="__main__":
    # asyncio.run(main())
    main()
