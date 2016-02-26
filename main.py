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
        if line.strip(' ')[0] == '#':
            continue
        l = filter(lambda x: x!= '', line.split(' '))
        # handle faces
        if l[0] == 'f':
            if len(l) == 5:
                obj['faces'].append((int(l[1]), int(l[2]), int(l[3]), int(l[4])))
            elif len(l) == 4:
                obj['faces'].append((int(l[1]), int(l[2]), int(l[3])))
            else:
                print "Illegal condition: Too many vertices in face."
                exit(1)
        # handle vertices
        elif l[0] == 'v':
            if len(l) == 4:
                obj['vertices'][vertex_count] = (float(l[1]), float(l[2]), float(l[3]))
                vertex_count += 1
            else:
                print "Illegal condition: Too many coordinates for a vertex."
                exit(1)
        else:
            print l
            print "Illegal condition: "
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

    x, y, z = (dir1_y*dir2_z - dir1_z*dir2_y), (dir1_z*dir2_x - dir2_z*dir1_x), (dir1_x*dir2_y - dir1_y*dir2_x)
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

       if dotProduct(view_ray, normal) < 0:
           newfaces.append(f)

    print "{0}/{1} faces culled.".format(len(faces) - len(newfaces), len(faces))
    obj["faces"] = newfaces
    return obj

def ZwithFaceTuple(face, vertices):
    """ Convert face to tuple with centroid Z.

    face -- a single face
    vertices -- the vertex set of object

    Returns a tuple like: (z, face) where z is the z coordinate of face.
    """

    if len(face) == 3:
        a, b, c = face
        z = (vertices[a][2] + vertices[b][2] + vertices[c][2])/3
    if len(face) == 4:
        a, b, c, d = face
        z = (vertices[a][2] + vertices[b][2] + vertices[c][2] + vertices[d][2])/4

    return (z, face)

def orderFacesPainters(obj):
    """ Orders faces of a 3d object accordng to Painter's algorithm aka farthest z first.

    obj -- the 3d object

    Returns the faces in this order.
    """
    faceWithZ = map(lambda x: ZwithFaceTuple(x, obj["vertices"]), obj["faces"])

    from operator import itemgetter
    sorted_faceWithZ = sorted(faceWithZ, key=itemgetter(0))

    sorted_faces = map(lambda (x, y): y, sorted_faceWithZ)
    return sorted_faces

def projectVerticesTo2D(vertices, params):
    """ Project vertices to the XY plane.

    Return the set of vertices on XY plane.
    """
    xv, yv, zv = params["vx"], params["vy"], params["vz"]

    img_vertices = {}
    for v_no, vertex in vertices.items():
        x, y, z = vertex
        z = -z
        x_ = (z*xv + x*zv)/(z + zv)
        y_ = (z*yv + y*zv)/(z + zv)
        img_vertices[v_no] = (x_, y_, 0)

    return img_vertices

def project2D(obj, params):
    """ Project 3d object to 2d image. 
    
    obj -- the 3d object itself
    params -- hash of params

    Returns the 2d image structure with faces in the correct order.
    """

    # blindly convert 3d points to 2d set
    img = {}

    # first ready faces in correct order
    img["faces"] = orderFacesPainters(obj)

    # then convert 3d points to 2d
    img["vertices"] = projectVerticesTo2D(obj["vertices"], params)

    return img

def drawSvg(img, filename):
    """ Draw svg image from img structure.

    img -- struct of image data
    filename -- output file name

    Creates a svg file called -- filename.svg containing required image.
    """
    vertices = img["vertices"]

    f = open(filename, 'w')
    f.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.1">')
    f.write('\n')

    for face in img["faces"]:
        # format the point string
        if len(face) == 3:
            a, b, c = face
            vertex_str = "{0},{1} {2},{3} {4},{5}".format(vertices[a][0], vertices[a][1], vertices[b][0], vertices[b][1], vertices[c][0], vertices[c][1])
        if len(face) == 4:
            a, b, c , d = face
            vertex_str = "{0},{1} {2},{3} {4},{5} {6},{7}".format(vertices[a][0], vertices[a][1], vertices[b][0], vertices[b][1], vertices[c][0], vertices[c][1], vertices[d][0], vertices[d][1])
        # draw polygon
        f.write('<polygon points="{0}" style="fill:red;stroke:black;stroke-width:1" />'.format(vertex_str))
        f.write('\n')
    f.write('</svg>')
    f.close()

def dummyScaleUp(img):
    """ Dummy placeholder scaleup for test purpose. """

    orig_vert = img["vertices"]
    new_vert = {}
    for v in orig_vert.keys():
        x, y, z =  orig_vert[v]
        v_ = int(100*x), int(100*y), int(100*z)
        new_vert[v] = v_
    img["vertices"] = new_vert
    return img

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

  # object roations etc here

  # back face culling
  print "Back face culling..."
  obj = backFaceCull(obj, params)

  # move back object to negative z here

  # project to 2d in the right order
  print "Projecting to 2d..."
  img = project2D(obj, params)

  # scale up/down etc to fit in viewport here

  # dummy scale up to make stuff visible
  img = dummyScaleUp(img)

  # create svg from 2d image
  print "Creating svg image: {0}".format("output.svg")
  drawSvg(img, 'output.svg')

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
