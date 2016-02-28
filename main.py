"""
Create a 2d svg image from a 3d object.

User input:
  1. Viewpoint
  2. Input obj file
  3. Dimensions of viewport
  4. Rotations about each axes

Output:
  1. svg file

Assumptions:
  1. Only backface culling
"""

import optparse
from math import radians, cos, sin

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
        # ignore comments in obj file
        if line.strip(' ')[0] == '#':
            continue
        # ignore '\r'
        if line.strip(' ')[0] == '\r':
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
            print "Illegal condition: Unrecogonized line found"
            exit(1)

    return obj

def findBoundingCube(vertices):
    """ Return max and min x, y, z of object in that order.
    """

    # init all to first vertex found
    max_x, min_x = vertices[1][0], vertices[1][0]
    max_y, min_y = vertices[1][1], vertices[1][1]
    max_z, min_z = vertices[1][2], vertices[1][2]

    for v in vertices.keys():
        x, y, z = vertices[v]

        if x > max_x:
            max_x = x
        if x < min_x:
            min_x = x

        if y > max_y:
            max_y = y
        if y < min_y:
            min_y = y

        if z > max_z:
            max_z = z
        if z < min_z:
            min_z = z

    return max_x, min_x, max_y, min_y, max_z, min_z

def rotateAboutX(vertices, degree):
    """ Rotate vertices about x axis by degree in anti-clockwise direction. """
    angle = radians(degree)
    ca, sa = cos(angle), sin(angle)

    for v in vertices.keys():
        x, y, z = vertices[v]
        vertices[v] = x, ca*y - sa*z, sa*y + ca*z

    return vertices

def rotateAboutY(vertices, degree):
    """ Rotate vertices about y axis by degree in anti-clockwise direction. """
    angle = radians(degree)
    ca, sa = cos(angle), sin(angle)

    for v in vertices.keys():
        x, y, z = vertices[v]
        vertices[v] = ca*x + sa*z, y, -1*sa*x + ca*z

    return vertices

def rotateAboutZ(vertices, degree):
    """ Rotate vertices about z axis by degree in anti-clockwise direction. """
    angle = radians(degree)
    ca, sa = cos(angle), sin(angle)

    for v in vertices.keys():
        x, y, z = vertices[v]
        vertices[v] = ca*x - sa*y, sa*x + ca*y, z

    return vertices

def rotateObject(obj, params):
    """ Rotate object around center of bounding cube in all 3 axis as necessary.

    Returns new obj hash.
    """
    vertices = obj["vertices"]

    # find bounding cube
    max_x, min_x, max_y, min_y, max_z, min_z = findBoundingCube(vertices)

    # find center of said cube
    cx, cy, cz = (max_x + min_x)/2, (max_y + min_y)/2, (max_z + min_z)/2

    # translate object such that center is at 0,0,0
    vertices = translateVertices(vertices, -1*cx, -1*cy, -1*cz)

    # rotate about 3 axis one by one
    vertices = rotateAboutX(vertices, params["rx"])
    vertices = rotateAboutY(vertices, params["ry"])
    vertices = rotateAboutZ(vertices, params["rz"])

    # translate final object back to actual center
    vertices = translateVertices(vertices, cx, cy, cz)

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

def drawSvg(img, filename, w, h):
    """ Draw svg image from img structure.

    img -- struct of image data
    filename -- output file name
    w -- width of svg
    h -- height of svg

    Creates a svg file called -- filename.svg containing required image.
    """
    vertices = img["vertices"]

    f = open(filename, 'w')
    f.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.1">')
    f.write('\n')

    # draw border around svg
    f.write('<rect x="0" y="0" width="{0}" height="{1}" style="fill:white;stroke:black;stroke-width:1"/>\n'.format(w, h))

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

def moveBackInZ(obj, params):
    """ Move back entire object and view point to ensure ebject is in negative z.

    Return new (obj, params).
    """

    # loop over vertices and find the max z 
    max_z = 0
    for v in obj["vertices"].values():
        x_, y_, z_ = v
        if z_ > max_z:
            max_z = z_

    if max_z == 0:
        # no transformation necessary
        return (obj, params)
    else:
        # move vertices and viewpoint
        for k in obj["vertices"].keys():
            x_, y_, z_ = obj["vertices"][k]
            obj["vertices"][k] = (x_, y_, z_ - (max_z+1))

        params["vz"] -= max_z+1

        # sanity check new viewpoint
        if params["vz"] <= 0:
            print "View point in negative (or 0) z after z adjustment for viewing."
            exit(1)
        return (obj, params)

