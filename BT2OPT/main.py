# import random
from time import time
import numpy as np
import pandas as pd


PATH = ["Djibouti", "Qatar", "Uruguay", "Western Sahara", "Zimbabwe"]


TIME_LIMIT = 60
CITY_LIMIT = 1000


# retorna a matriz de adjacencia da cidade em PATH[indexPath]


def readInstance(indexPath):

    with open("../data/processed/" + PATH[indexPath] + ".tsp", "r") as f:
        lines = f.readlines()

    for i in range(len(lines)):
        lines[i] = lines[i].split()
        for j in range(len(lines[i])):
            lines[i][j] = float(lines[i][j])

    return lines


# Calcula a regra de 3 para o tempo de execução da instância
def instanceTimeLimit(nCities):

    return TIME_LIMIT * nCities / CITY_LIMIT


def opt2(arr, a: int, b: int):

    newArr = arr.copy()

    while(a < b):

        aux = newArr[a]
        newArr[a] = newArr[b]
        newArr[b] = aux
        a += 1
        b -= 1
    return newArr


def qualityOfSolution(solution, matrizDistancias):

    totalDistance = 0
    for i in range(len(solution) - 1):
        totalDistance += matrizDistancias[solution[i]][solution[i+1]]

    totalDistance += matrizDistancias[solution[-1]][solution[0]]
    return totalDistance


def writeToFile(instancia, autoria, algoritmo, q_medio, q_desvio, t_medio):

    headers = ["instancia", "autoria", "algoritmo",
               "q-medio", "q-desvio", "t-medio"]

    df = pd.DataFrame({"instancia": instancia, "autoria": autoria,
                       "algoritmo": algoritmo, "q-medio": q_medio,
                       "q-desvio": q_desvio, "t-medio": t_medio})

    df.to_csv("./resultados.csv", header=headers, index=False)

# Busca tabu realizada sem aspiração. O pivot inicial é escolhido
# aleatoriamente, e os subsequentes são atualizados a cada iteração
# do loop externo, recebendo o melhor vizinho da iteração interna.
# A cada troca do pivot, os dois valores do 2-opt são adicionados a
# lista tabu.


def tabuSearch(tInitial, tLimit, matrizDistancias, nCidades):

    mandato = nCidades // 5
    # mandatoValues = [0 for _ in range(nCidades)]
    mandatoValues = np.array([0 for _ in range(nCidades)], dtype=np.int32)

    tabuList = []

    # pivot = [x for x in range(nCidades)]
    # random.shuffle(pivot)

    pivot = np.array([x for x in range(nCidades)], dtype=np.int32)
    np.random.shuffle(pivot)

    bestQuality = qualityOfSolution(pivot, matrizDistancias)

    size = len(pivot)

    x = 0

    while (x < size) and (time() - tInitial < tLimit):

        if mandatoValues[pivot[x]] != 0:
            x += 1
            continue

        nextQuality = -1
        nextSolution = -1
        nextToTabu = ()

        y = x + 2  # Comeca a partir de x + 2, para evitar 2opt com adjacente;
        while (y < size) and (time() - tInitial < tLimit):

            if (mandatoValues[pivot[y]] != 0):
                y += 1
                continue

            newSolution = opt2(pivot, x, y)
            newQuality = qualityOfSolution(newSolution, matrizDistancias)

            if (newQuality < nextQuality) or (nextQuality == -1):
                nextQuality = newQuality
                nextSolution = newSolution
                nextToTabu = (pivot[x], pivot[y])

            y += 1

        pivot = nextSolution

        # Atualiza a melhor qualidade
        if nextQuality < bestQuality:
            bestQuality = nextQuality

        # Atualiza a lista tabu
        newTabuList = []
        for i in tabuList:
            mandatoValues[i] -= 1
            if mandatoValues[i] != 0:
                newTabuList.append(i)
        tabuList = newTabuList

        # Adiciona x e y para a lista tabu
        for i in nextToTabu:
            tabuList.append(i)
            mandatoValues[tabuList[-1]] = mandato

        x = 0

    return bestQuality, tInitial


def main():

    averages = []  # array com a avg das melhores solucoes para cada instancia
    deviations = []  # array com o dp das melhores solucoes para cada instancia
    times = []  # array com o tempo de execução para cada instancia

    for i in range(len(PATH)):

        matrizDistancias = readInstance(i)
        nCidades = len(matrizDistancias)
        tLimit = instanceTimeLimit(nCidades)

        qualities = []
        localTime = []

        for _ in range(10):

            bestQuality, tInitial = tabuSearch(
                time(), tLimit, matrizDistancias, nCidades)

            qualities.append(bestQuality)
            localTime.append(time() - tInitial)

        # media da qualidade
        averages.append(round(sum(qualities) / len(qualities)))
        avgTime = 0

        for lTime in localTime:  # Media do tempo de execução da instancia
            avgTime += lTime

        avgTime = avgTime / len(localTime)
        times.append(round(avgTime))

        variance = 0  # desvio padrao da qualidade
        for quality in qualities:
            variance += (quality - averages[-1]) ** 2
        variance = variance / len(qualities)
        deviations.append(round(variance ** 0.5, 2))

    writeToFile(PATH, "Fernando", "BT2opt", averages, deviations, times)


main()
