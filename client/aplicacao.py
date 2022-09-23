from modulefinder import packagePathMap
from enlace import *
import time
import numpy as np
import random

serialName = "COM4"

class Client:
    def __init__(self):

        self.dir = "./imgs/imageR.png"
        self.imagem = open(self.dir, 'rb').read()

        self.id = 15

        self.com = enlace(serialName)
        self.com.enable()

        self.num_total = len(self.imagem) // 114
        self.num_pacote = 1

        self.h8 = b'\x00'
        self.h9 = b'\x00'

        self.erro_ordem = False
        # self.erro_tempo = False

    def disable(self):
        self.com.disable()
        return "Comunicação encerrada"

    def sacrifica_byte(self):
        time.sleep(.2)
        self.com.sendData(b'0000')
        time.sleep(1)

    def converte_em_binario(self, num):
        return (num).to_bytes(1, byteorder='big')
    
    def tipo_1(self, num_servidor):
        ocioso = False
        while ocioso == False:
            self.payload = b'\x00'
            self.eop = b'\xaa\xbb\xcc\xdd'
            self.h0 = b'\x01'
            self.h1 = self.converte_em_binario(num_servidor)
            self.h2 = b'\x00'
            self.h3 = self.converte_em_binario(self.num_total)
            self.h4 = b'\x00'
            self.h5 = self.converte_em_binario(self.id)
            self.h6 = b'\x00'
            self.h7 = b'\x00'
            self.head = self.h1+self.h2+self.h3+self.h4+self.h5+self.h6+self.h7+self.h8+self.h9
            self.pacote = self.head+self.payload+self.eop
            self.com.sendData(self.pacote)
            time.sleep(5)
            if self.com.rx.getIsEmpty():
                ocioso = False
            else:
                rxBuffer, nRx = self.com.getData(14)
                if rxBuffer[0] == 2 and rxBuffer[5] == self.id:
                    ocioso = True
    
    def tipo_5(self): # handshake?
        self.payload = b'\x00'
        self.eop = b'\xaa\xbb\xcc\xdd'
        self.h0 = b'\x05'
        self.h1 = b'\x00'
        self.h2 = b'\x00'
        self.h3 = self.converte_em_binario(self.num_total)
        self.h4 = b'\x00'
        self.h5 = self.converte_em_binario(self.id)
        self.h6 = b'\x00'
        self.h7 = b'\x00'
        self.head = self.h1+self.h2+self.h3+self.h4+self.h5+self.h6+self.h7+self.h8+self.h9
        self.pacote = self.head+self.payload+self.eop
        self.com.sendData(self.pacote)

    def erro_interrupção(self): ...

    def tipo_3(self):
        pacotes_enviados = 0

        while self.num_pacote <= self.num_total:
            self.payload = b''
            if len(self.imagem) - pacotes_enviados < 0: 
                self.payload += self.imagem[pacotes_enviados:]
            else:
                self.payload += self.imagem[pacotes_enviados:pacotes_enviados+114]
                pacotes_enviados += 114

            self.eop = b'\xaa\xbb\xcc\xdd'
            self.h0 = b'\x03'
            self.h1 = b'\x00'
            self.h2 = b'\x00'
            self.h3 = self.converte_em_binario(self.num_total)
            self.h4 = self.converte_em_binario(self.num_pacote)
            self.h5 = self.converte_em_binario(len(self.payload))
            self.h6 = b'\x00'
            self.h7 = b'\x00'
            self.head = self.h1+self.h2+self.h3+self.h4+self.h5+self.h6+self.h7+self.h8+self.h9
            self.pacote = self.head+self.payload+self.eop

            enviado = False
            while enviado == False:
                self.com.sendData(self.pacote)
                start1 = time.time()
                start2 = time.time()
                msg_correta = False
                while msg_correta == False:
                    while self.com.rx.getIsEmpty() or self.com.getData(14)[0][0] != 4:
                        # while self.com.rx.getIsEmpty():
                        #     pass 
                        if start1 - time.time() <= 5:
                            # while self.com.rx.getIsEmpty():
                            #     pass 
                            if start2 - time.time() <= 20:
                                rxBuffer, nRx = self.com.getData(14)
                                try:
                                    if rxBuffer[0] == 6:
                                        self.num_pacote = rxBuffer[6]
                                        self.com.sendData(self.pacote)
                                        start1 = time.time()
                                        start2 = time.time()
                                    msg_correta = False
                                        # enviado = False
                                except:
                                    # self.erro_interrupção()
                                    start = time.time()
                                    while self.com.rx.getIsEmpty():
                                        pass
                                    if start - time.time() < 20:
                                        enviado = True 
                                    else:
                                        self.disable()
                            else: # erro de tempo... é automático?
                                self.tipo_5()
                                self.disable()
                        
                        else:
                            self.com.sendData(self.pacote)
                            start1 = time.time()
                            # while self.com.rx.getIsEmpty():
                            #     pass
                            if start2 - time.time() <= 20:
                                rxBuffer, nRx = self.com.getData(14)
                                try:
                                    if rxBuffer[0] == 6:
                                        self.num_pacote = rxBuffer[6]
                                        self.com.sendData(self.pacote)
                                        start1 = time.time()
                                        start2 = time.time()
                                    msg_correta = False
                                        # enviado = False
                                except:
                                    # self.erro_interrupção()
                                    start = time.time()
                                    while self.com.rx.getIsEmpty():
                                        pass
                                    if start - time.time() < 20:
                                        enviado = True 
                                    else:
                                        self.disable()
                            else:
                                self.tipo_5()
                                self.disable()    
                    else:                        
                        rxBuffer, nRx = self.com.getData(14)
                        if rxBuffer[0] == 4:
                            if self.erro_ordem == True: self.num_pacote += 10
                            else:
                                self.num_pacote += 1
                                enviado = True
                                msg_correta = True
                        else: ...
        if self.num_pacote == self.num_total:
            self.disable()
    
    def main(self):
        self.sacrifica_byte()
        self.tipo_1()
        self.tipo_5()

if __name__ == "__main__":
    try:
        Client.main()

    except Exception as erro:
        Client.disable()