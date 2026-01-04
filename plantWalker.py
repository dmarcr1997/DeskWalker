from servo import Servo
from time import sleep

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

# -----------------------------
# Main
# -----------------------------
try:
    set_pose(HR0, FR0, HL0, FL0, hold=0.6)
    while True:
        play(WALK)
except KeyboardInterrupt:
    stop_all()
