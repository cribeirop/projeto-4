#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np
import random

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)


class Client:
    def __init__(self, com1):

        self.handshake_on = True
        self.transmissao_on = False
        self.conclusao_on = False
        
        self.com1 = com1

        # self.pacote_anterior = 0
        self.num_pacote = 0
        

        self.resposta = 'S'
        self.erre = True

        imageR = "./imgs/imageR.png"
        self.mensagem = open(imageR, 'rb').read()
        self.ultimo_byte = 0
        self.total_pacotes = len(self.mensagem)//114 + 1
        self.payload = None
        self.head = None

    def sacrifica_byte(self):
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        print('Enviando 2 bytes de sacrifício')
        time.sleep(.2)
        self.com1.sendData(b'0000')
        time.sleep(1)
        print('Byte sacrificado')

    def handshake(self):
        print('Entrou no handshake')
        head = b'\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00'
        self.envia_pacote(head)

        start = time.time()
        end = time.time()
        tempo = end - start

        time_in = tempo < 5
        
        while self.com1.rx.getIsEmpty() and time_in:
            end = time.time()
            tempo = end - start
            time_in = tempo < 5
        
        if not time_in:
            self.resposta = input("Servidor inativo. Tentar novamente? S/N ")
        else:
            rxBuffer, nRx = self.recebe_pacote()
            print('Servidor está vivo!')
            self.handshake_on = False
            self.transmissao_on = True
            
        

    
    def transmissao(self):
        print('Entrou na transmissão'*5)
        self.num_pacote += 1

        print(f'\nLen total da mensagem: {len(self.mensagem)}')

        mensagem_restante = len(self.mensagem[self.ultimo_byte:])
        print(f'Mensagem restante a ser enviada: {mensagem_restante}')
        nao_ultimo_pacote = mensagem_restante >= 114

        if nao_ultimo_pacote:
            self.payload = self.mensagem[self.ultimo_byte:self.ultimo_byte+114]
            self.ultimo_byte += 114
        else:
            self.payload = self.mensagem[self.ultimo_byte:]
            self.transmissao_on = False
            self.conclusao_on = True
        
        self.head = b'\x01\x00' + self.num_pacote.to_bytes(1, 'big') + self.total_pacotes.to_bytes(1, 'big') + len(self.payload).to_bytes(1, 'big') + b'\x00\x00\x00\x00\x00'
        ##############################################################
        # ERRO tamanho do payload
        
        # if self.erre:
        #     self.erre = False
        #     print('Entrou em self.erre')
        #     self.payload = self.mensagem[self.ultimo_byte:self.ultimo_byte+113]
        ##############################################################
        # ERRO pacote errado enviado
        # if self.erre:
        #     self.erre = False
        #     print('Entrou em self.erre')
        #     self.num_pacote -= 1
        #     self.head = b'\x01\x00' + (self.num_pacote).to_bytes(1, 'big') + self.total_pacotes.to_bytes(1, 'big') + len(self.payload).to_bytes(1, 'big') + b'\x00\x00\x00\x00\x00'
        ##############################################################
        self.envia_pacote(head=self.head,payload=self.payload)
        print('Pacote enviado')

        
        rxBuffer, nRx = self.recebe_pacote()
        print('Pacote recebido')

        if rxBuffer[0] == 2:
            if self.num_pacote == self.total_pacotes:
                self.transmissao_on = False
                self.conclusao_on = True
        elif rxBuffer[0] == 3:
            print('SITUAÇÃO DE ERRO!~~~~ '*5)

            if rxBuffer[8] == 1:
                tamanho_payload = rxBuffer[3]
                print(f'ERRO! Payload enviado não tem tamanho informado no head.\nTamanho correto é {tamanho_payload}. O enviado foi {len(self.payload)}')
                
                self.payload = self.mensagem[self.ultimo_byte:self.ultimo_byte+tamanho_payload]
                self.head = b'\x01\x00' + self.num_pacote.to_bytes(1, 'big') + self.total_pacotes.to_bytes(1, 'big') + int(tamanho_payload).to_bytes(1, 'big') + b'\x00\x00\x00\x00\x00'
                self.envia_pacote(head=self.head,payload=self.payload)

            elif rxBuffer[8] == 2:
                print(f'ERRO! Pacote enviado não é o correto.\nPacote correto é o {rxBuffer[2]}. O enviado foi {self.num_pacote}')
                dif_pacotes = self.num_pacote - rxBuffer[2]
                print(f'Dif entre pacotes: {dif_pacotes}')
                self.ultimo_byte += 114 * dif_pacotes
                print(f'Ultimo byte: {self.ultimo_byte}')
                self.payload = self.mensagem[self.ultimo_byte:self.ultimo_byte+114]
                self.head = b'\x01\x00' + int(rxBuffer[2]).to_bytes(1, 'big') + self.total_pacotes.to_bytes(1, 'big') + len(self.payload).to_bytes(1, 'big') + b'\x00\x00\x00\x00\x00'
                self.envia_pacote(head=self.head,payload=self.payload)
        

    def conclusao(self):
        self.com1.rx.clearBuffer()
        print('Entrou na Conclusao'*5)
        rxBuffer, nRx = self.recebe_pacote()
        print(f'\nRecebeu pacote {rxBuffer}')

        self.conclusao_on = False
        
        if rxBuffer[0] == 4:
            print('Transmissão concluída com sucesso!')
        
    def envia_pacote(self, head, payload=b'', eop=b'\x00\x00\x00\x00'):
        txBuffer = head + payload + eop
        self.com1.sendData(np.asarray(txBuffer))

    def recebe_pacote(self):
        
        headRxBuffer, headNRx = self.com1.getData(10)
        tamanho_payload = headRxBuffer[4]

        if tamanho_payload > 0:
            payloadRxBuffer, payloadNRx = self.com1.getData(tamanho_payload)

            eopRxBuffer, eopNRx = self.com1.getData(4)
            rxBuffer = headRxBuffer + payloadRxBuffer + eopRxBuffer
            nRx = headNRx + payloadNRx + eopNRx

            return rxBuffer, nRx
        
        eopRxBuffer, eopNRx = self.com1.getData(4)
        rxBuffer = headRxBuffer + eopRxBuffer
        nRx = headNRx + eopNRx

        return rxBuffer, nRx
        
def main():
    try:
        print("Iniciou o main")
        serialName = "COM5"
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)

        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        client = Client(com1)
        client.sacrifica_byte()

        envio_on = client.handshake_on or client.transmissao_on or client.conclusao_on

        while client.resposta == 'S' or envio_on:
                if client.handshake_on:
                    client.handshake()
                elif client.conclusao_on:
                    client.conclusao()
                while client.transmissao_on:
                    client.transmissao()
        
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