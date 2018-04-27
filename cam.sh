raspivid -o - -t 0 -w 1280 -h 720 -fps 25 -rot 180|cvlc stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264
