import socket
import Feature_matching
import time

def listen():
    #Listen on port 9878
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('192.168.1.252', 9879)
    sock.bind(server_address)
    sock.listen(1)

    while True:
        print('Waiting for connection')
        #Accept incoming connection
        connection, client_address = sock.accept()
        print('Connected')
        file_path_data = "".encode("utf-8")
        data = "".encode("utf-8")
        try:
            while True:
                #Read data sent from client
                file_path_data = file_path_data + connection.recv(1024)

                if "#" in file_path_data.decode("utf-8") and "java" in file_path_data.decode("utf-8"):
                    #Get top 6 thumbnail urls that best matched the captured image
                    file_path = file_path_data.decode("utf-8")
                    file_path_formatted = file_path.replace("#","")
                    print('All data received and now executing the feature matching solution')
                    top_thumbnail_urls = Feature_matching.match_captured_image_with_thumbnails(file_path_formatted)

                    if top_thumbnail_urls:
                        #Send top_thumbnail urls, with symbol "]d2C>^+" appended, to client
                        connection.sendall((top_thumbnail_urls).encode("utf-8"))
                        time.sleep(4)
                        connection.sendall(("]d2C>^+").encode("utf-8"))
                        print('Sent top thumbnail urls')
                    break

            while True:
                data = data + connection.recv(1024)

                if "FIN" in data.decode("utf-8"):
                    print('Received ACKFIN')
                    connection.sendall(("ACKFIN").encode("utf-8"))
                    print('Sent ACKFIN')
                    data = "".encode("utf-8")

                elif "ACK" in data.decode("utf-8"):
                    print('Received ACK')
                    connection.sendall(("CLOSED").encode("utf-8"))
                    break

        finally:
            time.sleep(1)
            print('Closing connection')
            connection.close()
