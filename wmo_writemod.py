# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 17:07:05 2019

@author: Nick
"""
from __future__ import division
import pandas as pd
import numpy as np
from math import *
import csv

"""Code's purpose is to write out the interpreted information from the readme object"""

class WriteOut():
    
    def __init__(self, vendor, df_temp_sig, df_wind_sig, df_mand, station_height, directory, testgroup1, name):
        self.vendor_name = vendor
        self.df_tempsig = df_temp_sig
        self.df_windsig = df_wind_sig
        self.df_mand = df_mand
        self.station_height = station_height
        self.directory = directory
        self.group31313 = testgroup1
        self.name = name
        #self.indent = testgroup2
        
    def global_commands(self):
        self.g31313()
        #self.ID()
        self.get_hundred_height() #getting the 100mb height level to seperate

        
    def g31313(self):
        def nothere(arg):
            if arg == None: # if code group is not there there will be missing note to it
                arg = 'Def Missing' #code won't break if not there
            return arg
        # WMO code table 3849: Sr - Solar and infrared radiation correction
        sr_dict = {'0': 'No correction',
                   '1': 'CIMO solar corrected and CIMO infrared corrected',
                   '2': 'CIMO solar corrected and infrared corrected',
                   '3': 'CIMO solar corrected only',
                   '4': 'Solar and infrared corrected automatically by radiosonde system',
                   '5': 'Solar corrected automatically by radiosonde system',
                   '6': 'Solar and infrared corrected as specified by country',
                   '7': 'Solar corrected as specified by country'
                   }
        # Entirety of WMO code table 3685 not included. Selection included for brevity. 
        rara_dict = {'11': 'Sippican LMS6 w/Chip Thermistor, external boom mounted capacitance relative humidity sensor, and derived pressure from GPS height',
                     '17': 'Graw DFM-09 (Germany)',
                     '23': 'Vaisala RS41/DigiCORA MW41 (Finland)',
                     '24': 'Vaisala RS41/AUTOSONDE (Finland)',
                     '41': 'Vaisala RS41 with pressure derived from GPS height/DigiCORA MW41 (Finland)',
                     '42': 'Vaisala RS41 with pressure derived from GPS height/DigiCORA MW41 (Finland)',
                     '77': 'Modem GPSonde M10 (France)',
                     '82': 'Lockheed Martin LMS-6 w/chip thermistor; external boom mounted polymer capacitive relative humidity sensor; capacitive pressure sensor and GPS wind'
                     }
        # Entirety of WMO code table 3872 not included. Selection included for brevity
        sasa_dict = {'00': 'No windfinding',
                     '01': 'Automatic with auxiliary otical direction finding',
                     '02': 'Automatic with auxiliary radio direction finding',
                     '03': 'Automatic with auxiliary ranging',
                     '04': 'Not used',
                     '05': 'Automatic with multiple VLF-Omega signals',
                     '06': 'Automatic cross chain Loran-C',
                     '07': 'Automatic with auxiliary wind profiler',
                     '08': 'Automatic satellite navigation',
                     '19': 'Tracking technique not specified'
                     }

        """We have three elements in the imported list [31313, second element(solar), third(time)]"""
   
        # upieces of 31313 (_undefined)
        sr_u = self.group31313[1][0] #first character in second element
        rara_u = self.group31313[1][1:3] #second and third character in second element
        sasa_u = self.group31313[1][3:] #fourth character in second element
    
        self.sr = sr_dict.get(sr_u) #see function above
        self.sr = nothere(self.sr)
        self.rara = rara_dict.get(rara_u)
        self.rara = nothere(self.rara)
        self.sasa = sasa_dict.get(sasa_u)
        self.sasa = nothere(self.sasa)
    
        self.ToL = self.group31313[2][1:] #second character to the end of the string in
                                            #in the third element

