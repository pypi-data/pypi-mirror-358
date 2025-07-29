from kuttyPy import *

# Our AVR Slave's I2C Address
AVR_SLAVE_ADDRESS = 0x20

def test_set_color(led_num, r, g, b):
    """Sends commands to set specific RGB values for an LED."""
    print(f"\n--- Setting LED {led_num} to R:{r}, G:{g}, B:{b} ---")
    if not I2CWriteBulk(AVR_SLAVE_ADDRESS, [0x10, led_num, r]):
        print("Failed to send Red command.")
        return
    time.sleep(0.01) # Small delay between commands for slave to process
    if not I2CWriteBulk(AVR_SLAVE_ADDRESS, [0x11, led_num, g]):
        print("Failed to send Green command.")
        return
    time.sleep(0.01)
    if not I2CWriteBulk(AVR_SLAVE_ADDRESS, [0x12, led_num, b]):
        print("Failed to send Blue command.")
        return
    time.sleep(0.5) # Allow time for LED update to be visible

def test_fade_loop(repetitions):
    """Sends command to start the fade loop."""
    print(f"\n--- Initiating Fade Loop for {repetitions} repetitions ---")
    if not I2CWriteBulk(AVR_SLAVE_ADDRESS, [0x20, repetitions]):
        print("Failed to send Fade Loop command.")
        return

    # Calculate approximate fade time
    # Each hue step is 2ms, 256 steps per cycle = 256 * 2ms = 512ms = 0.512 seconds per cycle
    approx_fade_time_sec = repetitions * 0.512
    print(f"Approximation: Fade will take ~{approx_fade_time_sec:.2f} seconds. Please observe LEDs.")
    time.sleep(approx_fade_time_sec + 1) # Wait for fade to complete + a buffer
    print("Fade loop should be complete.")

def main():
    print("--- Starting I2C AVR WS2812B Slave Test Program ---")

    # 1. Scan for I2C devices
    print("\n1. Scanning for I2C devices...")
    detected_devices = I2CScan()
    print(f"Detected devices: {[hex(addr) for addr in detected_devices]}")

    if AVR_SLAVE_ADDRESS not in detected_devices:
        print(f"Error: AVR Slave at {hex(AVR_SLAVE_ADDRESS)} not found on the bus.")
        print("Please ensure your AVR is powered, programmed, and wired correctly.")
        return

    print(f"AVR Slave ({hex(AVR_SLAVE_ADDRESS)}) found. Proceeding with tests.")

    while True:
        print("\n--- Choose a Test ---")
        print("1. Set LED 1 to various colors")
        print("2. Set LED 2 to various colors")
        print("3. Run continuous fade loop (0x20 command)")
        print("4. Set all LEDs OFF")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            # Test LED 1 colors
            test_set_color(1, 255, 0, 0) # Red
            time.sleep(1)
            test_set_color(1, 0, 255, 0) # Green
            time.sleep(1)
            test_set_color(1, 0, 0, 255) # Blue
            time.sleep(1)
            test_set_color(1, 255, 255, 0) # Yellow
            time.sleep(1)
            test_set_color(1, 0, 0, 0) # Off

        elif choice == '2':
            # Test LED 2 colors
            test_set_color(2, 0, 255, 0) # Green
            time.sleep(1)
            test_set_color(2, 255, 0, 0) # Red
            time.sleep(1)
            test_set_color(2, 0, 0, 255) # Blue
            time.sleep(1)
            test_set_color(2, 255, 0, 255) # Magenta
            time.sleep(1)
            test_set_color(2, 0, 0, 0) # Off

        elif choice == '3':
            try:
                num_repetitions = int(input("Enter number of 256-step fade repetitions (e.g., 5): "))
                if num_repetitions > 0:
                    test_fade_loop(num_repetitions)
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        elif choice == '4':
            print("\n--- Setting all LEDs OFF ---")
            test_set_color(1, 0, 0, 0)
            test_set_color(2, 0, 0, 0)
            print("All LEDs should be off now.")

        elif choice == '5':
            print("Exiting test program. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


