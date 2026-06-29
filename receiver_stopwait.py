import socket
import struct
import random
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("loss_rate", type=float)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    sock.bind(('127.0.0.1', args.port))

    expected_seq = 0
    file_open = False
    f = None

    while True:
        packet, addr = sock.recvfrom(2048)
        
        if random.random() < args.loss_rate:
            continue
            
        pkt_type, seq_num, _, data_len = struct.unpack('!IIII', packet[:16])
        data = packet[16:16+data_len]

        if pkt_type == 2:
            if not file_open:
                f = open('received_file.dat', 'wb')
                file_open = True
                expected_seq = 1
            ack_packet = struct.pack('!IIII', 1, seq_num, 1, 0)
            sock.sendto(ack_packet, addr)
            
        elif pkt_type == 0:
            if seq_num == expected_seq and file_open:
                f.write(data)
                expected_seq += 1
            ack_packet = struct.pack('!IIII', 1, seq_num, 1, 0)
            sock.sendto(ack_packet, addr)

        elif pkt_type == 3:
            if file_open:
                f.close()
                file_open = False
            ack_packet = struct.pack('!IIII', 1, seq_num, 1, 0)
            sock.sendto(ack_packet, addr)
            break

if __name__ == "__main__":
    main()