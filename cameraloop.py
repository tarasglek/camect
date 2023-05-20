import time
import psutil
import os
import os
import signal
import subprocess
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run_ffmpeg_in_background(ip, password):
    command = (f"ffmpeg -hide_banner -y -loglevel error -rtsp_transport tcp -use_wallclock_as_timestamps 1 -i rtsp://admin:{password}@{ip}:554/h264Preview_01_main -vcodec copy -acodec copy -f segment -reset_timestamps 1 -segment_time 30 -segment_format mkv -segment_atclocktime 1 -strftime 1 {ip}-%S.mkv")
    logging.debug(command)
    subprocess.Popen(command, shell=True)


def kill_child_processes(parent_pid, sig=signal.SIGKILL):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        logging.debug(f"killing {process}")
        process.send_signal(sig)


def main():
    cameras = ['172.16.1.151', '172.16.1.61']
    for ip in cameras:
        run_ffmpeg_in_background(ip, 'secret00')
    current_camera = 0
    while True:
        time.sleep(1)
        ip = cameras[current_camera]
        # list files starting with ip, sort by date
        files = sorted([f for f in os.listdir('.') if f.startswith('')], key=os.path.getctime)
        print([ip], files)
        


if __name__ == "__main__":
    try:
        main()
    finally:
        kill_child_processes(os.getpid())

    # Your code here