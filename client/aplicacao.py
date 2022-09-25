# from enlace import *
# import time
# import numpy as np
# import random

# serialName = "COM3"

# class Client:
#     def __init__(self):

#         self.dir = "./client/imgs/imageR.png"
#         self.imagem = open(self.dir, 'rb').read()

#         self.num_servidor = 14
#         self.id = 0

#         print("Iniciou o main")
#         self.com = enlace(serialName)
#         self.com.enable()
#         print("Abriu a comunicacao\n")

#         self.num_total = (len(self.imagem) // 114) + 1
#         self.num_pacote = 1

#         self.h8 = b'\x00'
#         self.h9 = b'\x00'

#         self.erro_ordem = False
#         # self.erro_tempo = False

#     def disable(self):
#         self.com.disable()
#         print("\n\n__________Comunicacao encerrada__________")

#     def sacrifica_byte(self):
#
#         self.com.sendData(b'0000')
#         time.sleep(1)

#     def converte_em_binario(self, num):
#         return (num).to_bytes(1, byteorder='big')
    
#     

#     def tipo_1(self):
#         ocioso = False
#         while ocioso == False:
#             self.payload = b''
#             self.eop = b'\xAA\xBB\xCC\xDD'
#             self.h0 = b'\x01'
#             self.h1 = self.converte_em_binario(self.num_servidor)
#             self.h2 = b'\x00'
#             self.h3 = self.converte_em_binario(self.num_total)
#             self.h4 = b'\x00'
#             self.h5 = self.converte_em_binario(self.id)
#             self.h6 = b'\x00'
#             self.h7 = b'\x00'
#             self.head = self.h0+self.h1+self.h2+self.h3+self.h4+self.h5+self.h6+self.h7+self.h8+self.h9
#             self.pacote = self.head+self.payload+self.eop
#             self.com.sendData(self.pacote)
#             self.atualiza_arquivo(tipo=1, tamanho=len(self.pacote))

#             time.sleep(5)
#             if self.com.rx.getIsEmpty():
#                 print("Servidor ocioso", end="")
#                 for i in range(10):
#                     print(".", end="")
#                     time.sleep(0.5)
#                 ocioso = False
#             else:
#                 rxBuffer, nRx = self.com.getData(14)
#                 self.atualiza_arquivo(tipo=1, tamanho=nRx, envio=False)
#                 if rxBuffer[0] == 2 and rxBuffer[5] == self.id:
#                     print("Servidor esta vivo!\n")
#                     ocioso = True
    
#     def tipo_5(self): 
#         self.payload = b'\x00'
#         self.eop = b'\xaa\xbb\xcc\xdd'
#         self.h0 = b'\x05'
#         self.h1 = b'\x00'
#         self.h2 = b'\x00'
#         self.h3 = self.converte_em_binario(self.num_total)
#         self.h4 = b'\x00'
#         self.h5 = self.converte_em_binario(self.id)
#         self.h6 = b'\x00'
#         self.h7 = b'\x00'
#         self.head = self.h0+self.h1+self.h2+self.h3+self.h4+self.h5+self.h6+self.h7+self.h8+self.h9
#         self.pacote = self.head+self.payload+self.eop
#         self.com.sendData(self.pacote)
#         self.atualiza_arquivo(tipo=5, tamanho=len(self.pacote))
#         print("\nTempo limite excedido")

#     def erro_interrupção(self): ...

#     def printw(self, texto=""): 
#         for i in range(10):
#             print(texto, end="")
#             print(".", end="")
#             time.sleep(1)

#     def tipo_3(self):
#         pacotes_enviados = 0

#         while self.num_pacote <= self.num_total:
#             self.payload = b''
#             if len(self.imagem) - pacotes_enviados < 0: 
#                 self.payload += self.imagem[pacotes_enviados:]
#             else:
#                 self.payload += self.imagem[pacotes_enviados:pacotes_enviados+114]
#                 pacotes_enviados += 114
#             print(f"\nPayload {self.num_pacote}: {self.payload[0:10]}... | Tamanho: {len(self.payload)}")

