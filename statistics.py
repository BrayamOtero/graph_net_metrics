import csv
from unicodedata import name 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

import os

PATH = '/home/brayam/Tesis/Daniela/DRSIR-DRL-routing-approach-for-SDN/SDNapps_proac'


def getNameFiles():
    return os.listdir("{}/Metrics".format(PATH))


def get_flies_sorted():
    names_info = getNameFiles()
    return sorted(names_info, key=lambda x: float(x[:-16]))


def getDelayLossMean():
    df = pd.read_csv("{}/Metrics/11_net_metrics.csv".format(PATH))

    delays = df.loc[:, "delay"].tolist()
    delay_mean = np.mean(delays)

    losses = df.loc[:, "pkloss"]
    loss_mean = np.mean(losses)

    print("Delay mean: {} Loss mean: {}".format(delay_mean,loss_mean))

def getMean(df, metric):
    return np.mean(df.loc[:, metric])

def meanData(meanData, newData):
    meanData += newData
    meanData /= 2
    return meanData
def generateHours():
    hours = []
    for h in range(24):
        if h < 10:
            hours.append("0{}:00".format(h))
        else:
            hours.append("{}:00".format(h))            
    return hours

'''
Como por cada hora de trafico se hizo dos monitoreos se agrupan entre dos
'''
def getMetricXHour(metric_historic):
    # en la primer monitoreo no se capturo trafico y
    # los ultimos dos tampoco, solo hasta el 48
    metricsXhour = []
    for i in range(1,48,2):
        mean = (metric_historic[i] + metric_historic[i+1])/2
        metricsXhour.append(mean)
    return metricsXhour

if __name__ == "__main__":
    if len(sys.argv) < 2:        
        raise Exception('Es necesario colocar un argumento')        
    up_to_num = 0
    #nombre del agente para guardarlo en la csv
    name_agent = "default"

    for arg in sys.argv[1:]:
        option = arg.split("=")
        if option[0] == '--up_to':
            up_to_num = int(option[1])
        if option[0] == '--path':
            PATH = option[1]
        if option[0] == '--agent':
            PATH = option[1]
                    
    cvs_sorted = get_flies_sorted()
    delay = 0
    loss = 0
    qlen = 0
    delay_historic = []
    loss_historic = []
    qlen_historic = []

    for i in range(up_to_num):
        file = cvs_sorted[i]
        df = pd.read_csv("{}/Metrics/{}".format(PATH,file))        
        
        delay_mean = getMean(df, "delay")
        loss_mean = getMean(df, "pkloss")        
        q1_mean = getMean(df, "qlen->")
        q2_mean = getMean(df, "<-qlen")

        q_mean = (q1_mean+q2_mean)/2

        delay_historic.append(delay_mean)
        loss_historic.append(loss_mean)
        qlen_historic.append(q_mean)

        delay = meanData(delay, delay_mean)
        loss = meanData(loss, loss_mean) 
        qlen = meanData(qlen, q_mean)       
    
    print("Delay mean: {}\nLoss mean: {}\nQlen mean {}".format(delay,loss,qlen))
    # print("Delay historic: ")
    # print(delay_historic)
    # print("Loss historic: ")
    # print(loss_historic)
    with open('./metric_info.csv','w') as csvfile:
        header_names = ['count','delay','pkloss', 'qlen']
        file = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)        
        file.writerow(header_names)
        for i in range(up_to_num):            
            file.writerow([i, round(delay_historic[i],3), round(loss_historic[i],4), round(qlen_historic[i],3)])

    # plt.bar(['delay', 'loss', 'qlen'], [delay, loss*100, qlen*100], width=0.4)
    # plt.show()
    #por cada dos monitoreos es una hora de trafico

    hours = generateHours()

    delayXhour = getMetricXHour(delay_historic)
    lossXhour = getMetricXHour(loss_historic)
    qlenXhour = getMetricXHour(qlen_historic)

    plt.bar(hours, delayXhour)
    plt.show()

    plt.bar(hours, lossXhour)
    plt.show()

    plt.bar(hours, qlenXhour)
    plt.show()
    
    