import os

availPort=5560

#assumed multiple pis will always be used since large roads is the most viable
serverEnd=""
serverStart=""
clientEnd=""
clientStart=""

serverEnd1=""
serverStart1=""
clientEnd1=""
clientStart1=""

serverEnd2=""
serverStart2=""
clientEnd2=""
clientStart2=""

ipAddresses=[]

#store ipAddresses
lineNum=0
with open('IPAddresses.txt') as fp:
    for line in fp:
        if lineNum!=0:
            line = line[:(len(line)-1)] #remove new line char
            ipAddresses.append(line)
        else:
            lineNum=1

    print(ipAddresses)
    
#begin storing templates
state=0
with open('Templates/serverEnd.py') as fp:
    for line in fp:
        if state==0:
            if line=="#insertHere\n":
                #print("enter")
                state=1
            else:
                serverEnd1+=line
        else:
            serverEnd2+=line
    
state=0
with open('Templates/serverStart.py') as fp:
    for line in fp:
        if state==0:
            if line=="#insertHere\n":
                #print("enter")
                state=1
            else:
                serverStart1+=line
        else:
            serverStart2+=line

    
state=0
with open('Templates/clientEnd.py') as fp:
    for line in fp:
        if state==0:
            if line=="#insertHere\n":
                #print("enter")
                state=1
            else:
                clientEnd1+=line
        else:
            clientEnd2+=line

    
state=0
with open('Templates/clientStart.py') as fp:
    for line in fp:
        if state==0:
            if line=="#insertHere\n":
                #print("enter")
                state=1
            else:
                clientStart1+=line
        else:
            clientStart2+=line

    
state=0
with open('Templates/serverEnd.py') as fp:
    for line in fp:
        if state==0:
            if line=="#insertHere\n":
                #print("enter")
                state=1
            else:
                serverEnd1+=line
        else:
            serverEnd2+=line

#end storing templates

#generate directory
    directory="Generated"
    if not os.path.exists(directory):
        os.makedirs(directory)

#generate code and write to files
for i in range(0,len(ipAddresses)):
    directory="Generated/pi"+str(i)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    #
    client=0
    server=0
    if i%2==0:
        client=1
        server=3
    else:
        client=3
        server=1
    
    file = open(directory+'/serverStart.py', 'w+')
    with file as fp:
        line1="host="+"\""+ipAddresses[i]+"\""+"\n"
        line2="port="+str(availPort+server+0)+"\n"
        fp.write(serverStart1+line1+line2+serverStart2)
        
    file = open(directory+'/serverEnd.py', 'w+')
    with file as fp:
        line1="host="+"\""+ipAddresses[i]+"\""+"\n"
        line2="port="+str(availPort+server+1)+"\n"
        fp.write(serverEnd1+line1+line2+serverEnd2)
        
    file = open(directory+'/clientStart.py', 'w+')
    with file as fp:
        line1="host="+"\""+ipAddresses[(i-1)%len(ipAddresses)]+"\""+"\n"
        line2="port="+str(availPort+client+0)+"\n"
        fp.write(clientStart1+line1+line2+clientStart2)
        
    file = open(directory+'/clientEnd.py', 'w+')
    with file as fp:
        line1="host="+"\""+ipAddresses[(i+1)%len(ipAddresses)]+"\""+"\n"
        line2="port="+str(availPort+client+1)+"\n"
        fp.write(clientEnd1+line1+line2+clientEnd2)