per https://medium.com/@tom.humph/saving-rtsp-camera-streams-with-ffmpeg-baab7e80d767

ffmpeg -re -stream_loop -1 -i list.txt -c copy  -f flv "rtmp://a.rtmp.youtube.com/live2/mh4g-ap4u-gp0y-ezaw-66bg"
Using wallclock is cool

