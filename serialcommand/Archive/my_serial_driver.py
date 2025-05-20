import serial
import time
import os
from datetime import datetime

class SerialCommandDriver:
    def __init__(self, port='COM5', baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.cycle_counter = 0
        self.log_file = None
        self.start_time = datetime.now()
        self.create_log_file()

    def create_log_file(self):
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"log_{timestamp}.txt"
        self.log_file = open(filename, "a", encoding="utf-8")
        self.log(f"Log started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def log(self, message):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_entry = f"{timestamp} {message}"
        print(log_entry)
        if self.log_file:
            self.log_file.write(log_entry + "\n")

    def finalize_log(self):
        self.log("")
        self.log("--- Process Summary ---")
        self.log(f"Total cycles completed: {self.cycle_counter}")
        self.log_file.close()

    def open_connection(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.log(f"Connected to {self.port} at {self.baudrate} baud rate.")
        except Exception as e:
            self.log(f"Error opening connection: {e}")

    def close_connection(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.log(f"Connection to {self.port} closed.")
        else:
            self.log(f"No active connection to {self.port}.")

    def send_command(self, command):
        if self.ser and self.ser.is_open:
            self.ser.write(command.encode('utf-8'))
            self.log(f"Command sent: {command.strip()}")
        else:
            self.log("No active connection to send command.")

    def sanitize_response(self, response):
        return ''.join([char for char in response if char.isprintable()])

    def receive_response(self, timeout_seconds, delay_seconds=5):
        if self.ser and self.ser.is_open:
            start_time = time.time()
            while time.time() - start_time < timeout_seconds:
                response = self.ser.readline().decode('utf-8').strip()
                sanitized = self.sanitize_response(response)
                if sanitized == "NO" or not sanitized:
                    time.sleep(delay_seconds)
                    continue
                self.log(f"Received: '{sanitized}'")
                return sanitized
            self.log(f"Timeout reached after {timeout_seconds} seconds.")
            return None
        else:
            self.log("No active connection to receive response.")
            return None

if __name__ == "__main__":
    driver = SerialCommandDriver(port='COM5', baudrate=9600)
    driver.open_connection()
    stop_loop = False

    while not stop_loop:
        driver.cycle_counter += 1
        driver.log(f"\n--- Starting cycle {driver.cycle_counter} ---\n")

        # Send 'B'
        driver.send_command("B\n")
        response = driver.receive_response(timeout_seconds=60)

        if response == "BOK":
            driver.log("Received 'BOK'. Now waiting for the next response...")

            decap_response = driver.receive_response(timeout_seconds=120)

            if decap_response == "DECAP_OK":
                driver.log("Received 'DECAP_OK'. Now sending 'C'...")

                driver.send_command("C\n")
                cok_response = driver.receive_response(timeout_seconds=60)

                if cok_response == "COK":
                    recap_result = driver.receive_response(timeout_seconds=120)

                    if recap_result == "RECAP_OK":
                        driver.log("Received 'RECAP_OK'. Process complete.")
                    elif recap_result in ["RECAP_ERR", "STATUS_WRONG_TUBE"]:
                        driver.log(f"Error received: '{recap_result}'. Stopping the loop.")
                        stop_loop = True
                    else:
                        driver.log("Did not receive 'RECAP_OK'. Stopping the loop.")
                        stop_loop = True
                else:
                    driver.log("Did not receive 'COK'. Stopping the loop.")
                    stop_loop = True

            elif decap_response in ["STATUS_WRONG_TUBE", "DECAP_ERR"]:
                driver.log(f"Error received: '{decap_response}'. Stopping the loop.")
                stop_loop = True
            else:
                driver.log("Did not receive 'DECAP_OK'. Stopping the loop.")
                stop_loop = True

        elif response in ["STATUS_WRONG_TUBE", "BNO", "CNO"]:
            driver.log(f"Error received: '{response}'. Stopping the loop.")
            stop_loop = True
        else:
            driver.log("Did not receive 'BOK' within the expected time. Stopping the loop.")
            stop_loop = True

        time.sleep(1)

    driver.close_connection()
    driver.finalize_log()
