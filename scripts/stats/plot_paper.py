#!/usr/bin/env python3

# Given a stats.txt file and a file name for the output plot, draws the ROC curve and computes the AUC score. If the
# run was incomplete, but all true alarms were discovered, then an additional parameter TOTAL, the total number of
# alarms in the benchmark, may be specified, and the script will automatically complete the ranking.
# ./auc.py js_500stat.txt auc.pdf [TOTAL]
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
#from scipy.interpolate import spline
import numpy as np
import math
import sys

program = sys.argv[1]
totalAlarm = sys.argv[2] if len(sys.argv) >= 3 else None
nBaseC = sys.argv[3]
dirPath = sys.argv[4]

TOOL = "Bingo"
MLN = "Baseline"

def read_stats0(filename):
    numTrue = 0
    numFalse = 0
    index = 0
    xindices = [0]
    yindices = [0]
    for line in open(filename):
        if index > 0:
            if line.find('TrueGround') >= 0:
                numTrue = numTrue + 1
            else:
                numFalse = numFalse + 1
            xindices.append(numFalse)
            yindices.append(numTrue)
        index = index + 1

    if totalAlarm != None:
        while index <= int(totalAlarm):
            numFalse = numFalse + 1
            xindices.append(numFalse)
            yindices.append(numTrue)
            index = index + 1
    return (numTrue, numFalse, xindices, yindices)

def ratio(num, indices):
    return list(map(lambda x: float(x) / float(num), indices))

def auc(numTrue, numFalse, xindices, yindices):
    (xindices, yindices) = (ratio(numFalse, xindices), ratio(numTrue, yindices))

    # auc
    x0 = 0.0
    auc = 0.0
    for (x,y) in zip(xindices, yindices):
        auc = auc + (x - x0) * y
        x0 = x

    print('AUC: {0}'.format(auc))

# plot
    plt.rcParams['axes.xmargin'] = 0
    plt.rcParams['axes.ymargin'] = 0
    fig, ax = plt.subplots()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


    plt.tight_layout()
    plt.xlabel('False Positive Ratio')
    plt.ylabel('True Positive Ratio')

    markevery = 10
    linewidth = 1

    (_, _, xindices1, yindices1) = read_stats0(program + "/stats-1.txt")
    (_, _, xindices2, yindices2) = read_stats0(program + "/stats-2.txt")
    (_, _, xindices3, yindices3) = read_stats0(program + "/stats-3.txt")
    (_, _, xindices4, yindices4) = read_stats0(program + "/stats-4.txt")
    (_, _, xindices5, yindices5) = read_stats0(program + "/stats-5.txt")

    (xindices1, yindices1) = (ratio(numFalse, xindices1), ratio(numTrue, yindices1))
    (xindices2, yindices2) = (ratio(numFalse, xindices2), ratio(numTrue, yindices2))
    (xindices3, yindices3) = (ratio(numFalse, xindices3), ratio(numTrue, yindices3))
    (xindices4, yindices4) = (ratio(numFalse, xindices4), ratio(numTrue, yindices4))
    (xindices5, yindices5) = (ratio(numFalse, xindices5), ratio(numTrue, yindices5))

    plt.plot(xindices, yindices, 'b', marker='', markevery = markevery, linewidth=1, label=TOOL)
    plt.plot(xindices1, yindices1, 'c-.', marker='', linewidth = linewidth,markevery = markevery, label=MLN)
    plt.plot(xindices2, yindices2, 'm-.', marker='', linewidth = linewidth,markevery = markevery)
    plt.plot(xindices3, yindices3, 'y-.', marker='', linewidth = linewidth,markevery = markevery)
    plt.plot(xindices4, yindices4, 'k-.', marker='', linewidth = linewidth,markevery = markevery)
    plt.plot(xindices5, yindices5, 'g-.', marker='', linewidth = linewidth,markevery = markevery)
    plt.plot([0,1],[0,1],'r--', linewidth=linewidth, label="Random")

    plt.legend() 
    plt.savefig(program + "/" + program + '_1.pdf', bbox_inches='tight')
    plt.close()

