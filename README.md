per https://medium.com/@tom.humph/saving-rtsp-camera-streams-with-ffmpeg-baab7e80d767

Using wallclock is cool cos it segments at same second! and you can do math to know which file to show

172.16.1.61 poolcam

ffmpeg -hide_banner -y -loglevel error -rtsp_transport tcp -use_wallclock_as_timestamps 1 -i rtsp://admin:secret00@172.16.1.61:554/h264Preview_01_main -vcodec copy -acodec copy -f segment -reset_timestamps 1 -segment_time 30 -segment_format mkv -segment_atclocktime 1 -strftime 1 poolcam-%S.mkv

ffmpeg -hide_banner -y -loglevel error -rtsp_transport tcp -use_wallclock_as_timestamps 1 -i rtsp://admin:secret00@172.16.1.151:554/h264Preview_01_main -vcodec copy -acodec copy -f segment -reset_timestamps 1 -segment_time 30 -segment_format mkv -segment_atclocktime 1 -strftime 1 kitchen-%S.mkv

rtsp://admin:secret00@172.16.1.151:554/h264Preview_01_main

172.16.1.167

172.16.1.151

Changing playlist files on the fly ¶
The concat demuxer opens the referenced files only when they are needed. This allows us to swap the referenced files atomically behind the demuxers back to be able to use the concat demuxer as a changeable live source. Check out the following example file list.txt:

ffconcat version 1.0
file dummy.mxf
file dummy.mxf
dummy.mxf is referenced twice to make sure the concat demuxer reopens the file when it reaches it. Combine this with infinite looping and you are done:

ffmpeg -re -stream_loop -1 -i list.txt -flush_packets 0 -f mpegts udp://127.0.0.1:5000?pkt_size=1316
Now you can change the looping clip by a simple move command:

mv next_clip.mxf dummy.mxf