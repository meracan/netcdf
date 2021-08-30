import os
import numpy as np
import json
from netCDF4 import Dataset,stringtochar,chartostring,Variable,Group
from .utils import getT,setT,is_json,getType,getType3,NpEncoder,getDimensionsV,getVariablesG

class NetCDF(Dataset):
  def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
    self.set_auto_mask(False)
    
  def __getitem__(self, idx):
    variable=super().__getitem__(idx)
    if(isinstance(variable,Variable)):return VariableCDF(variable)
    if(isinstance(variable,Group)):return GroupCDF(variable)
    return variable
  
  def updateMetadata(self,newmetadata):
    metadata=self.metadata
    for key in newmetadata:
      metadata[key]=newmetadata[key]
      
    for key in metadata:
      value=metadata[key]
      if isinstance(value,dict):value=json.dumps(value,cls=NpEncoder)
      setattr(self, key, value)
    
  
  @property
  def metadata(self):
    obj={}
    for key in self.ncattrs():
      value=self.getncattr(key)
      if is_json(value):value=json.loads(value)
      obj[key]=value
    return obj
  
  @property
  def _dimensions(self):
    dimensions={}
    for id in self.dimensions:
      dimensions[id]=self.dimensions[id].size
    return dimensions
    
  @property
  def _variables(self):
    variables={}
    for vname in self.variables:
      variables[vname]=self[vname].attributes
    
    return variables

  @property
  def allvariables(self):
    
    variables={}
    for vname in self.variables:
      variables[vname]=self[vname].attributes
    
    
    for gname in self.groups:
        group=self[gname].obj
        for vname in group['variables']:
          variables[vname]=group['variables'][vname]
    return variables
  
  @property
  def _groups(self):
    groups={}
    for gname in self.groups:
      groups[gname]=self[gname].obj
    return groups
  
  @property
  def obj(self):
    metadata=self.metadata
    dimensions=self._dimensions
    variables=self._variables
    groups=self._groups
    
      
    dimensionsV=getDimensionsV(variables)
    for gname in groups:
      dimensionsV=getDimensionsV(groups[gname]['variables'],dimensionsV)
    for dname in dimensionsV:
      dimensionsV[dname]=sorted(list(set(dimensionsV[dname])))
    
    groupsByVariable=getVariablesG(groups)  
    
    
    
    return {
      "metadata":metadata,
      "dimensions":self._dimensions,
      "variables":self._variables,
      "groups":self._groups,
      "dimensionsByVariable":dimensionsV,
      "groupsByVariable":groupsByVariable,
    }
  
    
    
    
  @staticmethod
  def create(filePath,metadata={},dimensions={},variables={},groups={},netcdf3=False):
    format="NETCDF4" if not netcdf3 else "NETCDF3_CLASSIC"
    if not os.path.isdir(os.path.dirname(filePath)):
      os.makedirs(os.path.dirname(filePath), exist_ok=True)
      
    with NetCDF(filePath, "w",format=format) as netcdf:
      NetCDF._create(netcdf,metadata,dimensions,variables)
      for name in groups:
        group = netcdf.createGroup(name)
        NetCDF._create(group,**groups[name])
        
  
  @staticmethod
  def _create(netcdf,metadata={},dimensions={},variables={},groups={}):
    # Write metadata
    for key in metadata:
      value=metadata[key]
      if isinstance(value,dict):value=json.dumps(value,cls=NpEncoder)
      setattr(netcdf, key, value)
    
    
    # Write Dimensions
    for name in dimensions:
      netcdf.createDimension(name, dimensions[name])
    
    for name in variables:
      NetCDF._createVariable(netcdf,name,variables[name])
    
    
    for name in groups:
      group = netcdf.createGroup(name)
      NetCDF._create(group,**groups[name])
    
  
  @staticmethod
  def getCharDimension(data):
    type=np.array(data).dtype
    return int(type.itemsize/4)
    
  @staticmethod
  def _createVariable(netcdf,name,variable):
    """
    variables:{"{name}":obj}
    """
    if not 'type' in variable:raise Exception("Variable need a type - {} - {}".format(name,variable))
    if not 'dimensions' in variable:raise Exception("Variable need dimensions")
    data=variable.pop("data",None)
    type=variable.pop("type")
    stype=variable.pop("stype",None)
    dimensions=variable.pop("dimensions")
    lsd = variable.pop('least_significant_digit',None)
    type=getType(type)
    variable['ftype']=ftype=variable.pop("ftype",type)
    zlib=True
    
    
    if type=="M" or ftype=="M":
      variable['units']="ms since 1970-01-01 00:00:00.0"
      variable['calendar']="gregorian"
      type="d"
      variable['ftype']="M"
    
    if stype:
      if not 'max' in variable:
        if data is None:raise Exception("Variable needs max value to properly store data")
        variable['max']=np.max(data)
      if not 'min' in variable:
        if data is None:raise Exception("Variable needs min value to properly store data")
        variable['min']=np.min(data)
    else:
      stype=type

    if netcdf.file_format=="NETCDF3_CLASSIC":
      stype=getType3(stype)
      zlib=False
    
    _var=netcdf.createVariable(name,stype,dimensions,zlib=zlib,least_significant_digit=lsd)
    
    for key in variable:
      setattr(_var, key, variable[key])  
    if not data is None:
      _var=netcdf[name]
      _var[:]=data
  
class GroupCDF(object):
  def __init__(self,group):
    self.group=group
  
  def __getitem__(self, idx):
    variable=self.group.__getitem__(idx)
    
    if(isinstance(variable,Variable)):return VariableCDF(variable)
    if(isinstance(variable,Group)):return GroupCDF(variable)
    return variable
  
  def __setitem__(self, idx,value):
    return self.group.__setitem__(idx,value)
  
  @property
  def metadata(self):
    obj={}
    for key in self.group.ncattrs():
      value=self.group.getncattr(key)
      if is_json(value):value=json.loads(value)
      obj[key]=value
    return obj
  
  @property
  def dimensions(self):
    dimensions={}
    for id in self.group.dimensions:
      dimensions[id]=self.group.dimensions[id].size
    return dimensions
    
  @property
  def variables(self):
    variables={}
    for vname in self.group.variables:
      variables[vname]=self[vname].attributes
    
    return variables
  
  @property
  def obj(self):
    return {
      "metadata":self.metadata,
      "dimensions":self.dimensions,
      "variables":self.variables,
    }
    
    
class VariableCDF(object):
  def __init__(self,variable):
    self.variable=variable
    self.isChar=False
  
  @property
  def obj(self):
    return self.attributes
    
  @property
  def shape(self):
    return self.variable.shape
    
  @property
  def nchar(self):
    return self.variable.shape[1]
  
  @property
  def attributes(self):
    obj={
      "dimensions":list(self.variable.dimensions),
      "type":np.dtype(self.variable.dtype).char,
      "ftype":np.dtype(self.variable.dtype).char,
    }
    for key in self.variable.ncattrs():
      obj[key]=getattr(self.variable, key)  
    return obj
  
  def __getitem__(self, idx):
    value=self.variable.__getitem__(idx)
    value=getT(self.attributes,value)
    return value
      
  def __setitem__(self, idx,value):
    value=setT(self.attributes,value,isChar=self.isChar,variable=self.variable)
    self.variable.__setitem__(idx,value)