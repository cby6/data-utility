import pandas as pd
import os
import sys
import json
from numpy import mean, median
from dateparse import dateparse

def plot_skus(data, plot_name, save=True):
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    q = data['q']
    p = data['ppr']
    flag = data['promo_flag']
    np = data['npr']

    fig, ax = plt.subplots(figsize=(15,8))
    q.plot(ax=ax, grid=True, color='black')
    p.plot(ax=ax, secondary_y=True, grid=True, color='red')
    np.plot(ax=ax, secondary_y=True, grid=True, color='gray')
    flag.plot(ax=ax, secondary_y=True, grid=True, color='blue')
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.set_ylabel(q.name)
    ax.right_ax.set_ylabel(p.name)
    fig.autofmt_xdate()
    ax.legend()
    fig.tight_layout()
    fig.savefig(plot_name)
    plt.close(fig)
    plt.cla()
    return None

def plot_elasticity(q, p, elast, plot_name):
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    from numpy import linspace
    fig, ax = plt.subplots(figsize=(10,8))
    X = linspace(p.min(), p.max(), 100)
    ax.plot(p, q, 'bo', label='data')
    ax.plot(X, elast(X), 'g-', label='fit')
    ax.legend()
    fig.tight_layout()
    fig.savefig(plot_name)
    plt.close(fig)
    plt.cla()
    return None

if __name__ == "__main__":
    conf_file = sys.argv[1]
    with open(conf_file, 'r') as f:
        config = json.load(f)
    path = config['path']
    gt_week = config['forecast week']
    wk_map_file = path + 'data/skustore/' + config['week map file']
    hdf_participation_file = path + 'data/skustore/' + config['store participation file hdf'] 
    training_file = path + 'data/skustore/' + config['training file name']
    model_path = config['model path'] + 'NN_best_weights.h5'
    results = path + config['results path'] + config['training file name'].replace('gt_cleaned', config['results name']).replace('.h5', '.csv')

    if os.path.isfile(training_file):
        data = pd.read_hdf(training_file)

    plot_dir = path + 'plots/ALLSKU/'
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    print "Aggregating..."
    G = data.groupby(['date', 'sku'], as_index=False).agg({'q':sum, 'ppr':median, 'npr':median, 'promo_flag':mean, 'dept':median})
    G.index = G.date

    print "Plotting..."
    for sk in G.sku.unique():
        plot_name = plot_dir + '{0}/'.format(G[G.sku==sk].dept.unique()[0])
        if not os.path.exists(plot_name):
            os.makedirs(plot_name)
        plot_skus(G[G.sku==sk], plot_name + '{0}.pdf'.format(sk))


