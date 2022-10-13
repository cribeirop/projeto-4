from enlace import *
import numpy as np
from crc import Crc16

class Client:
    def __init__(self, com1):
        self.com1 = com1
        imagem = "imgs/imageR.png"
        self.mensagem = open(imagem, 'rb').read()
        self.numPck = len(self.mensagem)//114 + 1
        self.id_server = 14
        self.id_arquivo = 0
        self.inicia = False
        self.cont = 0
        self.sucesso = False
        self.encerrou = False
        ###############################################################
        # self.erre=False
        ################################### CASO 2 - ERRO
        self.erre=True
        ###############################################################
    
    def sacrifica_byte(self):
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        print('Enviando 2 bytes de sacrifício')
        time.sleep(.2)
        self.com1.sendData(b'0000')
        time.sleep(1)
        print('Byte sacrificado')
        self.com1.rx.clearBuffer()

    def atualiza_arquivo(self, pacote_enviado=None, total_pacotes=None,instante=time.ctime(time.time()), envio=True, tipo=3, tamanho=128, CRC='' ):
        time.sleep(1)
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

    def crcSet(self, payload):
        crc = Crc16(payload).to_bytes(2, 'big')
        h8 = crc[0]
        h9 = crc[1]
        return h8 + h9

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

        while not client.inicia:
            print("Quero falar com você")
            # t1
            
            head = b'\x01' + client.id_server.to_bytes(1, 'big') + b'\x00' + client.numPck.to_bytes(1, 'big') + b'\x00' + client.id_arquivo.to_bytes(1, 'big') + b'\x00\x00\x00\x00'
            client.envia_pacote(head)
            client.atualiza_arquivo(tipo=head[0], tamanho=14)
            time.sleep(5)
            recebeu_msg = not client.com1.rx.getIsEmpty()
            if recebeu_msg:
                rxBuffer, nRx = client.recebe_pacote()
                tipo = rxBuffer[0]
                client.atualiza_arquivo(envio=False, tipo=tipo, tamanho=nRx)
                if tipo == 2:
                    print("Respondeu na escuta")
                    client.inicia = True
        while not client.encerrou and not client.sucesso:
            
            print(f'Sem sucesso e sem encerramento. Contagem de pacotes: {client.cont}')
            
            if client.cont <= client.numPck:
                client.cont += 1
                # t3
                if client.erre:
                    client.cont = 2
                    client.erre=False
                payload = client.mensagem[(client.cont-1)*114:(client.cont)*114] if client.cont < client.numPck else client.mensagem[(client.cont-1)*114:]
                head = b'\x03\x00\x00' + client.numPck.to_bytes(1, 'big') + client.cont.to_bytes(1, 'big') + len(payload).to_bytes(1, 'big') + b'\x00\x00' + client.crcSet(payload)
                client.envia_pacote(head, payload=payload)
                client.atualiza_arquivo(pacote_enviado=client.cont, total_pacotes=client.numPck)
                print(f'Enviou pacote {client.cont}')

                # Reenvio
                timer1 = time.time()
                # Time out
                timer2 = time.time()
                print("Setou Timer1 e Timer2")
                tipo = head[0]
                msg_recebida = not client.com1.rx.getIsEmpty()
                if msg_recebida:
                    rxBuffer, nRx = client.recebe_pacote()
                    tipo = rxBuffer[0]
                    client.atualiza_arquivo(envio=False, tipo=tipo, tamanho=nRx)

                

                while not tipo == 4 and not client.encerrou:
                    print('Não recebi tipo 4')
                    if time.time() - timer1 > 5:
                        print('Mais do que 5 segundos')
                        # t3
                        client.cont -= 1
                        payload = client.mensagem[(client.cont-1)*114:(client.cont)*114] if client.cont < client.numPck else client.mensagem[(client.cont-1)*114:]
                        head = b'\x03\x00\x00' + client.numPck.to_bytes(1, 'big') + client.cont.to_bytes(1, 'big') + len(payload).to_bytes(1, 'big') + b'\x00\x00' + client.crcSet(payload)
                        print(f'Pacote sendo enviado: {client.cont}')
                        client.envia_pacote(head, payload=payload)
                        client.atualiza_arquivo(pacote_enviado=client.cont, total_pacotes=client.numPck)
                        print(f'Enviou pacote {client.cont}')
                        timer1 = time.time()
                        msg_recebida = not client.com1.rx.getIsEmpty()
                        if msg_recebida:
                            rxBuffer, nRx = client.recebe_pacote()
                            tipo = rxBuffer[0]
                            client.atualiza_arquivo(envio=False, tipo=tipo, tamanho=nRx)
                        
                        ################### TIMEOUT ###################
                        else:
                            client.cont+=1
                        ################### TIMEOUT ###################
                        
                    if time.time() - timer2  > 20:
                        print('TIMEOUT')
                        # Envia msg t5
                        head = b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        client.envia_pacote(head)
                        client.atualiza_arquivo(tipo=head[0], tamanho=14)
                        client.encerrou = True
                    else:
                        if tipo == 6:
                            client.cont = rxBuffer[6]
                            tipo=4
                        
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