def translateVertices(vertices, x, y, z = 0):
    """ Translate vertices by x, y.

    Add x,y to each vertex.
    """
    for v in vertices.keys():
        x_, y_, z_ = vertices[v]
        vertices[v] = (x_ + x, y_ + y, z_ + z)

    return vertices

def negateY(vertices):
    """ Negate vertices y coordinate.

    As svg as a southeast facing coordinate system.
    """
    for v in vertices.keys():
        x_, y_, z_ = vertices[v]
        vertices[v] = (x_, -1*y_, z_)

    return vertices

def scaleVertices(vertices, sx, sy):
    """ Scale by given dimensions.

    Simply multiply all corrdinates by given scale factor.
    """
    for v in vertices.keys():
        x_, y_, z_ = vertices[v]
        vertices[v] = (x_*sx, y_*sy, z_)

    return vertices

def fitInViewPort(img, params):
    """ Fit image to view port.

    Move northwest most point to 0, 0
    Flip y to -y.
    Scale by max of (vh-2/bottom_y ,vw-2/right_x) -- preserve shape
    Translate by +1,+1
    """

    # assuming there is atleast one vertice
    left_x, right_x = img["vertices"][1][0], img["vertices"][1][0]
    top_y, bottom_y = img["vertices"][1][1], img["vertices"][1][1]

    for v in img["vertices"].values():
        x, y, _ = v

        if x < left_x:
            left_x = x
        if x > right_x:
            right_x = x

        if y < bottom_y:
            bottom_y = y
        if y > top_y:
            top_y = y

    vertices = img["vertices"]

    # move northwest most point to (0, 0)
    vertices = translateVertices(vertices, -1*left_x, -1*top_y)

    # negate y
    vertices = negateY(vertices)

    # scale to min of height/width
    l = min(params["W"], params["H"])

    # scale to fit in viewport
    if right_x == left_x:
        scale_x = 1
    else:
        scale_x = (l - 20)/(right_x - left_x)
    if bottom_y == top_y:
        scale_y = 1
    else:
        scale_y = (l - 20)/(-1*(bottom_y - top_y))


    vertices = scaleVertices(vertices, scale_x, scale_y)

    # translate to 10, 10
    vertices = translateVertices(vertices, 10, 10)

    # return new image
    img["vertices"] = vertices
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
  obj = rotateObject(obj, params)

  # back face culling
  print "Back face culling..."
  obj = backFaceCull(obj, params)

  # move back object to negative z here
  print "Adjusting z, moving object to object space..."
  obj, params = moveBackInZ(obj, params)

  # project to 2d in the right order
  print "Projecting to 2d..."
  img = project2D(obj, params)

  # scale up/down etc to fit in viewport here
  print "Scaling to viewport..."
  img = fitInViewPort(img, params)

  # create svg from 2d image
  print "Creating svg image: {0}".format(params["outfile"])
  drawSvg(img, params["outfile"], params["W"], params["H"])

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

  parser.add_option("-i", "--rx", type="int", dest="rx", default="0", help="rotation about x axis in degrees in anticlockwise direction")
  parser.add_option("-j", "--ry", type="int", dest="ry", default="0", help="rotation about y axis in degrees in anticlockwise direction")
  parser.add_option("-k", "--rz", type="int", dest="rz", default="0", help="rotation about z axis in degrees in anticlockwise direction")

  parser.add_option("-o", "--output", type="string", dest="outfile", default="output.svg", help="name of file to ouput svg drawing to")

  (options, args) = parser.parse_args()

  if len(args) != 1:
    parser.error("incorrect number of arguments")

  params = {}
  params['vx'] = options.vx
  params['vy'] = options.vy
  params['vz'] = options.vz
  params['H'] = options.vh
  params['W'] = options.vw

  params['rx'] = options.rx
  params['ry'] = options.ry
  params['rz'] = options.rz

  params['outfile'] = options.outfile

  print "Using values: "
  print params

  # pass on to main worker
  convertToImage(params, args[0])

if __name__ == "__main__":
  main()
