from socket import *
import sys

import os
import hashlib

CACHE_DIR = "cache"

def get_cache_path(url):
    hashed_url = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, hashed_url)

def proxyCache(portNo):

    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    try:
        tcpSerSock = socket(AF_INET, SOCK_STREAM)
        tcpSerSock.bind(("0.0.0.0", portNo))
        tcpSerSock.listen(5)
        print(f"Proxy server started on port {portNo}")
    except Exception as e:
        print(f"Error starting proxy server: {e}")
        sys.exit(1)

    while True:
        print("Ready to serve...")
        try:
            tcpCliSock, addr = tcpSerSock.accept()
            print(f"Received a connection from: {addr}")
            message = tcpCliSock.recv(4096).decode()

            if not message:
                print("No message received, closing connection.")
                tcpCliSock.close()
                continue

            request_line = message.split("\n")[0]
            print(f"Request Line: {request_line}")
            url = request_line.split(" ")[1]

            cache_path = get_cache_path(url)

            if os.path.exists(cache_path):
                print(f"Cache hit for {url}")
                with open(cache_path, "rb") as cache_file:
                    cached_response = cache_file.read()
                tcpCliSock.sendall(cached_response)
                tcpCliSock.close()
                continue

            print("Cache miss, fetching from server.")

            http_pos = url.find("://")
            temp = url[(http_pos+3):] if http_pos != -1 else url
            port_pos = temp.find(":")
            path_pos = temp.find("/")
            if path_pos == -1:
                path_pos = len(temp)

            webserver = temp[:port_pos] if port_pos != -1 and port_pos < path_pos else temp[:path_pos]
            port = int(temp[(port_pos+1):path_pos]) if port_pos != -1 and port_pos < path_pos else 80
            path = temp[path_pos:]

            print(f"Connecting to webserver: {webserver}, port: {port}, path: {path}")

            webSock = socket(AF_INET, SOCK_STREAM)
            webSock.connect((webserver, port))

            headers_and_body = message.split("\n", 1)[1]
            request_line = f"{request_line.split(' ')[0]} {path} HTTP/1.1"
            host_header = f"Host: {webserver}\r\n"

            headers = headers_and_body.split("\n")
            headers = [h for h in headers if not h.lower().startswith("host:")]
            headers.insert(0, host_header)

            formatted_headers = "\r\n".join(headers).strip()
            http_request = f"{request_line}\r\n{formatted_headers}\r\n\r\n"

            webSock.sendall(http_request.encode())

            response = b""
            while True:
                data = webSock.recv(4096)
                if not data:
                    break
                response += data
                tcpCliSock.sendall(data)

            with open(cache_path, "wb") as cache_file:
                cache_file.write(response)

            webSock.close()
            print("Reply forwarded to client and cached.")

        except KeyboardInterrupt:
            print("Proxy server shutting down.")
            tcpSerSock.close()
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            tcpCliSock.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Type: text/plain\r\n\r\nBad Gateway")
        finally:
            tcpCliSock.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 proxyCache.py proxyTCPPort")
        sys.exit(1)
    else:
        proxyCache(int(sys.argv[1]))