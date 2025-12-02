
try:
    import cv2
    print("✅ cv2 imported successfully")
except ImportError as e:
    print(f"❌ cv2 import failed: {e}")

try:
    import imageio_ffmpeg
    print(f"✅ imageio_ffmpeg imported successfully: {imageio_ffmpeg.get_ffmpeg_exe()}")
except ImportError as e:
    print(f"❌ imageio_ffmpeg import failed: {e}")

try:
    from PIL import Image
    print("✅ PIL imported successfully")
except ImportError as e:
    print(f"❌ PIL import failed: {e}")

try:
    import numpy
    print("✅ numpy imported successfully")
except ImportError as e:
    print(f"❌ numpy import failed: {e}")
