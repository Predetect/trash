import time
from datetime import datetime
import csv
import json
import numpy
import time
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

def epoch_to_readable(timestamp):
    return(time.strftime("%Z - %Y/%m/%d, %H:%M:%S", time.localtime(timestamp)))

def import_volumes(filename):
    
    """
    Expects json of {'id':[volume history]}
    to be present in working directory
    """
    
    with open(filename) as f:
        volumes = json.load(f)
    
    missing = []
    for itemid in volumes:
        if type(volumes[str(itemid)]) == list:
            volumes[str(itemid)] = list(map(int, volumes[str(itemid)]))
        else:
            missing.append(str(itemid))
    for itemid in missing:
        del(volumes[itemid])
    return(volumes)

def id_to_name(itemid):
    
    """
    Expects jsons nonmembs and membs
        {'id':{'id': int, 'name': str}}
    to be present in working directory
    """
    
    with open('nonmembs.json') as f:
        nonmembs = json.load(f)
    with open('membs.json') as f:
        membs = json.load(f)
    
    if str(itemid) in nonmembs:
        return(nonmembs[str(itemid)]['name'], 'nonmembs')
    elif str(itemid) in membs:
        return(membs[str(itemid)]['name'], 'membs')
    else:
        raise KeyError('Can not find item')

def load(itemid):
    raw = []
    with open('%s.csv' % str(itemid), 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            raw.append(row)
    return(raw)

def strip(raw):
    data = []
    for i in range(1, len(raw)):
        for j in range(1, len(raw[i])):
            data.append(eval(raw[i][j]))
    return(data)

def chop_at_gap(itemid, maxgap):
    chopped = {}
    data = strip(load(itemid))
    j = 1
    for i in range(j, len(data)):
        td = data[i]['timestamp'] - data[i-1]['timestamp']
        if td > 3600:
            chopped[str(j)] = data[j:i-1]
            j = i
    chopped[str(j)] = data[j:]
    return(chopped)

def visu(data, plot_or_not):
    
    plt.clf()
    x1 = []
    x2 = []
    buy = []
    sell = []
    squant = []
    bquant = []
    
    for element in data:
        if element['buying'] != 0:
            buy.append(element['buying'])
            x1.append(datetime.fromtimestamp(int(element['timestamp'])))
            bquant.append(element['buyingQuantity'])
        if element['selling'] != 0:
            sell.append(element['selling'])
            x2.append(datetime.fromtimestamp(int(element['timestamp'])))
            squant.append(element['sellingQuantity'])
            
    if plot_or_not == True:
        
        fig, ax1 = plt.subplots()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(byhour=[0,2]))

        ax1.plot(x1, buy, label='buy', color='b', marker='o', linestyle='--', markersize=4, alpha=.8)
        ax1.plot(x2, sell, label='sell', color='orange', marker='o', linestyle='--', markersize=4, alpha=.8)

        xmin,xmax,ymin,ymax = ax1.axis()

        ax1.axis((xmin,xmax,ymin-(.2*ymin),ymax))

        ax2 = ax1.twinx()
        ax2.plot(x1, bquant, label='buy', color='b', alpha=0.2)
        ax2.plot(x2, squant, label='sell', color='orange', alpha=0.2)
        ax2.fill_between(x1, 0, bquant, facecolor="b", alpha=0.4)
        ax2.fill_between(x2, 0, squant, facecolor="orange", alpha=0.4)

        plt.gcf().autofmt_xdate()
        fig.set_size_inches(18.5, 10.5)
        plt.show()
        
        print(buy, sell)
    return(buy, sell)

def plothisto(data, bins):
    hist, bins = np.histogram(data, bins=20)
    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2
    plt.bar(center, hist, align='center', width=width)
    plt.show()

def avg_daily(volumes, interval):
    """
    Return avg. daily trading volume of past [interval] days
    """
    return(int(sum(volumes[len(volumes)-interval:])/interval))