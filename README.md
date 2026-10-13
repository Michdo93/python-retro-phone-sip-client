# python-retro-phone-sip-client
A Python script and a complete, reliable solution for running a USB retro phone continuously as a background service, controlling the transition between answering and hanging up calls, and dynamically adjusting the volume during operation using the hardware buttons. Calls are made using the `SIP` and `RTP` protocols.

---

## Explanation

### SIP (Session Initiation Protocol)

`SIP (Session Initiation Protocol)` is the global industry standard for `IP telephony` and `VoIP (Voice over IP)`. It ensures that your device for example a Raspberry Pi (as a `SIP client)` can connect to a `Asterisk server`, establish a call, control it (such as placing it on hold or hanging up), and terminate it.

---

### RTP (Real-time Transport Protocol)

Once the connection is established, the actual voice is transmitted back and forth in real time as an audio stream via another protocol called `RTP (Real-time Transport Protocol)`. However, `SIP` is responsible for controlling the connection and establishing it throughout the entire process.

---

## Installation

### Required Installations on the Client

Run these commands in your terminal to install the necessary system libraries (HID support, ALSA audio tools, and the Linphone CLI SIP client) and Python packages:

```bash
sudo apt update
sudo apt install -y libhidapi-dev linphone alsa-utils
pip install hidapi
```

Initialize and register Linphone once with your Asterisk server details (replace `192.168.X.X` with your Asterisk server IP):

```bash
linphonecsh init
linphonecsh register --host 192.168.X.X --username retro-phone --password 1234
```

---

### The Python Script (`/opt/retro-phone/retro_phone_client.py`)

Create a folder `/opt/retro-phone/`, place the script inside as `retro_phone_client.py`, and make it executable (`chmod +x retro_phone_client.py`).

```bash
git clone https://github.com/Michdo93/python-retro-phone-sip-client
cd python-retro-phone-sip-client
sudo cp retro_phone_client.py /opt/retro-phone/retro_phone_client.py
sudo chown $USER:$USER /opt/retro-phone/retro_phone_client.py
```

#### Customization

Please open the Python file with following command:

```
nano /opt/retro-phone/retro_phone_client.py
```

Then you have to change following lines:

```
# ==========================================
# CONFIGURATION
# ==========================================
ASTERISK_IP = "192.168.X.X"  # Replace with your Asterisk Server IP
EXTENSION = "100"             # Complaint hotline extension

# Optional Vendor ID / Product ID filter (leave as None for auto-detection)
VENDOR_ID = None
PRODUCT_ID = None
```

---

### Setup as a systemd Service

To ensure the script runs continuously in the background (even after reboots), set it up as a systemd service.

1. Create the service configuration file:
```bash
sudo nano /etc/systemd/system/retro-phone-client.service
```

2. Add the following content (adjust paths and user name if needed, e.g., `pi`):
```ini
[Unit]
Description=Retro Phone USB Button & SIP Call Handler
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/retro-phone
ExecStart=/usr/bin/python3 /opt/retro-phone/retro_phone_client.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable retro-phone-client.service
sudo systemctl start retro-phone-client.service
```

4. Check the service status or view live logs anytime:
```bash
sudo systemctl status retro-phone-client.service
sudo journalctl -u retro-phone-client.service -f
```

## Further Informations

The project grew out of the [python-retro-phone](https://github.com/Michdo93/python-retro-phone) project.

This project is used in combination with [complaints-hotline](https://github.com/Michdo93/complaints-hotline).

For more information on how to install and configure Asterisk, see the [asterisk-smarthome](https://github.com/Michdo93/asterisk-smarthome) project.

## License

Distributed under the MIT License. See `LICENSE` for more information.
