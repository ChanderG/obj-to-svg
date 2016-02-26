"""
Create a 2d svg image from a 3d object.

User input:
  1. Viewpoint
  2. Input obj file.
  3. Dimensions of viewport

Output:
  1. svg file

Assumptions:
  1. Only backface culling
"""

import optparse

def loadObjectFromObj(filename):
  """ Load object from obj file into custom structure.

  INPUT
  -----
  filename -- name of obj file

  OUPUT
  -----
  dict object containing vertices and faces
  """
  obj = {}
  obj['vertices'] = {}
  obj['faces'] = []

  # raw text from obj
  obj_raw = open(filename).read().strip('\n')
  
  # content lines
  obj_raw_lines = filter(lambda x: x!="", obj_raw.split('\n'))

  vertex_count = 1

  for line in obj_raw_lines:
    l = filter(lambda x: x!= '', line.split(' '))
    # handle faces
    if l[0] == 'f':
	    if len(l) == 5:
	      obj['faces'].append((int(l[1]), int(l[2]), int(l[3]), int(l[4])))
	    elif len(l) == 4:
	      obj['faces'].append((int(l[1]), int(l[2]), int(l[3])))
	    else:
	      print "Illegal condition"
	      exit(1)
    # handle vertices
    elif l[0] == 'v':
      if len(l) == 4:
        obj['vertices'][vertex_count] = (float(l[1]), float(l[2]), float(l[3]))
        vertex_count += 1
      else:
				print "Illegal condition"
				exit(1)
    else:
      print "Illegal condition"
      exit(1)

  return obj

def convertToImage(params, filename):
  """ Convert obj object to svg image. 
  
  Top level worker for business logic.

  INPUT
  -----
  params -- hash of params
  filename -- name of input obj file
  """

  # load object from obj file
  obj = loadObjectFromObj(filename)
  print obj

def main():
  """ Main runner. 
  
  Just a wrapper on main worker to take in args etc.
  """
  usage = "usage: %prog [options] <name of obj file>"
  parser = optparse.OptionParser(usage=usage)

  parser.add_option("-x", "--vx", type="int", dest="vx", default="0", help="viewer x coordinate")
  parser.add_option("-y", "--vy", type="int", dest="vy", default="0", help="viewer y coordinate")
  parser.add_option("-z", "--vz", type="int", dest="vz", default="0", help="viewer z coordinate")

  parser.add_option("-H", "--vh", type="int", dest="vh", default="100", help="viewport height")
  parser.add_option("-W", "--vw", type="int", dest="vw", default="100", help="viewport width")

  (options, args) = parser.parse_args()

  if len(args) != 1:
    parser.error("incorrect number of arguments")

  params = {}
  params['vx'] = options.vx
  params['vy'] = options.vy
  params['vz'] = options.vz
  params['H'] = options.vh
  params['W'] = options.vw

  print "Using values: "
  print params

  # pass on to main worker
  convertToImage(params, args[0])

if __name__ == "__main__":
  main()
