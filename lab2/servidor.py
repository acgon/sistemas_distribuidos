import os
import socket


def acharPalavras(nome_arq):

    # Dicionário que armazena as palavras e a quantidade
    quantPalavra = {}

    # Checando se o arquivo existe
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

    # Encontrando as 5 palavras mais frequentes
    palavras_freq = []
    for i in range(5):
        maiorPalavra = None # Palavra mais encontrada
        quantMaiorPalavra = 0 # Quantidade de ocorrências

        for palavra, cont in quantPalavra.items():
            if cont > quantMaiorPalavra:
                maiorPalavra = cont
                quantMaiorPalavra = palavra

        palavras_freq.append(maiorPalavra)
        del quantPalavra[maiorPalavra] 
    return palavras_freq # Retorna as 5 palavras mais encontradas

HOST = ''    
PORTA = 5000 

# Criar um socket com os valores default
sock = socket.socket()   

# Vincular interface e porta de comunicação
sock.bind((HOST, PORTA))

# Esperar pela conexão
sock.listen(1) 

while True:

# Aceitar a primeira conexão da fila, que pode ser bloqueante
    novoSock, endereco = sock.accept() # Retornar um novo socket e o endereco do par conectado
    print ('Conectado com: ', endereco)
# Esperar uma mensagem
    msg = novoSock.recv(1024) 
    envio = bytes(acharPalavras(str(msg,encoding='utf8')),encoding='utf8')
    print(str(envio))
    novoSock.send(envio)

    # Fechar o socket
    novoSock.close()

# Fechar o socket principal
sock.close() 
