#!/usr/bin/env python
import math
import numpy as np
import open3d as o3d
import open3d.visualization as vis
import os
import random
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import open3d_tutorial as o3dtut

def normalize(v):
    a = 1.0 / math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (a * v[0], a * v[1], a * v[2])

def make_point_cloud(npts, center, radius, colorize):
    pts = np.random.uniform(-radius, radius, size=[npts, 3]) + center
    cloud = o3d.geometry.PointCloud()
    cloud.points = o3d.utility.Vector3dVector(pts)
    if colorize:
        colors = np.random.uniform(0.0, 1.0, size=[npts, 3])
        cloud.colors = o3d.utility.Vector3dVector(colors)
    return cloud

def nothing():
    # Empty white window
    vis.draw()

def single_object():
    # No colors, no normals, should appear unlit black
    cube = o3d.geometry.TriangleMesh.create_box(1, 2, 4)
    vis.draw(cube)

def multi_objects():
    pc_rad = 1.0
    pc_nocolor = make_point_cloud(100, (0, -2, 0), pc_rad, False)
    pc_color = make_point_cloud(100, (3, -2, 0), pc_rad, True)
    r = 0.4
    sphere_unlit = o3d.geometry.TriangleMesh.create_sphere(r)
    sphere_unlit.translate((0, 1, 0))
    sphere_colored_unlit = o3d.geometry.TriangleMesh.create_sphere(r)
    sphere_colored_unlit.paint_uniform_color((1.0, 0.0, 0.0))
    sphere_colored_unlit.translate((2, 1, 0))
    sphere_lit = o3d.geometry.TriangleMesh.create_sphere(r)
    sphere_lit.compute_vertex_normals()
    sphere_lit.translate((4, 1, 0))
    sphere_colored_lit = o3d.geometry.TriangleMesh.create_sphere(r)
    sphere_colored_lit.compute_vertex_normals()
    sphere_colored_lit.paint_uniform_color((0.0, 1.0, 0.0))
    sphere_colored_lit.translate((6, 1, 0))
    big_bbox = o3d.geometry.AxisAlignedBoundingBox((-pc_rad, -3, -pc_rad),
                                                   (6.0 + r, 1.0 + r, pc_rad))
    sphere_bbox = sphere_unlit.get_axis_aligned_bounding_box()
    sphere_bbox.color = (1.0, 0.5, 0.0)
    lines = o3d.geometry.LineSet.create_from_axis_aligned_bounding_box(sphere_lit.get_axis_aligned_bounding_box())
    lines_colored = o3d.geometry.LineSet.create_from_axis_aligned_bounding_box(sphere_colored_lit.get_axis_aligned_bounding_box())
    lines_colored.paint_uniform_color((0.0, 0.0, 1.0))

    vis.draw([pc_nocolor, pc_color, sphere_unlit, sphere_colored_unlit,
              sphere_lit, sphere_colored_lit, big_bbox, sphere_bbox,
              lines, lines_colored])

def actions_layout():
    pc = make_point_cloud(200, (0, 0, 0), 1, True)
    actions = []
    for a in ["Supercalifragilisticexpialidocious", "Action 1", "Action 2",
              "Action 3"]:
        def make_callback(name):
            def on_action(drawvis):
                print('Trigged action "' + name + '"')
            return on_action
        actions.append((a, make_callback(a)))
    vis.draw([pc], actions=actions, menu_actions=actions)

def actions():
    SOURCE_NAME = "Source"
    RESULT_NAME = "Result (Poisson reconstruction)"
    TRUTH_NAME = "Ground truth"
    bunny = o3dtut.get_bunny_mesh()
    bunny.paint_uniform_color((1, 0.75, 0))
    bunny.compute_vertex_normals()
    cloud = o3d.geometry.PointCloud()
    cloud.points = bunny.vertices
    cloud.normals = bunny.vertex_normals

    def make_mesh(drawvis):
        mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(cloud)
        mesh.paint_uniform_color((1, 1, 1))
        mesh.compute_vertex_normals()
        drawvis.add_geometry({"name": RESULT_NAME, "geometry": mesh })
        drawvis.show_geometry(SOURCE_NAME, False)

    def toggle_result(drawvis):
        truth_vis = drawvis.get_geometry(TRUTH_NAME).is_visible
        drawvis.show_geometry(TRUTH_NAME, not truth_vis)
        drawvis.show_geometry(RESULT_NAME, truth_vis)

    vis.draw([{ "name": SOURCE_NAME, "geometry": cloud },
              { "name": TRUTH_NAME, "geometry": bunny, "is_visible": False }],
             actions=[("Create Mesh", make_mesh),
                      ("Toggle truth/result", toggle_result)])