def auc_absolute(numTrue, numFalse, xindices, yindices):
    plt.rcParams['axes.xmargin'] = 0
    plt.rcParams['axes.ymargin'] = 0
    plt.tight_layout()
    fig, ax = plt.subplots()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.xlabel('# False Alarms (total = ' + str(numFalse) + ')')
    plt.ylabel('# Bugs (total = ' + str(numTrue) + ')')

    markevery = 10
    linewidth = 1
    plt.plot(xindices, yindices, 'b', marker='', linewidth = linewidth, markevery = markevery, label=TOOL)

    (_, _, xindices1, yindices1) = read_stats(program + "/stats-1.txt")
    (_, _, xindices2, yindices2) = read_stats(program + "/stats-2.txt")
    (_, _, xindices3, yindices3) = read_stats(program + "/stats-3.txt")
    (_, _, xindices4, yindices4) = read_stats(program + "/stats-4.txt")
    (_, _, xindices5, yindices5) = read_stats(program + "/stats-5.txt")

    plt.plot(xindices1, yindices1, 'c-.', marker='', linewidth = linewidth,markevery = markevery, label=MLN)
    plt.plot(xindices2, yindices2, 'm-.', marker='', linewidth = linewidth,markevery = markevery)
    plt.plot(xindices3, yindices3, 'y-.', marker='', linewidth = linewidth,markevery = markevery)
    plt.plot(xindices4, yindices4, 'k-.', marker='', linewidth = linewidth,markevery = markevery)
    plt.plot(xindices5, yindices5, 'g-.', marker='', linewidth = linewidth,markevery = markevery)
    plt.plot([0,numFalse],[0,numTrue],'r--', linewidth=linewidth, label="Random")

    plt.legend() 
    plt.savefig(program + "/" + program + '_2.pdf', bbox_inches='tight')
    plt.close()

def iteration(numTrue, numFalse, xindices, yindices, smooth=False):
    plt.rcParams['axes.xmargin'] = 0
    plt.rcParams['axes.ymargin'] = 0
    plt.tight_layout()

    fig, ax = plt.subplots()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    total = numTrue + numFalse
    plt.xlabel('# Iterations (total = ' + str(total) + ')')
    plt.ylabel('# Found Bugs (total = ' + str(numTrue) + ')')


    markersize = 3
    iters = range(0, total + 1)
#    plt.plot([0,numTrue],[0,numFalse],'r--')

    (_, _, xindices1, yindices1) = read_stats0(program + "/stats-1.txt")
    (_, _, xindices2, yindices2) = read_stats0(program + "/stats-2.txt")
    (_, _, xindices3, yindices3) = read_stats0(program + "/stats-3.txt")
    (_, _, xindices4, yindices4) = read_stats0(program + "/stats-4.txt")
    (_, _, xindices5, yindices5) = read_stats0(program + "/stats-5.txt")
    
    bests = []
    medians = []
    medians_mark = []
    worsts = []
    whiskers = []
    index = 0
    markevery = int(len(xindices) / 10)
#    for d in zip(yindices1, yindices2, yindices3, yindices4, yindices5):
#        d = sorted(d)
#        medians.append(d[2])
#        if index % markevery == 0:
#            bests.append(d[4])
#            medians_mark.append(d[2])
#            worsts.append(d[0])
#            whiskers.append(index)
#        index += 1

    if smooth:
        # Bayesian
        iters_sm = np.array(iters)
        yindices_sm = np.array(yindices)
        iters_smooth = np.linspace(iters_sm.min(), iters_sm.max(), 200)
        yindices_smooth = spline(iters, yindices, iters_smooth)
        plt.plot(iters_smooth, yindices_smooth, 'b', linewidth=1, markersize=markersize, label=TOOL)

        # MLN
        medians_sm = np.array(medians)
        iters_smooth = np.linspace(iters_sm.min(), iters_sm.max(), 100)
        medians_smooth = spline(iters, medians, iters_smooth)
        plt.plot(iters_smooth, medians_smooth, 'g-', 'o', markevery = 10000, linewidth=1, markersize=markersize, label=MLN)
    else:
        plt.plot(iters, yindices, 'b', linewidth=1, label=TOOL)
#        plt.plot(iters, medians, 'g', linewidth=1, markevery=100000, marker = 'o', markersize=5, label=MLN)
        plt.plot([0,len(iters)-1],[0,numTrue],'r--', linewidth=1, label="Random")

#    plt.scatter(whiskers[1:], bests[1:], marker='_', c='g')
#    plt.scatter(whiskers, medians_mark, marker='o', c='g', s=8)
#    plt.scatter(whiskers[1:], worsts[1:], marker='_', c='g', linewidths=0.05)
#    plt.vlines(whiskers[1:], worsts[1:], bests[1:], colors='g', linewidth=0.5)

    plt.legend() 
    plt.savefig(program + "/" + program + '_3.pdf', bbox_inches='tight')
    plt.close()


