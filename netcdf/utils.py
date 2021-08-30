import numpy as np
import json
from netCDF4 import Dataset,stringtochar,chartostring,Variable,Group

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except:
    return False
  return True

def getType(type):
  t=np.dtype(type).char
  if t=="S":return 'S1'
  if t=="U":return 'U1'
  return t
  
def getType3(type):
  
  t=np.dtype(type).char
  if t=="B":return 'b'
  if t=="H":return 'h'
  if t=="I":return 'i'
  if t=="l":return 'i'
  if t=="S":return 'S1'
  if t=="U":return 'U1'
  return t

def prepareTransformAttributes(attributes):
  dtype=attributes.get("type")
  dtype="{}".format(dtype)
  min=attributes.get("min")
  max=attributes.get("max")
  ftype=attributes.get("ftype")
  maxV=np.power(2.0,np.iinfo(np.dtype(dtype)).bits)-1.0
  minO=np.iinfo(np.dtype(dtype)).min
  maxO=np.iinfo(np.dtype(dtype)).max
  f=maxV/(max-min)
  return min,max,minO,maxO,f,dtype,ftype



def getT(attributes,value,isChar=False):
  ftype=attributes['ftype']
  if "min" in attributes and "max" in attributes and attributes['type']!=attributes['ftype'] :
    min,max,minO,maxO,f,dtype,ftype=prepareTransformAttributes(attributes)
    value=(((value+np.abs(minO))/f)+min).astype(ftype)
    
  if ftype=="M":value=value.astype('datetime64[ms]')
  if ftype=="S1":value=value.astype("S1") if isChar else chartostring(value.astype("S1"))
  
  return value
 
def setT(attributes,value,isChar=False,variable=None):
  ftype=attributes['ftype']
  if ftype=="M":value=value.astype("datetime64[ms]").astype("f8")
  if ftype=='S1' and not isChar:value=stringtochar(np.array(value).astype("S{}".format(variable.shape[1])))
  
  if "min" in attributes and "max" in attributes and attributes['type']!=attributes['ftype'] :
    min,max,minO,maxO,f,dtype,x=prepareTransformAttributes(attributes)
    value=np.clip(value, min, max)
    value=(value-min)*f-np.abs(minO)
    # value=np.rint(np.nextafter(value, value+1))
    value=np.rint(value)
    value=np.clip(value, minO, maxO)
    value=value.astype(dtype)      
  
  return value


class NpEncoder(json.JSONEncoder):
  """ 
  Encoder to change numpy type to python type.
  This is used for creating JSON object.
  """
  def default(self, obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return super(NpEncoder, self).default(obj)
        
def getDimensionsV(variables,dimensionsV={}):
  for vname in variables:
    for dname in variables[vname]['dimensions']:
      if dname in dimensionsV:dimensionsV[dname].append(vname)
      else:dimensionsV[dname]=[vname]
  return dimensionsV
  
def getVariablesG(groups):
  obj={}
  for gname in groups:
    for vname in groups[gname]['variables']:
      if vname in obj:obj[vname].append(gname)
      else:obj[vname]=[gname]
  for vname in obj:
    obj[vname]=sorted(list(set(obj[vname])))
  return obj   