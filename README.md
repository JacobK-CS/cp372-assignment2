# CP372 Assignment 2

Reliable file transfer over UDP using three protocols:

- Stop-and-Wait
- Go-Back-N (GBN)
- Selective Repeat

## Required Environment

- Python 3.8+
- Tested on macOS

## Repository Contents

- `sender_stopwait.py`: Stop-and-Wait Protocol sender
- `receiver_stopwait.py`: Stop-and-Wait Protocol receiver
- `sender_gbn.py`: Go-Back-N Protocol sender
- `receiver_gbn.py`: Go-Back-N Protocol receiver
- `sender_sr.py`: Selective Repeat Protocol sender
- `receiver_sr.py`: Selective Repeat Protocol receiver
- `bonus.txt`: SR bonus notes and summary of requirements

## Protocol and Packet Format

Packets use a 16-byte header: `pkt_type`, `seq_num`, `is_ack`, `data_len` (all 4-byte unsigned ints), followed by payload bytes.

Packet types:

- `0`: data
- `1`: ACK
- `2`: start
- `3`: end

Data chunk size: `1024` bytes.

## How to Start the Server and Client

### Server

```bash
python3 receiver_<protocol>.py <port> <loss_rate>
```

- `port`: UDP port to listen on
- `loss_rate`: simulated packet loss probability in `[0.0, 1.0]`

### Client

```bash
python3 sender_<protocol>.py <host> <port> <filename> <timeout>
```

- `host`: receiver host (for local testing, use `127.0.0.1`)
- `port`: receiver port
- `filename`: input file to send
- `timeout`: socket timeout in seconds (example: `0.01`)

## How to Run all 3 protocols

Open 2 terminals in this folder.

### How to run Stop-and-Wait

Terminal 1:

```bash
python3 receiver_stopwait.py 5000 0.2
```

Terminal 2:

```bash
python3 sender_stopwait.py 127.0.0.1 5000 test.txt 0.01
```

Output file: `received_file.dat`

### How to run Go-Back-N

Terminal 1:

```bash
python3 receiver_gbn.py 5001 0.2
```

Terminal 2:

```bash
python3 sender_gbn.py 127.0.0.1 5001 test.txt 0.01
```

Output file: `received_file_gbn.dat`

### How to run Selective Repeat (Bonus)

Terminal 1:

```bash
python3 receiver_sr.py 5002 0.2
```

Terminal 2:

```bash
python3 sender_sr.py 127.0.0.1 5002 test.txt 0.01
```

Output file: `received_file_sr.dat`

## Implementation Notes

- Stop-and-Wait sends a single packet at a time and retransmits on timeout.
- GBN uses a sender window (`window_size = 10`) with cumulative ACK behavior.
- SR uses a sender window (`window_size = 10`) and per-packet ACK tracking.
- SR receiver buffers out-of-order packets and writes to file in order.
- Packet loss is simulated at the receiver by dropping incoming packets with probability `loss_rate`. Set it in the receiver command (`0.0` = no loss, `0.2` = 20% expected loss).
- Output files are overwritten for each new transfer run.


## Key Assumptions Made

- Sender and receiver run on IPv4 UDP sockets.
- Receiver binds to localhost (`127.0.0.1`) in the provided implementation.
- ACK packets can also be effectively lost due to receiver-side drop simulation before response logic.
- Payload chunk size is fixed at 1024 bytes.
- Window size for GBN and SR is fixed at 10 packets.

## Metrics included in the report

Each sender reports:

- total transfer time
- throughput (bytes/second)
- total retransmissions

## Validation and Testing

Test with both text and binary files.

To verify file integrity after a transfer:

```bash
cmp -s test.txt received_file_gbn.dat; echo $?
```

`0` means files are identical.