def iteration2(numTrue, numFalse, xindices, yindices, smooth=False):
    plt.rcParams['axes.xmargin'] = 0
    plt.rcParams['axes.ymargin'] = 0
    plt.tight_layout()

    fig, ax = plt.subplots()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    total = numTrue + numFalse
    plt.xlabel('# Iterations (total = ' + str(total) + ')')
    plt.ylabel('# Found Bugs (total = ' + str(numTrue) + ')')


    markersize = 3
    iters = []
#    plt.plot([0,numTrue],[0,numFalse],'r--')

    (_, _, xindices1, yindices1) = read_stats(program + "/stats-1.txt")
    (_, _, xindices2, yindices2) = read_stats(program + "/stats-2.txt")
    (_, _, xindices3, yindices3) = read_stats(program + "/stats-3.txt")
    (_, _, xindices4, yindices4) = read_stats(program + "/stats-4.txt")
    (_, _, xindices5, yindices5) = read_stats(program + "/stats-5.txt")
    
    bests = []
    medians = []
    medians_mark = []
    worsts = []
    whiskers = []
    index = 0
    markevery = int(len(xindices) / 10)
    for d in zip(yindices1, yindices2, yindices3, yindices4, yindices5):
        d = sorted(d)
        medians.append(d[2])
        iters.append(index)
        if index % markevery == 0:
            bests.append(d[4])
            medians_mark.append(d[2])
            worsts.append(d[0])
            whiskers.append(index)
        index += 1
        if d[0] == numTrue:
            break
    plt.plot(iters, yindices[0:len(iters)], 'b', linewidth=1, label=TOOL)
    plt.plot(iters, medians[0:len(iters)], 'g', linewidth=1, markevery=100000, marker = 'o', markersize=3, label=MLN)
    plt.plot([0,len(iters)-1],[0,numTrue * (len(iters)-1) / total],'r--', linewidth=1, label="Random")

    plt.scatter(whiskers[1:], bests[1:], marker='_', c='g')
    plt.scatter(whiskers, medians_mark, marker='o', c='g', s=8)
    plt.scatter(whiskers[1:], worsts[1:], marker='_', c='g', linewidths=0.05)
    plt.vlines(whiskers[1:], worsts[1:], bests[1:], colors='g', linewidth=0.5)
    
    if numTrue < 10:
        plt.yticks(range(0, numTrue+1))
    plt.legend() 
    plt.savefig(program + "/" + program + '_4.pdf', bbox_inches='tight')
    plt.close()

def read_stats(filename, totalAlarm):
    index = 1
    trues = []
    for line in open(filename):
        if line.find('TrueGround') >= 0:
            trues.append(index)
        index = index + 1
#    trues = [ x / float(totalAlarm) * 100 for x in trues ]
    return trues

labels = ["BINGO", "BASE-C"]
titlesize=27
labelsize=25
ticksize=20

def draw(program, totalAlarm):
    plt.rcParams['axes.titlepad'] = 15
    plt.rc('xtick', labelsize=ticksize)
    plt.rc('ytick', labelsize=ticksize)
    plt.rcParams['xtick.major.pad']= 10
    filename = dirPath + "/" + program + "/stats.txt"

    try:
        bingo_trues = read_stats(dirPath+"/"+program+"/stats.txt", totalAlarm)

        #mln_trues1 = read_stats(program+"/stats-1.txt", totalAlarm)
        #mln_trues2 = read_stats(program+"/stats-2.txt", totalAlarm)
        #mln_trues3 = read_stats(program+"/stats-3.txt", totalAlarm)
        #mln_trues4 = read_stats(program+"/stats-4.txt", totalAlarm)
        #mln_trues5 = read_stats(program+"/stats-5.txt", totalAlarm)
        #mln_zipped = zip(mln_trues1, mln_trues2, mln_trues3, mln_trues4, mln_trues5)
        #mid_ndx = 2

        print('nBaseC is  {0}'.format(nBaseC))
        mln_all = []
        for i in range(0, int(nBaseC)):
           mln_all.append(read_stats(dirPath+"/"+program+"/stats-"+str(i+1)+".txt", totalAlarm))
        mln_zipped = zip (*mln_all)
        mid_ndx = (int(nBaseC) - (int(nBaseC) % 2)) // 2 
        print('midndx is {0}'.format(mid_ndx))

        mln_trues = []
        for mln in mln_zipped:
            mln = sorted(mln)
            mln_trues.append(mln[mid_ndx])
    except:
        mln_trues = [int(totalAlarm)]
    print ('mln_trues are: {0}'.format(mln_trues))
    rate = float(numTrue) / float(totalAlarm) * 100
    random_trues = []
    index = 1
