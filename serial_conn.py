import serial
import time

try: 
    serial_connection = serial.Serial("/dev/ttyACM0", 115200)
    print("Connected successfully!")
except:
    print("Error connecting to printer")

time.sleep(2)

serial_connection.reset_input_buffer()

time.sleep(0.5)

serial_connection.write(b'M115\n')
response = None

print("Reading response:")

while response==None:
    if serial_connection.in_waiting:
        response = serial_connection.readline().decode("utf-8")
        print(f"> {response}")
    else:
        print("No data yet...")
        time.sleep(0.1)

serial_connection.close()

# serial_connection.write(b'G91\n')
# serial_connection.write(b'G1 X-30 F1000\n')
# serial_connection.write(b'G1 X30 F1000\n')
# serial_connection.write(b'G1 Y30 F1000\n')
# serial_connection.write(b'G1 Y-30 F1000\n')
# serial_connection.write(b'G1 Z30 F1000\n')
# serial_connection.write(b'G1 Z-30 F1000\n')
# serial_connection.write(b'G90\n')
# serial_connection.write(b'M18\n')
