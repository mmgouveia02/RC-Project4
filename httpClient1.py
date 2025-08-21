#!/usr/bin/env python
import http.client
import sys
def doGet( http_server):
    #create a connection
    conn = http.client.HTTPConnection(http_server)

    while True:
        print("\nTwo commands are valid. Examples and explanation below:")
        print("GET /rc2425/index.html  ; the ẗext file contents will be written to stdout")
        print("GET /rc2425/docs/coco512.mp4 x.mp4 ; binary file contents will be written to x.mp4")
        cmd = input("input command: ")

        cmd = cmd.split()
        if cmd[0] == "exit": #tipe exit to end it
            return

        if cmd[0] == "GET":
            #request command to server
            conn.request(cmd[0], cmd[1])

            #get response from server
            rsp = conn.getresponse()

            #print server response and data
            print(rsp.status, rsp.reason)
            data_received = rsp.read()
            contentType=rsp.headers["Content-type"]
            typeOfContents = contentType.split("/")[0]
            if typeOfContents == "text":
                print(data_received)
            else:
                f = open(cmd[2], "wb")
                f.write(data_received)
                f.close()

            conn.close()
        else:
            print("Method not supported")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        hostName = sys.argv[1]
        doGet( hostName)
    else:
        print("Usage: python3 httpClient1 hostname")


