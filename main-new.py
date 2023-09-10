"""
 Copyright (c) 2023 Bryan Hunter (TheModdersDen) | https://github.com/TheModdersDen

 Permission is hereby granted, free of charge, to any person obtaining a copy of
 this software and associated documentation files (the "Software"), to deal in
 the Software without restriction, including without limitation the rights to
 use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 the Software, and to permit persons to whom the Software is furnished to do so,
 subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 """

# Import required modules
import sys
from sys import platform
import subprocess
import socket
import logging

class PortForwarder():

    def __init__(self):
        self.ports = {}

        with open("ports.txt", "r") as f:
            for line in f.readlines():
                if line.strip() == "":
                    continue
                if line.strip()[0] == "#":
                    continue
                if line.strip().find("=") == -1:
                    continue
                port = line.strip().split("=")[0]
                port_type = line.strip().split("=")[1]
                self.ports[port] = port_type
            
        if len(self.ports) == 0:
            print("No ports to forward!" + "\n")
            self.exit_program(0)
            
        # Get the LAN IP of the current device
        self.device_ip = socket.gethostbyname(socket.gethostname())
        if self.get_os() == "Windows":
            # Get the gateway's external IP
            self.gateway_ip = subprocess.check_output("ipconfig | findstr /i \"Gateway\"", shell=True).decode("utf-8").split(":")[1].strip()
        elif (self.get_os() == "MacOS") or (self.get_os() == "Linux"):
            # Get the gateway's external IP
            self.gateway_ip = subprocess.check_output("ip route | grep default | awk '{print $3}'", shell=True).decode("utf-8").strip()
        # Create a log file
        logging.basicConfig(filename="log-latest.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

        logging.info("Starting port forwarding...")
        logging.debug("Device IP: " + self.device_ip)
        logging.debug("Gateway IP: " + self.gateway_ip)

    def get_os(self) -> str:
        if sys.platform == "win32":
            return "Windows"
        elif sys.platform == "darwin":
            return "MacOS"
        elif sys.platform == "linux":
            return "Linux"
        else:
            return "Unknown"


    def exit_program(self, code: int = 0) -> None:
            print("Press enter to exit...")
            input()
            sys.exit(code)
    
    # Forward the ports using the UPnP protocol
    def forward_ports(self) -> None:
        for port in self.ports:
            port_type = self.ports[port]
            if port_type == "TCP":
                port_type = "TCP"
            elif port_type == "UDP":
                port_type = "UDP"
            else:
                port_type = "TCP"
            try:
                if (self.get_os() == "Windows"):
                    subprocess.check_output("netsh interface portproxy add v4tov4 listenport=" + port + " listenaddress=" + self.device_ip + " connectport=" + port + " connectaddress=" + self.device_ip, shell=True)
                elif (self.get_os() == "Linux"):
                    # Enable IP forwarding
                    subprocess.check_output("sudo sysctl -w net.ipv4.ip_forward=1", shell=True)
                    # Forward the port
                    subprocess.check_output("sudo iptables -t nat -A PREROUTING -p " + port_type.lower() + " --dport " + port + " -j DNAT --to-destination " + self.device_ip + ":" + port, shell=True)
                elif (self.get_os() == "MacOS"):
                    # Enable IP forwarding
                    subprocess.check_output("sudo sysctl -w net.inet.ip.forwarding=1", shell=True)
                    # Forward the port
                    subprocess.check_output("sudo ipfw add fwd " + self.device_ip + "," + port + " tcp from any to " + self.device_ip + " dst-port " + port + " in", shell=True)
                else: # Unknown OS
                    logging.error("Unknown OS!")
                    self.exit_program(1)
                logging.info("Forwarded port " + port + " (" + port_type + ")")
            except:
                logging.warning("Failed to forward port " + port + " (" + port_type + ")")
                
        logging.info("Port forwarding complete!")

    # Verify that the self.ports are forwarded
    def verify_ports(self) -> None:
        for port in self.ports:
            port_type = self.ports[port]
            if port_type == "TCP":
                port_type = "TCP"
            elif port_type == "UDP":
                port_type = "UDP"
            else:
                port_type = "TCP"
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.device_ip, int(port)))
                s.close()
                logging.info("Verified port " + port + " (" + port_type + ")")
            except:
                logging.warning("Failed to verify port " + port + " (" + port_type + ")")
                

if __name__ == "__main__":
    pf = PortForwarder()
    pf.forward_ports()
    pf.verify_ports()