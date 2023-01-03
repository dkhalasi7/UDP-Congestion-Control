import socket
import time
import os
import math
import matplotlib.pyplot as plt
import numpy as np

packets = []
timePerPacket = []
port = input("Enter port number: ")
portNumber = int(port)

#since this is running on localhost we dont type anything for the ip
server = ("", portNumber)

senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
senderSocket.connect(server)

#counting packets
packetCount = 1
with open('message.txt', 'r') as openedMessage:
    while True:
        file_eof = openedMessage.read(1000)
        if(file_eof == ''):
            print("Appended all packets. End of File")
            break

        message = str(packetCount) + "|" + file_eof
        packets.append(message)
        packetCount = packetCount+1


#resetting packet count to start sending the first packet
packetCount = 0
moveToNextPacket = True
lostPackets = 0
while(packetCount < len(packets)):
    if (moveToNextPacket == True):
        start = time.time()
        ePacket = str.encode(packets[packetCount])
    else:
        lostPackets = lostPackets+1
    
    senderSocket.settimeout(5)
    try:
        senderSocket.send(ePacket)
        ack = senderSocket.recv(1500).decode()
        timePerPacket.append(time.time() - start)

        #now printing output
        print() #blank line
        print("Current Window: [", packetCount+1, "]")
        print("Sequence Number of Packet Sent: ", packetCount+1)
        print("Acknowledgement Number Received: ", packetCount+1)
        print() #blank line
        packetCount = packetCount+1
        moveToNextPacket = True
    except socket.timeout:
        moveToNextPacket = False

aDelay = (sum(timePerPacket)/len(timePerPacket))*1000
aThroughput = (os.stat("message.txt").st_size / (sum(timePerPacket)/len(timePerPacket)*1000)) * 8
performance = math.log(aThroughput, 10) - math.log(aDelay,10)

print(lostPackets, " packets were lost")
print("Average Delay: ", aDelay, " milliseconds")
print("Average Throughput: ", aThroughput, " bits per seconds")
print("Performance: ", performance)

xCoordinatesDelay = list(range(1, len(timePerPacket)+1))

plt.plot(xCoordinatesDelay,timePerPacket)
plt.xlabel('Packet Number')
plt.ylabel('RTT')
plt.title('Part 1 Plot of Per Packet Delays')
plt.savefig('Part 1 Plot of Per Packet Delays')

yCoordinateThroughput = []
for i in range(len(timePerPacket)):
    yCoordinateThroughput.append(1000*8/ timePerPacket[i])
plt.plot(xCoordinatesDelay,yCoordinateThroughput)
plt.xlabel('PacketNumber')
plt.ylabel('Throughput')
plt.title('Part 1 Plot of Per Packet Throughput')
plt.savefig('Part 1 Plot of Per Packet Throughput')