import random
from time import time
import pandas as pd

PATH = ["Djibouti", "Qatar", "Uruguay", "Western Sahara", "Zimbabwe"]


def readInstance(indexPath):

    file = open("./Docs/" + PATH[indexPath] + ".txt", "r")
    lines = file.readlines()
    file.close()

    for i in range(len(lines)):
        lines[i] = lines[i].split()
        for j in range(len(lines[i])):
            lines[i][j] = float(lines[i][j])

    return lines


def opt2(arr, a, b):
    x = arr[a:b]

    if len(x) > 0:
        A = arr[:a]
        B = arr[b:]
        x.reverse()
    A.extend(x)
    A.extend(B)

    return A


def distanciaTotal(caminho, distancias):

    distancia = 0

    for i in range(len(caminho) - 1):
        distancia += distancias[caminho[i]][caminho[i + 1]]

    distancia += distancias[caminho[(len(caminho) - 1)]][caminho[0]]

    return distancia


def writeToFile(instancia, autoria, algoritmo, q_medio, q_desvio, t_medio):

    headers = ["instancia", "autoria", "algoritmo",
               "q-medio", "q-desvio", "t-medio"]

    df = pd.DataFrame({"instancia": instancia, "autoria": autoria,
                       "algoritmo": algoritmo, "q-medio": q_medio,
                       "q-desvio": q_desvio, "t-medio": t_medio})

    df.to_csv("./resultados.csv", header=headers, index=False)


def BLMM2opt(tLimit, matrizDistancias, nCidades):

    tInitial = time()

    solution = [x for x in range(nCidades)]
    random.shuffle(solution)

    menorDistancia = distanciaTotal(solution, matrizDistancias)

    size = len(solution)
    x = 0
    while x < size:

        y = x + 1
        while(y < size) and (time() - tInitial < tLimit):
            if x == y:
                y += 1
                continue

            newSolution = opt2(solution, x, y)

            newQuality = distanciaTotal(newSolution, matrizDistancias)

            if(newQuality < menorDistancia):

                menorDistancia = newQuality
                solution = newSolution
                x = 0
                y = 0

            y += 1

        x += 1

    return menorDistancia, tInitial


def main():

    averages = []  # array com a avg das melhores solucoes para cada instancia
    deviations = []  # array com o dp das melhores solucoes para cada instancia
    times = []  # array com o tempo de execução para cada instancia

    for i in range(len(PATH)):
        print(f"Startin {PATH[i]}")
        matrizDistancias = readInstance(i)
        nCidades = len(matrizDistancias)
        tLimit = 60 * nCidades / 1000

        qualities = []
        localTime = []

        for _ in range(10):

            bestQuality, tInitial = BLPM2opt(
                tLimit, matrizDistancias, nCidades)

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
