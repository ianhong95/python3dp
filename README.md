# Python3DP

## Overview
This is a Python interface for sending gcode commands to Marlin-based 3D printers over the device's serial port. This allows experiments with scripted motions for custom tool paths.

## Usage
**Basic Example**

```    
from python_gcode_api import Printer

p = Printer("dev/ttyACM0")

p.moveX(5)  # Moves the print head 5mm in the positive X direction at default speed

p.moveSpeedY(5, 1000)    # Moves the print head 5mm in the positive y direction at a speed of 1000 mm/min
```

**Command Chaining**  
Each movement method in the library returns the `self` object, which allows you to chain methods in a single line.  
  
The following line draws a 10mm x 10mm square with the print head.  
`p.moveX(10).moveY(10).moveX(0).moveY(0)`
    
