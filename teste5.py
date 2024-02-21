import threading
import random
import time
import statistics

# Parâmetros do problema
max_passageiros = int(input("Digite o número total de passageiros: "))
num_carros = int(input("Digite o número total de carros disponíveis: "))
capacidade_carro = int(input("Digite a capacidade de cada carro: "))
Te = 0.3
Tm = 4
Tp_min = 0.1
Tp_max = 0.3

fila_mutex = threading.Semaphore(1)
carro_mutex = threading.Semaphore(1)
embarque_mutex = threading.Semaphore(1)
desembarque_mutex = threading.Semaphore(1)

# Classe Passageiro
class Passageiro:
    id = 1
    def __init__(self):
        self.id = Passageiro.id
        Passageiro.id += 1
        self.hora_chegada = 0
        self.hora_embarque = 0

# Classe Fila
class Fila:
    fila_espera = []
    total_passageiro = 0

    @staticmethod
    def chegada_passageiros():
        for _ in range(max_passageiros):
            time.sleep(random.uniform(Tp_min, Tp_max))
            passageiro = Passageiro()
            Fila.entra_fila(passageiro)

    @staticmethod
    def entra_fila(passageiro):
        fila_mutex.acquire()
        Fila.fila_espera.append(passageiro)
        Fila.total_passageiro += 1
        passageiro.hora_chegada = time.time()
        fila_mutex.release()
        print(f"{time.time():.2f} - Passageiro {passageiro.id} chegou.")

    @staticmethod
    def sair_fila():
        fila_mutex.acquire()
        passageiro = None
        if Fila.fila_espera:
            passageiro = Fila.fila_espera.pop(0)
            passageiro.hora_embarque = time.time()
        fila_mutex.release()
        return passageiro

    @staticmethod
    def funcionando():
        fila_mutex.acquire()
        resultado = (Fila.total_passageiro < max_passageiros) or ((Fila.total_passageiro >= max_passageiros) and Fila.fila_espera)
        fila_mutex.release()
        return resultado

# Classe Carro
class Carro:
    id = 1
    tempo_total_em_movimento = 0

    def __init__(self):
        self.id = Carro.id
        Carro.id += 1
        self.capacidade = capacidade_carro
        self.assento = []
        self.semaforo = threading.Semaphore(0)

    def embarcar_passageiro(self):
        print(f"{time.time():.2f} - Carro {self.id} começou o embarque.")
        while len(self.assento) < self.capacidade and Fila.funcionando():
            passageiro = Fila.sair_fila()
            if passageiro is not None:
                embarque_mutex.acquire()
                time.sleep(Te)
                print(f"{time.time():.2f} - Passageiro {passageiro.id} embarcou no Carro {self.id}.")
                self.assento.append(passageiro)
                embarque_mutex.release()
            else:
                time.sleep(Tp_min)

    def inicio_jornada(self):
        print(f"{time.time():.2f} - Carro {self.id} começou o passeio.")
        time.sleep(Tm)

    def fim_jornada(self):
        print(f"{time.time():.2f} - Carro {self.id} retornou e começou o desembarque.")
        for passageiro in self.assento:
            time.sleep(Te)
            desembarque_mutex.acquire()
            print(f"{time.time():.2f} - Passageiro {passageiro.id} desembarcou do Carro {self.id}")
            self.assento.remove(passageiro)
            desembarque_mutex.release()
        self.assento = []

    def jornada(self):
        while Fila.funcionando():
            self.embarcar_passageiro()
            self.inicio_jornada()
            self.fim_jornada()
            Carro.tempo_total_em_movimento += Tm

# Função para imprimir o relatório
def imprimir_relatorio():
    tempo_espera_fila = [p.hora_embarque - p.hora_chegada for p in Passageiro.__dict__.values() if isinstance(p, Passageiro)]
    tempo_minimo_espera = min(tempo_espera_fila)
    tempo_maximo_espera = max(tempo_espera_fila)
    tempo_medio_espera = statistics.mean(tempo_espera_fila)
    tempo_total = time.time()
    eficiencia_carros = (Carro.tempo_total_em_movimento / tempo_total) * 100

    print("----------------------------------------")
    print(f"Número de passageiros: {max_passageiros}")
    print(f"Número de carros: {Carro.id - 1}")
    print(f"Capacidade do carro: {capacidade_carro}")
    print("----------------------------------------")
    print("Relatório:")
    print(f"Tempo mínimo de espera na fila: {tempo_minimo_espera:.2f} seg")
    print(f"Tempo máximo de espera na fila: {tempo_maximo_espera:.2f} seg")
    print(f"Tempo médio de espera na fila: {tempo_medio_espera:.2f} seg")
    print(f"Eficiência do carro: {eficiencia_carros:.2f}% (Tempo em movimento / Tempo total)")

if __name__ == "__main__":
    carros = [Carro() for _ in range(num_carros)]
    chegada_thread = threading.Thread(target=Fila.chegada_passageiros)

    chegada_thread.start()
    for carro in carros:
        carro_thread = threading.Thread(target=carro.jornada)
        carro_thread.start()

    chegada_thread.join()
    for carro in carros:
        carro_thread.join()

    imprimir_relatorio()
