import time
from PIL import Image, ImageDraw, ImageFont
import board
import adafruit_mmc56x3
import ST7789 as ST7789

# 1. Define Display HAT Mini dimensions
width = 320
height = 240

# 2. Setup the ST7789 driver with custom pins and a safe SPI speed
# The Display HAT Mini uses SPI port 0, Chip Select 1, DC 9, and Backlight 13
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
draw = ImageDraw.Draw(buffer)# Load fonts
try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    font_data = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except IOError:
    font_title = ImageFont.load_default()
    font_data = ImageFont.load_default()

# 4. Initialize I2C Bus and MMC5603 Magnetometer
i2c = board.I2C()
sensor = adafruit_mmc56x3.MMC5603(i2c)

print("Starting readings... Press Ctrl+C to exit.")

try:
    while True:
        # Clear canvas
        draw.rectangle((0, 0, width, height), fill=(20, 24, 33))
        
        # Read magnetometer vector values (in micro-Teslas)
        mag_x, mag_y, mag_z = sensor.magnetic
        temp = sensor.temperature

        print("magnetometer readings x {}, y {}, z {}, temp {} ".format(mag_x, mag_y, mag_z, temp))
        
        # Write text layout onto the buffer
        draw.text((10, 10), "MMC5603 Magnetometer", font=font_title, fill=(255, 255, 255))
        draw.line((10, 38, 310, 38), fill=(100, 100, 100), width=1)
        
        draw.text((20, 60),  f"X Axis:  {mag_x:8.2f} uT", font=font_data, fill=(255, 100, 100))
        draw.text((20, 100), f"Y Axis:  {mag_y:8.2f} uT", font=font_data, fill=(100, 255, 100))
        draw.text((20, 140), f"Z Axis:  {mag_z:8.2f} uT", font=font_data, fill=(100, 100, 255))
        draw.text((20, 190), f"Temp:    {temp:6.1f} °C", font=font_data, fill=(240, 180, 50))
        
        # 5. Push the updated buffer using the native display driver method
        disp.display(buffer)
        
        time.sleep(5)

except KeyboardInterrupt:
    # Clear display upon clean exit
    draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
    disp.display(buffer)
    print("\nProgram closed cleanly.")
