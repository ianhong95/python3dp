import time
import serial
from python_gcode_api import Printer
import asyncio


p = Printer("/dev/ttyACM0")

def test_motion():
    p.homeXYZ()

    p.relMoveZ(10)
    p.relMoveX(50).relMoveY(100)

    p.linearHop(50, 50, "X")
    p.relMoveCircle(25)
    p.linearHop(50, -50, "X")

    p.relMoveX(-50).relMoveY(-100)

    p.disable_all()


def batch():
    p.homeXYZ()

    p.batch_write(f"G0 X2", 20)

    p.disable_all()


def circHop():
    p.homeXYZ()
    p.circHop2(100.00)
    # p.homeXYZ()

def main():
    # test_motion()
    # batch()
    circHop()
    # pass


if __name__=="__main__":
    # asyncio.run(main())
    main()
