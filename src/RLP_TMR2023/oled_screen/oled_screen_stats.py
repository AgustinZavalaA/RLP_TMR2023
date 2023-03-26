import time
import subprocess

from board import SCL, SDA
import busio
import adafruit_ssd1306

# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

while True:
    cmd = "hostname -I | cut -d' ' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = 'cut -f 1 -d " " /proc/loadavg'
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")

    # Display image.
    disp.fill(0)
    new_font = "src/RLP_TMR2023/oled_screen/font5x8.bin"
    disp.text('IP: ' + IP, 0, 0, 1, font_name=new_font)
    disp.text('CPU load: ' + CPU, 0, 8, 1, font_name=new_font)
    disp.text(MemUsage, 0, 16, 1, font_name=new_font)
    disp.text(Disk, 0, 25, 1, font_name=new_font)
    disp.show()
    time.sleep(0.1)
    
disp.fill(0)
disp.show()