import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

#Create a histogram with a normal distribution fit

def plot(dataFile):
    data = pd.read_json(dataFile, typ = 'series').sort_values()
    maxDistance = data.values.max()
    totalPages = len(data)

    fit = stats.norm.pdf(data, np.mean(data), np.std(data)) #probability density function

    fig = data.hist(figsize=(11,8.5), alpha = 0.5, facecolor = 'cornflowerblue', normed = 1) #Create the histogram
    fig.set_ylabel('Frequency',  fontsize = 12)
    fig.set_xlabel("Distance (links)", fontsize = 12)
    fig.tick_params(left='off', bottom='off')
    fig.set_yticklabels(fig.yaxis.get_majorticklabels(), fontsize = 6)


    plt.title('Distance Distribution of {} Random Pages'.format(totalPages))
    plt.plot(data, fit, '-o') #Add the best-fit line
    plt.plot() #Plot the histogram
    plt.tight_layout()
    plt.savefig('./results/Distance Distribution.png', dpi=150)
    plt.show()




