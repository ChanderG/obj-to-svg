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

def calculateCentroid(face, vertices):
    """
    Calculate centroid of face.
    Face can be a 3-tuple( triangle ) or 4-tuple( square ).
    Vertices is the record of all vertices.

    Returns the 3 coordinates of the centroid.
    """

    if len(face) == 3:
        a, b, c = face
        x = (vertices[a][0] + vertices[b][0] + vertices[c][0])/3
        y = (vertices[a][1] + vertices[b][1] + vertices[c][1])/3
        z = (vertices[a][2] + vertices[b][2] + vertices[c][2])/3
        return (x, y, z)

    if len(face) == 4:
        a, b, c, d = face
        x = (vertices[a][0] + vertices[b][0] + vertices[c][0] + vertices[d][0])/4
        y = (vertices[a][1] + vertices[b][1] + vertices[c][1] + vertices[d][1])/4
        z = (vertices[a][2] + vertices[b][2] + vertices[c][2] + vertices[d][2])/4
        return (x, y, z)

def calculateNormal(face, vertices):
    """
    Calculate centroid of face.
    Face can be a 3-tuple( triangle ) or 4-tuple( square ).
    Vertices is the record of all vertices.

    Returns the normal vector components along i, j and k.
    """
    if len(face) == 3:
        a, b, c = face
    if len(face) == 4:
        a, b, c, d = face

    dir1_x, dir1_y, dir1_z = (vertices[b][0] - vertices[a][0]), (vertices[b][1] - vertices[a][1]), (vertices[b][2] - vertices[a][2])
    dir2_x, dir2_y, dir2_z = (vertices[c][0] - vertices[a][0]), (vertices[c][1] - vertices[a][1]), (vertices[c][2] - vertices[a][2])

    x, y, z = (dir1_y*dir2_z - dir1_z*dir2_y), (dir1_z*dir2_x - dir2_z*dir1_x), (dir1_x*dir2_y - dir1_x*dir2_y)
    return (x, y, z)

def dotProduct(vector1, vector2):
    """ Return dot product.

    Input is represented in terms of 3-tuples.
    """
    x1, y1, z1 = vector1
    x2, y2, z2 = vector2

    return (x1*x2 + y1*y2 + z1*z2)

def backFaceCull(obj, params):
    """ Cull back faces. 

    INPUT
    -----
    obj -- existing object structure
    params -- gen params

    OUPUT
    -----
    obj -- the updated object
    """

    # for each face, calculate normals, compare and remove if necessary
    vertices = obj["vertices"]
    faces = obj["faces"]
    newfaces = []

    for f in faces:
       (px, py, pz) = calculateCentroid(f, vertices)
       view_ray =  (px - params["vx"], py - params["vy"], pz - params["vz"])
       normal = calculateNormal(f, vertices)

       print view_ray, normal
       print dotProduct(view_ray, normal)
       if dotProduct(view_ray, normal) < 0:
           newfaces.append(f)

    print "{0} faces culled.".format(len(faces) - len(newfaces))
    print faces
    print newfaces
    obj["faces"] = newfaces
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

  print "Back face culling..."
  obj = backFaceCull(obj, params)

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
