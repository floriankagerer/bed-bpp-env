"""
Module responsible for rigid world simulation in Blender.

Links:
- https://docs.blender.org/api/current/bpy.types.RigidBodyWorld.html#bpy.types.RigidBodyWorld
"""

import bpy  # type: ignore


def enable_rigid_body_world_simulation() -> None:
    """Enables evaluation of rigid body simulation environment."""
    bpy.context.scene.rigidbody_world.enabled = True

    # Collection containing objects participating in this simulation
    bpy.context.scene.rigidbody_world.collection = bpy.data.collections["Collection"]
