import logging

log = logging.getLogger("rpi-babycam.mqtt_handler")

class MqttHandler:
    def __init__(self, broker_address):
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            log.warning("paho isn't installed. For MQTT functionality install paho and run again.")
            self.client = None
            self.broker_address = None
        else:
            self.client = mqtt.Client(client_id="TentRPI", clean_session=True, protocol=mqtt.MQTTv311,callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
            self.broker_address = broker_address

    def connect(self):
        try:
            self.client.connect(self.broker_address,1883,60)
            self.client.loop_start()
        except Exception as e:
            log.exception(f"Failed to connect to MQTT broker: {e}")
            return False
        return True

    def publish_motion_event(self, topic="camera/motion", message="Motion detected"):
        try:
            self.client.publish(topic, message)
        except Exception as e:
            log.exception(f"Failed to publish MQTT message: {e}")

    def stop(self):
        self.client.loop_stop()

    def disconnect(self):
        try:
            self.client.disconnect()
            self.stop()
        except Exception as e:
            log.exception(f"Error during MQTT disconnect: {e}")


