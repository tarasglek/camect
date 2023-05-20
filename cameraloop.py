import time
import psutil
import os
import os
import signal
import subprocess
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

SWITCH_TIME = 10
def run_ffmpeg_in_background(ip, password):
    command = (f"ffmpeg -hide_banner -y -loglevel quiet -rtsp_transport tcp -use_wallclock_as_timestamps 1 -i rtsp://admin:{password}@{ip}:554/h264Preview_01_main -vcodec copy -acodec copy -f segment -reset_timestamps 1 -segment_time {SWITCH_TIME} -segment_format mkv -segment_atclocktime 1 -strftime 1 {ip}-%S.mkv")
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
    cameras = ['172.16.1.151', '172.16.1.61', '172.16.1.60']
    for ip in cameras:
        run_ffmpeg_in_background(ip, 'secret00')
    current_camera = 0
    while True:
        time.sleep(SWITCH_TIME)
        ip = cameras[current_camera]
        # list files starting with ip, sort by date(oldest->newest)
        files = sorted([f for f in os.listdir('.') if f.startswith(ip)], key=os.path.getctime)
        # remove all except last 2 files
        for f in files[:-2]:
            logging.info(f"rm {f}")
            os.remove(f)
        # rename second to last file to current.mkv
        if len(files) > 1:
            logging.info(f"mv {files[-2]} current.mkv")
            os.rename(files[-2], 'current.mkv')
        current_camera = (current_camera + 1) % len(cameras)
        


if __name__ == "__main__":
    try:
        main()
    finally:
        kill_child_processes(os.getpid())

    # Your code here