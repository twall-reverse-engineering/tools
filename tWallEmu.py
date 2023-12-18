import socket
import datetime
import threading
import time

logger_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
logger_ip = None
logger_port = 33401
software_version = "2023-12-18T12:00:00"

def serve_twall_csv():
    global software_version
    server_ip = "0.0.0.0"
    server_port = 33402

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((server_ip, server_port))

    print(f"Serve server listening on {server_ip}:{server_port}")

    while True:
        data, client_address = server_socket.recvfrom(1024)
        message = data.decode("ASCII")
        print(f"[serve] Received message: {message}")

        # Check if the message contains the "twall?" command
        if "twall?" == message:
            # Assuming you want to send a fake response
            fake_response = "tWall-0xbadbee;dev11.lan;" + software_version
            print(f"[serve] answer: {fake_response}")
            server_socket.sendto(fake_response.encode("ASCII"), client_address)

def serve_twall():
    global logger_ip

    server_ip = "0.0.0.0"
    server_port = 33400

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((server_ip, server_port))
    server_socket.listen()

    print(f"tWall server listening on {server_ip}:{server_port}")

    serve_thread = threading.Thread(target=serve_twall_csv)
    serve_thread.start()

    while True:
        # Wait for a client to connect
        client_socket, client_address = server_socket.accept()
        print(f"[tWall] Accepted connection from {client_address}")
        
        while is_socket_open(client_socket):
            # Receive data from the connected client
            data = client_socket.recv(1024)
            if not data:
                continue
            message = data.decode("ASCII")
            if len(message) == 0:
                continue
            print(f"[tWall] Received message: {message.strip()}")

            command_with_args = message.split()
            if len(command_with_args) == 0:
                continue
            command = command_with_args[0]
            args = command_with_args[1::]

            response = None
            if command == "log_ext":
                logger_ip = args[0]
                response = ""
                # optional?
                # send_log_message("param", "name")
            elif command == "version":
                response = software_version
            elif command == "language":
                response = "OK" # Crash if not there
            elif command == "login":
                response = "OK" # Crash if not there
            elif command == "set_date":
                response = "OK" # Crash if not there
            elif command == "twall_info":
                response = f"OK\nwidth:8\nheight:8\ntwall_type:other\nlanguage:de\n."
            elif command == "abort":
                response = "OK"
            elif command == "logout":
                response = "OK"
                break
            elif command == "ping":
                response = "OK"
            elif command == "save_log":
                response = "OK"
            elif command == "save_hitcounter":
                response = "OK"
            elif command == "get_margin":
                response = "OK 1"
                # public enum PlayingField { Full, Half, Focus }
            elif command == "set_margin":
                # args[0] 1, 2, 3 
                response = "OK"
            elif command == "get_brightness":
                response = "OK 100"
            elif command == "set_brightness":
                # args[0] = 100
                response = "OK"
            elif command == "get_screensaver":
                response = "OK" # Licence Check
            elif command == "start":
                # args[0] = Weiss.pkg
                response = "OK"
            elif command == "list_tng":
                response = "OK\n."
            elif command == "list_ext":
                response = "OK\n."
            elif command == "list":
                # tags "fav,two_players,agility,condition,childrens_game,brain_teaser,with_sound
                response = "OK\nWeiss;Weiss.pkg;two_players\nTest;Test.pkg\n."
            elif command == "get_manifest":
                response = "ERROR"
            elif command == "get_program_image":
                response = "ERROR"
            else:
                response = "ERROR"
                
            if response is not None:
                print(f"[tWall] answer: {response}")
                response = response + "\n"
                client_socket.send(response.encode("ASCII"))

        print("[tWall] Client socket is closed.")
        # Close the connection
        client_socket.close()
    serve_thread.stop()

def send_log_message(event_params, event_name):
    # Get current timestamp in seconds since the epoch
    current_timestamp = int(time.time())

    # Format the message string
    log_message = f"{current_timestamp};{event_params};{event_name}"

    if logger_ip is not None:
        logger_socket.sendto(log_message.encode("ASCII"), (logger_ip, logger_port))
        print(f"[logger] answer: {log_message}")

def is_socket_open(sock):
    try:
        # Try to get the file descriptor of the socket
        fileno = sock.fileno()
        peername = sock.getpeername()
        return True
    except (socket.error, OSError):
        # An exception will be raised if the socket is closed
        return False

def serve_twall_log():
    pass

if __name__ == "__main__":
    twall_thread = threading.Thread(target=serve_twall)
    twall_thread.start()