from random import randrange, choice
from time import time
from math import ceil
import pandas as pd
import heapq


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


def qualityOfSolution(solution, matrizDistancias):

    totalDistance = 0
    for i in range(len(solution) - 1):
        totalDistance += matrizDistancias[solution[i]][solution[i+1]]

    totalDistance += matrizDistancias[solution[-1]][solution[0]]
    return totalDistance


def BCGa(tInitial, tLimit, matrizDistancias, nCidades):

    bestQuality = -1

    while time() - tInitial < tLimit:

        atualCity = randrange(nCidades)

        solution = [atualCity]

        localCities = [i for i in range(nCidades) if i != atualCity]

        while len(solution) != nCidades:

            # localCities.sort(key=lambda x: matrizDistancias[atualCity][x])
            heapq.nlargest(ceil(len(localCities) * 0.3), localCities,
                           key=lambda x: matrizDistancias[atualCity][x])

            chosen = choice(
                localCities[:ceil(len(localCities) * 0.3)])

            solution.append(chosen)
            localCities.remove(chosen)

            atualCity = chosen

        quality = qualityOfSolution(solution, matrizDistancias)

        if quality < bestQuality or bestQuality == -1:
            bestQuality = quality

    return bestQuality, tInitial


def writeToFile(instancia, autoria, algoritmo, q_medio, q_desvio, t_medio):

    headers = ["instancia", "autoria", "algoritmo",
               "q-medio", "q-desvio", "t-medio"]

    df = pd.DataFrame({"instancia": instancia, "autoria": autoria,
                       "algoritmo": algoritmo, "q-medio": q_medio,
                       "q-desvio": q_desvio, "t-medio": t_medio})

    df.to_csv("./resultados.csv", header=headers, index=False)


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

            bestQuality, tInitial = BCGa(
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

    writeToFile(PATH, "Fernando", "BCGα", averages, deviations, times)


main()
