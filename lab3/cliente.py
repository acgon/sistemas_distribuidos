# Exemplo basico socket (lado ativo)

import socket
import pickle

HOST = ''
PORTA = 5000

# Criar o socket
sock = socket.socket() 

# Conectar com o servidor
sock.connect((HOST, PORTA))

msg = input("Insira o nome do arquivo: \n")
sock.send(pickle.dumps(msg))
msg = sock.recv(1024)
msg = pickle.loads(msg) 
    
print(msg)

# Encerrar a conexão
sock.close
