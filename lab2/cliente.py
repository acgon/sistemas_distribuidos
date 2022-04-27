# Exemplo basico socket (lado ativo)

import socket

HOST = ''
PORTA = 5000

# Criar o socket
sock = socket.socket() 

# Conectar com o servidor
sock.connect((HOST, PORTA)) 


msg = input("Insira o nome do arquivo: \n")
sock.send(bytes(msg , 'utf-8'))
msg = sock.recv(1024) 
    
print(str(msg,  encoding='utf-8'))

# Encerrar a conexão
sock.close
