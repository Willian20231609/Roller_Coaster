import threading
import random
import time
import statistics

# Parâmetros do problema
max_passageiros = 21
C = 10
Te = 0.3
Tm = 4
Tp_min = 0.1
Tp_max = 0.3

inicio = time.time()

fila_mutex = threading.Semaphore(1)
jornada_mutex = threading.Semaphore(1)
embarque_mutex = threading.Semaphore(1)
carro_mutex = threading.Semaphore(1)
relatorio_mutex = threading.Semaphore(1)

class Passageiro:
    id = 1
    passageiro = []
    def __init__(self):
        self.id = Passageiro.id
        Passageiro.id += 1
        self.hora_chegada = 0
        self.hora_embarque = 0 
        Passageiro.passageiro.append(self)


class Fila:
    fila_espera = []
    total_passageiro = 0
    ultimo_carro = -1

    def chegada_passageiros():
        for i in range(max_passageiros):
            time.sleep(random.uniform(Tp_min, Tp_max))
            passageiro = Passageiro()
            Fila.entra_fila(passageiro)
            

    def entra_fila(passageiro):
        fila_mutex.acquire()
        Fila.fila_espera.append(passageiro)
        Fila.total_passageiro += 1
        horario_atual = time.time() - inicio
        passageiro.hora_chegada = horario_atual 
        fila_mutex.release()
        print(f"{horario_atual:.2f} - Passageiro {passageiro.id} chegou.")


    def sair_fila():
        fila_mutex.acquire()
        if len(Fila.fila_espera) > 0:
            passageiro = Fila.fila_espera.pop(0)
            horario_atual = time.time() - inicio
            passageiro.hora_embarque = horario_atual
        else:
            passageiro = None
        fila_mutex.release()
        return passageiro

    def funcionando():
        fila_mutex.acquire()
        resultado = (Fila.total_passageiro < max_passageiros) or ((Fila.total_passageiro >= max_passageiros) and (len(Fila.fila_espera) > 0))
        fila_mutex.release()
        return resultado
    
class Carro:
    id = 1
    carros = []
    tempo_total_em_movimento = 0

    def __init__(self, c):
        self.id = Carro.id
        Carro.id += 1
        self.capacidade = c
        self.assento = []
        Carro.carros.append(self)
        self.semaforo = threading.Semaphore(0)

    def embarcar_passageiro(self):
        print(f"{time.time()-inicio:.2f} - Carro {self.id} começou o embarque.")
        while (len(self.assento) < self.capacidade) and Fila.funcionando():
            passageiro = Fila.sair_fila()
            if passageiro is not None:
                time.sleep(Te)
                print(f"{time.time()-inicio:.2f} - Passageiro {passageiro.id} embarcou no Carro {self.id}.")
                self.assento.append(passageiro)
            else:
                time.sleep(Tp_min)

    def inicio_jornada(self):
        print(f"{time.time()-inicio:.2f} - Carro {self.id} começou o passeio.")
        time.sleep(Tm)

    def fim_jornada(self):
        print(f"{time.time()-inicio:.2f} - Carro {self.id} retornou e começou o desembarque.")
        for passageiro in self.assento:
            time.sleep(Te)
            print(f"{time.time()-inicio:.2f} - Passageiro {passageiro.id} desembarcou do Carro {self.id}.")
        self.assento = []

    def jornada(self):
        while Fila.funcionando():
            while (Carro.proximo_carro() != self) and (Fila.funcionando()):
                self.semaforo.acquire()
            
            if Fila.funcionando():
                embarque_mutex.acquire()
                self.embarcar_passageiro()
                embarque_mutex.release()
                jornada_mutex.acquire()
                self.chamar_proximo()
                self.inicio_jornada()
                jornada_mutex.release()
                embarque_mutex.acquire()
                self.fim_jornada()
                embarque_mutex.release()

                relatorio_mutex.acquire()
                Carro.tempo_total_em_movimento += Tm
                relatorio_mutex.release()

            else: 
                self.chamar_proximo()

            

    def proximo_carro():
        carro_mutex.acquire()
        proximo = Carro.carros[0]
        carro_mutex.release()
        return proximo
    
    def chamar_proximo(self):
        carro_mutex.acquire()
        proximo= Carro.carros.pop(0)
        Carro.carros.append(proximo)
        Carro.carros[0].semaforo.release()
        carro_mutex.release()

# Função para imprimir o relatório
def imprimir_relatorio():
    tempo_espera_fila = [p.hora_embarque - p.hora_chegada for p in Passageiro.passageiro]
    tempo_minimo_espera = min(tempo_espera_fila)
    tempo_maximo_espera = max(tempo_espera_fila)
    tempo_medio_espera = statistics.mean(tempo_espera_fila)
    tempo_total = time.time() - inicio
    eficiencia_carros = (Carro.tempo_total_em_movimento / tempo_total) * 100

    print("----------------------------------------")
    print(f"Número de passageiros: {max_passageiros}")
    print(f"Número de carros: {len(Carro.carros)}")
    print(f"Capacidade do carro: {C}")
    print("----------------------------------------")
    print("Relatório:")
    print(f"Tempo mínimo de espera na fila: {tempo_minimo_espera:.2f} seg")
    print(f"Tempo máximo de espera na fila: {tempo_maximo_espera:.2f} seg")
    print(f"Tempo médio de espera na fila: {tempo_medio_espera:.2f} seg")
    print(f"Eficiência do carro: {eficiencia_carros:.2f}% (Tempo em movimento / Tempo total)")

if __name__ == "__main__":
    carros = [Carro(C),Carro(C),Carro(C),Carro(C),Carro(C)]
    carro_threads = [threading.Thread(target=i.jornada) for i in carros]
    chegada_thread = threading.Thread(target=Fila.chegada_passageiros)

    chegada_thread.start()
    for i in carro_threads:
        i.start()

    chegada_thread.join()
    for i in carro_threads:
        i.join()

    imprimir_relatorio()
    