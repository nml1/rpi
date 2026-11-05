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
      
        temp = round(sensor.temperature,2)

        print("magnetometer readings x {}, y {}, z {}, temp {} ".format(mag_x, mag_y, mag_z, temp))
        
        # refresh the display every 5 seconds with average values  (15 * 0.2 seconds)  
        if loopcnt >= 15:
          # calculate average values
            avg_x = avg_x / loopcnt
            avg_y = avg_y / loopcnt
            avg_z = avg_z / loopcnt
            avg_x2 = (tot_x2 / loopcnt) ** 0.5
            avg_y2 = (tot_y2 / loopcnt) ** 0.5
            avg_z2 = (tot_z2 / loopcnt) ** 0.5
            avg_xyz2 = avg_x2 + avg_y2 + avg_z2
          # Write text layout onto the buffer
            draw.text((10, 10), "MMC5603 Magnetometer", font=font_title, fill=(255, 255, 255))
            draw.line((10, 38, 310, 38), fill=(100, 100, 100), width=1)
            draw.text((20, 60),  f"X Axis: av {avg_x:8.2f} av2 {avg_x2:8.2f} uT", font=font_data, fill=(255, 100, 100))
            draw.text((20, 100), f"Y Axis: av {avg_y:8.2f} av2 {avg_y2:8.2f} uT", font=font_data, fill=(100, 255, 100))
            draw.text((20, 140), f"Z Axis: av {avg_z:8.2f} av2 {avg_z2:8.2f} uT", font=font_data, fill=(100, 100, 255))
            draw.text((20, 190), f"Temp: {temp:6.1f} °C Sum2 {avg_xyz2:8.2f}", font=font_data, fill=(240, 180, 50))
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
