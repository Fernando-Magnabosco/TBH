import random
from time import time
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


def BLPM2opt(tInitial, tLimit, matrizDistancias, nCidades):

    solution = [x for x in range(nCidades)]
    random.shuffle(solution)

    bestQuality = qualityOfSolution(solution, matrizDistancias)

    size = len(solution)
    x = 0
    while x < size:

        y = x + 1
        while(y < size) and (time() - tInitial < tLimit):
            if x == y:
                y += 1
                continue

            newSolution = opt2(solution, x, y)

            newQuality = qualityOfSolution(newSolution, matrizDistancias)

            if(newQuality < bestQuality):

                bestQuality = newQuality
                solution = newSolution
                x = 0
                y = 0

            y += 1

        x += 1

    return bestQuality, tInitial


def main():

    averages = []  # array com a avg das melhores solucoes para cada instancia
    deviations = []  # array com o dp das melhores solucoes para cada instancia
    times = []  # array com o tempo de execução para cada instancia

    for i in range(len(PATH)):
        print(f"Startin {PATH[i]}")
        matrizDistancias = readInstance(i)
        nCidades = len(matrizDistancias)
        tLimit = instanceTimeLimit(nCidades)

        qualities = []
        localTime = []

        for _ in range(10):

            bestQuality, tInitial = BLPM2opt(
                time(), tLimit, matrizDistancias, nCidades)

            qualities.append(bestQuality)
            localTime.append(time() - tInitial)

            print(f"Time elapsed: {time()-tInitial}")

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

    writeToFile(PATH, "Fernando", "BLPM2opt", averages, deviations, times)


main()
