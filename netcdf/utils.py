import numpy as np
import json

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

def getT(attributes,value):
  if not attributes:return value
  min,max,minO,maxO,f,dtype,ftype=prepareTransformAttributes(attributes)
  value=(((value+np.abs(minO))/f)+min).astype(ftype)
  return value
 
def setT(attributes,value):
  if not attributes:return value
  min,max,minO,maxO,f,dtype,x=prepareTransformAttributes(attributes)
  value=np.clip(value, min, max)
  value=np.rint((value-min)*f-np.abs(minO))
  value=np.clip(value, minO, maxO)
  return value.astype(dtype)      


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