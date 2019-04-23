from tkinter import *
from tkinter import ttk
import os
import zipfile
from time import gmtime, strftime, sleep
from shutil import move
import datetime

f = open("Config.txt", "r+")
siteid = f.read(4)


def NCEI_Archive2(data):
    m = str(month.get())

    b = strftime(siteid + m + "%y", gmtime())

    os.chdir("C:\Win9000 Messages\Archive")


    if not os.path.isfile("C:\Win9000 Messages\Archive/"+b+".zip"):
        mz = zipfile.ZipFile(b+".zip", "w")
        os.chdir("C:\Win9000 Messages")
        mz.write(data)

        mz.close()
        print("Creating Zip archive file.")
    else:
        mz = zipfile.ZipFile(b+".zip", "a")
        os.chdir("C:\Win9000 Messages")
        mz.write(data)

        mz.close()
        print("Appending archive data to the monthly zip file.")
    os.chdir("C:\Win9000 Messages")

def NCEI_Archive2_pre(data,i):
    m = str(month.get())

    b = strftime(siteid + m + "%y", gmtime())

    os.chdir("C:\Win9000 Messages\Archive")


    if not os.path.isfile("C:\Win9000 Messages\Archive/"+b+".zip"):
        mz = zipfile.ZipFile(b+".zip", "w")
        os.chdir("C:\Win9000 Messages/Ascensions/"+i)
        mz.write(data)

        mz.close()
        print("Creating Zip archive file.")
    else:
        mz = zipfile.ZipFile(b+".zip", "a")
        os.chdir("C:\Win9000 Messages/Ascensions/"+i)
        mz.write(data)

        mz.close()
        print("Appending archive data to the monthly zip file.")
    os.chdir("C:\Win9000 Messages/Ascensions/"+i)
def organizeFlights(start, end):
    os.chdir("C:/Users\Public\Documents/Win9000/flights")

    d = datetime.date.today()
    m = str(month.get()).zfill(2)
    y = str(year.get())
    destinationdir = "C:/Users/Public/Documents/Win9000/flights/" + m + "_" + y
    if not os.path.exists(destinationdir):
        print("Creating folder here:" + destinationdir)
        os.makedirs(destinationdir)

    for i in range(start, end):
        i = str(i).zfill(3)
        for j in os.listdir(os.getcwd()):
            if i in j:
                move(j, destinationdir)

    os.chdir("C:\Win9000 Messages")

def runtool():
    start = int(flnum_start.get())
    end = int(flnum_end.get())


    os.chdir("C:\Win9000 Messages")

    for i in range(start,end):
        i = str(i).zfill(3)
        print(i)
        if not os.path.exists("C:\Win9000 Messages\Ascensions/" + i):
            os.makedirs("C:\Win9000 Messages\Ascensions/" + i)
            path = ("C:\Win9000 Messages/Ascensions/"+i)

        for j in os.listdir(os.getcwd()):
            if ('T'+i) in j:
                NCEI_Archive2(j)
        for j in os.listdir(os.getcwd()):
            if ('H'+i) in j:
                NCEI_Archive2(j)
        for j in os.listdir(os.getcwd()):
            if ('C'+i in j) and ('bufr' not in j):
                NCEI_Archive2(j)
        for j in os.listdir(os.getcwd()):
            if i in j:
                move(j,"C:\Win9000 Messages/Ascensions/"+i+"/"+j)

    organizeFlights(start,end)


def runtoolpre():
    start = int(flnum_start.get())
    end = int(flnum_end.get())


    os.chdir("C:\Win9000 Messages\Ascensions")

    for i in range(start,end):
        i = str(i).zfill(3)
        print(i)
        os.chdir('C:\Win9000 Messages\Ascensions/'+i)

        for j in os.listdir(os.getcwd()):
            if ('T'+i) in j:
                NCEI_Archive2_pre(j,i)
        for j in os.listdir(os.getcwd()):
            if ('H'+i) in j:
                NCEI_Archive2_pre(j,i)
    organizeFlights(start, end)

root = Tk()
root.title("TROS Archive Tool")
mainframe = ttk.Frame(root,padding="9 9 36 36",height=640,width=800)

mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

flnum_start = StringVar()
flnum_end = StringVar()
month = StringVar()
year = StringVar()

flnum_start_entry = ttk.Entry(mainframe, width=4, textvariable=flnum_start)
flnum_start_entry.grid(column=2,row=1)

flnum_end_entry = ttk.Entry(mainframe, width=4, textvariable=flnum_end)
flnum_end_entry.grid(column=2,row=2)

month_entry = ttk.Entry(mainframe, width=4, textvariable=month)
month_entry.grid(column=2,row=3)

year_entry = ttk.Entry(mainframe, width=4, textvariable=year)
year_entry.grid(column=2,row=4)

ttk.Label(mainframe, text="Beginning (Inclusive) flight number:").grid(column=1,row=1,pady=7,padx=2,sticky=W)
ttk.Label(mainframe, text="Ending (Exclusive) flight number:").grid(column=1,row=2,pady=7,padx=2,sticky=W)
ttk.Label(mainframe, text="Month:").grid(column=1,row=3,pady=7,padx=2,sticky=W)
ttk.Label(mainframe, text="Year:").grid(column=1,row=4,pady=7,padx=2,sticky=W)

ttk.Button(mainframe, text="Run Tool (New)", command=runtool).grid(column=1,row=5,columnspan=2)
ttk.Button(mainframe, text="Run Tool (Old)", command=runtoolpre).grid(column=2,row=5,columnspan=2)

root.mainloop()
