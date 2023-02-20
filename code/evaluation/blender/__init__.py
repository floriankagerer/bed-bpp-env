'''
This package contains a script that generates a scene in Blender that can be used for a stability evaluation.
'''
import pathlib

TEMPLATEFILE = pathlib.Path(__file__).parent.resolve().joinpath("template.blend")
'''The template blender file that is used for the stability evaluation.'''
