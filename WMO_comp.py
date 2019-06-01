# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 11:57:44 2019
Algorithm:
    User is prompted to type the vendor. With that name, datareturn() will determine the vendor type and
    the specific files to look for that files that the software outputs. Once files are imported
    The TTAA TTBB TTCC TTDD PPBB PPDD code blocks are seperated into one long string with level data.
    This data wont include any special groups.
    This should be the end of any differences between vendors.
    
    The next step is to make this long string into a 5
    character block with each block as an element in a list. After that, values were seperated
    into columns. This is done to organize the data before final interpretation. Pressure and Height
    for the significant levels is converted to a numeric value.
    
    The next step is to interpret the data into numeric form and seperate into the code blocks
    to output to a csv file.
    
    The high res file is then compared to the WMO file. The pressure/height is used to get the closest value
    in the high res file. That line of data in the high res file is taken and subracted by
    the WMO code. These differences are included in the originial dataframes and printed out to 
    a csv file.
@author: Nick
"""
from __future__ import division
from tkinter import filedialog
import pandas as pd
import numpy as np
from math import *
import csv
    

class ReadIn:
    """Initialized funtion that takes in the variable when the object is first created
    self. is used to make a global variable in respect with this class"""
    def __init__(self, vendor, station_id, station_height, last_press, sig_sep):
        self.vendor_name = vendor
        self.station_id = station_id
        self.station_height = station_height
        self.last_press = last_press
        self.sig_sep = sig_sep
        self.rad = 0.0174533
    def global_commands(self):
        self.datareturn() 
        
        self.list_data()#moves data from one big string to 5 character blocks
        
        self.get_data_sig()#moves data from 5 character blocks to actual datapoints
        self.get_data_mand()
        
        self.interpret_mand()#interprets the three dataframes created
        self.interpret_windsig()
        self.interpret_tempsig()
    #def lockheed_commands(self):
        
    """used to distinguish what vendor is being analyzed. Each vendor has a different way to 
    output their WMO code. This is case sensitive. Vendor name must be written in a specific way
    or code will break. TODO make is a case blind as possible or ask again if nothing matches up."""   
    def datareturn(self):
        #indicator read in from the main file. This will decide what following functions
        #will be used for the data file
        if self.vendor_name == 'GRAW' or self.vendor_name == 'Graw':
            self.from_graw()
            self.separate_file_graw()
        if self.vendor_name == 'Vaisala':
            self.from_vaisala()
            self.separate_file_vaisala()
        if self.vendor_name == 'Lockheed':
            self.from_lockheed()
            self.separate_file_lockheed()
            #self.lockheed_commands() #commands specific to lockheed martin files
        if self.vendor_name == 'Modem':
            self.from_modem()
            self.separate_file_modem()
            
    def fix_file(self):
        """this is used in the single flight data processing package. This is not used in the WMO code
        consider removing."""
        self.df.set_index('Elapsed_Time', inplace = True) 
        self.df = self.df[~self.df.index.duplicated(keep = 'first')]
    """Lockheed part of the program(MAYBE) Would like separate_file to be global for all vendors"""            
    def from_lockheed(self):
        """Asks for the files needed. The three WMO code files and the high resolution file"""
        print ("\nEnter in the data files in the following order:\n"
               "Mandatory\nSignificant\nABV\nprofile data\n")
        self.Mandfile = filedialog.askopenfilename()
        self.Sigfile = filedialog.askopenfilename()
        self.ABVfile = filedialog.askopenfilename()
        self.Profile = filedialog.askopenfilename()
        """Creating datafrom from the profile/highresolution file. In Lockheeds case it is an .RTSO file
        Many of the columns are dropped to have less data in the dataframe. Speeds up dataprocessing
        Wind speed must be in knots"""
        self.df = pd.read_csv(self.Profile, delimiter='\s+', skiprows = 9, names =['Elapsed_Time','P','TEMP','RH','HeightMSL', 'DEWP',
                                'B','C','D','E','F','G','H','I','J','K','L','M','N','O','SPEED','DIR','Pf','Q','R','Lon','Lat','GpsHeight'])
        self.df = self.df.drop(['Elapsed_Time','Lat','Lon','B','C','D','E','F','G','H','I','J','K','L','M','N','O','Pf','Q','R', 'GpsHeight'], axis=1)
        #self.df['Elapsed_Time'] = self.df['Elapsed_Time'].astype(np.int64)
        self.df = self.df.replace("///./",np.NaN)
        self.df['P'] = pd.to_numeric(self.df['P'], errors='coerce')
        self.df['TEMP'] = pd.to_numeric(self.df['TEMP'], errors='coerce')
        self.df['RH'] = pd.to_numeric(self.df['RH'], errors='coerce')
        rh_series = self.df.RH[0].astype('float')
        temp_series = self.df.TEMP[0].astype('float')
        self.df.DEWP[0] = round(243.04*((np.log(rh_series/100.0)+((17.625*temp_series)/(243.04+temp_series)))/(17.625-np.log(rh_series/100.0)-((17.625*temp_series)/(243.04+temp_series)))),1) 
        #self.df.DEWP = round(self.df.DEWP, 1)
        self.df['DEWP'] = pd.to_numeric(self.df['DEWP'], errors='coerce')
        self.df['SPEED'] = pd.to_numeric(self.df['SPEED'], errors='coerce')
        self.df['SPEED'] = round(self.df['SPEED'] * 1.9438, 0)
        #round the SPEED elements to the nearest 5
                
        self.df['DIR'] = pd.to_numeric(self.df['DIR'], errors='coerce')
        self.df['HeightMSL'] = pd.to_numeric(self.df['HeightMSL'], errors='coerce')
    def from_vaisala(self):
        """same logic as above except in the vaisala context"""
        print ("\nEnter in the data files in the following order:\n"
       "tempa\ntempb\ntempc\ntempd\npilotb\npilotd\nprofile data\n")
        self.tempa = filedialog.askopenfilename()
        self.tempb = filedialog.askopenfilename()
        self.tempc = filedialog.askopenfilename()
        self.tempd = filedialog.askopenfilename()
        self.pilotb = filedialog.askopenfilename()
        self.pilotd = filedialog.askopenfilename()
        self.Profile = filedialog.askopenfilename()
        self.df = pd.read_csv(self.Profile, delimiter='\s+', skiprows = 2, names =['n','Elapsed_Time','UTC','HeightMSL', 'GpsHeightMSL',
                             'P', 'TEMP', 'RH', 'DEWP', 'DIR', 'SPEED', 'Ecomp', 'Ncomp', 'Lat', 'Lon'])
        #self.df = self.df.drop(['Pc','Pm'], axis=1)
        #IMPORTANT: fix file is called to set Elapsed time as the index for this dataframe
        self.df['SPEED'] = round(self.df['SPEED'] * 1.9438, 0)
        self.df= self.df.drop(['UTC','Lat','Lon','GpsHeightMSL','Elapsed_Time', 'Ecomp', 'Ncomp', 'n'], axis = 1)
        #self.df = self.fix_file()
    def from_graw(self):
        """NOTE: GRAW PROFILE DATA FILE IS DIFFERENT FROM HIGH RESOLUTION. AS PER GRAW, THE 
        WMO CODE IS FROM THE PROFILE DATA FILE AND NOT THE HIGH RESOLUTION FILE. SINGLE FLIGHT
        DATA ANALYSIS USES HIGH RESOLUTION DATA FILE"""
        
        print ("\nEnter in the data files in the following order:\n"
       "WMO_100\nWMO_end\nprofile data(not high res)\n")
        self.lower = filedialog.askopenfilename()
        self.upper = filedialog.askopenfilename()
        self.Profile = filedialog.askopenfilename()
        self.df = pd.read_csv(self.Profile, delimiter='\s+', skiprows = 3, names =['Elapsed_Time', 'P', 'TEMP', 'RH', 'SPEED', 'DIR', 
                                                'Lon', 'Lat','GpsHeight','HeightMSL', 'DEWP', 'Rs', 'Ele', 'Az', 'Range'])
        self.df = self.df.drop(['Rs','Lat','Lon','GpsHeight','Elapsed_Time', 'Ele', 'Az', 'Range'], axis = 1)
        self.df = self.df.replace(999999,np.NaN)
        self.df = self.df.replace(999999.0,np.NaN)
        self.df['P'] = pd.to_numeric(self.df['P'], errors='coerce')
        self.df['SPEED'] = pd.to_numeric(self.df['SPEED'], errors='coerce')
        #self.df['Speed'] = self.df.Speed/1.94 #note this is only for GRAW testing in knots
        self.df['TEMP'] = pd.to_numeric(self.df['TEMP'], errors='coerce')
        self.df['RH'] = pd.to_numeric(self.df['RH'], errors='coerce')
        self.df['DIR'] = pd.to_numeric(self.df['DIR'], errors='coerce')

    def from_modem(self): #Alt height is used as GPM height due to the need for it in the rest of the program
        print ("\nEnter in the data files in the following order:\n"
       "temp\npilot\nprofile data\n")
        self.temp = filedialog.askopenfilename()
        self.pilot = filedialog.askopenfilename()
        self.Profile = filedialog.askopenfilename()
        self.df = pd.read_csv(self.Profile, delimiter = '\s+', skiprows = 1, names = ['Elapsed_Time', 'HeightMSL', 'Lat', 'Lon', 'Ecomp',
                                'Ncomp', 'Ascent', 'SPEED', 'DIR', 'DEWP', 'TEMP', 'RH', 'P', 'Flag'])
        self.df['SPEED'] = round(self.df['SPEED'] * 1.9438, 0)
        self.df= self.df.drop(['Lat','Lon','Elapsed_Time', 'Ecomp', 'Ncomp', 'Flag'], axis = 1)
        print (self.df.dtypes)
    def separate_file_lockheed(self):
        """functions below seperate the WMO coded file from the station id.
        So the elements will be the block of code inbetween the station id's. 
        Everything in the file to the first station id will be the 0th element.
        Spaces in the WMO code are removed in this part of the code. The line breaks
        are also removed. 
        Python is a base zero coding language."""
        with open(self.Mandfile, 'r') as f_one:
            TT = f_one.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        #supplementary data from 31313 group
        self.TTAAsup_id = TT.split(self.station_id)[1]
        self.TTAA = TT.split(self.station_id)[2]
        with open(self.Sigfile, 'r') as f_two:
            TT = f_two.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        self.TTBB = TT.split(self.station_id)[2]
        self.PPBB = TT.split(self.station_id)[3]
        with open(self.ABVfile, 'r') as f_three:
            TT = f_three.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        self.TTCC = TT.split(self.station_id)[2]
        self.TTDD = TT.split(self.station_id)[3]
        self.PPDD = TT.split(self.station_id)[4]
    def separate_file_vaisala(self):
        with open(self.tempa, 'r') as f_one:
            TT = f_one.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        self.TTAAsup_id = TT.split(self.station_id)[0]
        self.TTAA = TT.split(self.station_id)[1]
        with open(self.tempb, 'r') as f_two:
            TT = f_two.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        self.TTBB = TT.split(self.station_id)[1]

        with open(self.tempc, 'r') as f_three:
            TT = f_three.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        self.TTCC = TT.split(self.station_id)[1]
        with open(self.tempd, 'r') as f_four:
            TT = f_four.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        self.TTDD = TT.split(self.station_id)[1]
        with open(self.pilotb, 'r') as f_five:
            TT = f_five.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        self.PPBB = TT.split(self.station_id)[1]
        with open(self.pilotd, 'r') as f_six:
            TT = f_six.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        self.PPDD = TT.split(self.station_id)[1]
    def separate_file_modem(self):
        with open(self.temp, 'r') as f_one:
            TT = f_one.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        self.TTAAsup_id = TT.split(self.station_id)[0]
        self.TTAA = TT.split(self.station_id)[1]
        self.TTBB = TT.split(self.station_id)[2]
        self.TTCC = TT.split(self.station_id)[3]
        self.TTDD = TT.split(self.station_id)[4]
        with open(self.pilot, 'r') as f_two:
            TT = f_two.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        self.PPBB = TT.split(self.station_id)[2]
        self.PPDD = TT.split(self.station_id)[4]     
        
    def separate_file_graw(self):
        with open(self.lower, 'r') as f_one:
            TT = f_one.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        self.TTAAsup_id = TT.split(self.station_id)[1]
        self.TTAA = TT.split(self.station_id)[2]
        self.TTBB = TT.split(self.station_id)[4]
        self.PPBB = TT.split(self.station_id)[6]
        with open(self.upper, 'r') as f_two:
            TT = f_two.readlines()
            TT = ''.join(map(str, TT))
            TT = TT.replace(" ", "")
            TT = TT.replace('\n', '')
        self.TTCC = TT.split(self.station_id)[2]
        self.TTDD = TT.split(self.station_id)[4]
        self.PPDD = TT.split(self.station_id)[6]       
    def list_data(self):
        """This function may have a better approach. Currently it is designed to only get the 
        meteorological data. No supplementary information. Then a new list is made to seperate
        the meteorological data into 5 character blocks. The blocks could be seperated using the 
        ' ' seperator and then into a list in the above function. This would only be useful to get the TTAA block of 
        code since that is 4 characters. Current logic still works"""
        i = 0
        TTAA_ = "" #this will be a block that increased from 1-5. Once at 5 it will append the total
                    #and go through the process again
        TTAA_t = "" #total list of the meteorological data
        #loops through each character of the TTAA message
        for c in self.TTAA:
            #if i >34:
            if i%5 == 0:
                TTAA_t += TTAA_
                TTAA_ = ""
            TTAA_ += c
            """Once code gets to 88 then that ends the meteorological data for the TTAA group"""
            if i >70 and TTAA_ =='88':
                break
            i = i + 1
            #make sure the coded messages stop at the 88 after the mandatory codes
        #print (TTAAsup_id)                      
        i = 0
        TTBB_ = ""
        TTBB_t = ""
        for c in self.TTBB:
            #if i >34:
            if i%5 == 0:
                TTBB_t += TTBB_
                TTBB_ = ""
            TTBB_ += c
            if i >20 and TTBB_ == self.sig_sep:#sometimes will be 31313
                #21212 indicates the significant levels are done reporting
                break
            i = i + 1
        i = 0
        TTCC_ = ""
        TTCC_t = ""
        for c in self.TTCC:
            #if i >34:
            if i%5 == 0:
                TTCC_t += TTCC_
                TTCC_ = ""
            TTCC_ += c
            if i >20 and TTCC_ =='88':
                # same as the mandatory levels except over 100 mb
                break
            i = i + 1 
        i = 0
        TTDD_ = ""
        TTDD_t = ""
        for c in self.TTDD:
            if i%5 == 0:
                TTDD_t += TTDD_
                TTDD_ = ""
            TTDD_ += c
            if i >30 and TTDD_ == self.sig_sep:
                break
            i = i + 1
        i = 0
        PPBB_ = ""
        PPBB_t = ""
        for c in self.PPBB:
            #if i >34:
            if i%5 == 0:
                PPBB_t += PPBB_
                PPBB_ = ""
            PPBB_ += c
            if i >20 and PPBB_ =='=':#sometimes will be 31313
                #21212 indicates the significant levels are done reporting
                break
            i = i + 1
        i = 0
        PPDD_ = ""
        PPDD_t = ""
        for c in self.PPDD:
            if i%5 == 0:
                PPDD_t += PPDD_
                PPDD_ = ""
            PPDD_ += c
            if i >5 and PPDD_ =='=':
                break
            i = i + 1
        """this part of the code will seperate the long string of characters into a list
        with each element having 5 characters as seen in the WMO code. It will list the data"""
        self.new_TTAA = [TTAA_t[x:x+5] for x in range(0, len(TTAA_t),5)]
        self.new_TTBB = [TTBB_t[y:y+5] for y in range(0, len(TTBB_t), 5)]
        self.new_TTCC = [TTCC_t[y:y+5] for y in range(0, len(TTCC_t), 5)]
        self.new_TTDD = [TTDD_t[z:z+5] for z in range(0, len(TTDD_t), 5)]
        #Seperates the string into 5 characters per element the way the code is shown in the file
        self.new_PPBB = [PPBB_t[y:y+5] for y in range(0, len(PPBB_t), 5)]
        self.new_PPDD = [PPDD_t[z:z+5] for z in range(0, len(PPDD_t), 5)]
        #self.new_TTAAsup_t = [TTAAsup_t[w:w+5] for w in range(0,len(TTAAsup_t), 5)]
        self.new_TTAAsup_id = []
        for w in range(0, len(self.TTAAsup_id)):
            if w == 4:
                self.new_TTAAsup_id.append(self.TTAAsup_id[0:w])
                self.new_TTAAsup_id.append(self.TTAAsup_id[w:])
    def get_data_sig(self):
        wind_direction_pp = []
        height_pp = []
        temp_dewpoint_sig = []
        pressure_sig = []
        """function will place the elements of the code into lists of a common data. Example,
        every third element will have temperature and dewpoint information in the 5 character block
        All of these character blocks will be in the same list to be distinguished at a later time"""

        for i in range(len(self.new_PPBB)):
            """If the wind significant level shows a 9, wind data will follow. If there are 
            slashes then wind data isn't present. This is not the case for the surface. A slash
            after the 90/12 is really surface 300 600 levels. First element is hardcoded because
            of this case in the first 90000 block of characters. Any other case will only have
            2 significant level. eg a 92/56 will have levels at 25*300meters and 26*300meters. 
            Only there will be the same list for both the PPBB and PPDD code."""
            if self.new_PPBB[i][0]=='9': #first character in the ith element
                if i == 0:
                    count = 0
                    """Since the number in the 90000 code is multiplied by 300, I have seperated
                    the logic into thousands and hundreds. The value following the 9 is the thousands.
                    When a 3, we have heights at least at 9000, ready to be added by whatever the
                    hundreds give. Of course these characters are not integers and need to be converted
                    to such."""
                    ppbb_heights_thousands = int(self.new_PPBB[i][1])*3000
                    """element 2-4 (third element to the fifth element) will have the hundreds
                    integers. However many there are will be counted for the loop below."""
                    ppbb_heights_hundreds = self.new_PPBB[i][2:5]
                    """the line below is only for the case of the surface"""
                    ppbb_heights_hundreds = [item.replace("/", '0') for item in ppbb_heights_hundreds]
                    for j in range(len(ppbb_heights_hundreds)):
                        if ppbb_heights_hundreds[j]=='':
                            continue
                        else:
                            #MUST COUNT HOW MANY VALUES THERE ARE IN CHARACTER 3,4,5
                            #IF IT IS THREEE THIS LOOP HAPPENS THREEE TIME BEFORE THE NEXT HEIGHT INDICATING CODE
                            count = count + 1
                            """The height here is calculated, it won't be in string for obviously"""
                            height_pp.append(ppbb_heights_thousands + (int(ppbb_heights_hundreds[j])*300))
                    z = 1 #z=1 is used to the a base 1 rather than 0.
                    if i == 0:
                        count = 3
                    for k in range(count):
                        """The data to the corresponding heights. This data will be in a string
                        and will still need to be interpreted to a wind speed and wind direction
                        data columns"""
                        wind_direction_pp.append(self.new_PPBB[i+z])
                        """k may also be used with a plus one. Python is base 0 and we need to
                        add 1 for the first element. The first element is k = 0"""
                        z = z + 1 #adds with the loop like any other counter
                else: 
                    """if PPBB after the first 90000 block of code. Logic still the same except
                    the slash is replaced with nothing ie removed."""
                    count = 0 
                    ppbb_heights_thousands = int(self.new_PPBB[i][1])*3000
                    ppbb_heights_hundreds = self.new_PPBB[i][2:5]
                    ppbb_heights_hundreds = [item.replace("/", "") for item in ppbb_heights_hundreds]
                    for j in range(len(ppbb_heights_hundreds)):
                        if ppbb_heights_hundreds[j]=='':
                            continue
                        else:
                            #MUST COUNT HOW MANY VALUES THERE ARE IN CHARACTER 3,4,5
                            #IF IT IS THREEE THIS LOOP HAPPENS THREEE TIME BEFORE THE NEXT HEIGHT INDICATING CODE
                            count = count + 1
                            height_pp.append(ppbb_heights_thousands + (int(ppbb_heights_hundreds[j])*300))
                    z = 1
                    if i == 0:
                        count = 3
                    for k in range(count):
                        wind_direction_pp.append(self.new_PPBB[i+z])
                        z = z + 1
        height_pp[0]=self.station_height
        index = 0
        skip = 0
        for i in range(len(self.new_PPDD)):
            if index < skip:
                #SINCE THERE WILL BE SOME HEIGHT INDICATORS LEADING WITH A '1', WE MUST SKIP LOOP ITERATIONS THAT ARE
                #WIND SPEED AND DIRECTION INFORMATION
                #KEEP INDEXING UNTIL THE NEW HEIGHT INDICATOR CODE
                index = index +1
                continue
            if self.new_PPDD[i][0]=='9' or i == 0: #I EQUALS TO 0 IS HARD CODED
                count = 0
                ppdd_heights_thousands = int(self.new_PPDD[i][1])*3000
                ppdd_heights_hundreds = self.new_PPDD[i][2:5]
                ppdd_heights_hundreds = [item.replace("/", "") for item in ppdd_heights_hundreds]
                for j in range(len(ppdd_heights_hundreds)):
                    if ppdd_heights_hundreds[j]=='':
                        continue
                    else:
                        count = count + 1
                        height_pp.append(ppdd_heights_thousands + (int(ppdd_heights_hundreds[j])*300))
                z = 1
                skip = count
                index = 0
                for k in range(count):
                    wind_direction_pp.append(self.new_PPDD[i+z])
                    z = z + 1
            if self.new_PPDD[i][0]=='1' :
                """Once the wind level is high enough, a 1 is used instead of a 9. This will only
                be present in a PPDD code. The rest of the logic is the same as above"""
                count = 0
                ppdd_heights_thousands = int(self.new_PPDD[i][1])*3000+30000
                ppdd_heights_hundreds = self.new_PPDD[i][2:5]
                ppdd_heights_hundreds = [item.replace("/", "") for item in ppdd_heights_hundreds]
                for j in range(len(ppdd_heights_hundreds)):
                    if ppdd_heights_hundreds[j]=='':
                        continue
                    else:
                        count = count + 1
                        height_pp.append(ppdd_heights_thousands + (int(ppdd_heights_hundreds[j])*300))
                z = 1
                skip = count
                index = 0
                for k in range(count):
                    wind_direction_pp.append(self.new_PPDD[i+z])
                    z = z + 1
        #DETERMINE PRESSURE FOR SIGNIFICANT LEVELS
        for i in range(len(self.new_TTBB)):
            """The even elements 0,2,4 will b with elements with pressure data. And will be
            the 3rd to the 5th character in the block. If it is less than 100, it will have 
            pressure greater than 1000 for TTBB. If anything else, it will be a straight 
            conversion from the three characters to integer, trivial."""
            if i%2 ==0:
                if (int(self.new_TTBB[i][2:5])) < 100:
                    pressure_sig.append(int(self.new_TTBB[i][2:5]) + 1000)
                else:
                    pressure_sig.append(int(self.new_TTBB[i][2:5]))
            if i%2 ==1:
                """temp_dewpoint list will be in characters and need further interpretation"""
                temp_dewpoint_sig.append(self.new_TTBB[i])
        for i in range(len(self.new_TTDD)):
            if i%2 ==0:
                #if (int(new_TTDD[i][2:5])) < 100:
                    #pressure_DD.append(int(new_TTDD[i][2:5]) + 1000)
                #else:
                pressure_sig.append(int(self.new_TTDD[i][2:5])/10)
            if i%2 ==1:
                temp_dewpoint_sig.append(self.new_TTDD[i])
        data_temp = {'Pressure':pressure_sig, 'TempDew':temp_dewpoint_sig}
        data_wind = {'Height': height_pp, 'WindDir':wind_direction_pp}
        """put into dataframes to keep data organized. Dataframes are global variables
        to be accessed at another time"""
        self.df_tempsig =  pd.DataFrame(data_temp)
        self.df_windsig =  pd.DataFrame(data_wind) 
    def get_data_mand(self):
        #initialize lists to fill with strings of 5 characters as above
        #the data is organized to where it needs to be but not in value form 
        pressure_height_mand = [] 
        temp_dewpoint_mand = []
        wind_direction_mand = []
        """function takes the seperated WMO lists and puts the lists into a dataframe that 
        can be interpreted in a later function. Don't let the pressure height paradox confuse.
        Lower pressure, heigher height."""
        for i in range(len(self.new_TTAA)):
            if i == 0:
                """first pressure will be an integer. The height is entered in later since
                this information does not come from the WMO code"""
                if int(self.new_TTAA[i])>99900: #if surface pressure is below 1000 mb, make sure it has the proper format
                    self.new_TTAA[i] = (int(self.new_TTAA[i])-99000)
                    pressure_height_mand.append(self.new_TTAA[i])
                else: #if surface pressure is below 1000mb (level above 1000mb in height)
                    self.new_TTAA[i] = (int(self.new_TTAA[i])-98000)
                    pressure_height_mand.append(self.new_TTAA[i])    
            if i%3 == 0 and i != 0: #logic seperates each 5 characters into a group to be decoded
                pressure_height_mand.append(self.new_TTAA[i])
            if i%3 ==1: #fiver character block right after pressure height
                temp_dewpoint_mand.append(self.new_TTAA[i])
            if i%3 ==2: #five character block 2 after the pressure height
                wind_direction_mand.append(self.new_TTAA[i])
        for i in range(len(self.new_TTCC)): #logic the same as above, in the same list since it is mandatory
            if i%3 == 0:
                pressure_height_mand.append(self.new_TTCC[i])
            if i%3 ==1:
                temp_dewpoint_mand.append(self.new_TTCC[i])
            if i%3 == 2:
                wind_direction_mand.append(self.new_TTCC[i])
        data_mand = {'PressHgt': pressure_height_mand, 'WindDir':wind_direction_mand,
                         'TempDew': temp_dewpoint_mand}
        """one big mandatory dataframe. Will be interpreted later"""
        self.df_mand =  pd.DataFrame(data_mand)
    def pressure_mand_list(self):
        """returns pressure list basd on the last recorded mandatory level."""
        pressure = [1000, 925, 850, 700,500,400,300,250,200,150,100, 70, 50 ,30, 20,10,7]
        pressure_mand = []
        for i in range(len(pressure)):
            if pressure[i] > self.last_press:
                pressure_mand.append(pressure[i])
            if pressure[i] == self.last_press:
                pressure_mand.append(pressure[i])
                break
        return pressure_mand

    def interpret_mand(self):
        """height logic won't change. This is the interpretation that goes on in the code."""
        pressure_mand = self.pressure_mand_list()
        height_mand = []
        #HEIGHTS FOR MANDATORY LEVELS
        for i in range(len(self.df_mand.PressHgt)):
            if i ==0:
                #first element will be the first element in the presshgt list. It is an integer
                pressure_mand.insert(0,self.df_mand.PressHgt[i])
                height_mand.append(self.station_height) #configured height
            if i ==1:
                height_mand.append(int(self.df_mand.PressHgt[i]))
            if i==2:
                height_mand.append(int(self.df_mand.PressHgt[i])-92000)
            if i==3:
                height_mand.append((int(self.df_mand.PressHgt[i])-85000)+1000)
            if i==4:
                height_mand.append((int(self.df_mand.PressHgt[i])-70000)+3000)
            if i==5:
                height_mand.append((int(self.df_mand.PressHgt[i])-50000)*10)
            if i==6:
                height_mand.append((int(self.df_mand.PressHgt[i])-40000)*10)
            if i==7:
                if int(self.df_mand.PressHgt[i]) <30400:
                    height_mand.append((int(self.df_mand.PressHgt[i])-30000)+10000)
                else:
                    height_mand.append((int(self.df_mand.PressHgt[i])-30000)*10) 
            if i==8:
                height_mand.append(((int(self.df_mand.PressHgt[i])-25000)+1000)*10)
            if i==9:
                if self.df_mand.PressHgt[i]== '20///':
                    height_mand.append(0)
                else:
                    height_mand.append(((int(self.df_mand.PressHgt[i])-20000)+1000)*10)
            if i==10:
                height_mand.append(((int(self.df_mand.PressHgt[i])-15000)+1000)*10)
            if i==11:
                height_mand.append(((int(self.df_mand.PressHgt[i])-10000)+1000)*10)
            if i ==12:
                height_mand.append(((int(self.df_mand.PressHgt[i])-70000)+1000)*10)
            if i ==13:
                
                if int(self.df_mand.PressHgt[i]) <50400:
                    height_mand.append(((int(self.df_mand.PressHgt[i])-50000)+2000)*10)
                else:
                    height_mand.append(((int(self.df_mand.PressHgt[i])-50000)+1000)*10) 
            if i ==14:
                if self.df_mand.PressHgt[i]== '30///':
                    height_mand.append(0)
                else:
                    height_mand.append(((int(self.df_mand.PressHgt[i])-30000)+2000)*10)
            if i ==15:
                if self.df_mand.PressHgt[i]== '20///':
                    height_mand.append(0)
                else:
                    height_mand.append(((int(self.df_mand.PressHgt[i])-20000)+2000)*10)
            if i ==16:
                height_mand.append(((int(self.df_mand.PressHgt[i])-10000)+3000)*10)
            if i ==17:
                height_mand.append(((int(self.df_mand.PressHgt[i])-8000)+3000)*10)
        pressure_mand = pressure_mand[0:len(height_mand)]
        #pressure_mand list must be the same length as heigh_mand to put into a dataframe
        speed_mand = []
        direction_mand = []
        """If there is a surface pressure above 1000mb (<1000mb) there will be slashes for that
        missing data. This part of the function will seperate the wind speed and direction from
        the string."""
        #THIS LOOP HANDLES THE SPEED AND DIRECTION FOR MANDATORY LEVELS TTAA AND TTBB
        for i in range(len(self.df_mand.WindDir)):
            if self.df_mand.TempDew[i]=='/////': # if the surface pressure is below 1000mb, 1000mb surface values will be /////
                speed_mand.append(np.nan)
                direction_mand.append(np.nan)
        
            else:
                direction_i = int(self.df_mand.WindDir[i][0:3])
                speed_i = float(self.df_mand.WindDir[i][3:5])
                if direction_i%5 == 0:
                    direction_mand.append(direction_i)
                    speed_mand.append(round(speed_i,2))
                if direction_i%5 !=0:
                    direction_mand.append(direction_i - direction_i%5)
                    speed_mand.append(round((speed_i + (direction_i%5*100)), 2))

        temp_mand = []
        dewpoint_mand = []
        """dewpoint_i is really the dewpoint depression. IF it's less than or equal to 50, it is
        divided by 10. If greater, the dewpoint depression will be equal to the 3:5 value minus 50"""
        for i in range(len(self.df_mand.TempDew)):
            #print (temp_dewpoint[i])
            if self.df_mand.TempDew[i]=='/////':
                temp_mand.append(np.nan)
                dewpoint_mand.append(np.nan)
            else:
                temp_i = float(self.df_mand.TempDew[i][0:3])
                dewpoint_i = float(self.df_mand.TempDew[i][3:5])
                #if i==0:
                if i < 12:
                    if temp_i%2==0:
                        temp_mand.append(temp_i/10)
                        if dewpoint_i <= 50.0:
                            dewpoint_mand.append(round((temp_mand[i] - dewpoint_i/10),2))
                        if dewpoint_i >50.0:
                            dewpoint_d = dewpoint_i - 50.0
                            dewpoint_mand.append(round((temp_mand[i] - dewpoint_d),2))
                    if temp_i%2!=0:
                        temp_mand.append(temp_i*-1/10)
                        if dewpoint_i <= 50.0:
                            dewpoint_mand.append(round((temp_mand[i] - dewpoint_i/10),2))
                        if dewpoint_i >50.0:
                            dewpoint_d = dewpoint_i - 50.0
                            dewpoint_mand.append(round((temp_mand[i] - dewpoint_d),2))
                if i >= 12:
                    if temp_i%2==0:
                        temp_mand.append(temp_i/10)
                        if dewpoint_i <= 50.0:
                            dewpoint_mand.append(round((temp_mand[i] - dewpoint_i/10),2))
                        if dewpoint_i >50.0:
                            dewpoint_d = dewpoint_i - 50.0
                            dewpoint_mand.append(round((temp_mand[i] - dewpoint_d),2))
                    if temp_i%2!=0:
                        temp_mand.append(temp_i*-1/10)
                        if dewpoint_i <= 50.0:
                            dewpoint_mand.append(round((temp_mand[i] - dewpoint_i/10),2))
                        if dewpoint_i >50.0:
                            dewpoint_d = dewpoint_i - 50.0
                            dewpoint_mand.append(round((temp_mand[i] - dewpoint_d),2))

        #make list into a series
        """All six lists are the same length. Make them into a data series so that 
        they can be put into a the self.df_mand dataframe. The series that had strings are
        then dropped and no longer needed"""
        temp_mand_series = pd.Series(temp_mand)
        dewpoint_mand_series = pd.Series(dewpoint_mand)
        speed_mand_series = pd.Series(speed_mand)
        direction_mand_series = pd.Series(direction_mand)
        pressure_mand_series = pd.Series(pressure_mand)
        height_mand_series = pd.Series(height_mand)
        self.df_mand["Pressure"] = pressure_mand_series.values
        self.df_mand["Height"] = height_mand_series.values
        self.df_mand["Temp"] = temp_mand_series.values
        self.df_mand["Dewpoint"] = dewpoint_mand_series.values
        self.df_mand["Direction"] = direction_mand_series.values
        self.df_mand["Speed"] = speed_mand_series.values
        self.df_mand = self.df_mand.drop(['PressHgt', 'WindDir', 'TempDew'], axis=1)

    def interpret_windsig(self):
        """logic for significant wind direction and speeed is the same as the mandatory.
        The height series was calculated above. This is the only series that is in integer
        for before the interpret functions are called."""
        direction_sig = []
        speed_sig = []
        for i in range(len(self.df_windsig)):
            direction_i = int(self.df_windsig.WindDir[i][0:3])
            speed_i = float(self.df_windsig.WindDir[i][3:5])
            if direction_i%5 == 0:
                direction_sig.append(direction_i)
                speed_sig.append(round(speed_i,2))
            if direction_i%5 !=0:
                direction_sig.append(direction_i - direction_i%5)
                speed_sig.append(round((speed_i + (direction_i%5 * 100)), 2))        

        speed_sig_series = pd.Series(speed_sig)
        direction_sig_series = pd.Series(direction_sig)
        self.df_windsig["Direction"] = direction_sig_series.values
        self.df_windsig["Speed"] = speed_sig_series.values
        self.df_windsig = self.df_windsig.drop(['WindDir'], axis=1)
    def interpret_tempsig(self): 
        """temp sig dataframe has pressure in integer form as well. Temperature dewpoint logic
        is the same as the mandatory """               
        temp_sig = []
        dewpoint_sig = []
        for i in range(len(self.df_tempsig)):
            #print (temp_dewpoint_sig[i])
            if self.df_tempsig.TempDew[i]=='/////':
                temp_sig.append(np.nan)
                dewpoint_sig.append(np.nan)
            else:
                temp_i = float(self.df_tempsig.TempDew[i][0:3])
                dewpoint_i = float(self.df_tempsig.TempDew[i][3:5])
                #if i==0:
                if temp_i%2==0:
                    temp_sig.append(temp_i/10)
                    if dewpoint_i <= 50.0:
                        dewpoint_sig.append(round((temp_sig[i] - dewpoint_i/10),2))
                    if dewpoint_i >50.0:
                        dewpoint_d = dewpoint_i - 50.0
                        dewpoint_sig.append(round((temp_sig[i] - dewpoint_d),2))
                if temp_i%2!=0:
                    temp_sig.append(temp_i*-1/10)
                    if dewpoint_i <= 50.0:
                        dewpoint_sig.append(round((temp_sig[i] - dewpoint_i/10),2))
                    if dewpoint_i >50.0:
                        dewpoint_d = dewpoint_i - 50.0
                        dewpoint_sig.append(round((temp_sig[i] - dewpoint_d),2))
        temp_sig_series = pd.Series(temp_sig)
        dewpoint_sig_series = pd.Series(dewpoint_sig)
        self.df_tempsig["Temp"] = temp_sig_series.values
        self.df_tempsig["Dewpoint"] = dewpoint_sig_series.values
        self.df_tempsig = self.df_tempsig.drop(['TempDew'], axis=1)
        
