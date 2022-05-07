import multiprocessing
import os
import pickle
import select
import socket
import sys

entradas = [sys.stdin]
conexoes = {} # Histórico de conexões

def acharPalavras(nome_arq):

    quantPalavra = {} # Dicionário que guarda as palavras e a quantidade de aparições
    
    if os.path.exists(nome_arq + '.txt'): 
        with open(nome_arq + '.txt') as arquivo:
            for linha in arquivo.readlines():
                for palavra in linha.split(' '):
                    if palavra in quantPalavra:
                        quantPalavra[palavra] += 1
                    else:
                        quantPalavra[palavra] = 1
    else:
        print("Erro, arquivo não encontrado")
        falha = "O arquivo enviado não foi encontrado"
        return falha

    # Procurando as 5 palavras mais frequentes
    palavras_freq = []
    for i in range(5):
        maiorPalavra = None # Palavra mais encontrada
        maiorValor = 0 # Quantidade de ocorrências

        for palavra, contagem in quantPalavra.items():
            if contagem > maiorValor:
                maiorPalavra = palavra
                maiorValor= contagem

        palavras_freq.append(maiorPalavra)
        del quantPalavra[maiorPalavra]

    # Retornar as 5 palavras mais encontradas
    return palavras_freq

# Função que atende as requisições dos clientes
def atenderReq(clisock,endr):
    data = pickle.loads(clisock.recv(1024))
    envio = acharPalavras(data) # Utiliza a função para encontrar as 5 palavras mais comuns
    if not data:
        print(str(endr) + '-> encerrou')
        clisock.close() 
        return
    
    print(envio)
    
    clisock.send(pickle.dumps(envio)) # Envia o resultado para o cliente
    
    # Fecha o socket de conexão
    clisock.close

HOST = '' 
PORTA = 6000 

# Armazena os clientes para o join
clientes = []

# Criar um socket para a comunicação
sock = socket.socket() 
sock.bind((HOST, PORTA))

# Define o limite de conexões e espera por elas
sock.listen(5)

entradas.append(sock)

while True:
    leitura, escrita, excecao = select.select(entradas,[],[])
    for pronto in leitura:
        if pronto == sock:
            clisock, endr = sock.accept()
            print ('Conectado com: ', endr)
            conexoes[clisock] = endr
            cliente = multiprocessing.Process(target=r, args=(clisock,endr))
            cliente.start()
            clientes.append(cliente) # Armazena a referência da thread
        elif pronto == sys.stdin:
            cmd = input()
            if cmd == 'fim': # Solicitar a finalização
                for cli in clientes: # Aguardar os processos terminarem e sair
                    cli.join()
                sock.close()
                sys.exit
 
