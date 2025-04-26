import serial
import time
from python_gcode_api import Printer
import readline


def userSetup():
    pass


def setupReadline():
    readline.parse_and_bind("tab: complete")  # Optional autocomplete
    try:
        readline.read_history_file(".printer_history")  # Load previous session history
    except FileNotFoundError:
        print("Error: file not found")
        pass


def runTerminal():
    try: 
        # p = Printer("/dev/ttyACM0")
        print("Connected successfully!")
    except:
        print("Error connecting to printer")

    time.sleep(2)

    while True:
        cmd = input("> Enter a command.\n> ")
        try:
            result = eval(cmd)
            print(f"> Executed {cmd}")
        except ValueError:
            print("Invalid argument")
        except:
            print("Invalid command.")
        print(f"--------------------------------")


def main():
    setupReadline()
    runTerminal()

if __name__=="__main__":
    main()