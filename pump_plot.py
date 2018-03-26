import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
import datetime as dt
import time
import os
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mtick
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.axes_grid.anchored_artists import AnchoredText
import datetime


def plot_layout(file_path, indicies):
    plt.close('all')
    fig = plt.figure(num=1, figsize=(17,11))
    filepath, filename = os.path.split(file_path)
    filename, extension = os.path.splitext(filename)
    title_list = os.path.split(file_path)[0]
    title_list, serial_number = os.path.split(title_list)
    title_list, ca_number = os.path.split(title_list)
    title = ca_number + ' / SN: ' + serial_number + ' / ' + filename
    fig.suptitle(title, fontsize=14, fontweight='bold')
    fig.text(0.983,0.965, datetime.datetime.now().strftime("%m/%d/%y"), horizontalalignment='right')
    gs1 = gridspec.GridSpec(len(indicies) / 2, 2)
    
    data = np.genfromtxt(file_path, delimiter=',', dtype=str)
    header = data[0,:]
    units = data[1,:]
    data = data[2:,:]
    data = data.astype(np.float)
    time = data[:,0]
    plot_pos = 0
    for i in indicies:
        pump_plot = fig.add_subplot(gs1[plot_pos])
        plot(pump_plot, i, data, header, time, units, plot_pos)
        plot_pos += 1
    gs1.tight_layout(fig, rect=[None,0.01,None,0.97], pad=2)
    #plt.savefig("test.png")
    make_pdf(file_path)
    #plt.show()

def plot(pump_plt, index, data, header, time, units, plot_pos):
    y_name = units[index]
    y_data = data[:,index]
    pump_plt.set_title(header[index])
    x_name = ''
    if plot_pos >= 4:
        x_name = 'Time (Hours)'
    pump_plt.set_xlabel(x_name)
    pump_plt.set_ylabel(y_name)
    pump_plt.grid(True)
    pump_plt.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f'))
    pump_plt.set_ylim(y_data.min()*0.5, y_data.max()*1.5)
    pump_plt.set_xlim(time.min(), time.max())
    pump_plt.plot(time,y_data)
    at = AnchoredText('Mean:         ' + "{:.2f}".format(y_data.mean()) + ' ' + y_name
                      + '\n' + 'Max:           ' + "{:.2f}".format(y_data.max()) + ' ' + y_name
                      + '\n' + 'Min:            ' + "{:.2f}".format(y_data.min()) + ' ' + y_name
                      + '\n' + 'Test Time:  ' + "{:.2f}".format(time.max()) + ' ' + 'Hours'
                      + '\n' + 'On Time:    ' + "{:.2f}".format(data[:,3].max() / 3600) + ' ' + 'Hours',
                      prop=dict(size=8), frameon=True,
                      loc=1
                      )
    #at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    pump_plt.add_artist(at)


def make_pdf(file_path):
    pp = PdfPages(file_path.replace('.csv','.pdf'))
    pp.savefig()
    pp.close()

if __name__ == "__main__":
    
    #plot_layout('/home/pi/Data/CA1234/A1234/3250_RPM.csv', [7,8,10,12,13,15])
    plot_layout(r'C:\Users\gtetil\Downloads\Data\CA2017-2327\268781\8500_RPM.csv', [7, 8, 10, 12, 13, 15])
