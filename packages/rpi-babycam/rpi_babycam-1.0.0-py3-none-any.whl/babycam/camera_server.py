import os
import logging
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder, H264Encoder
from picamera2.outputs import FileOutput, CircularOutput
from streaming import StreamingOutput, StreamingServer, StreamingHandler
from motion_detection import MotionDetector
from mqtt_handler import MqttHandler

log = logging.getLogger("rpi-babycam.camera_server")

def start_camera_server(record_motion, bounding_box, sensitivity, mqtt_broker, port, save_path):

    
    # Initialize components
    picamera2 = Picamera2()
    motion_detector = MotionDetector(threshold=sensitivity)
    
    if mqtt_broker:
        # Avoid calling mqttHandler class unless it's configured by the user
        mqtt_handler = MqttHandler(mqtt_broker)
        mqtt_handler.connect()
    else:
        mqtt_handler = None

    picamera2.configure(picamera2.create_video_configuration(main={"size": (1280, 720)}))

    encoder = None
    if record_motion:
        os.makedirs(save_path, exist_ok=True)
        encoder = H264Encoder(bitrate=1000000)
        encoder.output = CircularOutput()
        picamera2.encoder = encoder

    output = StreamingOutput(encoder, motion_detector, mqtt_handler, bounding_box, record_motion)
    picamera2.start_recording(MJPEGEncoder(bitrate=10000000), FileOutput(output))

    # Main loop to handle streaming
    try:
        address = ('', port)
        server = StreamingServer(address, StreamingHandler)
        server.output = output  # Pass the output to the server instance
        log.info(f"Starting MJPEG server on {address[0]}:{address[1]}")
        server.serve_forever()
    except Exception as e:
        log.exception(f"Failed to start server: {e}")
    finally:
        picamera2.stop_recording()
        if mqtt_handler:
            mqtt_handler.stop()

