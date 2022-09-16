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

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)

class Server():

    def __init__(self, com1):

        self.handshake_on = True
        self.transmissao_on = False
        self.conclusao_on = False
        
        self.com1 = com1

        self.pacote_anterior = 0
        self.num_pacote = 0

        self.sem_erros = True

        self.mensagem = None


    def sacrifica_byte(self):
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        print('Esperando 2 bytes de sacrifício')
        rxBuffer_0, nRx_0 = self.com1.getData(2)
        self.com1.rx.clearBuffer()
        time.sleep(1)
        print('Byte sacrificado')

    def handshake(self, rxBuffer):

        print('Entrou no handshake')
        ######################################## ERRO DE TIMEOUT ##########################################
        # time.sleep(15)
        # self.com1.rx.clearBuffer()
        ####################################### ERRO DE TIMEOUT ##########################################

        self.com1.sendData(np.asarray(rxBuffer))
        print('Enviou o estou vivo')
        self.handshake_on = False
        self.transmissao_on = True

    def transmissao(self, rxBuffer, nRx):
        print('\nEntrou na transmissao')

        self.pacote_anterior = self.num_pacote
        self.num_pacote = rxBuffer[2]
        num_total = rxBuffer[3]
        tamanho_payload = rxBuffer[4]
        tamanho_pacote = tamanho_payload + 14

        payload = rxBuffer[10:10+tamanho_payload]

        print(f'\npayload: {payload} len: {len(payload)}\n')


        print(f'\ntamanho_pacote: {tamanho_pacote}\n nRx: {nRx}')
        print(f'\nnum_pacote: {self.num_pacote}\npacote_anterior + 1: {self.pacote_anterior + 1}')
        
        payload_esperado = tamanho_pacote == nRx
        pacote_esperado = self.num_pacote == (self.pacote_anterior + 1)

        if not payload_esperado:
            print(f'Payload com tamanho errado. Tamanho esperado era {tamanho_payload} e foi recebido {nRx-14}\n')
            self.sem_erros = False
            
            print(tamanho_payload.to_bytes(1,'big'))
            solicitacao = b'\x03\x00' + tamanho_payload.to_bytes(1, 'big') + b'\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00'
            self.com1.sendData(np.asarray(solicitacao))
        elif not pacote_esperado:
            print(f'Número do pacote errado.\nCorreto deveria ser {self.pacote_anterior + 1} e foi recebido {self.num_pacote}')
            self.sem_erros = False
            solicitacao = b'\x03\x00' + (self.pacote_anterior+1).to_bytes(1, 'big') + b'\x01\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00'
            self.com1.sendData(np.asarray(solicitacao))
        else:
            print('Recebeu sem erros!')
            self.sem_erros = True

            if self.mensagem == None:
                self.mensagem = payload
            else:
                self.mensagem += payload

            confirmacao = b'\x02\x00' + bytes(self.num_pacote + 1) + b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            self.com1.sendData(np.asarray(confirmacao))
            print('Enviou confirmação de recebimento')
        
        if num_total == self.num_pacote and self.sem_erros:
            self.transmissao_on = False
            self.conclusao_on = True
            print('Tudo pronto para iniciar conclusão.')
            print(self.mensagem)
            

        

    def conclusao(self):
        
        imageW = "./imgs/recebidaCopia.png"
        print("Salvando dados no arquivo:")
        print(" - {}".format(imageW))
        f = open(imageW, 'wb')
        f.write(self.mensagem)
        f.close()

        sucesso = b'\x04\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00'
        self.com1.sendData(np.asarray(sucesso))
        self.conclusao_on = False


    def recebe_pacote(self):
        headRxBuffer, headNRx = self.com1.getData(10)
        tamanho_payload = headRxBuffer[4]
        print(f'Tamanho do payload é {tamanho_payload}')

        if tamanho_payload > 0:
            payloadRxBuffer, payloadNRx = self.com1.getData(tamanho_payload)
            lenEop = self.com1.rx.getBufferLen()
            eopRxBuffer, eopNRx = self.com1.getData(lenEop)
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
        serialName = "COM4"
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)

        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        server = Server(com1)
        server.sacrifica_byte()
        
        while server.handshake_on or server.transmissao_on:
            rxBuffer, nRx = server.recebe_pacote()
            tipo_mensagem = rxBuffer[0]

            if tipo_mensagem == 0:
                server.handshake(rxBuffer)
            elif tipo_mensagem == 1:
                server.transmissao(rxBuffer, nRx)

        if  server.conclusao_on:
            server.conclusao()
        
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