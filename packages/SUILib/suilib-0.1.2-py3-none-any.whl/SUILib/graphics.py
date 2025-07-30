"""
Wireframe 3D graphics utilities for SUILib

This module provides simple classes for representing and manipulating 3D wireframe
objects, including vertices, edges, and wireframes. It supports basic geometric
transformations (translation, scaling, rotation) and drawing with pygame.

Author: Martin Krcma <martin.krcma1@gmail.com>
Github: https://github.com/0xMartin
Date: 17.02.2022

Copyright (C) 2022 Martin Krcma

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import pygame
import math


class Vertex:
    """
    Represents a 3D point (vertex) in space.

    Provides methods for getting, setting, and rotating the vertex
    around X, Y, and Z axes.

    Attributes:
        x (float): X coordinate.
        y (float): Y coordinate.
        z (float): Z coordinate.
    """

    def __init__(self, coordinates: list):
        """
        Initialize a vertex with given coordinates.

        Args:
            coordinates (list): List or tuple of 3 floats [x, y, z].
        """
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.z = coordinates[2]

    def setX(self, x: float):
        """Set X coordinate."""
        self.x = x

    def setY(self, y: float):
        """Set Y coordinate."""
        self.y = y

    def setZ(self, z: float):
        """Set Z coordinate."""
        self.z = z

    def getX(self) -> float:
        """Get X coordinate."""
        return self.x

    def getY(self) -> float:
        """Get Y coordinate."""
        return self.y

    def getZ(self) -> float:
        """Get Z coordinate."""
        return self.z

    def rotateX(self, center, angle):
        """
        Rotate this vertex around the X axis.

        Args:
            center (Vertex): The center of rotation.
            angle (float): Angle in radians.
        """
        y = self.y - center.y
        z = self.z - center.z
        d = math.hypot(y, z)
        theta = math.atan2(y, z) + angle
        self.z = center.z + d * math.cos(theta)
        self.y = center.y + d * math.sin(theta)

    def rotateY(self, center, angle):
        """
        Rotate this vertex around the Y axis.

        Args:
            center (Vertex): The center of rotation.
            angle (float): Angle in radians.
        """
        x = self.x - center.x
        z = self.z - center.z
        d = math.hypot(x, z)
        theta = math.atan2(x, z) + angle
        self.z = center.z + d * math.cos(theta)
        self.x = center.x + d * math.sin(theta)

    def rotateZ(self, center, angle):
        """
        Rotate this vertex around the Z axis.

        Args:
            center (Vertex): The center of rotation.
            angle (float): Angle in radians.
        """
        x = self.x - center.x
        y = self.y - center.y
        d = math.hypot(y, x)
        theta = math.atan2(y, x) + angle
        self.x = center.x + d * math.cos(theta)
        self.y = center.y + d * math.sin(theta)


class Edge:
    """
    Represents an edge (line segment) connecting two vertices.

    Attributes:
        start (Vertex): Starting vertex.
        end (Vertex): Ending vertex.
    """

    def __init__(self, start: Vertex, end: Vertex):
        """
        Initialize an edge from start to end vertex.

        Args:
            start (Vertex): Starting vertex.
            end (Vertex): Ending vertex.
        """
        self.start = start
        self.end = end

    def setStart(self, start: Vertex):
        """Set start vertex."""
        self.start = start

    def setEnd(self, end: Vertex):
        """Set end vertex."""
        self.end = end

    def getStart(self) -> Vertex:
        """Get start vertex."""
        return self.start

    def getEnd(self) -> Vertex:
        """Get end vertex."""
        return self.end


class Wireframe:
    """
    Represents a 3D wireframe model.

    Provides methods to construct, transform, and draw wireframe objects.
    Supports adding vertices and edges, translation, scaling and rotation.

    Attributes:
        vertices (list): List of Vertex objects.
        edges (list): List of Edge objects.
        vertexColor (tuple): RGB color of vertices.
        edgeColor (tuple): RGB color of edges.
        vertexSize (int): Size of vertex circles in pixels.
    """

    def __init__(self):
        """
        Initialize an empty wireframe object.
        """
        self.vertices = []
        self.edges = []
        self.vertexColor = (255, 255, 255)
        self.edgeColor = (200, 200, 200)
        self.vertexSize = 3

    def setVertexColor(self, color):
        """
        Set the color used to render vertices.

        Args:
            color (tuple): RGB color.
        """
        self.vertexColor = color

    def setEdgeColor(self, color):
        """
        Set the color used to render edges.

        Args:
            color (tuple): RGB color.
        """
        self.edgeColor = color

    def getVertexCount(self) -> int:
        """
        Get the number of vertices in the wireframe.

        Returns:
            int: Number of vertices.
        """
        return len(self.vertices)

    def getEdgeCount(self) -> int:
        """
        Get the number of edges in the wireframe.

        Returns:
            int: Number of edges.
        """
        return len(self.edges)

    def addVertex(self, coordinates: list):
        """
        Add a single vertex to the wireframe.

        Args:
            coordinates (list): [x, y, z] coordinates.
        """
        self.vertices.append(Vertex(coordinates))

    def addVertices(self, vertexList: list):
        """
        Add multiple vertices.

        Args:
            vertexList (list): List of [x, y, z] coordinate lists.
        """
        for v in vertexList:
            self.vertices.append(Vertex(v))

    def addEdge(self, start_index: int, end_index: int):
        """
        Add an edge between two vertices by their indices.

        Args:
            start_index (int): Index of the start vertex.
            end_index (int): Index of the end vertex.
        """
        if start_index >= 0 and end_index >= 0 and start_index < len(self.vertices) and end_index < len(self.vertices):
            self.edges.append(
                Edge(self.vertices[start_index], self.vertices[end_index]))

    def addEdges(self, edgeList: list):
        """
        Add multiple edges.

        Args:
            edgeList (list): List of (start_index, end_index) tuples.
        """
        for (start, end) in edgeList:
            self.edges.append(Edge(self.vertices[start], self.vertices[end]))

    def draw(self, screen, offset, displayVertex=True, displayEdge=True):
        """
        Draw the wireframe on the given pygame Surface.

        Args:
            screen (pygame.Surface): Surface to draw on.
            offset (tuple): (x, y) offset for drawing.
            displayVertex (bool): Whether to draw vertices.
            displayEdge (bool): Whether to draw edges.
        """
        if displayEdge:
            for edge in self.edges:
                pygame.draw.line(
                    screen,
                    self.edgeColor,
                    (edge.start.x + offset[0], edge.start.y + offset[1]),
                    (edge.end.x + offset[0], edge.end.y + offset[1]),
                    2)
        if displayVertex:
            for vertex in self.vertices:
                pygame.draw.circle(
                    screen,
                    self.vertexColor,
                    (int(vertex.x + offset[0]), int(vertex.y + offset[1])),
                    self.vertexSize, 0)

    def translate(self, axis, d):
        """
        Translate (move) all vertices along a single axis.

        Args:
            axis (str): Axis to move ('x', 'y', or 'z').
            d (float): Distance to move.
        """
        if axis in ['x', 'y', 'z']:
            for vertex in self.vertices:
                setattr(vertex, axis, getattr(vertex, axis) + d)

    def scale(self, center, scale):
        """
        Scale the wireframe around a center point.

        Args:
            center (tuple): The (x, y, z) center point.
            scale (float): Scaling factor.
        """
        for vertex in self.vertices:
            vertex.x = center[0] + scale * (vertex.x - center[0])
            vertex.y = center[1] + scale * (vertex.y - center[1])
            vertex.z *= scale

    def computeCenter(self):
        """
        Compute the geometric center of the wireframe.

        Returns:
            tuple: (x, y, z) center position.
        """
        cnt = len(self.vertices)
        avg_x = sum([v.x for v in self.vertices]) / cnt
        avg_y = sum([v.y for v in self.vertices]) / cnt
        avg_z = sum([v.z for v in self.vertices]) / cnt
        return (avg_x, avg_y, avg_z)

    def rotateX(self, center, angle):
        """
        Rotate the wireframe around the X axis.

        Args:
            center (tuple): (x, y, z) center of rotation.
            angle (float): Angle in radians.
        """
        for vertex in self.vertices:
            y = vertex.y - center[1]
            z = vertex.z - center[2]
            d = math.hypot(y, z)
            theta = math.atan2(y, z) + angle
            vertex.z = center[2] + d * math.cos(theta)
            vertex.y = center[1] + d * math.sin(theta)

    def rotateY(self, center, angle):
        """
        Rotate the wireframe around the Y axis.

        Args:
            center (tuple): (x, y, z) center of rotation.
            angle (float): Angle in radians.
        """
        for vertex in self.vertices:
            x = vertex.x - center[0]
            z = vertex.z - center[2]
            d = math.hypot(x, z)
            theta = math.atan2(x, z) + angle
            vertex.z = center[2] + d * math.cos(theta)
            vertex.x = center[0] + d * math.sin(theta)

    def rotateZ(self, center, angle):
        """
        Rotate the wireframe around the Z axis.

        Args:
            center (tuple): (x, y, z) center of rotation.
            angle (float): Angle in radians.
        """
        for vertex in self.vertices:
            x = vertex.x - center[0]
            y = vertex.y - center[1]
            d = math.hypot(y, x)
            theta = math.atan2(y, x) + angle
            vertex.x = center[0] + d * math.cos(theta)
            vertex.y = center[1] + d * math.sin(theta)
