from cmath import atanh
import socket
import time
import os
import math
import sys

packets = []
timePerPacket = []
windowSize = 1
ssthresh = 16 
sstd = 0
EstRTT = 0
DevRTT = 0
port = input("Enter port number: ")
portNumber = int(port)
firstpackflag = False 

def windowSizeupdate(case):
    global windowSize
    global sstd
    global ssthresh
    if(case == 0): #no congestion 
        if(windowSize < ssthresh):
          if(sstd == 0):
            windowSize = windowSize * 2   #slowstart
          else:
            windowSize = windowSize + 1  #slowstart already over (entering congestion control)
        else:
          sstd = 1 
          windowSize = windowSize + 1 #congestion control
    elif(case == 1): #duplicate ack
        windowSize = math.floor(windowSize/2)
    elif(case == 2): #timeout
        windowSize = 1 
    print("WindowSize:",windowSize)

def dynamictimeout(SampleRTT):
    global EstRTT
    global DevRTT
    EstRTT = 0.875*EstRTT + 0.125*SampleRTT
    DevRTT = (0.75*DevRTT) + 0.25*(abs(SampleRTT - EstRTT))
    Timeout = EstRTT + (4 * DevRTT)
    return Timeout

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
            windowSizeupdate(1)
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
            print("This is the current time: ", currTime, " and this is time being appended: ", currTime-packetStartTimes[receiverResponse-1])
            RTT.append(currTime -packetStartTimes[receiverResponse-1])
            firstpackflag = True
            sampleRTT = finishingTime - start
            timePerPacket.append(RTT*1000)
            if(not(firstpackflag)):
              EstRTT = sampleRTT
            senderSocket.settimeout(dynamictimeout(sampleRTT))
            windowSizeupdate(0)
    except socket.timeout:
        #if we get a timeout, then we count it as a lost packet and resend.
        windowSizeupdate(2)
        dup = 0
        lostPackets = lostPackets+1
        senderSocket.send(str.encode(packets[receiverResponse]))


print("These are the packet total times: ", RTT)
aDelay = sum(RTT)/len(RTT)*1000
aThroughput = os.stat("message.txt").st_size / aDelay * 8
performance = math.log(aThroughput, 10) - math.log(aDelay,10)

print(lostPackets, " packets were lost")
print("Average Delay: ", aDelay, " milliseconds")
print("Average Throughput: ", aThroughput, " bits per seconds")
print("Performance: ", performance)