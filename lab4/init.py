# Programa que inicia a eleição de líder
from sys import exit

import rpyc

while True:
    elec = input("Pronto para iniciar a votação. Indique o id do processo e o tipo de eleição (M para maior id e m para menor id separados por espaço)\nPara encerrar, digite N\n")
    if elec[0] == 'N':
        exit()
    elec = elec.split(" ")
    con = rpyc.connect('localhost', 5000+int(elec[0]))
    resultado = con.root.exposed_election(elec[1])
    print("elec concluida, com lider eleito sendo:{}".format(resultado))
    con.close()
    con = rpyc.connect('localhost', 5000+int(elec[0]))
    con.root.exposed_reset()
    con.close()
