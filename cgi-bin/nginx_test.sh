#!/usr/bin/bash
count=0
while [ $count -lt 20 ]; do
  curl http://127.0.0.1/fastcgi_hello &
  #echo "Done $count"
  count=$((count + 1))
done

wait
