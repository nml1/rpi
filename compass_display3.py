import time
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import board
import adafruit_mmc56x3
import ST7789 as ST7789
from gpiozero import Button  # Added for hardware button tracking

# 1. Define Display HAT Mini dimensions
width = 320
height = 240

# 2. Setup the ST7789 driver with custom pins and a safe SPI speed
disp = ST7789.ST7789(
    height=height,
    width=width,
    rotation=180,           # Flips the text right-side up for this HAT
    port=0,
    cs=1,
    dc=9,
    backlight=13,
    spi_speed_hz=16000000,  # 16 MHz - significantly cleaner for jumper wires
    offset_left=0,
    offset_top=0
)

# Start the display hardware
disp.begin()

# 3. Create the PIL Image buffer
buffer = Image.new("RGB", (width, height), color=(0, 0, 0))
draw = ImageDraw.Draw(buffer)

# Load fonts
try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    font_data = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except IOError:
    font_title = ImageFont.load_default()
    font_data = ImageFont.load_default()

# 4. Initialize I2C Bus and MMC5603 Magnetometer
i2c = board.I2C()
sensor = adafruit_mmc56x3.MMC5603(i2c)

# --- Button Initialization & Control State ---
is_paused = False
should_restart = False

def handle_restart():
    global should_restart
    print("Button A Pressed: Restarting program...")
    should_restart = True

def handle_pause():
    global is_paused
    if not is_paused:
        print("Button B Pressed: Pausing readings...")
        is_paused = True

def handle_resume():
    global is_paused
    if is_paused:
        print("Button X Pressed: Resuming readings...")
        is_paused = False

# Map Display HAT Mini Buttons (Pins: A=5, B=6, X=16)
btn_a = Button(5, pull_up=True)
btn_b = Button(6, pull_up=True)
btn_x = Button(16, pull_up=True) # Replaces requested "C" button 

btn_a.when_pressed = handle_restart
btn_b.when_pressed = handle_pause
btn_x.when_pressed = handle_resume
# ---------------------------------------------

print("Starting readings... Press Ctrl+C or Button A to exit/restart.")
loopcnt = 0
tot_x2 = 0
tot_y2 = 0
tot_z2 = 0
avg_x = 0
avg_y = 0
avg_z = 0
avg_x2 = 0
avg_y2 = 0
avg_z2 = 0

draw.rectangle((0, 0, width, height), fill=(0, 0, 0))

try:
    while True:
        # Check if button A requested a software restart
        if should_restart:
            # Clear display cleanly before spinning up a new instance
            draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
            disp.display(buffer)
            # Re-execute the current script
            os.execv(sys.executable, ['python3'] + sys.argv)

        # If paused, bypass sensor read and display updates
        if is_paused:
            time.sleep(0.2)
            continue

        # Clear canvas
        draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
      
        # Read magnetometer vector values (in micro-Teslas)
        mag_x, mag_y, mag_z = sensor.magnetic

        mag_x = round(mag_x, 6)
        mag_y = round(mag_y, 6)
        mag_z = round(mag_z, 6)
        loopcnt += 1
        avg_x = avg_x + mag_x
        avg_y = avg_y + mag_y
        avg_z = avg_z + mag_z
        tot_x2 = tot_x2 + (mag_x * mag_x)
        tot_y2 = tot_y2 + (mag_y * mag_y)
        tot_z2 = tot_z2 + (mag_z * mag_z)
      
        temp = round(sensor.temperature, 2)

        print("magnetometer readings x {}, y {}, z {}, temp {} ".format(mag_x, mag_y, mag_z, temp))
        
        # refresh the display every 5 seconds with average values (15 * 0.2 seconds)  
        if loopcnt >= 15:
            # calculate average values
            avg_x = avg_x / loopcnt
            avg_y = avg_y / loopcnt
            avg_z = avg_z / loopcnt
            avg_x2 = (tot_x2 / loopcnt) ** 0.5
            avg_y2 = (tot_y2 / loopcnt) ** 0.5
            avg_z2 = (tot_z2 / loopcnt) ** 0.5
            
            # Write text layout onto the buffer
            draw.text((10, 10), "MMC5603 Magnetometer", font=font_title, fill=(255, 255, 255))
            draw.line((10, 38, 310, 38), fill=(100, 100, 100), width=1)
            draw.text((20, 60),  f"X Axis: av {avg_x:8.2f} av2 {avg_x2:8.2f} uT", font=font_data, fill=(255, 100, 100))
            draw.text((20, 100), f"Y Axis: av {avg_y:8.2f} av2 {avg_y2:8.2f} uT", font=font_data, fill=(100, 255, 100))
            draw.text((20, 140), f"Z Axis: av {avg_z:8.2f} av2 {avg_z2:8.2f} uT", font=font_data, fill=(100, 100, 255))
            draw.text((20, 190), f"Temp:    {temp:6.1f} °C loopcnt {loopcnt:3.0f}", font=font_data, fill=(240, 180, 50))
            
            loopcnt = 0
            tot_x2 = 0
            tot_y2 = 0
            tot_z2 = 0
            avg_x = 0
            avg_y = 0
            avg_z = 0  
            avg_x2 = 0
            avg_y2 = 0
            avg_z2 = 0            
            
            # Push the updated buffer using the native display driver method
            disp.display(buffer)
        
        time.sleep(0.2)

except KeyboardInterrupt:
    # Clear display upon clean exit
    time.sleep(10)
    draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
    disp.display(buffer)
    print("\nProgram closed cleanly.")
