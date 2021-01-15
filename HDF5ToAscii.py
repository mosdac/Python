#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 14:36:35 2021

@author: sazid
"""

import numpy as np
import h5py
from pyproj import Proj, transform



#==============Start of function def HDF5ToAsciiFullGlobe(InputHDF5File,DatasetName):

def HDF5ToAsciiFullGlobe(InputHDF5File,DatasetName):
    """
    #---------------------------Arguments-------------------------------------------
    InputHDF5File : Any Full globe L1B,L2B,L3B HDF5 product
                   e.g. L1B : 3DIMG_15AUG2020_0600_L1B_STD.h5
                        L2B : 3DIMG_15AUG2020_0600_L2B_HEM.csv,3DIMG_15AUG2020_0600_L2B_SST.h5 etc
    DatasetName   : e.g. L1B Datasets are : 1 Km:IMG_VIS,IMG_SWIR, 4 Km: IMG_TIR1,IMG_TIR2,IMG_MIR, 8 km: IMG_WV
                    e.g. L2B datasets are : HEM,LST,SST etc
                    
    #-------------------------------------------------------------------------------
    
    Functionality : It creates an ASCII File named InputHDF5File(-.h5)_DatasetName.csv 
                    in format "Latitude Longitude Datasetvalue" for all Valid dataset values
                    
    NOTE: This function Supports Extraction of Full Globe L1B,L2B,L3B Products
    """
    
    FileFd = h5py.File(InputHDF5File,'r')
    
    print("HDF5 Keys\n:",FileFd.keys())
   
    if("L1B" in InputHDF5File ):
        if(("IMG_VIS" in DatasetName) or ("IMG_VIS" in DatasetName)):
            LatDataset = "Latitude_VIS"
            LonDataset = "Longitude_VIS"
        elif(("IMG_TIR1" in DatasetName) or ("IMG_TIR2" in DatasetName) or ("IMG_MIR" in DatasetName) ):
            LatDataset = "Latitude"
            LonDataset = "Longitude"
        elif(("IMG_WV" in DatasetName)):
            LatDataset = "Latitude_WV"
            LonDataset = "Longitude_WV"
    else: # for L2B and L3B
        LatDataset = "Latitude"
        LonDataset = "Longitude"
        
    print("Actual LatDataset,LonDataset,DatasetName:",LatDataset,LonDataset,DatasetName)
    
    
    d1 = FileFd.get(LatDataset)
    d2 = FileFd.get(LonDataset)
    d3 = FileFd.get(DatasetName)
    
    ScaleFactor_LatLon = d1.attrs['scale_factor']
    FillValue_LatLon   = d1.attrs['_FillValue']
    
    FillValue_d3   = d3.attrs['_FillValue']
    
    print("LatDataset  Fill value, Scale:",LatDataset,FillValue_LatLon,ScaleFactor_LatLon)
    print("DatasetName Fill value :",DatasetName ,FillValue_d3)
    
    d1 = np.array(d1)
    d2 = np.array(d2)
    d3 = np.array(d3[0])
    
    if ( ("L2B" in InputHDF5File ) or ("L3B" in InputHDF5File ) ): #L2B case
        #d3_mask = np.ma.masked_where(d3 == -999.0,d3)
        d3_mask = np.ma.masked_where(d3 == FillValue_d3[0],d3)
    
    elif("L1B" in InputHDF5File ): #L1B case
    
        d3_mask = np.ma.masked_where(d1 == FillValue_LatLon[0] ,d1)
    
    print("Data type of d1 and size\n", d1.dtype,d1.size,d1.shape)
    print("Data type of d2 and size\n", d2.dtype,d2.size,d2.shape)
    print("Data type of d3 and size\n", d3.dtype,d3.size,d3.shape)
    
    
    d1_masked = d1[~d3_mask.mask].copy()
    d2_masked = d2[~d3_mask.mask].copy()
    d3_masked = d3[~d3_mask.mask].copy()

    D1=d1_masked.flatten() * ScaleFactor_LatLon[0]
    D2=d2_masked.flatten() * ScaleFactor_LatLon[0]
    D3=d3_masked.flatten() 
    table = np.array([D1,D2,D3]) 
    """
    d1=d1.flatten() * ScaleFactor
    d2=d2.flatten() * ScaleFactor
    d3=d3.flatten() 
    table = np.array([d1,d2,d3]) 
    """
    
    
    transpose_table = table.transpose()
    #OutputAsciiFile = InputHDF5File[:-2] + "csv"
    OutputAsciiFile = InputHDF5File[:-3] + "_" + DatasetName+".csv"
    np.savetxt(OutputAsciiFile,transpose_table,delimiter='\t',fmt='%10.5f')
    
    FileFd.close()
#==============End of function def HDF5ToAsciiFullGlobe(InputHDF5File,DatasetName):
    
    
    
#==============Start of function def HDF5ToAsciiSector(InputHDF5File,DatasetName):
def HDF5ToAsciiSector(InputHDF5File,DatasetName):
    """
    #---------------------------Arguments-------------------------------------------
    InputHDF5File : Any Full globe L1C,L2C,L3C HDF5 product
                   e.g. L1C : 3DIMG_15AUG2020_0600_L1C_ASIA_MER.h5,3DIMG_15AUG2020_0600_L1C_SGP.h5
                        L2C : 3DIMG_15AUG2020_0600_L2C_INS.h5,3DIMG_15AUG2020_0600_L2C_FOG.h5 etc
    DatasetName   : e.g. L1C Datasets are : All 4 Km : IMG_VIS,IMG_SWIR,IMG_TIR1,IMG_TIR2,IMG_MIR,IMG_WV
                    e.g. L2C datasets are : INS, FOG, SNW
    #----------------------------------------------------------------------
    
    Functionality : It creates an ASCII File named InputHDF5File(-.h5)_DatasetName.csv 
                    in format "Latitude Longitude Datasetvalue" for all Valid dataset values
    
    NOTE: This function Supports Extraction of Full Globe L1C,L2C,L3C Products                
    """
    
    FileFd = h5py.File(InputHDF5File,'r')
    
    print("HDF5 Keys\n:",FileFd.keys())
    
    Y = FileFd.get("Y") # Y :Latitude
    X = FileFd.get("X") # X :Longitude
    d3 = FileFd.get(DatasetName)
    FillValue_d3   = d3.attrs['_FillValue']
    print("DatasetName Fill value d3:",DatasetName,FillValue_d3)
    
    #=====================Convert X,Y to Lon/Lat==========================
    
    Y=np.array(Y)
    X=np.array(X)            
    projinfo=FileFd.get('Projection_Information')
    lat_0=float(projinfo.attrs['standard_parallel'])
    lon_0=float(projinfo.attrs['longitude_of_projection_origin'])
    
    string='+proj=merc +lat_ts='+str(lat_0)+' +lon_0='+str(lon_0)
    X_2D,Y_2D = np.meshgrid(X,Y,sparse=False)
    newproj=Proj(string)
    outProj = Proj(init='epsg:4326')
    d2,d1 = transform(newproj,outProj,X_2D,Y_2D) # d2=lon,d1=lat
    
    #=====================================================================
    
    d3 = np.array(d3[0])
    
    #d3_mask = np.ma.masked_where(d3 == -999.0,d3)
    d3_mask = np.ma.masked_where(d3 == FillValue_d3[0],d3)
    
    
    print("Data type of d1 (Lat) and size\n", d1.dtype,d1.size,d1.shape)
    print("Data type of d2 (Lon) and size\n", d2.dtype,d2.size,d2.shape)
    print("Data type of d3 and size\n", d3.dtype,d3.size,d3.shape)
    
    
    d1_masked = d1[~d3_mask.mask].copy()
    d2_masked = d2[~d3_mask.mask].copy()
    d3_masked = d3[~d3_mask.mask].copy()

    D1=d1_masked.flatten() 
    D2=d2_masked.flatten()
    D3=d3_masked.flatten() 
    table = np.array([D1,D2,D3]) 
    
    transpose_table = table.transpose()
    
    #OutputAsciiFile = InputHDF5File[:-2] + "csv"
    OutputAsciiFile = InputHDF5File[:-3] + "_" + DatasetName +".csv"
    np.savetxt(OutputAsciiFile,transpose_table,delimiter='\t',fmt='%10.5f')
    
    FileFd.close()   
#==============End of function def HDF5ToAsciiSector(InputHDF5File,DatasetName):    

#-------------------------Testing Sectionfor L1B/L2B---------------------------------
#========================Testing Section for L2B============================
#==================Testing SST=============Tested OK================= 
InputFile = "/tmp/extract/3DIMG_15AUG2020_0600_L2B_SST.h5"
DatasetName = "SST"
HDF5ToAsciiFullGlobe(InputFile,DatasetName)


"""
#==================Testing HEM============Tested OK================== 
InputFile = "/tmp/extract/3DIMG_15AUG2020_0600_L2B_HEM.h5"
DatasetName = "HEM"
HDF5ToAsciiFullGlobe(InputFile,DatasetName)
"""

"""
#========================Testing Section for L1B============================
InputFile = "/tmp/extract/3DIMG_15AUG2020_0600_L1B_STD.h5"
#DatasetName = "IMG_TIR1"
DatasetName = "IMG_WV" 
#DatasetName = "IMG_VIS" 
HDF5ToAsciiFullGlobe(InputFile,DatasetName)
"""
#-------------------------Testing Sectionfor L1CL2C---------------------------------

"""
#========================Testing Sectionfor L2C============Tested OK================ 
InputFile = "/tmp/extract/3DIMG_15AUG2020_0600_L2C_INS.h5"
#DatasetName = "INS"
DatasetName = "DHI"
HDF5ToAsciiSector(InputFile,DatasetName)
"""

"""
#========================Testing Sectionfor L1C===========Tested OK================= 
InputFile = "/tmp/extract/3DIMG_15AUG2020_0600_L1C_ASIA_MER.h5"
#DatasetName = "IMG_TIR1"
DatasetName = "IMG_WV"
HDF5ToAsciiSector(InputFile,DatasetName)
"""   
    
    