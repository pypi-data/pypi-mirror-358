import sharklog

from malphite import OpenCVCameraConfig, SharedCameraServer

sharklog.init()

cs = SharedCameraServer()
config = OpenCVCameraConfig(name="test_camera", camera_path="/dev/video0", width=1280, height=480, fps=5)
sharklog.info(f"Adding camera with config: {config}")
shared_config = cs.append_camera(
    config
)
sharklog.info(f"Camera added: {shared_config.name}")
sharklog.info(f"Shared memory name: {shared_config.shared_memory_name}")
sharklog.info(f"Shared memory size: {shared_config.shared_memory_size} bytes")

cs.activate_camera_streaming("test_camera")
sharklog.info("Camera streaming activated.")

while True:
    pass
