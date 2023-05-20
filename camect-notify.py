import logging
import os
import signal
import subprocess
import camect
import psutil

cameras = {}
SWITCH_TIME = 30

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
def kill_child_processes(parent_pid, sig=signal.SIGKILL):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        logging.debug(f"killing {process}")
        process.send_signal(sig)

def run_ffmpeg_in_background(rtsp_url, name):
    command = (f"ffmpeg -hide_banner -y -loglevel quiet -rtsp_transport tcp -use_wallclock_as_timestamps 1 -i {rtsp_url} -vcodec copy -acodec copy -f segment -reset_timestamps 1 -segment_time {SWITCH_TIME} -segment_format mkv -segment_atclocktime 1 -strftime 1 {name}-%S.mkv")
    logging.debug(command)
    subprocess.Popen(command, shell=True)

def event_handler(evt):
    global selected_camera
    selected_cam_id = evt['cam_id']
    if selected_cam_id not in cameras:
        return
    logging.debug(evt)
    files = sorted([f for f in os.listdir('.') if f.startswith(cameras[selected_cam_id]['name']+"-")], key=os.path.getctime)

    # remove all except last 2 files
    for f in files[:-2]:
        logging.info(f"rm {f}")
        os.remove(f)
    # rename second to last file to current.mkv
    if len(files) > 1:
        logging.info(f"mv {files[-2]} current.mkv")
        os.rename(files[-2], 'current.mkv')

def main():
    hub = camect.Hub("localhost:1443", "admin", "camect")
    hub.get_name()

    hub.add_event_listener(event_handler)
    for cam in hub.list_cameras():
        # print("%s(%s) @%s(%s)" % (cam["name"], cam["make"], cam["ip_addr"], cam["mac_addr"]))
        if cam['disabled'] or cam['width'] != 2560:
            continue
        cameras[cam['id']] = cam
        print(cam)
        run_ffmpeg_in_background(cam['url'], cam['name'])

        # {'type': 'alert', 'desc': 'dahua1 just saw a car.', 'url': 'https://home.camect.com/v2/#hid=9c30defc7117309c706869616ef90e33d3d3b5fa&cid=e5a9f79efb7e48011e0c&ts=1684578651731', 'cam_id': 'e5a9f79efb7e48011e0c', 'cam_name': 'dahua1', 'detected_obj': ['car'], 'roi': {'contour': [{'point': [{'x': 0, 'y': 0.46666667}, {'x': 0, 'y': 0.9777778}, {'x': 0.15, 'y': 0.9777778}, {'x': 0.25, 'y': 0.73333335}, {'x': 0.25, 'y': 0.46666667}]}], 'object': [{'name': 'car', 'min_size': 0.025592744, 'max_size': 0.07612895, 'contour': [{'point': [{'x': 0, 'y': 0.46666667}, {'x': 0, 'y': 0.9777778}, {'x': 0.15, 'y': 0.9777778}, {'x': 0.25, 'y': 0.73333335}, {'x': 0.25, 'y': 0.46666667}]}], 'movement_trace': {'point': [{'x': 0.04025797, 'y': 0.8194609}, {'x': 0.044361643, 'y': 0.8086955}, {'x': 0.051141232, 'y': 0.79492724}, {'x': 0.063685164, 'y': 0.78953326}, {'x': 0.06894589, 'y': 0.7726842}, {'x': 0.07509124, 'y': 0.76622856}, {'x': 0.08397496, 'y': 0.7457746}, {'x': 0.08830173, 'y': 0.7315779}, {'x': 0.09121147, 'y': 0.72335815}, {'x': 0.09332432, 'y': 0.7129498}, {'x': 0.0987061, 'y': 0.70022833}, {'x': 0.100109935, 'y': 0.6874583}, {'x': 0.106574856, 'y': 0.67280257}, {'x': 0.109288536, 'y': 0.66286653}, {'x': 0.11444146, 'y': 0.6518502}, {'x': 0.1191348, 'y': 0.6385877}, {'x': 0.1291431, 'y': 0.629067}, {'x': 0.14301409, 'y': 0.6159022}, {'x': 0.15867345, 'y': 0.6059053}, {'x': 0.16427214, 'y': 0.59848374}]}, 'vehicle_status': 2}]}}
    import time
    while True:
        time.sleep(1000)

if __name__ == "__main__":
    try:
        main()
    finally:
        kill_child_processes(os.getpid())