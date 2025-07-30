# moonshine.py
import os
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
os.environ['OPENCV_FFMPEG_LOGLEVEL'] = '-8'
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'

import imghdr
import base64
import urllib.parse
import requests
import mimetypes
import dataclasses
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Union
from concurrent.futures import ThreadPoolExecutor
import cv2
import math
import asyncio
import json

import platform
import subprocess
import threading
import time
import re
from io import BytesIO

# Private configuration
_CONFIG = {
    'api_token': None
}

_GLOBAL_API = "https://api.usemoonshine.com"

_MULTIPART_UPLOAD_THRESHOLD = 50 * 1024 * 1024 * 10000000  # 50 MB * 10000000
_PART_SIZE = 15 * 1024 * 1024  # 15 MB
_MAX_CONCURRENT_UPLOADS = 5

try:
    from PIL import ImageGrab, Image
    have_pil = True
except ImportError:
    have_pil = False
    print("Pillow is required for capturing displays. Install it with 'pip install Pillow'.")

try:
    import mss
    have_mss = True
except ImportError:
    have_mss = False
    print("mss is recommended for efficient screen capture. Install it with 'pip install mss'.")
    
@dataclasses.dataclass
class IPCamera:
    def __init__(self, username: str, password: str, ip_address: str, port: int = 554):
        """
        Initialize the IPCamera class with authentication details and IP configuration.
        """
        self.username = self.validate_username(username)
        self.password = self.validate_password(password)
        self.ip_address = self.validate_ip(ip_address)
        self.port = self.validate_port(port)

        self.rtsp_url = f"rtsp://{self.username}:{self.password}@{self.ip_address}:{self.port}/stream1"

    @staticmethod
    def validate_username(username: str) -> str:
        if not username or not isinstance(username, str):
            raise ValueError("Invalid username: must be a non-empty string.")
        return username

    @staticmethod
    def validate_password(password: str) -> str:
        if not password or not isinstance(password, str):
            raise ValueError("Invalid password: must be a non-empty string.")
        return password

    @staticmethod
    def validate_ip(ip_address: str) -> str:
        ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        if not re.match(ip_pattern, ip_address):
            raise ValueError("Invalid IP address format. Expected format: 'xxx.xxx.xxx.xxx'")
        return ip_address

    @staticmethod
    def validate_port(port: int) -> int:
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ValueError("Invalid port: must be an integer between 1 and 65535.")
        return port

    def get_url(self) -> str:
        """Return the formatted RTSP URL."""
        return self.rtsp_url

    def test_connection(self) -> bool:
        """Test the connection to the IP camera."""
        cap = cv2.VideoCapture(self.rtsp_url)
        if not cap.isOpened():
            return False
        cap.release()
        return True

