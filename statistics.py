import csv
from unicodedata import name 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import re

import math

import manageFiles as mFile

PATH = '/home/brayam/Tesis/Daniela/DRSIR-DRL-routing-approach-for-SDN/SDNapps_proac'
up_to_num = 0
valid_monitoring = 0

capacity_links = {}

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
    if meanData == 0:
        return newData
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

def saveInfo(th, delay, loss, qlen, hours, name_agent):
    data = {
        'hour' : hours,
        'th' : th,
        'delay' : delay,
        'loss' : loss,
        'qlen' : qlen
    }
    df = pd.DataFrame(data)

    df.to_csv(''.join(['./metrics_csv/metrics_',name_agent, '.csv']), index=False)

def getThroughput(df):
    th = 0
    for i in df.index:
        if df["free_bw"][i] == 0.0:
            link = (df["node1"][i], df["node2"][i])
            th += getCapacityLink(link) * 1000
        else:
            th += df["used_bw"][i]/1000
        print(th)
    th = th/37
    return th# son 37 enlaces


def getCapacityLink(link):
    if len(capacity_links) == 0:        
        getCapacityLinks()
    
    return capacity_links[link]    
def getCapacityLinks():
    with open('bw.txt') as f:
        for line in f:
            data = line.split(',')
            link = (int(data[0]), int(data[1]))
            capacity_links[link] = float(data[3])    
'''
Como por cada hora de trafico se hizo dos monitoreos se agrupan entre dos
'''
def getMetricXHour(metric_historic):    
    # en la primer monitoreo no se capturo trafico y
    # los ultimos dos tampoco, solo hasta el 48
    metricsXhour = []
    # como se va dividir el monitoreo
    factor = valid_monitoring/24
    since_index = 0
    for i in range(24):
        to_index = math.ceil(factor*(i + 1))
        lst_hour = metric_historic[since_index : to_index]        
        mean = sum(lst_hour)/len(lst_hour)        
        metricsXhour.append(mean)
        since_index = to_index    
    return metricsXhour

'''
Obtiene el nombre del agente desde el nombre del csv metric_[name_agent].csv
'''
def getNameAgent(name_raw):
    m = re.search(r'metrics_([a-zA-Z]+)', name_raw)
    if m:
        return m.group(1)
    else: 
        return False

