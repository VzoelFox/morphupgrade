import time
import sys
import socket

# === System & Network Builtins for StandardVM ===

# --- System ---
def _sys_time_builtin():
    return time.time()

def _sys_sleep_builtin(seconds):
    time.sleep(float(seconds))

def _sys_platform_builtin():
    return sys.platform

def builtins_keluar(code=0):
    sys.exit(code)

# --- Network (Socket) ---
def _net_socket_builtin(family, type):
    # Default values handling usually done in Morph, but safety here
    f = family if family is not None else socket.AF_INET
    t = type if type is not None else socket.SOCK_STREAM
    return socket.socket(f, t)

def _net_connect_builtin(sock, host, port):
    sock.connect((host, port))

def _net_send_builtin(sock, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    sock.sendall(data)

def _net_recv_builtin(sock, bufsize):
    return sock.recv(bufsize)

def _net_close_builtin(sock):
    sock.close()

SYSTEM_BUILTINS = {
    # System
    "_sys_time_builtin": _sys_time_builtin,
    "_sys_sleep_builtin": _sys_sleep_builtin,
    "_sys_platform_builtin": _sys_platform_builtin,
    "keluar": builtins_keluar,

    # Network
    "_net_socket_builtin": _net_socket_builtin,
    "_net_connect_builtin": _net_connect_builtin,
    "_net_send_builtin": _net_send_builtin,
    "_net_recv_builtin": _net_recv_builtin,
    "_net_close_builtin": _net_close_builtin,
}
