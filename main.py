import os
import datetime
from os import walk
import shutil
import errno
import pump_plot
import numpy as np
from PyPDF2 import PdfFileMerger

#data_folder = 'C:\Users\gtetil\Downloads\Data'
data_folder = '/home/pi/Data'
sync_folder = os.path.join(data_folder, 'Sync')

def concat_files(data_file, sync_file):
    with open(data_file, 'a') as outfile:
        with open(sync_file) as infile:
            outfile.write(infile.read())

def remove_header(path):
    file_path = path
    with open(file_path) as f:
        lines = f.readlines()
    with open(file_path, 'w') as f:
        f.writelines(lines[2:])

def get_rel_file_paths():
    paths = []
    for path, subdirs, files in os.walk(sync_folder):
        for name in files:
            full_path = os.path.join(path, name)
            rel_path = os.path.relpath(full_path, sync_folder)
            paths.append(rel_path)
    return paths

def sync_file(file_rel_path):
    data_file_path = os.path.join(data_folder, file_rel_path)
    sync_file_path = os.path.join(sync_folder, file_rel_path)
    if os.path.isfile(data_file_path):
        #A file already exists for this data, so remove header and concat it with the existing file
        remove_header(sync_file_path)
        concat_files(data_file_path, sync_file_path)
    else:
        #This is the first data file, so just copy it to Data dirctory
        shutil.copyfile(sync_file_path, data_file_path)
    #Create relative time column, then create PDF plots
    if data_file_path.split("_")[1] == 'RPM.csv':
        create_rel_time(data_file_path)
        pump_plot.plot_layout(data_file_path, [7, 8, 10, 12, 13, 15])
    #File has either been concat with existing file, or copied. Now delete.
    os.remove(sync_file_path)

def copy_sync_folders():
    for (dirpath, dirnames, filenames) in os.walk(sync_folder):
        rel_path = os.path.relpath(dirpath, sync_folder)
        folder = os.path.join(data_folder, rel_path)
        if not os.path.isdir(folder):
            os.mkdir(folder)

def create_rel_time(path):
    print path
    inc = 0.1 #this represent 0.1 S/s or 6 samples per hour
    data = np.genfromtxt(path, delimiter=',', dtype=str)
    size = data.shape[0] - 2 #subtract 2 because of header/units
    time = np.linspace(0, (size-1)*inc, num=size)
    data[2:,0] = time
    np.savetxt(path, data, delimiter=',', fmt='%s')

def pdf_cat(input_folder, serial_number):
    merger = PdfFileMerger()
    for (dirpath, dirnames, filenames) in os.walk(input_folder):
        sorted_filenames = sorted(filenames)
        for pdf in sorted_filenames:
            try:
                if pdf.split("_")[1] == 'RPM.pdf':
                    merger.append(open(os.path.join(input_folder, pdf), 'rb'))
                    os.remove(os.path.join(input_folder, pdf))
            except:
                pass
    with open(os.path.join(input_folder, serial_number + '.pdf'), 'wb') as fout:
        merger.write(fout)


print 'starting'
print datetime.datetime.now()
copy_sync_folders()
rel_paths = get_rel_file_paths()
for path in rel_paths:
    sync_file(path)

# Create PDF summmary files
ca_folders = os.listdir(data_folder)
for ca_folder in ca_folders:
    if ca_folder != 'Sync':
        ca_path = os.path.join(data_folder, ca_folder)
        sn_folders = os.listdir(ca_path)
        for sn_folder in sn_folders:
            serial_number = sn_folder
            sn_path = os.path.join(ca_path, sn_folder)
            pdf_cat(sn_path, serial_number)

#create_rel_time(r'C:\Users\gtetil\Downloads\5950_RPM.csv')


