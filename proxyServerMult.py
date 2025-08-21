from socket import *
import sys
import threading

def proxyServer(portNo):

    tcpSerSock = socket(AF_INET, SOCK_STREAM)
    tcpSerSock.bind(("0.0.0.0", portNo))
    tcpSerSock.listen(5)

    while True:
        print('Ready to serve')
        try:
            tcpCliSock, addr = tcpSerSock.accept()
            clientThread = threading.Thread(target=handleClientConnection, args=(tcpCliSock,))
            clientThread.daemon = True
            clientThread.start()
        except KeyboardInterrupt:
            print("proxy exiting!")
            break
        print('Received a connection from:', addr)
    tcpSerSock.close()

def handleClientConnection(tcpCliSock):
    try:
        # Step 1: Receives request from the client
        request = tcpCliSock.recv(4096).decode()
        if not request:
            return

        # Parses the request and separate method, URL, and headers
        lines = request.splitlines()
        if len(lines) < 1:
            tcpCliSock.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            return

        firstLine = lines[0].split()
        if len(firstLine) < 2:
            tcpCliSock.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            return

        method = firstLine[0]
        url = firstLine[1]

        # Checks if the request method is GET
        if method != 'GET':
            tcpCliSock.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            return

        # Extracts the host and path from the URL
        if url.startswith("http://"):
            url = url[7:]  # Removes "http://"
        else:
            tcpCliSock.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            return

        host = url.split('/')[0]
        path = '/' + '/'.join(url.split('/')[1:]) if '/' in url else '/'

        print('Connecting to original destination')

        # Step 2: Connects to the original server
        try:
            serverSock = socket(AF_INET, SOCK_STREAM)
            serverSock.connect((host, 80))

            # Creates the request to forward to the original server
            server_request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            serverSock.send(server_request.encode())
        except Exception as e:
            tcpCliSock.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
            return

        print('Connected to original destination')

        # Step 3: Receives response from the original server
        response = b""
        while True:
            data = serverSock.recv(4096)
            if not data:
                break
            response += data

        print('received reply from http server')

        # Step 4: Forwards the server's response to the client
        tcpCliSock.sendall(response)
        print('reply forwarded to client')

    finally:
        # Close the sockets
        try:
            serverSock.close()
        except:
            pass
        tcpCliSock.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 proxyServer.py proxyTCPPort")
        sys.exit(1)
    else:
        proxyServer(int(sys.argv[1]))
        sys.exit(0)