def time_animation():
    orig = make_point_cloud(200, (0, 0, 0), 1.0, True)
    clouds = [{"name": "t=0", "geometry": orig, "time": 0}]
    drift_dir = (1.0, 0.0, 0.0)
    expand = 1.0
    n = 20
    for i in range(1, n):
        amount = float(i) / float(n - 1)
        cloud = o3d.geometry.PointCloud()
        pts = np.asarray(orig.points)
        pts = pts * (1.0 + amount * expand) + [amount*v for v in drift_dir]
        cloud.points = o3d.utility.Vector3dVector(pts)
        cloud.colors = orig.colors
        clouds.append({"name": "t=" + str(i), "geometry": cloud, "time": i})

    vis.draw(clouds)

def groups():
    building_mat = vis.rendering.Material()
    building_mat.shader = "defaultLit"
    building_mat.base_color = (1.0, .90, .75, 1.0)
    building_mat.base_reflectance = 0.1
    midrise_mat = vis.rendering.Material()
    midrise_mat.shader = "defaultLit"
    midrise_mat.base_color = (.475, .450, .425, 1.0)
    midrise_mat.base_reflectance = 0.1
    skyscraper_mat = vis.rendering.Material()
    skyscraper_mat.shader = "defaultLit"
    skyscraper_mat.base_color = (.05, .20, .55, 1.0)
    skyscraper_mat.base_reflectance = 0.9
    skyscraper_mat.base_roughness = 0.01

    buildings = []
    size = 10.0
    half = size / 2.0
    min_height = 1.0
    max_height = 20.0
    for z in range(0, 10):
        for x in range(0, 10):
            max_h = max_height * (1.0 - abs(half - x) / half) * (1.0 - abs(half - z) / half)
            h = random.uniform(min_height, max(max_h, min_height + 1.0))
            box = o3d.geometry.TriangleMesh.create_box(0.9, h, 0.9)
            box.compute_triangle_normals()
            box.translate((x + 0.05, 0.0, z + 0.05))
            if h > 0.333 * max_height:
                mat = skyscraper_mat
            elif h > 0.1 * max_height:
                mat = midrise_mat
            else:
                mat = building_mat
            buildings.append({ "name": "building_" + str(x) + "_" + str(z),
                               "geometry": box,
                               "material": mat,
                               "group": "buildings" })

    haze = make_point_cloud(5000, (half, 0.333 * max_height, half),
                            1.414 * half, False)
    haze.paint_uniform_color((0.8, 0.8, 0.8))

    smog = make_point_cloud(10000, (half, 0.25 * max_height, half),
                            1.2 * half, False)
    smog.paint_uniform_color((0.95, 0.85, 0.75))

    vis.draw(buildings + [
             { "name": "haze", "geometry": haze, "group": "haze" },
             { "name": "smog", "geometry": smog, "group": "smog" } ])

def remove():
    def make_sphere(name, center, color, group, time):
        sphere = o3d.geometry.TriangleMesh.create_sphere(0.5)
        sphere.compute_vertex_normals()
        sphere.translate(center)

        mat = vis.rendering.Material()
        mat.shader = "defaultLit"
        mat.base_color = color

        return { "name": name,
                 "geometry": sphere,
                 "material": mat,
                 "group": group,
                 "time": time }

    red = make_sphere("red", (0, 0, 0), (1.0, 0.0, 0.0, 1.0), "spheres", 0)
    green = make_sphere("green", (2, 0, 0), (0.0, 1.0, 0.0, 1.0), "spheres", 0)
    blue = make_sphere("blue", (4, 0, 0), (0.0, 0.0, 1.0, 1.0), "spheres", 0)
    yellow = make_sphere("yellow", (0, 0, 0), (1.0, 1.0, 0.0, 1.0), "spheres", 1)
    bbox = { "name": "bbox",
             "geometry": red["geometry"].get_axis_aligned_bounding_box() }

    def remove_green(visdraw):
        visdraw.remove_geometry("green")

    def remove_yellow(visdraw):
        visdraw.remove_geometry("yellow")

    def remove_bbox(visdraw):
        visdraw.remove_geometry("bbox")

    vis.draw([red, green, blue, yellow, bbox], 
             actions=[("Remove Green", remove_green),
                      ("Remove Yellow", remove_yellow),
                      ("Remove Bounds", remove_bbox)])

def main():
    nothing()
    single_object()
    multi_objects()
    # actions_layout()
    actions()
    time_animation()
    groups()
    # remove()

if __name__ == "__main__":
    main()