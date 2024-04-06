import serial
from azure.storage.blob import BlobServiceClient, ContentSettings
from picamera2 import Picamera2, Preview
import time
import RPi.GPIO as GPIO
from datetime import datetime
import os

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)})
picam2.configure(camera_config)
picam2.start_preview(Preview.QTGL)
picam2.start()
time.sleep(2)

# Replace 'your_connection_string' with your actual Azure Storage connection string
connection_string = 'DefaultEndpointsProtocol=https;AccountName=ammar;AccountKey=E33YWwqmclXsyttbOwQsmcwmgJqk0f1K23fE1Bp9x91JCcKVsSOIbCeGTpRaoEcwNsmoewzyU5V2+AStIW1ZjA==;EndpointSuffix=core.windows.net'
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name = 'data'
location_blob_name = 'location.txt'


servo_angle = 30  # Initial servo angle

# Servo motor setup
SERVO_PIN = 11  # GPIO pin connected to the servo
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)  # PWM with 50Hz frequency for servo control
servo.start(0)  # Start PWM with duty cycle of 0
def set_servo_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(SERVO_PIN, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO_PIN, False)
    servo.ChangeDutyCycle(0)

def nmea(line, dt):
    print(f"Received GPS data: {line}")
    parts = line.split(",")
    if parts[0] == '$GPGGA':
        print(f"Button pressed at: {dt}")
        gga(parts, dt)

def gga(parts, dt):
    print("Inside the gga function")
    latitude = parts[2]
    longitude = parts[4]

    # Vérifier si les valeurs de latitude et de longitude sont valides
    if latitude and longitude:
        print(f"Latitude: {latitude}, Longitude: {longitude}")
    else:
        print("Position not available. Latitude and Longitude set to 0.0")
        latitude = "0.0"
        longitude = "0.0"

    # Append the position information to the local location file
    with open("location.txt", "a") as f:
        f.write(f"{dt}: Latitude: {latitude}, Longitude: {longitude}\n")
        print("Location information appended to the local file.")
def capture_and_upload_image():
    global last_capture_time, servo_angle
   
    now = datetime.now()
    dt = now.strftime("%d%m%Y%H%M%S")  # Change format to remove ':' in time part
   
    local_file_path = f"{dt}.jpg"
    picam2.capture_file(local_file_path)
    print(f"Captured: {local_file_path}")


    blob_name = f'real_time_data/{dt}.jpg'
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, content_settings=ContentSettings(content_type='image/jpeg'))
    print("Image uploaded successfully.")

    os.remove(local_file_path)
    print("Local file removed")

    # Move the servo motor to the appropriate angle
    set_servo_angle(servo_angle)
   
    # Toggle servo angle between 90 and 30
    servo_angle = 170 if servo_angle == 30 else 30

def upload_location_blob():
    try:
        # Read the content from the local location file
        with open(location_blob_name, "r") as f:
            updated_content = f.read()

        # Upload the updated content to Azure Blob Storage
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=location_blob_name)
        blob_client.upload_blob(updated_content, overwrite=True)

        print("Location information uploaded to Azure Blob Storage.")
    except Exception as e:
        print(f"An error occurred while uploading location information: {e}")
   

ser = serial.Serial('/dev/ttyS0', timeout=2)
line = ""
dt = ""

try:
    while True:
        ch = ser.read()
        line = line + ch.decode('latin1')
        if ch == b'\n':  # Check for end of line
            nmea(line, dt)
            line = ""  # Reset line buffer
            dt = datetime.now().strftime("%d%m%Y%H%M%S")  # Update dt for the next iteration
           
            # Appel de la fonction pour capturer et télécharger l'image
            capture_and_upload_image()
           
            # Appel de la fonction pour télécharger les informations de position
            upload_location_blob()