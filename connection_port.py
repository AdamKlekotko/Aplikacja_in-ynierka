import serial
from time import sleep
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as optimization

class Connection_Port():

    def __init__(self,baud=9600,port='COM5',parity='N',bytesize=8,stopbits=1,timeout=1):
        print("try to create port")
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = baud
        self.serial_port.port = port
        self.serial_port.parity = parity
        self.serial_port.bytesize = bytesize
        self.serial_port.stopbits = stopbits
        self.serial_port.timeout = timeout
        self.number_of_samples = 32
        self.serial_port.write_timeout=0.5

    def open_port(self):
        while (self.serial_port.is_open == False):
            self.serial_port.open()

    def close_port(self):
        while (self.serial_port.is_open == True):
            self.serial_port.close()

    def change_freq(self,freq):
        psc = 200000 / freq
        psc2 = int(psc / 256)
        print(psc2)
        psc1 = int(psc - psc2 * 256)
        var32=0
        while(var32!=int(psc)):
            self.serial_port.write(b"c")
            self.serial_port.flushOutput()
            sleep(0.2)
            self.serial_port.write(int.to_bytes(psc1, 1, byteorder='little'))
            sleep(0.2)
            self.serial_port.flushOutput()
            self.serial_port.write(int.to_bytes(psc2, 1, byteorder='little'))
            sleep(0.2)
            self.serial_port.flushOutput()
            var3 = self.serial_port.read(2)
            self.serial_port.flushInput()
            print('read psc')
            var32 = int.from_bytes(var3, byteorder='little')
            print(var32)
            print("ACHTUNG!!!!!!")
        print(var32)
        sleep(0.7)

    def raw_measure(self):
        buffer=np.zeros(self.number_of_samples)
        print("start measure")
        sleep(0.3)
        self.serial_port.write(b"a")
        self.serial_port.flushOutput()
        print("send")
        sleep(0.3)
        for i in range(self.number_of_samples):
            sleep(0.03)
            t1 = time.time()
            var1 = self.serial_port.read(2)
            t2 = time.time()
            if t2 - t1 > 0.7:
                print('break measure loop')
                break
            var2 = int.from_bytes(var1, byteorder='little')
            buffer[i] = np.copy(var2)
            print(var2)
            sleep(0.03)
        return buffer

    def complex_measure(self,folder_path,start_freq,end_freq,step,average):
        frequences = np.arange(start_freq, (end_freq + step/2), step)
        data = np.zeros((len(frequences),int(average),self.number_of_samples))
        for k in range(len(frequences)):
            for jj in range(int(average)):
                self.open_port()
                sleep(0.4) # Waiting for open port
                print(frequences)
                self.change_freq(int(frequences[k]))
                sleep(0.01)
                while True:
                    tmp_data = np.copy(self.raw_measure())
                    if np.array_equal(tmp_data, np.zeros(self.number_of_samples)) == False:
                        break
                data[k, jj] = np.copy(tmp_data)
                sleep(0.01)
                self.close_port()
                sleep(0.7) # Waiting for close port
        self.save_data('%s/data%d.txt' %(folder_path,int(time.time())), data, frequences)
        self.create_fig(data, frequences,folder_path )


    def save_data(self,filename,data,frequences):
        my_file=open(filename, 'w')
        print(frequences)
        #file_write = csv.writer(my_file, delimiter=',')
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                my_file.write(str(frequences[i]) + ',')
                for k in range(data.shape[2]):
                    my_file.write(str(data[i, j, k]) + ',')
                my_file.write('\n')
                #file_write.writerow(list(frequences[i])+list(data[i,j]))
                #file_write.writerow( frequences[i])
        my_file.close()

    def create_fig(self,data,frequences,folder_path):
        def func_fit(x, a, b, c, d):
            return a * np.cos( b * x + c) + d


        for i in range(data.shape[0]):
            x0 = np.array([0., 1/(data.shape[2]), 0., 0.])
            coeff, cov_matr = optimization.curve_fit(func_fit, np.arange(data.shape[2]), np.mean(data[i], axis = 0), x0)
            A, B, C, D = coeff
            xarr = np.linspace(0, data.shape[2], 1000)
            plt.plot(np.mean(data[i], axis = 0), label='ADC Measure for %1.f Hz' % frequences[i],c='b')
            plt.plot(xarr, func_fit(xarr, A, B, C, D), c='r', label='fit')
            plt.xlabel('Clock count')
            plt.ylabel('12 Bit Value')
            plt.legend( loc=0, borderaxespad=0.)
            plt.savefig('%s/figure%1.f.png' %(folder_path, frequences[i]), bbox_inches='tight')
            plt.close()
            ### wypróbować
            #my_file = open('%s/equqtions%d.txt' %(folder_path,frequences[i]), 'w')
            #my_file.write(str('='+A+'*'+'cos('+B+'*x+'+C+')+'+D))
            #my_file.close()
            ###wypróbować




if __name__ == '__main__':
    new_port = Connection_Port()
    new_port.complex_measure('Data',0,0,0,0)

