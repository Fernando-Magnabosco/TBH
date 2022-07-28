from random import choice, choices, randrange
from time import time
import pandas as pd


PATH = ["Djibouti", "Qatar", "Uruguay", "Western Sahara", "Zimbabwe"]


TIME_LIMIT = 60
CITY_LIMIT = 1000


# retorna a matriz de adjacencia da cidade em PATH[indexPath]


def readInstance(indexPath):

    with open("../data/" + PATH[indexPath] + ".tsp", "r") as f:
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


def createPheromoneTable(nCidades):

    pheromoneTable = []

    for i in range(nCidades):
        pheromoneTable.append([])
        for j in range(nCidades):
            pheromoneTable[i].append(nCidades)

    return pheromoneTable


def BCCF(pTable, tInitial, tLimit, dTable, nCidades):

    bestQuality = -1

    while time() - tInitial < tLimit:

        atualCity = randrange(nCidades)

        solution = [atualCity]

        localCities = [i for i in range(nCidades) if i != atualCity]
        probabilities = [0 for i in range(nCidades) if i != atualCity]

        while len(solution) != nCidades:

            for i in range(len(localCities)):

                pheromone = pTable[atualCity][localCities[i]]
                distance = dTable[atualCity][localCities[i]]

                probabilities[i] = pheromone / (distance * distance)

            # check if all probabilities are 0 (choices bugs when all are 0)
            if not sum(probabilities):
                chosen = choice(localCities)

            else:
                chosen = choices(
                    localCities, weights=probabilities, k=1)[0]

            solution.append(chosen)

            index = localCities.index(chosen)
            localCities.pop(index)
            probabilities.pop(index)

            atualCity = chosen

        quality = qualityOfSolution(solution, dTable)

        # update pheromone table
        alpha = 0.8
        if quality < bestQuality or bestQuality == -1:
            bestQuality = quality
            alpha = 1.2

        # update pheromone table

        for i in range(len(solution) - 1):
            pTable[solution[i]][solution[i+1]] *= alpha
            pTable[solution[i+1]][solution[i]] *= alpha

        pTable[solution[-1]][solution[0]] *= alpha
        pTable[solution[0]][solution[-1]] *= alpha

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

        distanceTable = readInstance(i)
        nCidades = len(distanceTable)
        tLimit = instanceTimeLimit(nCidades)

        qualities = []
        localTime = []

        for _ in range(10):

            bestQuality, tInitial = BCCF(createPheromoneTable(nCidades),
                                         time(), tLimit, distanceTable,
                                         nCidades)

            qualities.append(bestQuality)
            localTime.append(time() - tInitial)

        # media da qualidade
        averages.append(round(sum(qualities) / len(qualities)))

        # media do tempo de execucao
        avgTime = sum(localTime) / len(localTime)

        times.append(round(avgTime))

        variance = 0  # desvio padrao da qualidade
        for quality in qualities:
            variance += (quality - averages[-1]) ** 2
        variance = variance / len(qualities)
        deviations.append(round(variance ** 0.5, 2))

    writeToFile(PATH, "Fernando", "BCCF", averages, deviations, times)


main()
