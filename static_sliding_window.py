from cmath import atanh
import socket
import time
import os
import math
import sys
import matplotlib.pyplot as plt
import numpy as np
packets = []
RTT = []
windowSize = 5
port = input("Enter port number: ")
portNumber = int(port)

#since this is running on localhost we dont type anything for the ip
server = ("", portNumber)

senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
senderSocket.connect(server)

#counting packets
packetNumber = 1
with open('message.txt', 'r') as openedMessage:
    while True:
        file_eof = openedMessage.read(1000)
        if(file_eof == ''):
            print("Appended all packets. End of File")
            break

        message = str(packetNumber) + "|" + file_eof
        packets.append(message)
        packetNumber = packetNumber+1

#len packets 2409

totalPacketsAcknowledged = 0

packetStartTimes = []
RTT = []
dup = 0

indexShifter = 0
nextPacketNumber = 0
lostPackets = 0
prevResponse = 0
window = []
totalPacketsOutbound = 0
print("This is the length of the packet array: ", len(packets))
while(totalPacketsOutbound != len(packets)):

    windowPacketCounter = nextPacketNumber
    while(windowPacketCounter < indexShifter + windowSize):
        window.append(windowPacketCounter+1)
        windowPacketCounter = windowPacketCounter+1

    while(nextPacketNumber < indexShifter + windowSize): #this mimicks the sliding of a window
        if(nextPacketNumber < 2409):
            start = time.time()
            packetStartTimes.append(start)
            senderSocket.send(str.encode(packets[nextPacketNumber]))
            nextPacketNumber = nextPacketNumber + 1
            totalPacketsOutbound = totalPacketsOutbound+1
            print()
            print("Current Window: ", window)
            print("Sequence Number of Packet Sent: ", nextPacketNumber)            
        else: 
            break
        
    senderSocket.settimeout(5)

    try:
        receiverResponse = int(senderSocket.recv(1500).decode())
        finishingTime = time.time()

        if(receiverResponse == prevResponse):
            dup = dup+1
            if(dup >= 3):
                print("We received 3 of the same acknowledgement. Something is going wrong. Ending Program")
                sys.exit()
        else:
            print("Acknowledgement Number Received: ", receiverResponse)
            print()

            dup = 0
            window.pop(0)
            indexShifter = indexShifter+1
            prevResponse = receiverResponse
            currTime = time.time()
            RTT.append(currTime -packetStartTimes[receiverResponse-1])
    except socket.timeout:
        #if we get a timeout, then we count it as a lost packet and resend.
        dup = 0
        lostPackets = lostPackets+1
        senderSocket.send(str.encode(packets[receiverResponse]))

aDelay = sum(RTT)/len(RTT)*1000
aThroughput = os.stat("message.txt").st_size / aDelay * 8
performance = math.log(aThroughput, 10) - math.log(aDelay,10)

print(lostPackets, " packets were lost")
print("Average Delay: ", aDelay, " milliseconds")
print("Average Throughput: ", aThroughput, " bits per seconds")
print("Performance: ", performance)

#now plotting
#x coordinates
xCoordinatesDelay = list(range(1, len(RTT)+1))

plt.plot(xCoordinatesDelay,RTT,label = 'Plot of Per Packet Delays (Part 2)' )
plt.savefig('Part 2 Plot of Per Packet Delays')

xCoordinatesDelay = list(range(1, len(RTT)+1))

plt.plot(xCoordinatesDelay,RTT)
plt.xlabel('Packet Number')
plt.ylabel('RTT')
plt.title('Part 2 Plot of Per Packet Delays')
plt.savefig('Part 2 Plot of Per Packet Delays')

yCoordinateThroughput = []
for i in range(len(RTT)):
    yCoordinateThroughput.append(1000*8/ RTT[i])
plt.plot(xCoordinatesDelay,yCoordinateThroughput)
plt.xlabel('PacketNumber')
plt.ylabel('Throughput')
plt.title('Part 2 Plot of Per Packet Throughput')
plt.savefig('Part 2 Plot of Per Packet Throughput')