#             self.eop = b'\xaa\xbb\xcc\xdd'
#             self.h0 = b'\x03'
#             self.h1 = b'\x00'
#             self.h2 = b'\x00'
#             self.h3 = self.converte_em_binario(self.num_total)
#             self.h4 = self.converte_em_binario(self.num_pacote)
#             self.h5 = self.converte_em_binario(len(self.payload))
#             self.h6 = b'\x00'
#             self.h7 = b'\x00'
#             self.head = self.h0+self.h1+self.h2+self.h3+self.h4+self.h5+self.h6+self.h7+self.h8+self.h9
#             self.pacote = self.head+self.payload+self.eop

#             enviado = False
#             while enviado == False:
#                 self.com.sendData(self.pacote)
#                 self.atualiza_arquivo(tamanho=len(self.pacote), pacote_enviado=self.num_pacote, total_pacotes=self.num_total)
#                 print("Enviou o pacote", end="")
#                 start1 = time.time()
#                 start2 = time.time()
#                 msg_correta = False
#                 while msg_correta == False:
                    
#                     while self.com.rx.getIsEmpty() or self.com.getData(14)[0][0] != 4:
#                         self.printw()
#                         # while self.com.rx.getIsEmpty():
#                         #     pass 
#                         if time.time() - start1 <= 5:
#                             # while self.com.rx.getIsEmpty():
#                             #     pass 
#                             if time.time() - start2 <= 20:
#                                 rxBuffer, nRx = self.com.getData(14)
#                                 self.atualiza_arquivo(tipo=rxBuffer[0], tamanho=nRx, envio=False)
#                                 try:
#                                     if rxBuffer[0] == 6:
#                                         self.num_pacote = rxBuffer[6]
#                                         self.com.sendData(self.pacote)
#                                         self.atualiza_arquivo(tamanho=len(self.pacote), tipo=6)
#                                         start1 = time.time()
#                                         start2 = time.time()
#                                     msg_correta = False
#                                         # enviado = False
#                                 except:
#                                     # self.erro_interrupção()
#                                     start = time.time()
#                                     while self.com.rx.getIsEmpty():
#                                         pass
#                                     if time.time() - start< 20:
#                                         enviado = True 
#                                     else:
#                                         self.disable()
#                             else: # erro de tempo... é automático?
#                                 self.tipo_5()
#                                 self.disable()
                        
#                         else:
#                             self.com.sendData(self.pacote)
#                             self.atualiza_arquivo(tamanho=len(self.pacote), pacote_enviado=self.num_pacote, total_pacotes=self.num_total)
#                             start1 = time.time()
#                             # while self.com.rx.getIsEmpty():
#                             #     pass
#                             if time.time() - start2 <= 20:
#                                 rxBuffer, nRx = self.com.getData(14)
#                                 self.atualiza_arquivo(tipo=rxBuffer[0], tamanho=nRx, envio=False)
#                                 try:
#                                     if rxBuffer[0] == 6:
#                                         self.num_pacote = rxBuffer[6]
#                                         self.com.sendData(self.pacote)
#                                         self.atualiza_arquivo(tamanho=len(self.pacote), tipo=6)
#                                         start1 = time.time()
#                                         start2 = time.time()
#                                     msg_correta = False
#                                         # enviado = False
#                                 except:
#                                     # self.erro_interrupção()
#                                     start = time.time()
#                                     while self.com.rx.getIsEmpty():
#                                         pass
#                                     if start - time.time() < 20:
#                                         enviado = True 
#                                     else:
#                                         self.disable()
#                             else:
#                                 self.tipo_5()
#                                 self.disable()    
#                     else:                        
#                         rxBuffer, nRx = self.com.getData(14)
#                         self.atualiza_arquivo(tipo=rxBuffer[0], tamanho=nRx, envio=False)
#                         if rxBuffer[0] == 4:
#                             if self.erro_ordem == True: self.num_pacote += 10
#                             else:
#                                 if self.num_pacote == self.num_total:
#                                     self.disable()
#                                 self.num_pacote += 1
#                                 enviado = True
#                                 msg_correta = True
#                         # else: ...
#         if self.num_pacote == self.num_total:
#             self.disable()
    
