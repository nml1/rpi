import time
from PIL import Image, ImageDraw, ImageFont
import board
import adafruit_mmc56x3
from displayhatmini import DisplayHATMini

# 1. First, define the dimensions based on the HAT properties
width = DisplayHATMini.WIDTH    # 320
height = DisplayHATMini.HEIGHT  # 240
print(width)
print(height)

# 2. Next, create the PIL Image buffer 
buffer = Image.new("RGB", (width, height), color=(0, 0, 0))
draw = ImageDraw.Draw(buffer)

# 3. Finally, pass the buffer straight into the HAT initialization
hat = DisplayHATMini(buffer)

# Load a default font
try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    font_data = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except IOError:
    font_title = ImageFont.load_default()
    font_data = ImageFont.load_default()

# 2. Initialize I2C Bus and MMC5603 Magnetometer
i2c = board.I2C()
sensor = adafruit_mmc56x3.MMC5603(i2c)

print("Starting readings... Press Ctrl+C to exit.")

try:
    while True:
        # Clear canvas to black background
        draw.rectangle((0, 0, width, height), fill=(20, 24, 33))
        
        # Read magnetometer vector values (in micro-Teslas)
        mag_x, mag_y, mag_z = sensor.magnetic
        temp = sensor.temperature

        print("magnetometer readings x {}, y {}, z {}, temp {} ".format(mag_x, mag_y, mag_z, temp))
        
        # Draw text to image buffer
        draw.text((10, 10), "MMC5603 Magnetometer", font=font_title, fill=(255, 255, 255))
        draw.line((10, 38, 310, 38), fill=(100, 100, 100), width=1)
        
        draw.text((20, 60),  f"X Axis:  {mag_x:8.2f} uT", font=font_data, fill=(255, 100, 100))
        draw.text((20, 100), f"Y Axis:  {mag_y:8.2f} uT", font=font_data, fill=(100, 255, 100))
        draw.text((20, 140), f"Z Axis:  {mag_z:8.2f} uT", font=font_data, fill=(100, 100, 255))
        
        draw.text((20, 190), f"Temp:    {temp:6.1f} °C", font=font_data, fill=(240, 180, 50))
        
        # Display the framed image on the HAT
        buffer.display(image)
        
        # Refresh rate delay
        time.sleep(0.2)

except KeyboardInterrupt:
    # Clear display upon safe exit
    draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
    buffer.display(image)
    print("\nProgram closed cleanly.")
