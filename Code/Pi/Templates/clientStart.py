import socket

#insertHere

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
state=True
while state:
    try:
        s.connect((host,port))
        state=False
    except:
        print("could not connect yet")

#comm=input("enter cmd: ")
s.send(str("u"))

def rec():


    reply=s.recv(1024)  
    return reply

#s.close()