#     def main(self):
#         try:
#             self.sacrifica_byte()
#             self.tipo_1()
#             self.tipo_3()
#         except Exception as erro:
#             print(erro)
#             print("ops! :-\\")
#             self.disable()

# if __name__ == "__main__":
#     Client().main()
from enlace import *

class Client:
    def __init__(self, com1):
        self.com1 = com1
        source = "imgs/imageR.png"
        self.imagem = open(source, 'rb').read()
        self.numPck = len(self.mensagem)//114 + 1
        self.id_server = 14
        self.inicia = False
        self.cont = 0
        self.sucesso = False
        self.encerrou = False
    
    def sacrifica_byte(self):
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        print('Enviando 2 bytes de sacrifício')
        time.sleep(.2)
        self.com1.sendData(b'0000')
        time.sleep(1)
        print('Byte sacrificado')

    def atualiza_arquivo(self, pacote_enviado=None, total_pacotes=None,instante=time.ctime(time.time()), envio=True, tipo=3, tamanho=128, CRC='' ):
        ########## ERRO ORDEM DOS PACOTES ##########
        # caso = 2
        ########## ERRO ORDEM DOS PACOTES ##########
        ########## ERRO TIME OUT ##########
        # caso = 3
        ########## ERRO TIME OUT ##########
        ########## SITUAÇÃO FIO TIRADO ##########
        # caso = 4
        ########## SITUAÇÃO FIO TIRADO ##########
        caso = 1
        with open(f'client{caso}.txt', 'a') as f:
            operacao = 'Envio' if envio else 'Recebimento'
            if envio:
                if tipo == 1:
                    f.write(f'{instante} / {operacao} / {tipo} / {tamanho} / {CRC}\n')
                elif tipo == 3:
                    f.write(f'{instante} / {operacao} / {tipo} / {tamanho} / {pacote_enviado} / {total_pacotes} / {CRC}\n')
                elif tipo == 5:
                    f.write(f'{instante} / {operacao} / {tipo} / {tamanho} / {CRC}\n')
            else:
                f.write(f'{instante} / {operacao} / {tipo} / {tamanho} / {CRC}\n')

    def envia_pacote(self, head, payload=b'', eop=b'\xAA\xBB\xCC\xDD'):
        txBuffer = head + payload + eop
        self.com1.sendData(np.asarray(txBuffer))

    def recebe_pacote(self):
        
        headRxBuffer, headNRx = self.com1.getData(10)
        
        eopRxBuffer, eopNRx = self.com1.getData(4)
        rxBuffer = headRxBuffer + eopRxBuffer
        nRx = headNRx + eopNRx

        return rxBuffer, nRx

def main():
    try:
        print("Iniciou o main")
        serialName = "COM3"
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)

        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()

        client = Client(com1)
        client.sacrifica_byte()

        while not client.inicia:
            print("Quero falar com você")
            # t1
            head = b''
            client.envia_pacote(head)
            time.sleep(5)
            recebeu_msg = not client.com1.rx.getIsEmpty()
            if recebeu_msg:
                rxBuffer, nRx = client.recebe_pacote()
                tipo = rxBuffer[0]
                if tipo == 2:
                    print("Respondeu na escuta")
                    client.inicia = True
        else:
            print(f'Contagem de pacotes: {client.cont}')
            client.cont += 1
            while not client.sucesso or not client.encerrou:
                if client.cont <= client.numPck:
                    # t3
                    head = b''
                    payload = client.mensagem[(client.cont-1)*114:(client.cont)*114] if client.cont < client.numPck else client.mensagem[(client.cont-1)*114:]
                    client.envia_pacote(head, payload=payload)
                    print(f'Enviou pacote {client.cont}')
                    
                    # Reenvio
                    timer1 = time.time()
                    # Time out
                    timer2 = time.time()
                    print("Setou Timer1 e Timer2")

                    rxBuffer, nRx = client.recebe_pacote()
                    tipo = rxBuffer[0]
                    recebeu_t4 = tipo == 4

                    while not recebeu_t4:
                        ...


                else:
                    print('Contador maior que o número de pacotes. SUCESSO')
                    client.sucesso = True
        
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()

            

            
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()