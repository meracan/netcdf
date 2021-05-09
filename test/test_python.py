import os
import numpy as np
import json
from netcdf import NetCDF
import copy

def test_1():
  folder="test"
  
  
  input={
    "metadata":{"string":"string","integer":1,"float":0.1,"object":{"o1":1,"o2":"a"}},
    "dimensions":{"d1":8,"d2":256,"d3":32,"d4":512,"d5":5,"nchar":6,"d0":1},
    "variables":{
        "a":{"type":"b","dimensions":["d2"],"units":"m" ,"standard_name":"A Variable" ,"long_name":"Long A Variable","data":np.arange(-128,128,dtype="byte")},
        "b":{"type":"f4","stype":"u1","dimensions":["d2"],"max":255,"min":0,"data":np.arange(0,256,dtype="f4")},
        "c":{"type":"f4","stype":"u1","dimensions":["d2"],"max":255,"min":0,"data":np.arange(0,256)},
        "d":{"type":"b","dimensions":["d1"],"data":np.arange(0,8)},
        "e":{"type":"f4","stype":"i4","dimensions":["d4"],"data":np.arange(0,512,dtype="f4")},
        "f":{"type":"f4","dimensions":["d1","d3"],"max":255,"min":0,"data":np.arange(0,256).reshape((8,32))},
        "g":{"type":"B","dimensions":["d1"],"data":np.arange(0,8)},
        "h":{"type":"B","dimensions":["d1"],"data":np.arange(0,8)},
        "i":{"type":"M","dimensions":["d1"],"data":np.datetime64('2017-01-01')+np.arange(8)*np.timedelta64(1, 'h')},
        "j":{"type":"d","dimensions":["d2"],"data":np.arange(0,256,dtype="d")},
        "k":{"type":"S1","dimensions":["d5","nchar"],"data":np.array(["a","bc","def","ghij a","b"])},
        "l":{"type":"f4","stype":"i2","dimensions":["d1","d3"],"max":255,"min":0,"data":np.arange(0,256).reshape((8,32))},
        "m":{"type":"d","ftype":"M","dimensions":["d1"],"data":np.datetime64('2017-01-01')+np.arange(8)*np.timedelta64(1, 'h')},
        "n":{"type":"b","dimensions":["d0"],"data":np.arange(0,1)},
        "o":{"type":"b","dimensions":["d0"],"data":1},
    },
    "groups":{
      "g1":{
      "metadata":{"shape":[250000,250000],"integer":1,"float":0.1,"object":{"o1":1,"o2":"a"}},
      "dimensions":{"e1":256},
      "variables":{
        "a":{"type":"b","dimensions":["d2"],"units":"m" ,"standard_name":"A Variable" ,"long_name":"Long A Variable","data":np.arange(-128,128,dtype="byte")},
      }
      }
    },
  }
  for netcdf3 in [False,True]:
    filePath = os.path.join(folder,"test_1.nc")
    obj=copy.deepcopy(input)
    if netcdf3:del obj['groups']
    NetCDF.create(filePath,netcdf3=netcdf3,**obj)
    with NetCDF(filePath, "r") as netcdf:
      np.testing.assert_array_equal(netcdf.metadata,{"string":"string","integer":1,"float":0.1,"object":{"o1":1,"o2":"a"}})
      np.testing.assert_array_equal(netcdf['a'][:],np.arange(-128,128,dtype="i1"))
      np.testing.assert_array_equal(netcdf['b'][:],np.arange(0,256,dtype="f4"))
      np.testing.assert_array_equal(netcdf['c'][:],np.arange(0,256))
      np.testing.assert_array_equal(netcdf['d'][:],np.arange(0,8))
      np.testing.assert_almost_equal(netcdf['e'][:],np.arange(0,512,dtype="f4"),4)
      np.testing.assert_array_equal(netcdf['f'][:],np.arange(0,256).reshape((8,32)))
      np.testing.assert_array_equal(netcdf['g'][:],np.arange(0,8))
      np.testing.assert_array_equal(netcdf['h'][:],np.arange(0,8))
      np.testing.assert_array_equal(netcdf['i'][:],np.datetime64('2017-01-01')+np.arange(8)*np.timedelta64(1, 'h'))
      np.testing.assert_array_equal(netcdf['j'][:],np.arange(0,256,dtype="d"))
      np.testing.assert_array_equal(netcdf['k'][:],np.array(["a","bc","def","ghij a","b"]))
      np.testing.assert_array_equal(netcdf['l'][:],np.arange(0,256).reshape((8,32)))
      np.testing.assert_array_equal(netcdf['m'][:],np.datetime64('2017-01-01')+np.arange(8)*np.timedelta64(1, 'h'))
      np.testing.assert_array_equal(netcdf['n'][:],np.arange(0,1))
      np.testing.assert_array_equal(netcdf['o'][:],np.arange(1,2))
      if not netcdf3:
        np.testing.assert_array_equal(netcdf['g1'].metadata['shape'],np.array([250000,250000]))
        np.testing.assert_array_equal(netcdf['g1']['a'][:],np.arange(-128,128,dtype="i1"))
        

if __name__ == "__main__":
  test_1()