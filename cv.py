from __future__ import division
from SimpleCV import *
from cluster import HierarchicalClustering

def getTableConvexHull(img):
    blue = img.colorDistance(Color.BLUE)
    s = img - blue
    blobs = s.findBlobs()
    table = blobs[-1]
    hull = table.mConvexHull
    return sorted([p for p in zip(hull, hull[1:] + [hull[-1]])],
                  reverse=True, key = length)
    
    
def length (segment):
    return ((segment[0][0] - segment[1][0])**2 + (segment[0][1] - segment[1][1])**2)**(1/2)

def asTuple(pointList):
    return tuple(map(tuple, pointList))

def getIntersection((x1, y1), (x2, y2), (x3, y3), (x4, y4), width, height):
    if([x1, y1] != [x3, y3] and [x2, y2] != [x4, y4] and x1 != x2 and x4 != x3):
        m1 = (y2 - y1) / (x2 - x1)    
        m2 = (y4 - y3) / (x4 - x3)    
        
        b1 = y1 - m1*x1
        b2 = y3 - m2*x3
        
        if m1 != m2:
            xi = int((b2 - b1) / (m1 - m2))
            yi = int(m1 * xi + b1)
            if(0 <= xi and 0 <= yi and xi < width and yi < height):
                return [xi, yi]
                        
def getIntersections(segments, width, height):
    intersections = []
    for [p1, p2] in segments[:8]:
        for [p3, p4] in segments[:8]:
            i = getIntersection(p1, p2, p3, p4, width, height)
            if(i):
                intersections.append(i)
    return intersections


def averageCoords(coordList):
    xl = map(lambda c: c[0], coordList)
    yl = map(lambda c: c[1], coordList)
    x = int(sum(xl)/len(xl))
    y = int(sum(yl)/len(yl))
    return [x, y]

def getCorners(intersections):
    cl = HierarchicalClustering(intersections, lambda p1, p2: length([p1, p2]))
    clusters = cl.getlevel(25)

    # probably want to make sure we actually have the corners at this point.
    # For now, I'm taking the 4 biggest clusters.
    cornerClusters = sorted(clusters, key=len, reverse=True)[:4]

    corners = map(averageCoords, cornerClusters)
    corners = sorted(corners, key= lambda p: p[0])
    left = sorted(corners[:2], key=lambda p: p[1])
    right = sorted(corners[2:], key=lambda p: p[1])
    #{'top-left': left[0], 'bottom-left': left[1],
    # 'top-right': right[0], 'bottom-right': right[1]}
    return left[0], left[1], right[0], right[1]

def drawLines(segments, img):
    for segment in segments:
        l = Line(img, (segment[0], segment[1]))
        l.draw(width=3)

def drawPoints(points, img):
    for point in points:
        l = Circle(img, point[0], point[1], 3)
        l.draw(color=(255, 0, 0), width=3)

def toTableCoords(points):
    return map(lambda p: [p[0]-points[1][0], p[1]-points[0][1]], points)

def validCorners(corners):
    tCorners = toTableCoords(corners)
    minC = min(sum(tCorners, []))
    if(minC < 0):
        print "Error! Invalid coordinate."
        print corners, tCorners
        return False
    #lrRatio = (tCorners[0][0] - tCorners[1][0]) / (tCorners[2][0] - tCorners[3][0]) 
    #tbRatio = (tCorners[0][1] - tCorners[2][1]) / (tCorners[1][1] - tCorners[3][1]) 
    aspectRatio = corners[3][0]/corners[3][1]
    if abs(aspectRatio - 1.8) > .4:
        print "Error! Bad aspect ratio."
        print corners, tCorners
        return False
    return True

def cropAndPerspectiveTransform(corners, img):
    tCorners = toTableCoords(corners)
    maxX = tCorners[3][0]
    maxY = max(tCorners[1][1], tCorners[3][1])
    minC = min(sum(tCorners, []))
    if(minC < 0):
        print "Error! Invalid coordinate :("
    else:
        table = img.crop(corners[1][0], corners[0][1],
                         corners[3][0]-corners[1][0],
                         corners[3][1] - corners[0][1])
        dst = ((0, 0), (0, maxY), (maxX, 0), (maxX, maxY))
        result = cv.CreateMat(3, 3, cv.CV_32FC1)
        cv.GetPerspectiveTransform(asTuple(tCorners), dst, result)
        return table.transformPerspective(result)

def makeTransformed(index):
    print "Processing table " + str(index) + "."
    
    img = Image("img/table" + str(index) + ".png")
    hImage = img * 0 
    
    segments = getTableConvexHull(img)
    
    intersections = getIntersections(segments, img.width, img.height)
    
    corners = getCorners(intersections)
    
    drawLines(segments[:10], hImage)
    drawPoints(corners, hImage)
    #drawPoints(intersections[:10], hImage)
    
    table = cropAndPerspectiveTransform(corners, img)
    if(table and validCorners(corners)):
        table.save("out/cropped" + str(index) + ".png")
        hImage.save("out/hull" + str(index) + ".png")

    print "\n-------------\n"

for x in range(0, 10):
    makeTransformed(x)
