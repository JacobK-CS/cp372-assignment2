import socket
import struct
import time
import os
import argparse

def create_packet(pkt_type, seq_num, data=b""):
    header = struct.pack('!IIII', pkt_type, seq_num, 0, len(data))
    return header + data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str)
    parser.add_argument("port", type=int)
    parser.add_argument("filename", type=str)
    parser.add_argument("timeout", type=float)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(args.timeout)
    server_addr = (args.host, args.port)

    retransmissions = 0
    seq_num = 0
    start_time = time.time()

    start_pkt = create_packet(2, seq_num)
    while True:
        try:
            sock.sendto(start_pkt, server_addr)
            ack_packet, _ = sock.recvfrom(2048)
            ack_type, ack_seq, is_ack, _ = struct.unpack('!IIII', ack_packet[:16])
            if ack_type == 1 and ack_seq == seq_num:
                seq_num += 1
                break
        except socket.timeout:
            retransmissions += 1

    chunks = []
    with open(args.filename, 'rb') as f:
        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            chunks.append(chunk)

    total_packets = len(chunks)
    base = 1
    next_seq_num = 1
    window_size = 10
    
    acked = {i: False for i in range(1, total_packets + 1)}

    while base < total_packets + 1:
        while next_seq_num < base + window_size and next_seq_num < total_packets + 1:
            data_pkt = create_packet(0, next_seq_num, chunks[next_seq_num - 1])
            sock.sendto(data_pkt, server_addr)
            next_seq_num += 1
            
        try:
            ack_packet, _ = sock.recvfrom(2048)
            ack_type, ack_seq, is_ack, _ = struct.unpack('!IIII', ack_packet[:16])
            
            if ack_type == 1 and 1 <= ack_seq <= total_packets:
                acked[ack_seq] = True
                
                if ack_seq == base:
                    while acked.get(base, False):
                        base += 1
                        
        except socket.timeout:
            for i in range(base, next_seq_num):
                if not acked.get(i, False):
                    retransmissions += 1
                    data_pkt = create_packet(0, i, chunks[i - 1])
                    sock.sendto(data_pkt, server_addr)

    end_seq = total_packets + 1
    end_pkt = create_packet(3, end_seq)
    while True:
        try:
            sock.sendto(end_pkt, server_addr)
            ack_packet, _ = sock.recvfrom(2048)
            ack_type, ack_seq, is_ack, _ = struct.unpack('!IIII', ack_packet[:16])
            if ack_type == 1 and ack_seq == end_seq:
                break
        except socket.timeout:
            retransmissions += 1

    end_time = time.time()
    print(f"\n--- FINAL METRICS ---")
    print(f"Total Time: {end_time - start_time:.2f} seconds")
    print(f"Throughput: {os.path.getsize(args.filename) / (end_time - start_time):.2f} bytes/sec")
    print(f"Total Retransmissions: {retransmissions}")

if __name__ == '__main__':
    main()