#    while rate * index > numTrue:
#        random_trues.append(random_trues)
#        index += 1

    plt.boxplot([bingo_trues, mln_trues], labels=labels, whis='range', showcaps=False)
    plt.scatter([1,2], [bingo_trues[0], mln_trues[0]], marker= 'o', c='black', s=90)
    plt.scatter([1,2], [bingo_trues[-1], mln_trues[-1]], marker= 'x', c='black', s=90)
    plt.ylabel("# Alarms", size=labelsize)
    plt.title(names[program] + ' (total = ' + str(totalAlarm) + ')', size = titlesize)
    plt.ylim(0,mln_trues[-1])

names = {'app-324': 'app-324',
         'noisy-sounds': 'noisy-sounds',
         'app-ca7': 'app-ca7',
         'app-kQm': 'app-kQm',
         'tilt-mazes': 'tilt-mazes',
         'andors-trail': 'andors-trail',
         'ginger-master': 'ginger-master',
         'app-018': 'app-018',
         'jspider': 'jspider',
         'hedc': 'hedc',
         'ftp': 'ftp',
         'weblech': 'weblech',
         'avrora': 'avrora',
         'luindex': 'luindex',
         'sunflow': 'sunflow',
         'testpgm': 'testpgm',
         'xalan': 'xalan'}

def draw2(program, totalAlarm, numTrue):
    print(plt.rcParams['axes.titlepad'])
    plt.rcParams['axes.titlepad'] = 15
    plt.rc('xtick', labelsize=ticksize)
    plt.rc('ytick', labelsize=ticksize)
    print(plt.rcParams['xtick.major.pad'])
    plt.rcParams['xtick.major.pad']= 10
    filename = program + "/stats.txt"

    try:
        bingo_trues = read_stats(program+"/stats.txt", totalAlarm)
        mln_trues1 = read_stats(program+"/stats-1.txt", totalAlarm)
        mln_trues2 = read_stats(program+"/stats-2.txt", totalAlarm)
        mln_trues3 = read_stats(program+"/stats-3.txt", totalAlarm)
        mln_trues4 = read_stats(program+"/stats-4.txt", totalAlarm)
        mln_trues5 = read_stats(program+"/stats-5.txt", totalAlarm)
        mln_trues = mln_trues1 + mln_trues2 + mln_trues3 + mln_trues4 + mln_trues5 
    except:
        mln_trues = [int(totalAlarm)]
#    fig = plt.figure()
    fig, ax1 = plt.subplots()
    rate = int(totalAlarm) / numTrue
    rate0 = rate / 2
    random_trues = []
    index = 1
    while rate0 <= int(totalAlarm):
        random_trues.append(rate0)
        rate0 += rate
#    random_trues = [ float(x) / float(totalAlarm) * 100 for x in random_trues ]
#    plt.boxplot([bingo_trues, mln_trues, random_trues], labels=labels, whis='range')
    plt.title(names[program] + ' (total = ' + totalAlarm + ')', size=titlesize)
#    plt.ylim(0,100)
    bingo_trues = sorted(bingo_trues)
    mln_trues = sorted(mln_trues)
    ax1.boxplot([bingo_trues, mln_trues], labels=labels, whis='range', showcaps=False)
    ax1.scatter([1,2], [bingo_trues[0], mln_trues[0]], marker= 'o', c='black', s=90)
    ax1.scatter([1,2], [bingo_trues[-1], mln_trues[-1]], marker= 'x', c='black', s=90)
    ax1.set_ylabel("# Alarms", size=labelsize)
    ax1.set_ylim(0,mln_trues[-1])

def boxplot(program, totalAlarm, numTrue):
#    fig, axes = plt.subplots(nrows=2, ncols=8, figsize=(50,50))
    draw(program, totalAlarm)
#    plt.boxplot(trues, whis='range') 
#    plt.savefig(program+'/'+program+'_box.pdf', bbox_inches='tight')
#    plt.close()
#    draw2(program, totalAlarm, numTrue)
    plt.savefig(program+'.pdf', bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print(program)
    try:
        (numTrue, numFalse, xindices, yindices) = read_stats0(dirPath+"/"+program+"/stats.txt")
        print('Total alarms: {0}'.format(numTrue + numFalse))
        print('True alarms: {0}'.format(numTrue))
        print('False alarms: {0}'.format(numFalse))
#        auc(numTrue, numFalse, xindices, yindices)
    except:
        pass
#    auc_absolute(numTrue, numFalse, xindices, yindices)
#    iteration(numTrue, numFalse, xindices, yindices, smooth=False)
#    iteration2(numTrue, numFalse, xindices, yindices, smooth=False)
    boxplot(program, totalAlarm, numTrue)
