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
        self.id = 14
        self.ocioso = True
        self.ligado = True
        self.cont = 0
        self.sucesso = False
        self.mensagem = None
        self.ultimo_pacote = -1
        self.com1 = com1

    def sacrifica_byte(self):
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        print('Esperando 2 bytes de sacrifício')
        rxBuffer_0, nRx_0 = self.com1.getData(2)
        self.com1.rx.clearBuffer()
        time.sleep(1)

    def recebe_pacote(self):
        headRxBuffer, headNRx = self.com1.getData(10)
        if headRxBuffer[0] == 5:
            self.ligado = False
            self.ocioso = True
            self.com1.disable()
            print("-------------------------")
            print("Comunicação encerrada por TIME OUT no CLIENTE")
            print("-------------------------")
            return 0,0
        
        else:
            tamanho_payload = headRxBuffer[5]
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

    def envia_pacote(self, head, payload=b'', eop=b'\xAA\xBB\xCC\xDD'):
        txBuffer = head + payload + eop
        self.com1.sendData(np.asarray(txBuffer))

    def atualiza_arquivo(self, pacote_enviado=None, total_pacotes=None,instante=time.time(), recebimento=True, tipo=3, tamanho=14, CRC='' ):
        with open('server1.txt', 'a') as f:
            operacao = 'Recebimento' if recebimento else 'Envio'
            if recebimento:
                f.write(f'{instante} / {operacao} / {tipo} / {tamanho} / {pacote_enviado} / {total_pacotes} / {CRC}\n')
            else:
                f.write(f'{instante} / {operacao} / {tipo} / {tamanho} / {CRC}\n')
        ########## ERRO ORDEM DOS PACOTES ##########
        # with open('server2.txt', 'a') as f:
        #     operacao = 'Recebimento' if recebimento else 'Envio'
            # if recebimento:
            #     f.write(f'{instante} / {operacao} / {tipo} / {tamanho} / {pacote_enviado} / {total_pacotes} / {CRC}\n')
            # else:
            #     f.write(f'{instante} / {operacao} / {tipo} / {tamanho} / {CRC}\n')
        ########## ERRO ORDEM DOS PACOTES ##########
        ########## ERRO TIME OUT ##########
        # with open('server3.txt', 'a') as f:
            # operacao = 'Recebimento' if recebimento else 'Envio'
            # if recebimento:
            #     f.write(f'{instante} / {operacao} / {tipo} / {tamanho} / {pacote_enviado} / {total_pacotes} / {CRC}\n')
            # else:
            #     f.write(f'{instante} / {operacao} / {tipo} / {tamanho} / {CRC}\n')        ########## ERRO TIME OUT ##########
        ########## SITUAÇÃO FIO TIRADO ##########
        # with open('server4.txt', 'a') as f:
        #     operacao = 'Recebimento' if recebimento else 'Envio'
            # if recebimento:
            #     f.write(f'{instante} / {operacao} / {tipo} / {tamanho} / {pacote_enviado} / {total_pacotes} / {CRC}\n')
            # else:
            #     f.write(f'{instante} / {operacao} / {tipo} / {tamanho} / {CRC}\n')
        ########## SITUAÇÃO FIO TIRADO ##########


def extrai_payload(rxBuffer):
    tamanho_payload = rxBuffer[5]
    payload = rxBuffer[10:10+tamanho_payload]
    return payload

def atualiza_mensagem(server, payload):
    if server.mensagem == None:
        server.mensagem = payload
    else:
        server.mensagem += payload
    
