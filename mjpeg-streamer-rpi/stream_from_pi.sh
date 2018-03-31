raspistill --nopreview -vf -hf -w 640 -h 480 -q 5 -o /tmp/stream/pic.jpg -tl 100 -t 9999999 -th 0:0:0 &

until LD_LIBRARY_PATH=/usr/local/lib mjpg_streamer -i "input_file.so -f /tmp/stream -n pic.jpg" -o "output_http.so -w /usr/local/www"; do
	echo "mjpg-streamer crashed with exit code $?.  Respawning.." >&2
	sleep 1
done
