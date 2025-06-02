import subprocess

def capture_packets(output_file='captures/packets.pcap', interface='lo'):
    cmd = ['tshark', '-i', interface, '-w', output_file]
    print(f"Capturing packets on {interface}...")
    subprocess.Popen(cmd)

if __name__ == '__main__':
    capture_packets()
