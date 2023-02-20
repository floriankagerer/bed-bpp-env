#!/usr/bin/env python
#
# Copyright 2012 Johannes 'josch' Schauer <j.schauer@email.de>
#
# This file is part of Sisyphus.
#
# Sisyphus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sisyphus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sisyphus.  If not, see <http://www.gnu.org/licenses/>.

import os

class Scene:
    def __init__(self, name, size):
        self.name = name
        self.items = []
        self.size = size

    def add(self, item):
        self.items.append(item)

    def svgstr(self):
        svgstr  = "<?xml version=\"1.0\"?>\n"
        svgstr += "<svg width=\"%d\" height=\"%d\" xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\">\n"%self.size
        svgstr += " <g style=\"fill-opacity:1.0; stroke:black; stroke-width:1;\">\n"
        for item in self.items:
            svgstr += item.svgstr()
        svgstr += " </g>\n</svg>\n"
        return svgstr

    def write(self, filename=None):
        if not filename:
            filename = self.name + ".svg"
        with open(filename, "w") as f:
            f.write(self.svgstr())

class Rectangle:
    def __init__(self, pos, size, color):
        self.pos = pos
        self.size = size
        self.color = color

    def svgstr(self):
        svgstr  = "  <rect x=\"%d\" y=\"%d\" "%self.pos
        svgstr += "width=\"%d\" height=\"%d\" "%self.size
        svgstr += "style=\"fill:#%02x%02x%02x;\"/>\n"%self.color
        return svgstr

if __name__ == "__main__":
    scene = Scene('test', (400, 400))
    scene.add(Rectangle((0,0),(100,100),(255,0,0)))
    scene.write()
