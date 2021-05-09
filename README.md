# NetCDF
Python [NetCDF4](https://github.com/Unidata/netcdf4-python) wrapper.

Created mainly to store data (e.g. byte, float, double) into a different smaller size format and save storage space. 
Most often used to store double precision (8bytes) format into byte format, where accurary is less important.


## Installation
```bash
git clone https://github.com/meracan/netcdf
pip install ./netcdf
```

## Example
The command `NetCDF.create` is used to create a NetCDF file.
Below shows a typical example to create a NetCDF file. In the variables object, variable `a` is a 8-bit singed interger format using dimension `d2`. There is no transformation.
Variable `b` is a float type format using dimension `d2` but requires transformation from float to 8-bit unsigned integers `stype:u1`. 
To make the transformation, the `min` and `max` needs to be specified as shown.

```python
from netcdf import NetCDF
input={
    "metadata":{"string":"string","integer":1,"float":0.1,"object":{"o1":1,"o2":"a"}},
    "dimensions":{"d1":8,"d2":256,"d3":32,"d4":512,"d5":5,"nchar":6,"d0":1},
    "variables":{
        "a":{"type":"b","dimensions":["d2"],"units":"m" ,"standard_name":"A Variable" ,"long_name":"Long A Variable","data":np.arange(-128,128,dtype="byte")},
        "b":{"type":"f4","stype":"u1","dimensions":["d2"],"max":255,"min":0,"data":np.arange(0,256,dtype="f4")},
    }
}
filePath = "test_1.nc"
NetCDF.create(filePath,**input) # <--- NetCDF was created and data was stored inside the NetCDF
with NetCDF(filePath, "r") as netcdf: # <--- Open NetCDF file
  np.testing.assert_array_equal(netcdf['a'][:],np.arange(-128,128,dtype="i1"))
  np.testing.assert_array_equal(netcdf['b'][:],np.arange(0,256,dtype="f4"))# <--- Data was stored as u1 but retrieved as float

```

Other examples are shown in `test_python.py`