import time
import serial

# Change this to the virtual COM port your GUI connects to
SIMULATED_PORT = 'COM2'
BAUDRATE = 9600
TIMEOUT = 1

def run_simulator():
    try:
        ser = serial.Serial(SIMULATED_PORT, BAUDRATE, timeout=TIMEOUT)
        print(f"Simulator running on {SIMULATED_PORT}...")

        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                print(f"Received: {data}")

                if data == "B":
                    print("Simulating process for B...")
                    ser.write(b'BOK\n')  # Send 'BOK'
                    # time.sleep(5)        # Wait for 5 seconds
                    # ser.write(b'NO\n')  # Send 'NOO'
                    time.sleep(5)        # Wait for another 5 seconds
                    ser.write(b'DECAP_OK\n')  # Send 'DECAP_OK'

                elif data == "C":
                    print("Simulating process for C...")
                    ser.write(b'COK\n')  # Send 'COK'
                    time.sleep(5)        # Wait for 5 seconds
                    ser.write(b'RECAP_OK\n')  # Send 'RECAP_OK'

            time.sleep(0.1)  # Small delay to prevent busy-waiting

    except Exception as e:
        print(f"Simulator error: {e}")

if __name__ == "__main__":
    run_simulator()