# Function that decodes identification data (WMO Section 1)
# Works for TEMP A,B,C,D PILOT B,D
# Accepts a list of 3 blocks. Ex ['TTAA', '73141', '72413']
# Tyler Trice - 20180109
#TOD0 looking to move this funciton to another module and have an output on an independent data file
    def ID(self):
        a4_dict = {'0': 'Pressure instrument associated with wind-measuring equipment',
                   '1': 'Optical theodolite',
                   '2': 'Radiotheodolite',
                   '3': 'Radar',
                   '4': 'Pressure instrument associated with wind-measuring equipment but pressure element failed during ascent',
                   '5': 'VLF-Omega',
                   '6': 'Loran-C',
                   '7': 'Wind profiler',
                   '8': 'Satellite navigation',
                   '9': 'Reserved'
                   }
    
        # 1st block
        messageID = self.ident[0]
        
        # Decodes 2nd block
        day = self.ident[1][0:2]
        if int(day) > 50:
            day = (int(day) - 50)
            windunit = 'knots'
        else:
            windunit = 'm/s'
        hour = self.ident[1][2:4]
        if messageID == 'TTAA':
            last = int(self.ident[1][4]) * 100
        elif messageID == 'TTBB' or messageID == "PPBB" or messageID == "PPDD":
            a4 = a4_dict.get(self.ident[1][4])
        elif messageID == 'TTCC':
            last = int(self.ident[1][4]) * 10
    
        # 3rd block
        stationindex = self.ident[2]
        blockID = self.ident[2][0:2]
        station_num = self.ident[2][2:]
    
        print('*** User input: ', self.ident, '***\n')
        
        print('Part: ', messageID, '\n')   
    
        print('Day of month/Wind unit (YY): ', day,',', windunit)
        print('Hour (GG): ', hour,'Z')
        if messageID == 'TTAA' or messageID == 'TTCC':
            print('Last wind level (Id): ', last, 'hPa')
        elif messageID == 'TTBB' or messageID == "PPBB" or messageID == "PPDD":
            print('Type of measuring equipment used (a4): ', a4, self.ident[1][4])
            
        print('\nStation Index: ', stationindex)
        print('WMO Block ID (II): ', blockID)
        print('Station Number (iii): ', station_num)
    """Basis of this function is to seperate the file into TTAA TTBB etc. Goal is 
    to get the index of the 100 pressure level and the 100 height level. The TEMP
    code files use pressure and the PP file uses height. Once that is seperated"""
    def get_hundred_height(self):
        for index, row in self.df_mand.iterrows():
            if self.df_mand.Pressure[index] == 100:
                hundred_height = self.df_mand.Height[index] #needed for the wind level
            if self.df_mand.Pressure[index] < 100:
                hundred_mand_index = index #get the index of the element with the first pressure
                                            #above 100 mb
                break
        for index, row in self.df_tempsig.iterrows():
            if self.df_tempsig.Pressure[index] < 100:
                hundred_sig_index = index
                break
        print (self.df_windsig)
        for index, row in self.df_windsig.iterrows():
            if self.df_windsig.Height[index] > hundred_height:
                wind_hundred_sig_index = index #this height will be an estimate
                break
        self.df_mand.Height[0] = 'surface'
        self.df_windsig.Height[0] = 'surface'
        with open(self.directory+'/'+self.name+'_WMO_coded_messages.csv', 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL, lineterminator = '\n')
            wr.writerow(["31313 group", self.group31313[1], self.group31313[2]])
            wr.writerow(["Solar IR correction", self.sr])
            wr.writerow(["Radisonde/system used", self.rara])
            wr.writerow(["Tracking technique/status of system used", self.sasa])
            wr.writerow(["Timer of Launch UTC: ", self.ToL])
            wr.writerow([" "])
            wr.writerow([self.vendor_name, "surface Hgt= ",self.station_height])
            wr.writerow(["TTAA    mb", "m","C","C", "degrees","Kts"])
            #write to the index so that it includes the 100 mb level
            self.df_mand[0:hundred_mand_index].to_csv(myfile, sep = ',', index = False)        
            wr.writerow(["TTCC    mb","m","C","C", "degrees","Kts"])
            #the first level after 100mb to the end of the file
            self.df_mand[hundred_mand_index:].to_csv(myfile, sep = ',', index = False)
            wr.writerow([" "])
            wr.writerow(["TTBB    mb","C","C"])
            self.df_tempsig[:hundred_sig_index].to_csv(myfile, sep = ',', index = False)
            wr.writerow(["TTDD    mb","C","C"])
            self.df_tempsig[hundred_sig_index:].to_csv(myfile, sep = ',', index = False)            
            wr.writerow([" "])
            wr.writerow(["PPBB    m", "degrees","Kts"])
            #write to the last height at or below 100mb
            self.df_windsig[:wind_hundred_sig_index].to_csv(myfile, sep = ',', index = False)
            wr.writerow(["PPDD    m", "degrees","Kts"])
            #write from that first index above 100 mb
            self.df_windsig[wind_hundred_sig_index:].to_csv(myfile, sep = ',', index = False)  