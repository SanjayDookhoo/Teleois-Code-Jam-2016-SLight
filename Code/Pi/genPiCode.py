import os

SLightCore1=""
SLightCore2=""
SLightCore3=""

piNum=0

#store ipNum
with open('IPAddresses.txt') as fp:
    for line in fp:
        line=int(line[:(len(line)-1)]) #remove new line char
        piNum=int(line)
        break
    print(line)
    
#begin storing templates

state=0
with open('Templates/SLightCore.py') as fp:
    for line in fp:
        if state==0:
            if line=="#insertHere\n":
                state=1
            else:
                SLightCore1+=line
        elif state==1:
            if line=="            #insertHere\n":
                state=2
            else:
                SLightCore2+=line
        else:
            SLightCore3+=line

#end storing templates

#generate directory
    directory="Generated"
    if not os.path.exists(directory):
        os.makedirs(directory)

#generate code and write to files
for i in range(0,piNum):
    state=0
    if i%2==0:
        state=0
    else:
        state=1
    
    file = open('Generated/pi'+str(i)+'/SLightCore.py', 'w+')
    with file as fp:
        if state==0:
            line1="import serverEnd\n"
            line1+="import serverStart\n"
            line1+="import clientEnd\n"
            line1+="import clientStart\n"
            
            line2="            receiveFromLeadingPi.setDataDict(ast.literal_eval(clientStart.rec()))\n"
            line2+="            receiveFromTrailingPi.setDataDict(ast.literal_eval(clientEnd.rec()))\n"
            line2+="            serverEnd.send(passToLeadingPi.getDataDict())\n"
            line2+="            serverStart.send(passToTrailingPi.getDataDict())\n"
            
            fp.write(SLightCore1+line1+SLightCore2+line2+SLightCore3)
        else:
            line1="import clientEnd\n"
            line1+="import clientStart\n"
            line1+="import serverEnd\n"
            line1+="import serverStart\n"
            
            line2="            serverEnd.send(passToLeadingPi.getDataDict())\n"
            line2+="            serverStart.send(passToTrailingPi.getDataDict())\n"
            line2+="            receiveFromLeadingPi.setDataDict(ast.literal_eval(clientStart.rec()))\n"
            line2+="            receiveFromTrailingPi.setDataDict(ast.literal_eval(clientEnd.rec()))\n"
            
            fp.write(SLightCore1+line1+SLightCore2+line2+SLightCore3)
    