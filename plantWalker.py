from servo import Servo
from time import sleep
import network
from umqtt.simple import MQTTClient
import config


#------------------------------
# MQTT PARAMS
#------------------------------
MQTT_TOPIC = "pico/walker"
MQTT_SERVER = config.mqtt_server
MQTT_PORT = 0
MQTT_USER = config.mqtt_username
MQTT_PASSWORD = config.mqtt_password
MQTT_CLIENT_ID = b"raspberrypi_picow"
MQTT_KEEPALIVE = 7200
MQTT_SSL = True
MQTT_SSL_PARAMS = {'server_hostname': MQTT_SERVER}

# -----------------------------
# Servos
# -----------------------------
hip_r  = Servo(pin=2)
foot_r = Servo(pin=4)
hip_l  = Servo(pin=15)
foot_l = Servo(pin=16)

# -----------------------------
# Calibration + safety
# -----------------------------
LIMITS = {
    "hip_r":  (50, 140),
    "foot_r": (30, 150),
    "hip_l":  (50, 140),
    "foot_l": (30, 150),
}

NEUTRAL = {
    "hip_r":  90,
    "foot_r": 90,
    "hip_l":  90,
    "foot_l": 90,
}

HIP_FWD_AMT   = 25
FOOT_LIFT_AMT = 25

HIP_R_FWD_SIGN   = -1
HIP_L_FWD_SIGN   = +1
FOOT_R_LIFT_SIGN = -1
FOOT_L_LIFT_SIGN = +1

RAMP_STEP_DEG = 1
RAMP_DT_SEC   = 0.015

cur = NEUTRAL.copy()
walking = False
stopped = True

def clamp(name, a):
    lo, hi = LIMITS[name]
    if a < lo: return lo
    if a > hi: return hi
    return a

def ramp_move(servo, start, end, step=RAMP_STEP_DEG, dt=RAMP_DT_SEC):
    start = int(start); end = int(end)
    if end > start:
        a = start
        while a <= end:
            servo.move(a); sleep(dt); a += step
    else:
        a = start
        while a >= end:
            servo.move(a); sleep(dt); a -= step

def set_pose(hr, fr, hl, fl, hold=0.10):
    hr = clamp("hip_r", hr); fr = clamp("foot_r", fr)
    hl = clamp("hip_l", hl); fl = clamp("foot_l", fl)

    ramp_move(hip_r,  cur["hip_r"],  hr)
    ramp_move(foot_r, cur["foot_r"], fr)
    ramp_move(hip_l,  cur["hip_l"],  hl)
    ramp_move(foot_l, cur["foot_l"], fl)

    cur["hip_r"], cur["foot_r"], cur["hip_l"], cur["foot_l"] = hr, fr, hl, fl
    sleep(hold)

def stop_all():
    hip_r.stop(); foot_r.stop(); hip_l.stop(); foot_l.stop()

def pose(hr, fr, hl, fl, hold=0.10):
    return (hr, fr, hl, fl, hold)

def set_neutral():
    set_pose(HR0, FR0, HL0, FL0, hold=0.6)

HR0, FR0, HL0, FL0 = NEUTRAL["hip_r"], NEUTRAL["foot_r"], NEUTRAL["hip_l"], NEUTRAL["foot_l"]

HR_FWD = HR0 + (HIP_FWD_AMT * HIP_R_FWD_SIGN)
HL_FWD = HL0 + (HIP_FWD_AMT * HIP_L_FWD_SIGN)

FR_LIFT = FR0 + (FOOT_LIFT_AMT * FOOT_R_LIFT_SIGN)
FL_LIFT = FL0 + (FOOT_LIFT_AMT * FOOT_L_LIFT_SIGN)

# 1) lift right
# 2) swing right hip forward
# 3) set right down
# 4) lift left
# 5) swing left hip forward
# 6) set left down
WALK = [
    pose(HR0, FR0,   HL0, FL0,   0.15),

    # Right step
    pose(HR0, FR_LIFT, HL0, FL0,  0.10),
    pose(HR_FWD, FR_LIFT, HL0, FL0, 0.10),
    pose(HR_FWD, FR0,   HL0, FL0,  0.12),

    # Left step
    pose(HR0, FR0,   HL0, FL_LIFT, 0.10),
    pose(HR0, FR0,   HL_FWD, FL_LIFT, 0.10),
    pose(HR0, FR0,   HL_FWD, FL0,   0.12),
]

def play(gait):
    for p in gait:
        set_pose(*p)

def initialize_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Connect to the network
    wlan.connect(ssid, password)

    # Wait for Wi-Fi connection
    connection_timeout = 10
    while connection_timeout > 0:
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        sleep(1)

    # Check if connection is successful
    if wlan.status() != 3:
        return False
    else:
        print('Connection successful!')
        network_info = wlan.ifconfig()
        print('IP address:', network_info[0])
        return True
def connect_mqtt():
    try:
        client = MQTTClient(client_id=MQTT_CLIENT_ID,
                            server=MQTT_SERVER,
                            port=MQTT_PORT,
                            user=MQTT_USER,
                            password=MQTT_PASSWORD,
                            keepalive=MQTT_KEEPALIVE,
                            ssl=MQTT_SSL,
                            ssl_params=MQTT_SSL_PARAMS)
        client.connect()
        return client
    except Exception as e:
        print('Error connecting to MQTT:', e)
        raise  # Re-raise the exception to see the full traceback

        
def subscribe(client, topic):
    client.subscribe(topic)
    print('Subscribe to topic:', topic)

def mqtt_callback(topic, message):
    global walking
    print(f"GOT:{message}")
    if message == b'WALK':
        print("GOING TO WALK")
        walking = True
        stopped = False
    elif message == b'STOP':
        print("GOING TO STOP")
        walking = False
    else:
        print("WAITING")

# -----------------------------
# Main
# -----------------------------
try:
    set_neutral()
    if not initialize_wifi(config.wifi_ssid, config.wifi_password):
        print('Error connecting to the network... exiting program')
    else:
        client = connect_mqtt()
        client.set_callback(mqtt_callback)
        subscribe(client, MQTT_TOPIC)
        while True:
            client.check_msg()
            
            if walking:
                play(WALK)
                
            else:
                if not stopped:
                    set_neutral()
                    stopped = True
                
            
except KeyboardInterrupt:
    stop_all()