def find_number(string):
    match = re.findall(r'\d+', string)
    if match:
        return match[0]
    else:
        return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:        
        raise Exception('Es necesario colocar un argumento')        
    
    #nombre del agente para guardarlo en la csv
    name_agent = "default"
    #graficar todos los datos de los agentes DRL
    plot_all = False

    resume_metrics = False

    for arg in sys.argv[1:]:
        option = arg.split("=")
        if option[0] == '--up_to':
            up_to_num = int(option[1])
        if option[0] == '--path':
            PATH = option[1]
        if option[0] == '--agent':
            name_agent = option[1]
        if option[0] == '--plot_all':
            plot_all = True
        if option[0] == '--resume':
            resume_metrics = True

    if plot_all:
        list_name = mFile.get_files_info_net()
        num_agent = len(list_name)
        info_metrcis = {}
        for name_info in list_name:
            dir_file = "./metrics_csv/" + name_info
            print(dir_file)
            df = pd.read_csv(dir_file)            
            info_metrcis[name_info] = df
        
        ind = np.arange(24) #24 hours 
        width = 0.8/num_agent
        metrics = ["th", "delay", "loss", "qlen"]
        for metric in metrics:
            is_first = True
            cout_move = 0
            for name_agent, df_info in info_metrcis.items():                                
                plt.bar(ind + cout_move * width, df_info.loc[:, metric].tolist(), width, label=name_agent[:-4])                
                cout_move += 1

            plt.ylabel(metric + ' mean')
            plt.title('Result of ' + metric)

            plt.xticks(ind + width/num_agent, df_info.loc[:, "hour"].tolist())
            plt.legend(loc='best')
            plt.show()
        exit()

    if resume_metrics:
        list_name = mFile.get_files_info_net()        
        info_metrcis = {}
        for name_info in list_name:
            dir_file = "./metrics_csv/" + name_info
            # print(dir_file)
            df = pd.read_csv(dir_file)            
            info_metrcis[name_info] = df
                
        metrics = ["th" ,"delay", "loss", "qlen"]
        data = {}
        # dict_hour = {"00:00" : [], "01:00" : [],"02:00" : [],"03:00" : [],"04:00" : [],"05:00" : [],"06:00" : [],"07:00" : [],"08:00" : [],"09:00" : [],"10:00" : [],"11:00" : [],"12:00" : [],"13:00" : [],"14:00" : [],"15:00" : [],"16:00" : [],"17:00" : [],"18:00" : [],"19:00" : [],"20:00" : [],"21:00" : [],"22:00" : [],"23:00" : []}        
        for raw_name_agent, df_info in info_metrcis.items():            
            name = getNameAgent(raw_name_agent)                
            if (name not in data):
                data.setdefault(name, {"th" : [], "delay" : [], "loss" : [], "qlen" : []})
            for metric in metrics:
                if metric == metrics[0] and int(find_number(raw_name_agent)) < 6:
                    continue
                data[name][metric].append(df_info.loc[:, metric].tolist())
        
        ind = np.arange(24) #24 hours         
        num_agent = len(data.keys())
        width = 0.8/num_agent
        for metric in metrics:
            cout_move = -1
            for nameAgent in data.keys():                
                npInfo = np.array(data[nameAgent][metric])
                if metric == metrics[0]:
                    npInfo = npInfo/37
                meanMetric = np.mean(npInfo, axis=0)
                data[nameAgent][metric] = meanMetric.tolist()

                plt.bar(ind + cout_move * width, data[nameAgent][metric], width, label=nameAgent)                
                cout_move += 1

            plt.ylabel(metric + ' mean')
            plt.title('Result of ' + metric)

            plt.xticks(ind + width/num_agent,  generateHours())
            plt.legend(loc='best')
            plt.show()
        
        exit()
    mFile.createDir('metrics_csv')
                    
    cvs_sorted = mFile.get_flies_sorted(PATH)
    delay = 0
    loss = 0
    qlen = 0
    th = 0
    delay_historic = []
    loss_historic = []
    qlen_historic = []
    th_historic = []

    num_file = 0
	
    while (num_file != up_to_num):
        valid_monitoring += 1
        file = cvs_sorted[valid_monitoring]
        num_file = int(re.findall('[0-9]+', file)[0])
        df = pd.read_csv("{}/Metrics/{}".format(PATH,file))

        delay_mean = getMean(df, "delay")
        loss_mean = getMean(df, "pkloss")
        th_mean = getMean(df, "free_bw")/37 # EL bw se escala a 10^3
        q1_mean = getMean(df, "qlen->")
        q2_mean = getMean(df, "<-qlen")

        q_mean = (q1_mean+q2_mean)/2

        delay_historic.append(delay_mean)
        loss_historic.append(loss_mean)
        qlen_historic.append(q_mean)
        th_historic.append(th_mean)

        delay = meanData(delay, delay_mean)
        loss = meanData(loss, loss_mean)
        qlen = meanData(qlen, q_mean)
        th = meanData(th, th_mean)         

    print("Throughput mean: {}\n Delay mean: {}\nLoss mean: {}\nQlen mean {}".format(th, delay,loss,qlen))
    # print("Delay historic: ")
    # print(delay_historic)
    # print("Loss historic: ")
    # print(loss_historic)
    #with open('./metrics_csv/metric_info.csv','w') as csvfile:
    #    header_names = ['count','delay','pkloss', 'qlen']
    #    file = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)        
    #    file.writerow(header_names)
    #    for i in range(up_to_num):            
    #        file.writerow([i, round(delay_historic[i],3), round(loss_historic[i],4), round(qlen_historic[i],3)])

    # plt.bar(['delay', 'loss', 'qlen'], [delay, loss*100, qlen*100], width=0.4)
    # plt.show()
    #por cada dos monitoreos es una hora de trafico

    hours = generateHours()

    delayXhour = getMetricXHour(delay_historic)
    lossXhour = getMetricXHour(loss_historic)
    qlenXhour = getMetricXHour(qlen_historic)
    thXhour = getMetricXHour(th_historic)

    saveInfo(thXhour, delayXhour, lossXhour, qlenXhour, hours, name_agent)

    plt.bar(hours, thXhour)
    plt.show()

    plt.bar(hours, delayXhour)
    plt.show()

    plt.bar(hours, lossXhour)
    plt.show()

    plt.bar(hours, qlenXhour)
    plt.show()
    
    