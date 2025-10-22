import paho.mqtt.client as mqtt
import sys
import os

# --- Cross-platform key input ---
if os.name == "nt":  # Windows
    import msvcrt

    def get_key():
        return msvcrt.getch().decode("utf-8")

else:  # Linux / macOS
    import termios
    import tty

    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


# MQTT settings
BROKER_ADDRESS = "192.168.4.1"  # địa chỉ broker
MQTT_PORT = 1883
TOPIC = "VR_control"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to broker:", BROKER_ADDRESS)
        client.subscribe(TOPIC)
    else:
        print(f"❌ Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    print(f"📩 Received: '{msg.payload.decode()}' on topic '{msg.topic}'")


def on_subscribe(mosq, obj, mid, granted_qos):
    print(f"🔔 Subscribed (mid={mid})")


def on_publish(mosq, obj, mid):
    print(f"📤 Message {mid} sent to broker")


# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_publish = on_publish

client.connect(BROKER_ADDRESS, MQTT_PORT, 60)
client.loop_start()


def main():
    print("🚀 Điều khiển robot bằng phím WASD, nhấn 'q' để thoát")

    while True:
        key = get_key().lower()
        cmd = ""

        if key == "w":
            cmd = "Forward"
        elif key == "s":
            cmd = "Backward"
        elif key == "a":
            cmd = "Left"
        elif key == "d":
            cmd = "Right"
        elif key == " ":
            cmd = "Stop"
        elif key == "q":
            print("❌ Thoát chương trình.")
            break

        if cmd:
            client.publish(TOPIC, cmd)
            print(f"➡️  Gửi: {cmd}")

    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
