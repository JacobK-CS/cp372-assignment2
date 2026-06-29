import socket
import struct
import random
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("loss_rate", type=float)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', args.port))

    base = 0
    window_size = 10
    buffer = {}
    file_open = False
    f = None

    print(f"Selective Repeat Receiver listening on port {args.port}...")

    while True:
        packet, addr = sock.recvfrom(2048)
        
        if random.random() < args.loss_rate:
            continue
            
        pkt_type, seq_num, _, data_len = struct.unpack('!IIII', packet[:16])
        data = packet[16:16+data_len]

        if pkt_type == 2:
            if not file_open:
                f = open('received_file_sr.dat', 'wb')
                file_open = True
                base = 1
                buffer.clear()
            ack_packet = struct.pack('!IIII', 1, seq_num, 1, 0)
            sock.sendto(ack_packet, addr)
            
        elif pkt_type == 0:
            if not file_open:
                continue
            
            if base <= seq_num < base + window_size:
                ack_packet = struct.pack('!IIII', 1, seq_num, 1, 0)
                sock.sendto(ack_packet, addr)
                
                if seq_num == base:
                    f.write(data)
                    base += 1
                    
                    while base in buffer:
                        f.write(buffer[base])
                        del buffer[base]
                        base += 1
                else:
                    buffer[seq_num] = data
                    
            elif base - window_size <= seq_num < base:
                ack_packet = struct.pack('!IIII', 1, seq_num, 1, 0)
                sock.sendto(ack_packet, addr)
                
        elif pkt_type == 3:
            ack_packet = struct.pack('!IIII', 1, seq_num, 1, 0)
            sock.sendto(ack_packet, addr)
            if file_open:
                f.close()
                file_open = False
                print("File transfer complete.")

if __name__ == '__main__':
    main()