@dataclasses.dataclass
class Stream:
    def __init__(self, index=None):
        self.device_id = None
        self.device_info = None
        self.available_sources = []
        self.stream_id = None
        
        if index is None:
            print("Warning: No Moonshine destination index provided. Streaming requires a destination index. Set one using <StreamOBJ>.destination(<index_name>).")
        else:
            self.destination(index)
            
    def destination(self, index):
        if not _CONFIG['api_token']:
            raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
        base_url = _GLOBAL_API + "/add-stream"
        
        payload = {
            'token': _CONFIG['api_token'], 
            'index': index
        }
        
        try:
            response = requests.post(base_url, json=payload)
            response.raise_for_status()
            check = response.json().get('status')
            if check == 'success':
                self.stream_id = response.json().get('stream_id')
                print(f"Stream destination set to index {index}.")
            elif response.json().get('error') == 'index does not exist':
                print(f"Index {index} does not exist. Create it first using moonshine.create_index(index='{index}', performance=True).")
            elif response.json().get('error') == 'this index is not compatible with streaming':
                print(f"Index {index} is not compatible with streaming. Create a performance index first by running moonshine.create_index(index=<name>, performance=True).")
            else:
                print(f"Failed to set stream destination: {response.json().get('error')}")
        except requests.RequestException as e:
            raise requests.RequestException(f"API request failed: {str(e)}")
        
    def sources(self, max_cameras=None, verbose=True):
        """List available sources (cameras and screens) and their names."""
        self.available_sources = []
        device_id = 0  # Start device_id counter

        # If max_cameras is None, detect the number of connected cameras
        if max_cameras is None:
            max_cameras = self._get_camera_count()

        # First, detect cameras
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._check_camera, i) for i in range(max_cameras)]
            for i, future in enumerate(futures):
                if future.result() is not None:
                    name = self._get_device_name(i)
                    # Make a source dict for the camera
                    source_info = {
                        'id': device_id,
                        'name': name,
                        'type': 'camera',
                        'index': i,  # The OpenCV index for the camera
                    }
                    self.available_sources.append(source_info)
                    device_id += 1

        # Now, detect screens
        displays = self._get_displays()
        for display in displays:
            source_info = {
                'id': device_id,
                'name': f"{display['name']} ({display['resolution']})",
                'type': 'screen',
                'display_info': display,  # Save the display info
            }
            self.available_sources.append(source_info)
            device_id += 1

        # Now, print the available sources if verbose
        if verbose:
            if self.available_sources:
                source_count = len(self.available_sources)
                print(f"\033[1m{source_count} Sources Detected\033[0m")
                print("=" * 50)
                print(f"{'Device':<10}{'Camera or Screen':<40}")
                print("-" * 50)
                for source in self.available_sources:
                    index = source['id']
                    name = source['name']
                    print(f"{index:<10}{name:<40}")
                print("=" * 50)
            else:
                print("\nNo video sources found.")
                print("Ensure your cameras/screens are connected and accessible.")

    def set(self, device_id=None):
        """Set the device the stream class is connected to."""
        if device_id is None:
            raise ValueError("Enter a valid device ID. Use <StreamOBJ>.sources() to get a list of available sources.")
        try:
            device_id = int(device_id)
        except (ValueError, TypeError):
            raise ValueError("Enter a valid device ID. Use <StreamOBJ>.sources() to get a list of available sources.")

        # Check if the device_id exists in available_sources
        if not any(source['id'] == device_id for source in self.available_sources):
            self.sources(verbose=False)
            if not any(source['id'] == device_id for source in self.available_sources):
                raise ValueError(f"Device ID {device_id} is not in the list of available stream sources.")

        # Set device_id and store device info
        self.device_id = device_id
        self.device_info = next((source for source in self.available_sources if source['id'] == device_id), None)
        if self.device_info:
            print(f"{self.device_info['name']} set as source")
        else:
            print(f"Device {device_id} set as source")

    def start(self, timeout=None):
        """Connect to source and start streaming protocol asynchronously."""
        
        if self.stream_id is None:
            raise Exception("Stream destination not set. Use <StreamOBJ>.destination(<index_name>) to set the destination index.")
        
        if self.device_id is None or self.device_info is None:
            raise Exception("Device not set. Use <StreamOBJ>.set(device_id) to set the device.")

        device_type = self.device_info.get('type')

        start_time = time.time()
        stop_event = threading.Event()
        max_workers = 5  # Set the maximum number of threads
        executor = ThreadPoolExecutor(max_workers=max_workers)

        stream_stopped = False
        stream_paused_info = {'paused': False, 'start_time': 0}

        try:
            if device_type == 'camera':
                # Camera capture code
                print(f"Connecting to camera source {self.device_info['name']}", end='\r')
                cap = cv2.VideoCapture(self.device_info['index'])  # Use the OpenCV index
                if not cap.isOpened():
                    raise Exception(f"Unable to connect to camera source with device ID {self.device_id}.")

                def process_frame():
                    nonlocal stream_stopped, stream_paused_info
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to read frame from camera.")
                        return

                    # Encode frame as PNG in memory
                    success, buffer = cv2.imencode('.png', frame)
                    if not success:
                        print("Failed to encode frame.")
                        return

                    # Base64 encode the image
                    image_bytes = buffer.tobytes()
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')

                    # Build the payload
                    payload = {
                        'base64_image': base64_image,
                        'stream_id': self.stream_id,
                        'time': int(time.time())
                    }

                    # Send the POST request
                    api_url = _GLOBAL_API + '/stream'
                    try:
                        response = requests.post(api_url, json=payload)
                        response.raise_for_status()
                        result = response.json()
                        if 'success' not in result:
                            print(f"Server reported failure: {result}")
                            stream_paused_info['paused'] = False
                        elif result.get('success') is False:
                            action = result.get('action')
                            if action == 'paused':
                                if not stream_paused_info['paused']:
                                    stream_paused_info['paused'] = True
                                    stream_paused_info['start_time'] = time.time()
                            elif action == 'stopped':
                                stream_stopped = True
                            else:
                                stream_paused_info['paused'] = False
                                print(f"Server reported failure: {result}")
                        else: # success == True
                            stream_paused_info['paused'] = False

                    except Exception as e:
                        print(f"Failed to send camera streaming packet: {e}")
                        stream_paused_info['paused'] = False

                # Main loop to schedule frame processing every second
                while not stream_stopped:
                    elapsed_time = int(time.time() - start_time)
                    if timeout is not None and elapsed_time >= timeout:
                        print(f"Timeout reached after {elapsed_time} seconds.")
                        break

                    # Submit the frame processing task to the executor
                    executor.submit(process_frame)

                    if stream_paused_info['paused']:
                        paused_duration = int(time.time() - stream_paused_info['start_time'])
                        print(f"Stream paused for {paused_duration} seconds", end='\r')
                    else:
                        print(f"{elapsed_time} seconds", end='\r')

                    # Sleep until the next second
                    time.sleep(1)
                
                if stream_stopped:
                    print(f"{' ' * 100}", end='\r')
                    print('Stream has been stopped.')

            elif device_type == 'screen':
                # Screen capture code
                print(f"Capturing from screen source {self.device_info['name']}", end='\r')
                display_info = self.device_info['display_info']

                x = display_info['x']
                y = display_info['y']
                width = display_info['width']
                height = display_info['height']

                def process_screenshot():
                    nonlocal stream_stopped, stream_paused_info
                    if have_mss:
                        # Use mss for efficient screen capture
                        with mss.mss() as sct:
                            monitor = {
                                "left": x,
                                "top": y,
                                "width": width,
                                "height": height
                            }
                            screenshot = sct.grab(monitor)
                            # Convert to image bytes
                            image = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
                    elif have_pil:
                        # Use PIL.ImageGrab as a fallback
                        bbox = (x, y, x + width, y + height)
                        image = ImageGrab.grab(bbox=bbox)
                    else:
                        # Use platform-specific commands as a last resort
                        system = platform.system()
                        if system == 'Darwin':
                            # macOS screenshot using screencapture
                            cmd = ['screencapture', '-x', '-R', f"{x},{y},{width},{height}", '-']
                            result = subprocess.run(cmd, capture_output=True)
                            if result.returncode != 0:
                                print(f"Failed to capture screenshot: {result.stderr.decode().strip()}")
                                return
                            image_bytes = result.stdout
                            image = Image.open(BytesIO(image_bytes))
                        elif system == 'Linux':
                            # Linux screenshot using import command from ImageMagick
                            cmd = ['import', '-window', 'root', '-crop', f"{width}x{height}+{x}+{y}", 'png:-']
                            result = subprocess.run(cmd, capture_output=True)
                            if result.returncode != 0:
                                print(f"Failed to capture screenshot: {result.stderr.decode().strip()}")
                                return
                            image_bytes = result.stdout
                            image = Image.open(BytesIO(image_bytes))
                        else:
                            print("Screen capture is not supported on this platform without Pillow or MSS.")
                            return

                    # Convert image to bytes
                    buffer = BytesIO()
                    image.save(buffer, format='PNG')
                    image_bytes = buffer.getvalue()
                    buffer.close()

                    # Base64 encode
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')

                    # Build payload and send
                    payload = {
                        'base64_image': base64_image,
                        'stream_id': self.stream_id,
                        'time': int(time.time())
                    }

                    api_url = _GLOBAL_API + '/stream'
                    try:
                        response = requests.post(api_url, json=payload)
                        response.raise_for_status()
                        result = response.json()
                        if 'success' not in result:
                            print(f"Server reported failure: {result}")
                            stream_paused_info['paused'] = False
                        elif result.get('success') is False:
                            action = result.get('action')
                            if action == 'paused':
                                if not stream_paused_info['paused']:
                                    stream_paused_info['paused'] = True
                                    stream_paused_info['start_time'] = time.time()
                            elif action == 'stopped':
                                stream_stopped = True
                            else:
                                stream_paused_info['paused'] = False
                                print(f"Server reported failure: {result}")
                        else: # success == True
                            stream_paused_info['paused'] = False
                    except Exception as e:
                        print(f"Failed to send display streaming packet: {e}")
                        stream_paused_info['paused'] = False

                # Main loop to schedule screenshot processing every second
                while not stream_stopped:
                    elapsed_time = int(time.time() - start_time)
                    if timeout is not None and elapsed_time >= timeout:
                        print(f"Timeout reached after {elapsed_time} seconds.")
                        break

                    # Submit the screenshot processing task to the executor
                    executor.submit(process_screenshot)

                    if stream_paused_info['paused']:
                        paused_duration = int(time.time() - stream_paused_info['start_time'])
                        print(f"Stream paused for {paused_duration} seconds", end='\r')
                    else:
                        print(f"{elapsed_time} seconds", end='\r')

                    # Sleep until the next second
                    time.sleep(1)

                if stream_stopped:
                    print(f"{' ' * 100}", end='\r')
                    print('Stream has been stopped.')

            else:
                raise Exception(f"Unknown device type '{device_type}' for device ID {self.device_id}.")

        except KeyboardInterrupt:
            print(f"\nStreamed for {int(time.time() - start_time)} seconds.")
            print("Stopped by user.")
        finally:
            # Release resources
            if device_type == 'camera':
                cap.release()

            executor.shutdown(wait=True)

    def _check_camera(self, index):
        """Check if a camera is available at the given index."""
        os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW if os.name == 'nt' else 0)
        if cap is not None and cap.isOpened():
            cap.release()
            return index
        if cap:
            cap.release()
        return None

    def _get_device_name(self, index):
        """Retrieve device name for the given index."""
        system = platform.system()
        if system == "Windows":
            try:
                import win32com.client
                wmi = win32com.client.GetObject("winmgmts:")
                devices = wmi.InstancesOf("Win32_PnPEntity")
                camera_devices = []
                for device in devices:
                    if 'Camera' in device.Caption or 'cam' in device.Caption.lower() or 'Video' in device.Caption:
                        camera_devices.append(device.Caption)
                return camera_devices[index] if index < len(camera_devices) else f"Camera {index}"
            except ImportError:
                print("Install pywin32 to enable device name retrieval on Windows. Use 'pip install pywin32'.")
                return f"Camera {index}"
            except Exception:
                return f"Camera {index}"
        elif system == "Linux":
            try:
                result = subprocess.run(
                    ["v4l2-ctl", "--list-devices"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
                devices = result.stdout.strip().split("\n\n")
                device_dict = {}
                for device_info in devices:
                    lines = device_info.strip().split("\n")
                    device_name = lines[0]
                    device_nodes = [line.strip() for line in lines[1:] if line.strip().startswith('/dev/video')]
                    for node in device_nodes:
                        device_index = int(node.replace('/dev/video', ''))
                        device_dict[device_index] = device_name
                return device_dict.get(index, f"Camera {index}")
            except FileNotFoundError:
                print("Install v4l-utils to enable device name retrieval on Linux. Use 'sudo apt-get install v4l-utils'.")
                return f"Camera {index}"
            except Exception:
                return f"Camera {index}"
        elif system == "Darwin":  # macOS
            try:
                result = subprocess.run(
                    ["system_profiler", "SPCameraDataType"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
                lines = result.stdout.splitlines()
                camera_names = []
                for line in lines:
                    line = line.strip()
                    if line.startswith("Model ID:"):
                        camera_names.append(line.split("Model ID:")[1].strip())
                return camera_names[index] if index < len(camera_names) else f"Camera {index}"
            except Exception:
                return f"Camera {index}"
        return f"Camera {index}"

    def _get_camera_count(self):
        """Returns the number of connected cameras."""
        system = platform.system()
        if system == 'Windows':
            try:
                import win32com.client
                wmi = win32com.client.GetObject("winmgmts:")
                devices = wmi.InstancesOf("Win32_PnPEntity")
                camera_devices = [device for device in devices if 'Camera' in device.Caption or 'cam' in device.Caption.lower() or 'Video' in device.Caption]
                return len(camera_devices)
            except ImportError:
                print("Install pywin32 to enable camera detection on Windows. Use 'pip install pywin32'.")
                return 10  # default to 10
            except Exception:
                return 10  # default to 10
        elif system == 'Linux':
            try:
                output = subprocess.check_output("ls /dev/video* 2>/dev/null", shell=True).decode()
                devices = output.strip().split('\n')
                return len([dev for dev in devices if re.match(r'/dev/video\d+', dev)])
            except Exception:
                return 10  # default to 10
        elif system == 'Darwin':  # macOS
            try:
                result = subprocess.run(["system_profiler", "SPCameraDataType"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
                lines = result.stdout.splitlines()
                camera_count = 0
                for line in lines:
                    line = line.strip()
                    if line.startswith("Model ID:"):
                        camera_count += 1
                return camera_count if camera_count > 0 else 10  # default to 10 if no cameras found
            except Exception:
                return 10  # default
        else:
            return 10  # default

    def _get_displays(self):
        """Detects displays based on the operating system."""
        system = platform.system()
        if system == 'Darwin':
            displays = self._get_displays_mac()
        elif system == 'Windows':
            displays = self._get_displays_windows()
        elif system == 'Linux':
            displays = self._get_displays_linux()
        else:
            print(f"Unsupported operating system: {system}")
            displays = []

        return displays

    def _get_displays_mac(self):
        import plistlib
        import subprocess
        try:
            import Quartz
        except ImportError:
            print("Install pyobjc-framework-Quartz to get display information on macOS.")
            return []

        # Run system_profiler command to get display information
        cmd = ['system_profiler', 'SPDisplaysDataType', '-xml']
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse the plist XML output
        plist_data = plistlib.loads(result.stdout.encode('utf-8'))

        # Extract display information
        displays = []

        # Get active displays and their bounds
        maxDisplays = 16  # Set this to the maximum number of displays you expect
        (err, activeDisplays, displayCount) = Quartz.CGGetActiveDisplayList(maxDisplays, None, None)
        if err != 0:
            raise Exception(f"CGGetActiveDisplayList error: {err}")

        display_bounds = {}
        for displayID in activeDisplays:
            bounds = Quartz.CGDisplayBounds(displayID)
            width = Quartz.CGDisplayPixelsWide(displayID)
            height = Quartz.CGDisplayPixelsHigh(displayID)
            display_bounds[displayID] = {
                'bounds': bounds,
                'width': width,
                'height': height,
                'x': int(bounds.origin.x),
                'y': int(bounds.origin.y)
            }

        # Now get the display info
        for display_dict in plist_data[0]['_items']:
            for display in display_dict.get('spdisplays_ndrvs', []):
                display_info = {
                    'name': display.get('_name', 'Unknown'),
                    'resolution': None,
                    'is_primary': False,
                    'is_built_in': False,
                    'id': display.get('spdisplays_display-id') or display.get('_spdisplays_displayID')
                }

                # Check for primary display status
                is_main = display.get('spdisplays_main')
                display_info['is_primary'] = (is_main is True) or (isinstance(is_main, str) and 'yes' in is_main.lower())

                # Check for built-in display status
                if '_name' in display and 'Color LCD' in display['_name']:
                    display_info['is_built_in'] = True
                elif 'spdisplays_builtin' in display and display['spdisplays_builtin'] is True:
                    display_info['is_built_in'] = True

                # Try different resolution keys in order of preference
                if 'spdisplays_resolution' in display:
                    display_info['resolution'] = display['spdisplays_resolution']
                elif '_spdisplays_resolution' in display:
                    display_info['resolution'] = display['_spdisplays_resolution']
                elif '_spdisplays_pixels' in display:
                    display_info['resolution'] = display['_spdisplays_pixels']

                # Convert display ID to int
                display_id = display_info['id']
                if display_id is not None:
                    if isinstance(display_id, str):
                        display_id = int(display_id, 0)  # Handles hex and decimal
                    elif not isinstance(display_id, int):
                        display_id = int(display_id)
                    display_info['id'] = display_id

                # Get the position and size from display_bounds
                if display_id in display_bounds:
                    bounds_info = display_bounds[display_id]
                    display_info.update({
                        'x': bounds_info['x'],
                        'y': bounds_info['y'],
                        'width': bounds_info['width'],
                        'height': bounds_info['height']
                    })
                else:
                    # If not found, use default screen size
                    main_display_id = Quartz.CGMainDisplayID()
                    screen_size = (
                        Quartz.CGDisplayPixelsWide(main_display_id),
                        Quartz.CGDisplayPixelsHigh(main_display_id),
                    )
                    display_info.update({
                        'x': 0,
                        'y': 0,
                        'width': screen_size[0],
                        'height': screen_size[1]
                    })
                displays.append(display_info)
        return displays

    def _get_displays_windows(self):
        try:
            import win32api
            import win32con
        except ImportError:
            print("Install pywin32 to get display information on Windows.")
            return []

        monitors = []
        for m in win32api.EnumDisplayMonitors():
            monitor_info = win32api.GetMonitorInfo(m[0])
            monitor_rect = monitor_info['Monitor']
            is_primary = bool(monitor_info.get('Flags', 0) & win32con.MONITORINFOF_PRIMARY)
            name = monitor_info.get('Device', 'Unknown')
            x = monitor_rect[0]
            y = monitor_rect[1]
            width = monitor_rect[2] - monitor_rect[0]
            height = monitor_rect[3] - monitor_rect[1]
            display = {
                'name': name,
                'resolution': f'{width}x{height}',
                'is_primary': is_primary,
                'is_built_in': False,  # Windows doesn't provide built-in status
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }
            monitors.append(display)
        return monitors

    def _get_displays_linux(self):
        # Use xrandr to get display info
        displays = []
        try:
            xrandr_output = subprocess.check_output('xrandr --listactivemonitors', shell=True).decode()
            lines = xrandr_output.strip().split('\n')
            for line in lines[1:]:
                # Example line: " 0: +*eDP-1 1920/344x1080/194+0+0  eDP-1"
                match = re.search(r'\s*(\d+):\s+\+(\*?)([^\s]+)\s+(\d+)/[^\s]+\s*x\s*(\d+)/[^\s]+\+(\d+)\+(\d+)\s+([^\s]+)', line)
                if match:
                    index = int(match.group(1))
                    is_primary = '*' in match.group(2)
                    name = match.group(3)
                    width = int(match.group(4))
                    height = int(match.group(5))
                    x = int(match.group(6))
                    y = int(match.group(7))
                    display = {
                        'name': name,
                        'resolution': f'{width}x{height}',
                        'is_primary': is_primary,
                        'is_built_in': False,  # Not easy to determine built-in status
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height
                    }
                    displays.append(display)
        except Exception as e:
            print(f"Failed to get displays using xrandr: {e}")
            # As a fallback, use the display size from tkinter
            try:
                from tkinter import Tk
                root = Tk()
                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()
                root.destroy()
                display = {
                    'name': 'Default Screen',
                    'resolution': f'{screen_width}x{screen_height}',
                    'is_primary': True,
                    'is_built_in': False,
                    'x': 0,
                    'y': 0,
                    'width': screen_width,
                    'height': screen_height
                }
                displays.append(display)
            except Exception as e:
                print(f"Failed to get screen size using tkinter: {e}")
        return displays

@dataclasses.dataclass
class VideoTarget:
    """
    Represents a video target for Moonshine tasks.
    
    Attributes:
        file_id (str): The target video ID.
        timestamp (Optional[float]): The target timestamp. Defaults to None.
    
    Raises:
        ValueError: If file_id is not provided.
    """
    file_id: str
    timestamp: Optional[float] = None

    def __post_init__(self):
        """
        Validate that both timestamp and file_id are provided.
        
        This method is automatically called after object initialization.
        """
        if self.file_id is None:
            raise ValueError("File ID must be provided")

# Private helper functions
def _is_video(filename: str) -> bool:
    """Determine if a file is a video based on its extension."""
    video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'}
    return os.path.splitext(filename.lower())[1] in video_extensions

def _get_video_info(filename: str) -> tuple[Optional[float], Optional[float]]:
    """Get video duration in seconds and FPS using OpenCV."""
    try:
        video = cv2.VideoCapture(filename)
        if not video.isOpened():
            return None, None
            
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        video.release()
        
        return duration, fps
        
    except Exception as e:
        print(f"Error reading video file: {e}")
        return None, None
    
def _does_bucket_exist(index: str) -> bool:
    """
    Check if a bucket exists in the Moonshine API.
    
    Args:
        index (str): The index to check
    
    Returns:
        bool: True if the bucket exists, False otherwise
        
    Raises:
        ValueError: If API token is not configured
        requests.RequestException: If the API request fails
    """
    if not _CONFIG['api_token']:
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
    base_url = _GLOBAL_API + "/does-group-exist"
    
    payload = {
        'token': _CONFIG['api_token'], 
        'index': index
    }
    
    try:
        # Use a POST request with JSON payload
        response = requests.post(base_url, json=payload)
        response.raise_for_status()
        return response.json().get('exists', False)
    except requests.RequestException as e:
        raise requests.RequestException(f"API request failed: {str(e)}")

def _get_file_info(filepath: str) -> tuple[int, str]:
    """Determine which bucket to use based on file size and type."""
    file_size = os.path.getsize(filepath)
    content_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
    
    return file_size, content_type

def _upload_part(s3_client: Any, bucket: str, key: str, upload_id: str, 
                part_number: int, data: bytes) -> Dict:
    """Upload a single part of a multipart upload."""
    response = s3_client.upload_part(
        Bucket=bucket,
        Key=key,
        UploadId=upload_id,
        PartNumber=part_number,
        Body=data
    )
    return {
        'PartNumber': part_number,
        'ETag': response['ETag']
    }
    
async def _upload_remote_file(
    src: str, 
    index: str, 
    progress_callback: Optional[Callable[[dict], None]] = None
) -> Optional[str]:
    """Upload a remote file using a signed URL."""
    
    if not _CONFIG.get('api_token'):
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")

    url = _GLOBAL_API + "/remote-upload"
    event_payload = {
        "url": src,
        "index": index,
        "token": _CONFIG.get('api_token')
    }
    
    file_id = None
    file_size = None

    # Define a function to process the server-sent events (SSE)
    def process_sse(response):
        for line in response.iter_lines():
            if line: 
                try:
                    data_str = line.decode('utf-8').strip()
                    if data_str.startswith("data: "):
                        data_str = data_str[6:]
                        update = json.loads(data_str)
                        if update.get('type') == 'error':
                            return print(f"Error: {update}")
                        
                        if update.get('type') == 'metadata':
                            nonlocal file_size
                            file_size = update.get('fileSize')
                            print(f"Video duration: {update.get('duration')} seconds")
                            print(f"Video FPS: {update.get('fps')}")
                        
                        if update.get('type') == 'file_authorized':
                            nonlocal file_id
                            file_id = update.get('key')
                        
                        if progress_callback and update.get('type') == 'progress':
                            progress_callback({
                                'status': 'uploading',
                                'progress': update.get('percentage', 0),
                                'src': src,
                                'file_id': file_id
                            })
                            
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    continue

    # Make the POST request and stream the response
    response = requests.post(url, json=event_payload, stream=True)

    if response.status_code == 200:
        process_sse(response)
        return file_id, float(file_size[:-3]) > 650
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)
    
async def _get_signed_upload(
    filename: str, index: str, duration: Optional[float] = None,
    fps: Optional[int] = None, file_size: Optional[int] = None,
    content_type: Optional[str] = None
) -> Optional[str]:
    """Call the pre-upload API to get a file ID."""
    base_url = _GLOBAL_API + '/api-pre-upload'
    payload = {
        "filename": filename,
        "index": index,
        "duration": math.ceil(duration) if duration else None,
        "fps": round(fps) if fps else None,
        "filesize": file_size,
        "content": content_type or "application/octet-stream"
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(base_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('key'), data.get('url')
    except requests.RequestException as e:
        raise requests.RequestException(f"Error in API call: {str(e)}")

# Public functions
def moo() -> None:
    """Print a cow saying hello."""
    print("  __________________")
    print(" < MOO, its Harold! >")
    print("  ------------------")
    print("         \\   ^__^")
    print("          \\  (oo)\\_______")
    print("             (__)\\       )\\/\\")
    print("                 ||----w |")
    print("                 ||     ||")

def config(API: str) -> None:
    """
    Configure the Moonshine client with your API token.
    
    Args:
        API (str): Your Moonshine API token
    """
    base_url = _GLOBAL_API + "/check-token"
    
    params = {
        'token': API,
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        if (response.json()["valid"]):
            _CONFIG['api_token'] = API
        else:
            raise ValueError("Invalid API token")
    except requests.RequestException as e:
        raise requests.RequestException(f"Could not validate your token: {str(e)}")

def create(index: str, performance: bool = False) -> Dict:
    """
    Create a new Moonshine index.
    
    Args:
        index (str): The name of the index to create
        performance (bool): Create an optimized index for additional capabilities, like streaming. Incur additional costs.
    
    Returns:
        Dict: The API response
        
    Raises:
        ValueError: If API token is not configured
        requests.RequestException: If the API request fails
    """
    if not _CONFIG['api_token']:
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
    if _does_bucket_exist(index):
        raise ValueError(f"Index {index} already exists.")
    
    base_url = _GLOBAL_API + "/create-index"
    
    params = {
        'token': _CONFIG['api_token'],
        'index': index,
    }
    
    if performance:
        params['type'] = 'performance'
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"API request failed: {str(e)}")
    
    
def inquire(index: str, prompt: str, json: Optional[Dict[str, str]] = None, guidance: Optional[str] = None, 
            target: Optional[VideoTarget] = None, subindex: list = None) -> str:
    """
    Generate responses to a prompt using a Moonshine index.
    
    Args:
        index (str): The project/bucket ID to search in
        prompt (str): The prompt query
        json (Dict[str, str], optional): A dictionary where all keys and values must be strings
        guidance (str): Optional guidance to match your expected output
        target (VideoTarget): Optional grounding target timestamp 
        subindex (list, optional): List of video_ids to search within. Defaults to None (search all)
    
    Returns:
        str: The API response
        
    Raises:
        ValueError: If API token is not configured or json validation fails
        requests.RequestException: If the API request fails
    """
    if not _CONFIG['api_token']:
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
    # Validate subindex if provided
    if subindex is not None:
        if not isinstance(subindex, list) or not all(isinstance(i, str) for i in subindex):
            raise ValueError("subindex must be a list of strings")
        if len(subindex) == 0:
            raise ValueError("subindex cannot be an empty list")
    
    if prompt is None or len(prompt) == 0:
        raise ValueError("Prompt cannot be empty")
    
    # Validate json parameter if provided
    if json is not None:
        if not isinstance(json, dict):
            raise ValueError("json parameter must be a dictionary")
        
        # Check that all keys and values are strings
        for key, value in json.items():
            if not isinstance(key, str):
                raise ValueError(f"All keys in json parameter must be strings. Found key of type {type(key).__name__}")
            if not isinstance(value, str):
                raise ValueError(f"All values in json parameter must be strings. Found value of type {type(value).__name__} for key '{key}'")
    
    base_url = _GLOBAL_API + "/inquire"
    
    # Build request payload
    payload = {
        'project_id': _CONFIG['api_token'] + index,
        'prompt': prompt,
    }
    
    if subindex is not None:
        payload['subindex'] = subindex
    
    if guidance and isinstance(guidance, str) and len(guidance) > 0:
        payload['guidance'] = guidance
    
    if target:
        if isinstance(target, VideoTarget):
            if target.timestamp is not None:
                payload['target'] = target.timestamp
            if target.file_id is not None:
                payload['target_video'] = target.file_id
        else:
            raise ValueError("Target must be a VideoTarget object. Hint: moonshine.VideoTarget(timestamp, file_id)")
    
    # Add json parameter if provided (stringified)
    if json is not None:
        payload['json'] = json.dumps(json)
    
    try:
        response = requests.post(
            base_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=3000
        )
        response.raise_for_status()
        return response.json()['output']
    except requests.RequestException as e:
        raise requests.RequestException(f"API request failed: {str(e)}")

def search(index: str, query: str = None, image: str = None, num_args: int = 5, 
           threshold: int = 1000, subindex: list = None) -> Dict:
    """
    Search media using the Moonshine API. Supports both text and image-based searches.
    
    Args:
        index (str): The project/bucket ID to search in
        query (str, optional): The text search query
        image (str, optional): Path to the image file or URL for visual search
        num_args (int, optional): Number of search results to return. Defaults to 5
        threshold (int, optional): Search threshold for text-based queries. Defaults to 1000
        subindex (list, optional): List of video_ids to search within. Defaults to None (search all)
    
    Returns:
        Dict: The API response
        
    Raises:
        ValueError: If API token is not configured or if neither query nor image is provided
        FileNotFoundError: If the image file doesn't exist
        TypeError: If the provided file is not a valid image
        requests.RequestException: If the API request fails
    """
    if not _CONFIG['api_token']:
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
    if query is None and image is None:
        raise ValueError("Either 'query' or 'image' parameter must be provided")
    
    # Validate subindex if provided
    if subindex is not None:
        if not isinstance(subindex, list) or not all(isinstance(i, str) for i in subindex):
            raise ValueError("subindex must be a list of strings")
        if len(subindex) == 0:
            raise ValueError("subindex cannot be an empty list")
    
    # Build the base payload for the API request
    payload = {
        'project_id': _CONFIG['api_token'] + index,
        'api': _CONFIG['api_token'],
        'numargs': num_args,
        'threshold': threshold
    }
    
    # Add subindex to payload if provided
    if subindex is not None:
        payload['subindex'] = subindex
    
    # Handle image-based search
    if image is not None:
        # Check if image is a URL
        if isinstance(image, str) and (image.startswith('http://') or image.startswith('https://')):
            payload['image'] = image
        else:
            # Validate image file exists
            if not os.path.exists(image):
                raise FileNotFoundError(f"Image file not found: {image}")
            
            # Validate file is actually an image
            image_type = imghdr.what(image)
            if image_type is None:
                raise TypeError(f"File is not a valid image: {image}")
                
            # Read and encode image
            try:
                with open(image, 'rb') as img_file:
                    payload['image'] = base64.b64encode(img_file.read()).decode('utf-8')
            except Exception as e:
                raise Exception(f"Failed to read or encode image: {str(e)}")
    
    # Handle text-based search
    if query is not None:
        payload['query'] = query
    
    # Make the API request
    try:
        response = requests.post(_GLOBAL_API + "/search", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if response.status_code == 400:
            raise ValueError(response.json())
        raise requests.RequestException(f"API request failed: {str(e)}")

async def upload(src: str, index: str, 
                progress_callback: Optional[Callable[[dict], None]] = None) -> Union[str, bool]:
    """
    Upload a file from either a local path or remote URL with progress tracking.
    
    Args:
        src: Local file path or remote URL of the file to upload
        index: Project name/ID
        progress_callback: Optional callback function to report upload progress with detailed status
        
    Returns:
        str: File ID if upload successful
        bool: False if upload failed
        
    Raises:
        ValueError: If API token is not configured or project doesn't exist
    """
    if not _CONFIG['api_token']:
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
    if not _does_bucket_exist(index):
        raise ValueError(f"Index {index} doesn't exist. Create it first. Hint: moonshine.create('{index}')")
    
    index = _CONFIG['api_token'] + index
    file_id = None  # Initialize file_id to be accessible throughout the function
    
    try:
        # Handle remote URL vs local file path
        if src.startswith(('http://', 'https://')):
            file_id, is_large = await _upload_remote_file(src, index[60:], progress_callback)
            if not file_id:
                raise ValueError("Remote file upload failed")
            
            if progress_callback:
                progress_callback({
                    'status': 'uploading',
                    'progress': 100,
                    'src': src,
                    'file_id': file_id
                })
                
            large_file = is_large
                
        else:
            # Original local file upload logic
            filename = os.path.basename(src)
            file_size = os.path.getsize(src)
            # Get file metadata
            duration = None
            fps = None
            file_size, content_type = _get_file_info(src)
            large_file = file_size > 1e9
            
            if _is_video(src) and content_type.startswith('video/'):
                duration, fps = _get_video_info(src)
                print(f"Video duration: {duration:.2f} seconds")
                print(f"Video FPS: {fps:.2f}")
                
                if large_file:
                    print("WARNING: This is a large format video file that will be transcoded before indexing. Indexing times may take longer.")
                
            else:
                raise ValueError("Only video files are supported.")
            
            # Get signed upload URL
            file_upload = await _get_signed_upload(filename, index, duration, fps, file_size, content_type)
            
            if not file_upload:
                raise ValueError("Unable to index media, insufficient account balance.")
            
            file_id, signed_upload_url = file_upload
            
            # Configure the requests session for uploads
            session = requests.Session()
            
            if file_size < _MULTIPART_UPLOAD_THRESHOLD:
                # Single-part upload
                with open(src, 'rb') as file:
                    response = session.put(
                        signed_upload_url,
                        data=_ProgressFileReader(file, file_size, 
                            lambda progress: progress_callback({
                                'status': 'uploading',
                                'progress': progress,
                                'src': src,
                                'file_id': file_id
                            }) if progress_callback else None),
                        headers={'Content-Type': content_type}
                    )
                    response.raise_for_status()
            
            if progress_callback:
                progress_callback({
                    'status': 'uploading',
                    'progress': 100,
                    'src': src,
                    'file_id': file_id
                })
        
        # Common post-upload processing for both local and remote files
        # Check transcoding status every 4 seconds
        while True and large_file:
            response = requests.get(
                _GLOBAL_API + '/compress-status',
                params={'video': file_id.split('.')[0]}
            )
            
            try:
                processing_status = int(response.json()['status'])
            except:
                processing_status = 0
            
            if progress_callback:
                progress_callback({
                    'status': 'transcoding',
                    'progress': min(math.floor(processing_status * (fps/30)), 100) if 'fps' in locals() else processing_status,
                    'src': src,
                    'file_id': file_id
                })
                    
            # Check if indexing is complete
            if processing_status >= 100:
                break
                
            # Wait 4 seconds before next check
            await asyncio.sleep(4)
            
        # Check indexing status every 4 seconds
        while True:
            response = requests.get(
                "https://www.moonshine-edge-compute.com" + '/status',
                params={'file_id': file_id}
            )
            processing_status = response.json()['status']
            processing_status = [int(status) for status in processing_status]
            
            # Calculate average progress (rounded down)
            avg_progress = math.floor(sum(processing_status) / len(processing_status))
            
            if progress_callback:
                progress_callback({
                    'status': 'indexing',
                    'progress': avg_progress,
                    'src': src,
                    'file_id': file_id
                })
            
            # Check if indexing is complete
            if avg_progress >= 100:
                break
                
            # Wait 4 seconds before next check
            await asyncio.sleep(4)
        
        return file_id
        
    except Exception as e:
        print(f"Upload failed: {str(e)}")
        return False
    
def remove(index: str, video_id: str) -> Dict:
    """
    Remove a video from the Moonshine index permanently.
    
    Args:
        index (str): The project/bucket ID where the video resides
        video_id (str): The ID of the video to be removed
    
    Returns:
        Dict: The API response indicating success or failure
        
    Raises:
        ValueError: If API token is not configured
        requests.RequestException: If the API request fails
    """
    if not _CONFIG['api_token']:
        raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
    
    base_url = _GLOBAL_API + "/remove-from-index"
    
    payload = {
        'token': _CONFIG['api_token'],
        'project_id': index,
        'video_id': video_id
    }
    
    try:
        response = requests.post(
            base_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        # Parse and return the JSON response
        return response.json()
    
    except requests.HTTPError as e:
        # Handle specific HTTP errors based on status code
        if e.response.status_code == 400:
            raise ValueError("Invalid token provided.")
        elif e.response.status_code == 404:
            error_details = e.response.json().get('error', 'Unknown error')
            raise ValueError(f"Error: {error_details}")
        else:
            raise requests.RequestException(f"Unexpected HTTP error: {e.response.text}")
    except requests.RequestException as e:
        raise requests.RequestException(f"API request failed: {str(e)}")

def run(flow: str, **kwargs) -> Dict:
    """
    Execute a custom flow/endpoint with arbitrary parameters.
    
    Args:
        flow (str): The flow/endpoint name (e.g., "core/content-moderation")
        **kwargs: Arbitrary keyword arguments to be sent as payload parameters
    
    Returns:
        Dict: The API response
        
    Raises:
        ValueError: If API token is not configured or flow is not valid
        requests.RequestException: If the API request fails
    """
    if not flow or not isinstance(flow, str):
        raise ValueError("Flow parameter must be a non-empty string")
    
    # Validate and format the flow parameter
    formatted_flow = flow.strip()
    
    # Check if flow already has a prefix (core/, workflow/, or any other /)
    if '/' in formatted_flow:
        # Split by first slash to check the prefix
        parts = formatted_flow.split('/', 1)
        prefix = parts[0]
        flow_name = parts[1] if len(parts) > 1 else ""
        
        # If the flow name after the slash is empty, return error
        if not flow_name:
            raise ValueError("Invalid workflow: flow name cannot be empty")
        
        # If it already has a valid prefix, use as is
        if prefix in ["core", "workflow"]:
            pass  # Keep as is
        else:
            # If it has some other prefix, assume it's a core flow
            formatted_flow = f"core/{formatted_flow}"
    else:
        # No slash in flow, need to determine the type
        if formatted_flow.isdigit():
            # If flow is just numbers, it's a workflow ID
            formatted_flow = f"workflow/wf-{formatted_flow}"
        elif formatted_flow.startswith("wf-"):
            # If flow starts with wf-, it's a workflow
            formatted_flow = f"workflow/{formatted_flow}"
        else:
            # Otherwise, it's a core flow
            formatted_flow = f"core/{formatted_flow}"
    
    # Build the payload with all provided keyword arguments
    payload = kwargs.copy()
    
    # Add the API token to the payload if not already present
    if 'token' not in payload:
        if _CONFIG['api_token'] is None:
            raise ValueError("API token not configured. Call moonshine.config(API='your-token') first.")
        payload['token'] = _CONFIG['api_token']
    
    # Construct the API endpoint URL
    endpoint_url = _GLOBAL_API + "/" + formatted_flow
    
    try:
        response = requests.post(
            endpoint_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        # Handle 404 errors specifically
        if response.status_code == 404:
            raise ValueError(f"Flow '{formatted_flow}' is not valid or does not exist")
        
        response.raise_for_status()
        return response.json()
        
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Flow '{formatted_flow}' is not valid or does not exist")
        else:
            raise requests.RequestException(f"HTTP error {e.response.status_code}: {e.response.text}")
    except requests.RequestException as e:
        raise requests.RequestException(f"API request failed: {str(e)}")

class _ProgressFileReader:
    """Wrapper for file object that reports read progress only when whole number percentage changes."""
    def __init__(self, file, total_size, callback=None):
        self.file = file
        self.total_size = total_size
        self.callback = callback
        self.bytes_read = 0
        self.last_reported_progress = -1  # Initialize to -1 to ensure first progress is reported
        
    def __iter__(self):
        return self
    
    def __next__(self):
        data = self.read(8192)  # Read in 8KB chunks
        if not data:
            raise StopIteration
        return data
    
    def read(self, size=-1):
        data = self.file.read(size)
        self.bytes_read += len(data)
        
        if self.callback:
            # Calculate current progress rounded down to nearest whole number
            current_progress = int(self.bytes_read / self.total_size * 100)
            
            # Only call callback if the whole number progress has changed
            if current_progress > self.last_reported_progress:
                self.last_reported_progress = current_progress
                self.callback(current_progress)
        
        return data
    
    def __len__(self):
        return self.total_size

async def _upload_part_with_signed_url(
    session: requests.Session,
    signed_url: str,
    part_number: int,
    data: bytes,
    content_type: str
) -> str:
    """Upload a single part using a signed URL."""
    response = session.put(
        signed_url,
        data=data,
        headers={'Content-Type': content_type}
    )
    response.raise_for_status()
    return response.headers['ETag']