#!/usr/bin/bash
count=0
while [ $count -lt 20 ]; do
  curl 127.0.0.1:8080/fcgi-bin/async.fcgi &
  #echo "Done $count"
  count=$((count + 1))
done

wait
