from enlace import *
import time
import numpy as np
import random

class Client:
    def __init__(self, serialName, id):
        self.com = enlace(serialName)
        self.com.enable()

        self.dir = "./imgs/imageR.png"
        self.imagem = open(self.dir, 'rb').read()

        self.id = id

        self.num_total = len(self.imagem) // 114
        self.num_pacote = 1

        self.h8 = b'\x00'
        self.h9 = b'\x00'

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
            start = time.time()
            while self.com.rx.getIsEmpty():
                pass
            end = time.time()
            if end - start <= 5:
                rxBuffer, nRx = self.com.getData(14)
                if rxBuffer[0] == 2 and rxBuffer[5] == id:
                    ocioso = True
            else: ocioso = False
    
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
                msg_correta = False
                while msg_correta == False:
                    if self.com.rx.getIsEmpty():
                        start = time.time()
                        while self.com.rx.getIsEmpty():
                            pass 
                        end = time.time()
                        if end - start <= 5:
                            while self.com.rx.getIsEmpty():
                                pass 
                            end = time.time()
                            if end - start <= 20:
                                rxBuffer, nRx = self.com.getData(14)
                                if rxBuffer[0] == 6:
                                    self.num_pacote -= 1
                                    self.com.sendData(self.pacote)
                                else: msg_correta = True
                            else: 
                                self.tipo_5()
                                self.com.disable()
                        else: 
                            self.com.sendData(self.pacote)
                            start = time.time()
                            while self.com.rx.getIsEmpty():
                                pass
                            end = time.time()
                            if end - start <= 20:
                                rxBuffer, nRx = self.com.getData(14)
                                if rxBuffer[0] == 6:
                                    self.num_pacote -= 1
                                    self.com.sendData(self.pacote) 
                                else: msg_correta = True
                            else:
                                self.tipo_5()
                                self.com.disable()                            
                    rxBuffer, nRx = self.com.getData(14)
                    if self.com.rx.getIsEmpty() == False:
                        if rxBuffer[0] == 4:
                            self.num_pacote += 1
                            enviado = True
                            msg_correta = True
                





