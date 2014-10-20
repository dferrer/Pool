from __future__ import division
from SimpleCV import *
from cluster import HierarchicalClustering
def getTableConvexHull(img):
    blue = img.colorDistance(Color.BLUE)
    s = img - blue
    blobs = s.findBlobs()
    table = blobs[-1]
    return table.mConvexHull
    
def length (segment):
    return ((segment[0][0] - segment[1][0])**2 + (segment[0][1] - segment[1][1])**2)**(1/2)

def getIntersections(segments):
    intersections = []
    for [[x1, y1], [x2, y2]] in segments[:6]:
        for [[x3, y3], [x4, y4]] in segments[:6]:
            if([x1, y1] != [x3, y3] and [x2, y2] != [x4, y4] and x1 != x2 and x4 != x3):
                m1 = (y2 - y1) / (x2 - x1)    
                m2 = (y4 - y3) / (x4 - x3)    

                b1 = y1 - m1*x1
                b2 = y3 - m2*x3

                if m1 != m2:
                    xi = int((b2 - b1) / (m1 - m2))
                    yi = int(m1 * xi + b1)
                    if(0 <= xi and 0 <= yi and xi < hImage.width and yi < hImage.height):
                        intersections.append([xi, yi])
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
    return sorted(corners, key=lambda p: p[0] + p[1])

def drawLines(segments):
    for segment in segments:
        l = Line(hImage, (segment[0], segment[1]))
        l.draw(width=3)

def drawPoints(points):
    for point in points:
        l = Circle(hImage, point[0], point[1], 3)
        l.draw(color=(255, 0, 0), width=3)

def toTableCoords(points):
    return map(lambda p: [p[0]-points[1][0], p[1]-points[0][1]], points)

def asTuple(pointList):
    return tuple(map(tuple, pointList))

def cropAndPerspectiveTransform(corners, img):
    table = img.crop(corners[1][0], corners[0][1],
                     corners[3][0]-corners[1][0],
                     corners[3][1] - corners[0][1])
    corners = toTableCoords(corners)
    maxX = corners[3][0]
    maxY = max(corners[1][1], corners[3][1])
    dst = ((0, 0), (0, maxY), (maxX, 0), (maxX, maxY))
    print dst, asTuple(corners)
    result = cv.CreateMat(3, 3, cv.CV_32FC1)
    cv.GetPerspectiveTransform(asTuple(corners), dst, result)
    return table.transformPerspective(result)

img = Image('table.png')
hImage = img * 0 

hull = getTableConvexHull(img)
segments = [p for p in zip(hull, hull[1:] + [hull[-1]])]
segments = sorted(segments, reverse=True, key = length)

intersections = getIntersections(segments)

corners = getCorners(intersections)

table = cropAndPerspectiveTransform(corners, img)

corners = toTableCoords(corners)
table.save("cropped.png")

drawLines(segments)
drawPoints(corners)

hImage.save("hull.png")
