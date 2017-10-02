import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import datetime

sku = 94048 
sp_limit = 1.2
margin_limit = 0.6
list = ['sales','asales','qty','aqty']

df = pd.read_csv(str(sku) + '.csv', delimiter='|', header=None, names=['date','price','cost','sales','asales','qty','aqty','margin'])
date = mdates.date2num(pd.to_datetime(df['date'], format='%Y%m%d'))
price = df['price']
cost = df['cost']
sales = df['sales']
asales = df['asales']
qty = df['qty']
aqty = df['aqty']
margin = df['margin']

for i in list:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax2 = ax.twinx()
    if i in ['sales','asales']:
        ax.plot(date, df[i], 'b-')
    if i in ['qty','aqty']:
        ax.plot(date, df[i], 'g-')
    ax2.plot(date, price, 'r-')
    plt.gca().xaxis_date()
    ax.set_xlabel('year')
    if i in ['sales']:
        ax.set_ylabel(i)
    if i in ['asales']:
        ax.set_ylabel('assoc sales')
    if i in ['qty']:
        ax.set_ylabel('quantity')
    if i in ['aqty']:
        ax.set_ylabel('assoc quantity')
    ax2.set_ylabel('price')
    ax2.set_ylim(ymin=0, ymax=sp_limit)
    ax.grid(True)
    fig.autofmt_xdate()
    fig.savefig(str(sku) + '_sp_' + i + '.png')
    plt.close(fig)

for i in list:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax2 = ax.twinx()
    if i in ['sales','asales']:
        ax.plot(date, df[i], 'b-')
    if i in ['qty','aqty']:
        ax.plot(date, df[i], 'g-')
    ax2.plot(date, margin, 'r-')
    plt.gca().xaxis_date()
    ax.set_xlabel('year')
    if i in ['sales']:
        ax.set_ylabel(i)
    if i in ['asales']:
        ax.set_ylabel('assoc sales')
    if i in ['qty']:
        ax.set_ylabel('quantity')
    if i in ['aqty']:
        ax.set_ylabel('assoc quantity')
    ax2.set_ylabel('margin')
    ax2.set_ylim(ymin=0, ymax=margin_limit)
    ax.grid(True)
    fig.autofmt_xdate()
    fig.savefig(str(sku) + '_margin_' + i + '.png')
    plt.close(fig)


#fig8 = plt.figure()
#ax = fig8.add_subplot(111)
#sales.plot(ax=ax, grid=True, color='blue')
#price.plot(ax=ax, secondary_y=True, grid=True, color='red')
#ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
#ax.set_ylabel('sales')
#ax.right_ax.set_ylabel('price')
#ax.right_ax.set_ylim(ymin=0, ymax=11)
#fig8.autofmt_xdate()
#ax.legend()
#fig8.savefig('38604_price_sales_test.png')
#plt.close(fig8)
#plt.cla()