"""class WriteOut():
    
    def __init__(self, vendor, df_temp_sig, df_wind_sig, df_mand, station_height, directory):
        self.vendor_name = vendor
        self.df_tempsig = df_temp_sig
        self.df_windsig = df_wind_sig
        self.df_mand = df_mand
        self.station_height = station_height
        self.directory = directory
        
    def global_commands(self):
        self.get_hundred_height() #getting the 100mb height level to seperate
        
    def get_hundred_height(self):
        for index, row in self.df_mand.iterrows():
            if self.df_mand.Pressure[index] == 100:
                hundred_height = self.df_mand.Height[index]
            if self.df_mand.Pressure[index] < 100:
                hundred_mand_index = index
                break
        for index, row in self.df_tempsig.iterrows():
            if self.df_tempsig.Pressure[index] < 100:
                hundred_sig_index = index
                break
        for index, row in self.df_tempsig.iterrows():
            if self.df_windsig.Height[index] > hundred_height:
                wind_hundred_sig_index = index
                break
        self.df_mand.Height[0] = 'surface'
        self.df_windsig.Height[0] = 'surface'
        with open(self.directory+'/'+'WMO_coded_messages.csv', 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL, lineterminator = '\n')
            wr.writerow([self.vendor_name, "surface Hgt= ",self.station_height])
            wr.writerow(["TTAA    mb", "m","C","C", "degrees","Kts"])
            self.df_mand[0:hundred_mand_index].to_csv(myfile, sep = ',', index = False)        
            wr.writerow(["TTCC    mb","m","C","C", "degrees","Kts"])
            self.df_mand[hundred_mand_index:].to_csv(myfile, sep = ',', index = False)
            wr.writerow([" "])
            wr.writerow(["TTBB    mb","C","C"])
            self.df_tempsig[:hundred_sig_index].to_csv(myfile, sep = ',', index = False)
            wr.writerow(["TTDD    mb","C","C"])
            self.df_tempsig[hundred_sig_index:].to_csv(myfile, sep = ',', index = False)            
            wr.writerow([" "])
            wr.writerow(["PPBB    m", "degrees","Kts"])
            self.df_windsig[:wind_hundred_sig_index].to_csv(myfile, sep = ',', index = False)
            wr.writerow(["PPDD    m", "degrees","Kts"])
            self.df_windsig[wind_hundred_sig_index:].to_csv(myfile, sep = ',', index = False)  
            
class Compare():
    
    def __init__(self, vendor, df, df_temp_sig, df_wind_sig, df_mand, directory):
        self.vendor_name = vendor
        self.df_n = df
        self.df_tempsig_n = df_temp_sig
        self.df_windsig_n = df_wind_sig
        self.df_mand_n = df_mand
        self.directory = directory
    def global_commands(self):
        self.mandatory_compare()
        self.tempsig_compare()
        self.windsig_compare()
        self.write_it_out()
        
    def get_highres_press(self, dataframe):
        index_min_i = []
        for index, row in dataframe.iterrows():
            diff = abs(dataframe.Pressure[index]- self.df_n.P)
            index_min_i.append(np.argmin(diff))
        df_add = self.df_n.iloc[index_min_i]
        df_add = df_add.reset_index(drop=True)
        return df_add
    
    def get_highres_height(self, dataframe):
        index_min_i = []
        for index, row in dataframe.iterrows():
            diff = abs(dataframe.Height[index]- self.df_n.HeightMSL)
            index_min_i.append(np.argmin(diff))
        df_add = self.df_n.iloc[index_min_i]
        df_add = df_add.reset_index(drop=True)
        return df_add
    
    def mandatory_compare(self):
        print (self.df_mand_n)
        self.df_mand_n = pd.concat([self.df_mand_n, self.get_highres_press(self.df_mand_n)], axis=1)
        #print (self.df_mand.Temp)
        self.df_mand_n["Temp_diff"] = self.df_mand_n["Temp"] - self.df_mand_n["TEMP"] #all capps is high res
        self.df_mand_n["Dewp_diff"] = self.df_mand_n.Dewpoint - self.df_mand_n.DEWP
        self.df_mand_n["Speed_diff"] = self.df_mand_n.Speed - self.df_mand_n.SPEED
        self.df_mand_n["Dir_diff"] = self.df_mand_n.Direction - self.df_mand_n.DIR
        
    def tempsig_compare(self):
        self.df_tempsig_n = pd.concat([self.df_tempsig_n, self.get_highres_press(self.df_tempsig_n)], axis=1)
        self.df_tempsig_n["Temp_diff"] = self.df_tempsig_n["Temp"] - self.df_tempsig_n["TEMP"] #all capps is high res
        self.df_tempsig_n["Dewp_diff"] = self.df_tempsig_n.Dewpoint - self.df_tempsig_n.DEWP
        
    def windsig_compare(self):
        self.df_windsig_n = pd.concat([self.df_windsig_n, self.get_highres_height(self.df_windsig_n)], axis=1)
        self.df_windsig_n["Speed_diff"] = self.df_windsig_n["Speed"] - self.df_windsig_n["SPEED"] #all capps is high res
        self.df_windsig_n["Dir_diff"] = self.df_windsig_n.Direction - self.df_windsig_n.DIR
        
    def write_it_out(self):
        self.df_mand_n.Height[0] = 'surface'
        self.df_windsig_n.Height[0] = 'surface'
        self.df_tempsig_n= self.df_tempsig_n.drop(['SPEED','DIR'], axis = 1)
        self.df_windsig_n= self.df_windsig_n.drop(['TEMP','DEWP'], axis = 1)
        with open(self.directory+'/'+'WMO_highres_comparison.csv', 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL, lineterminator = '\n')
            wr.writerow([self.vendor_name])
            wr.writerow(["Mandatory Level Comparisons"])
            self.df_mand_n.to_csv(myfile, sep = ',', index = False)
            wr.writerow([" "])
            wr.writerow(["Temp/Dew Sig Level Comparisons"])
            self.df_tempsig_n.to_csv(myfile, sep = ',', index = False)
            wr.writerow([" "])
            wr.writerow(["Speed/Dir Sig Level Comparisons"])
            self.df_windsig_n.to_csv(myfile, sep = ',', index = False)"""
      
    
        
        
        
                
                
                