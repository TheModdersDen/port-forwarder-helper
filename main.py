# Import required modules
import miniupnpc
import sys

# Forward the following list of ports using the UPnP protocol using miniupnpc:
ports = {}

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
        ports[port] = port_type
    
if len(ports) == 0:
    print("No ports to forward!")
    print("Press enter to exit...")
    input()
    sys.exit(0)

# Create a UPnP object
u = miniupnpc.UPnP()

# Discover UPnP devices on the network
u.discoverdelay = 200
u.discover()

# Select the first UPnP device found
u.selectigd()

# Get the LAN IP of the current device
deviceip = u.lanaddr

# Get the gateway's external IP
externalip = u.externalipaddress()

print("External IP: " + externalip)
print("Device IP: " + deviceip)

# The current port being forwarded
current_port = -1

# Clear the ports from the ports list
def clear_ports() -> None:
    for port, port_type in ports.items():
        print("Clearing port " + port + "...")
        # Delete the port mappings, in bulk...
        u.deleteportmapping(int(port), port_type)
        print("Port cleared!")
    
# Clear a specific port from the ports list
def clear_port(port) -> None:
    print("Clearing port " + port + "...")
    # Delete a specific port mapping
    u.deleteportmapping(int(port), ports[port])
    print("Port cleared!")

def forward_ports() -> None:
    # Forward the ports
    count = 1
    for port, port_type in ports.items():
        current_port = port
        print("Forwarding port " + port + "...")
        # Forward all the ports!!! :)
        # More like the ones in the "ports" list...
        u.addportmapping(int(port), port_type, deviceip, int(port), "Port # " + str(count), '')
        count += 1
        print("Port forwarded!")

def yes_no(question, default) -> bool:
    if default == True:
        question += " [Y/n] "
    else:
        question += " [y/N] "
    answer = input(question)
    if answer == "":
        return default
    elif answer.lower() == "y":
        return True
    elif answer.lower() == "n":
        return False
    else:
        return yes_no(question, default)

def list_forwarded_ports():
    for port, port_type in ports.items():
        if u.getspecificportmapping(int(port), ports[port]) != None:
            print("Port " + port + " is forwarded!")
        else:
            print("Port " + port + " is not forwarded!")
 
try:
    forward_ports()
    verify = yes_no("Verify port forwarding? (This will take a while)", True)
    if verify:
        list_forwarded_ports()
except Exception as e:
    print("Failed to forward port " + current_port + "!")
    print()
    print("Error:\n" + str(e))
    clear_port(current_port)
finally:
    print("Done!")
    print()
    print("Press enter to exit...")
    input()
    sys.exit(0)