import time
import subprocess
import hid

# ==========================================
# CONFIGURATION
# ==========================================
ASTERISK_IP = "192.168.X.X"  # Replace with your Asterisk Server IP
EXTENSION = "100"             # Complaint hotline extension

# Optional Vendor ID / Product ID filter (leave as None for auto-detection)
VENDOR_ID = None
PRODUCT_ID = None

# Global call state tracker
is_in_call = False

def get_phone_device():
    """Finds and opens the retro phone HID device."""
    devices = hid.enumerate()
    target = None

    if VENDOR_ID and PRODUCT_ID:
        for d in devices:
            if d['vendor_id'] == VENDOR_ID and d['product_id'] == PRODUCT_ID:
                target = d
                break
    else:
        for d in devices:
            prod_name = (d.get('product_string') or "").lower()
            if any(keyword in prod_name for keyword in ["phone", "audio", "handset", "telephony", "retro"]):
                target = d
                break
        
        if not target and devices:
            target = devices[0]

    if target:
        print(f"[INIT] Connected to: {target.get('product_string', 'Unknown Device')} (VID: {hex(target['vendor_id'])}, PID: {hex(target['produto_id'] if 'produto_id' in target else target['product_id'])})")
        device = hid.device()
        device.open_path(target['path'])
        return device
    
    return None

def parse_button_event(data):
    """
    Parses the raw HID byte array based on observed hardware protocol:
    - data[1] == 1 -> Volume Up
    - data[1] == 2 -> Volume Down
    - data[1] == 4 -> Call / End Call
    - data[1] == 0 -> Key Released
    """
    if not data or len(data) < 2:
        return None
    
    report_id = data[0]
    key_code = data[1]

    if report_id == 3:
        if key_code == 1:
            return "Volume Up"
        elif key_code == 2:
            return "Volume Down"
        elif key_code == 4:
            return "Call / End Call"
            
    return None

def handle_call_toggle():
    """Toggles between starting a call and hanging up via Linphone CLI."""
    global is_in_call
    if not is_in_call:
        print(f"[PHONE] Call button pressed -> Dialing extension {EXTENSION}...")
        subprocess.run(["linphonecsh", "dial", "--destination", f"sip:{EXTENSION}@{ASTERISK_IP}"])
        is_in_call = True
    else:
        print("[PHONE] End call button pressed -> Hanging up...")
        subprocess.run(["linphonecsh", "hangup"])
        is_in_call = False

def adjust_volume(direction):
    """Adjusts system speaker output volume dynamically during runtime."""
    step = "+5%" if direction == "up" else "5%-"
    try:
        # Using pactl (PipeWire/PulseAudio) which is standard on modern Raspberry Pi OS
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", step], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[AUDIO] Volume turned {direction}")
    except Exception as e:
        print(f"[ERROR] Failed to adjust volume: {e}")

def main():
    device = get_phone_device()
    if not device:
        print("[ERROR] No suitable USB HID device found. Make sure your retro phone is plugged in.")
        return

    device.set_nonblocking(True)
    print("[READY] Listening for button presses continuously... Press Ctrl+C to exit.\n")

    last_pressed_button = None

    try:
        while True:
            data = device.read(64)
            if data:
                key_code = data[1] if len(data) > 1 else 0

                if key_code != 0:
                    button_name = parse_button_event(data)
                    if button_name and button_name != last_pressed_button:
                        print(f"[EVENT] Button Pressed: {button_name}")
                        
                        if button_name == "Call / End Call":
                            handle_call_toggle()
                        elif button_name == "Volume Up":
                            adjust_volume("up")
                        elif button_name == "Volume Down":
                            adjust_volume("down")
                            
                        last_pressed_button = button_name
                else:
                    last_pressed_button = None

            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\n[STOP] Stopping script...")
    finally:
        device.close()
        print("[CLOSED] Device connection closed.")

if __name__ == "__main__":
    main()
