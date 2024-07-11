#!/bin/bash

# FastCGI loop
while true; do
    # Read FastCGI headers
    CONTENT_LENGTH=""
    while read -r LINE; do
        [ -z "$LINE" ] && break
        if [[ "$LINE" == Content-Length:* ]]; then
            CONTENT_LENGTH="${LINE#Content-Length: }"
        fi
    done

    # Read the POST data
    if [ -n "$CONTENT_LENGTH" ]; then
        read -n $CONTENT_LENGTH REQUEST_BODY
    fi

    # Output FastCGI response headers
    echo -ne "Status: 200 OK\r\nContent-Type: text/html\r\n\r\n"

    # Output HTML content
    echo "<html><head><title>FCGI Environment Variables</title></head><body>"
    echo "<h1>Environment Variables</h1>"
    echo "<table border=\"1\">"
    echo "<tr><th>Variable</th><th>Value</th></tr>"

    for VAR in $(printenv | sort); do
        echo "<tr><td>${VAR%%=*}</td><td>${VAR#*=}</td></tr>"
    done

    echo "</table>"
    echo "</body></html>"
done
