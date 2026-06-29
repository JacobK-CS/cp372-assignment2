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

    def send_and_wait(packet, expected_ack_seq):
        nonlocal retransmissions
        while True:
            try:
                sock.sendto(packet, server_addr)
                ack_packet, _ = sock.recvfrom(2048)
                ack_type, ack_seq, is_ack, _ = struct.unpack('!IIII', ack_packet[:16])
                
                if ack_type == 1 and is_ack == 1 and ack_seq == expected_ack_seq:
                    return
            except socket.timeout:
                retransmissions += 1

    print("Initiating transfer... (This may take several minutes at high loss rates)")
    start_pkt = create_packet(2, seq_num)
    send_and_wait(start_pkt, seq_num)
    seq_num += 1

    file_size = os.path.getsize(args.filename)
    
    with open(args.filename, 'rb') as f:
        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            data_pkt = create_packet(0, seq_num, chunk)
            send_and_wait(data_pkt, seq_num)
            
            # THE PROGRESS TRACKER
            if seq_num % 1000 == 0:
                print(f"Progress: Successfully sent {seq_num} packets...")
                
            seq_num += 1

    end_pkt = create_packet(3, seq_num)
    send_and_wait(end_pkt, seq_num)

    end_time = time.time()
    
    print("\n--- FINAL METRICS ---")
    print(f"Total Time: {end_time - start_time:.2f} seconds")
    print(f"Throughput: {file_size / (end_time - start_time):.2f} bytes/sec")
    print(f"Total Retransmissions: {retransmissions}")

if __name__ == "__main__":
    main()