def salva_dados(mensagem):
    imageW = "./imgs/recebidaCopia.png"
    print("Salvando dados no arquivo:")
    print(" - {}".format(imageW))
    f = open(imageW, 'wb')
    f.write(mensagem)
    f.close()

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

        while server.ligado:
            ### Início do handshake
            if server.ocioso:
                if server.com1.rx.getIsEmpty():
                    time.sleep(1)
                else:
                    rxBuffer, nRx = server.recebe_pacote()
                    if not rxBuffer == 0:
                        tipo = rxBuffer[0]
                        if tipo == 1:
                            id_destino = rxBuffer[1]
                            para_mim = server.id == id_destino
                            if para_mim:
                                server.ocioso = False
                                time.sleep(1)
                            else:
                                time.sleep(1)
            else:
                ### Inicia "na escuta!"
                id_arquivo = rxBuffer[5]
                numPckg = rxBuffer[4]
                head = b'\x02\x00\x00\x00\x00' + id_arquivo.to_bytes(1, 'big') + b'\x00\x00\x00\x00'
                server.envia_pacote(head)
            ### Fim do handshake
            ### Inicio da recebimento do pacote de dados
                
                while not server.sucesso and not server.ocioso:
                    server.cont += 1
                    if server.cont <= numPckg:
                        
                        timer1 = time.time()
                        timer2 = time.time()

                        verifica_t3 = True
                        while verifica_t3:
                            ### Inicia "pacotes de dados"
                            msg_recebida = not server.com1.rx.getIsEmpty()
                            if msg_recebida:
                                verifica_t3 = False
                                rxBuffer, nRx = server.recebe_pacote()
                                if not rxBuffer == 0:
                                    tipo = rxBuffer[0]
                                    if tipo == 3:
                                        ### pckg ok?
                                        
                                        tamanho_payload = rxBuffer[5]
                                        print(f'Deveria ser 124: {10+tamanho_payload}')
                                        pacote_correto = rxBuffer[4] == server.cont
                                        pos_eop_ok = rxBuffer[10+tamanho_payload:] == b'\xAA\xBB\xCC\xDD'
                                        pckg_ok = pacote_correto or pos_eop_ok

                                        if pckg_ok:
                                            print(f'Pacote {server.cont} recebido com sucesso')
                                            payload = extrai_payload(rxBuffer)
                                            atualiza_mensagem(server, payload)
                                            # Envia msg t4
                                            server.ultimo_pacote = rxBuffer[4]
                                            head = b'\x04\x00\x00\x00\x00\x00\x00' + server.ultimo_pacote.to_bytes(1, 'big') + b'\x00\x00'
                                            server.envia_pacote(head)
                                        else:
                                            # Envia msg t6
                                            pacote_solicitado = server.ultimo_pacote + 1
                                            if not pacote_correto:
                                                print('Pacote errado')
                                                head = b'\x06\x01\x00\x00\x00\x00' + pacote_solicitado.to_bytes(1, 'big') + server.ultimo_pacote.to_bytes(1, 'big') + b'\x00\x00'
                                            elif not pos_eop_ok:
                                                print('EOP na posição errada')
                                                head = b'\x06\x02\x00\x00\x00\x00' + pacote_solicitado.to_bytes(1, 'big') + server.ultimo_pacote.to_bytes(1, 'big') + b'\x00\x00'
                                            server.envia_pacote(head)
                                            # Remove 1 de cont pois irá ser adicionado no loop while not server.sucesso e não deveria
                                            server.cont -= 1
                            else:
                                time.sleep(1)
                                agora = time.time()
                                if timer2 - agora > 20:
                                    server.ocioso = True
                                    server.ligado = False
                                    # Envia msg t5
                                    head = b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                                    server.envia_pacote(head)
                                    # Encerra comunicação
                                    verifica_t3 = False
                                else:
                                    if timer1 - agora > 2:
                                        # Envia msg t4
                                        head = b'\x04\x00\x00\x00\x00\x00\x00' + server.ultimo_pacote.to_bytes(1, 'big') + b'\x00\x00'
                                        server.envia_pacote(head)
                                        # Reset timer
                                        timer1 = time.time()
                    else:
                        server.sucesso = True
                        salva_dados(server.mensagem)
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