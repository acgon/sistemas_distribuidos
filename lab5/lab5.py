import os
import threading
import time

import rpyc
from rpyc.utils.server import ThreadedServer

#  Pegar o id e alt porta dos processos
id = input("Entre com o id da aplicação: ")
id = int(id)
porta = 5000 + id

# Fila de prioridade dos processos que estão esperando para escrever
fila = []

# Variável que será replicada
var = 0

# Variável booleana que indicará se o processo é a cópia primária.
#  O processo terá, inicialmente, essa característica
if id == 1:
    prim = True
else:
    prim = False

# Dicionário para armazenar o histórico de mudanças na cópia primária
hist = {}

# Variável para indicar se alt thread está alterando o valor de var
alt = False

# Interface utilizada
def interface():
    global fila
    global alt
    global hist
    global var
    global id
    global prim
    while True:
        entrada = int(input("Selecione uma operação, de 1 a 4:\n 1)Ler o valor atual de var na cópia\n 2)Ler o histórico de alterações var\n 3)Alterar o valor de var\n 4)Encerrar o programa\n"))

        # Exibir o valor de var
        if entrada == 1:
            print("O valor de var, no momento, é: {}\n".format(var))  

        # Mostrar o histórico de alterações
        if entrada == 2:
            print("Histórico de alterações:{}\n".format(hist))

        # Tentar escrever
        if entrada == 3:
            # Checando se o processo já possui o chapéu.
            # Caso contrário, o processo entra em uma fila e, quando tiver certeza de que o processo que está com o chapéu não esta escrevendo no momento, ele tenta escrever
            if not prim:
                # Tomando as possiveis listas de outros processos que já entraram antes na fila
                for i in range(4):
                        id_teste_k = i+1
                        if id_teste_k!=id:
                            conn = rpyc.connect('localhost',5000+i+1)
                            fila_atual = conn.root.exposed_fila()
                            if len(fila_atual) != 0:                            
                                for elemento in fila_atual:
                                    fila.append(elemento)
                            conn.close()
                fila.append(id)

                # Removendo duplicatas
                fila = list(dict.fromkeys(fila))

                # Aguarda o processo que tem o chapéu terminar sua escrita, enquanto atualiza frequentemente alt lista de usuários com chapéu, certificando que está observando o processo correto
                while True:
                    # Aguarda um segundo para o caso de o processo que tomar o chapéu se eliminar da fila antes que o processo que possui chapéu no momento seja atualizado
                    time.sleep(1)
                    for i in range(4):
                        id_teste_i = i+1
                        if id_teste_i != id:
                            conn = rpyc.connect('localhost',5000+id_teste_i)
                            p_teste = conn.root.exposed_tem_chapeu()
                            conn.close()
                            if p_teste:
                                conn = rpyc.connect('localhost',5000+id_teste_i)
                                a_teste = conn.root.exposed_esta_escrevendo()
                                conn.close()
                                break
                    # Verificando que não há ninguem escrevendo e o processo é o único em sua fila, pega o chapéu e se remove da fila dos outros processos
                    if not a_teste and len(fila) == 1:
                        copPrim.exposed_pegar_chapeu(copPrim,id_teste_i)
                        alt = True
                        fila.remove(id)
                        for i in range(4):
                            id_teste_j = i+1
                            if id_teste_j!=id:
                                conn = rpyc.connect('localhost',5000+id_teste_j)
                                conn.root.exposed_atualizar_fila(id)
                                conn.close()
                        break
            # Se o processo já tiver o chapéu, basta alterar a variável para sinalizar e iniciar o processo de escrita
            else:
                alt = True
            c = input("Digite um novo valor para var\n")
            c = int(c)
            copPrim.exposed_modificar_variavel_local(copPrim,c)
            # Realizar o processo de escrita.
            # Usuário pode digitar 'n' para finalizar.
            while True:
                c = input("Digite o novo valor para alt variável local. Caso contrário, digite 'n'\n")
                # Se o usuário digitar 'n', todos os outros processos serão atualizados com o novo valor de var e será indicado que este processo não está mais escrevendo 
                if c == 'n':
                    print("Enviando o valor final para os outros processos. \n")
                    for k in range (4):
                        id_teste=k+1
                        if id_teste!= id:
                            conn = rpyc.connect('localhost',5000+id_teste)
                            conn.root.exposed_modificar_variavel_global(id,var)
                            conn.close()
                    alt = False
                    break                       
                else:
                    c = int(c)
                    copPrim.exposed_modificar_variavel_local(copPrim,c)
        # Encerrando a aplicação
        if entrada == 4:
            print("Finalizando a aplicação...")
            os._exit(1)
    

class copPrim(rpyc.Service):
    
    # Função que indica se a função atual está em uma fila
    def exposed_fila(self):
        global fila
        return fila

    # Função que pega chapeu
    def exposed_pegar_chapeu(self,id_chapeu):
        global prim
        conn = rpyc.connect('localhost',5000+id_chapeu)
        conn.root.exposed_tira_chapeu()
        conn.close()
        prim = True
                    
    # Função que modifica o valor de var nas réplicas após a réplica com chapéu finalizar suas modificações
    def exposed_modificar_variavel_global(self,id,mod):
        global var
        global hist
        var = mod
        aux1 = []
        aux2 = {}
        try:
            for i in hist[id]:
                aux1.append(i)
        except:
            pass
        aux1.append(var)
        aux2[id] = aux1
        hist.update(aux2) 
        
    # Função responsável por remover o chapéu da réplica                
    def exposed_tira_chapeu(self):
        global prim
        prim = False

    # Função que atualiza a fila dos outros processos
    def exposed_atualizar_fila(self,id_retirado):
        global fila
        try:
            fila.remove(id_retirado)
        except:
            pass 
    
    # Função responsavel por verificar se está escrevendo
    def exposed_esta_escrevendo(self):
        global alt
        return alt
                        
    # Função responsavel por modificar a variável localmente    
    def exposed_modificar_variavel_local(self,novo_valor):
        global var
        global id
        global prim 
        var = novo_valor
        aux1 = []
        aux2 = {}
        try:
            for i in hist[id]:
                aux1.append(i)
        except:
            pass
        aux1.append(var)
        aux2[id] = aux1
        hist.update(aux2) 

    # Função responsóvel verificar se um processo tem chapéu
    def exposed_tem_chapeu(self):
        global prim
        return prim

# Inicializar o servidor e a interface simultaneamente
t1 = threading.Thread(target = interface,args=())
t1.start()
server = ThreadedServer(copPrim,port = porta)
server.start()
                    
                
