#LIBRERIAS
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import math
from pyglet import clock

import sys, os
import numpy as np
root = os.path.dirname(os.path.abspath(__file__))

#MODULOS (cuidado con las rutas)
sys.path.append(root)
from utils.helpers import init_axis, mesh_from_file
from utils.camera import FreeCamera, OrbitCamera
from utils.scene_graph import SceneGraph
from utils import shapes
from utils.drawables import Texture, Model, Material, PointLight, DirectionalLight
from utils.colliders import Sphere as SphereCollider, CollisionManager

class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0
        self.light_mode = False
        self.show_reflection = False
        self.camera_mode = "free"

class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.array([0, 0, 0])
        self.speed = 20

    def time_update(self, dt):
        self.update()
        dir = self.direction[0] * self.forward + self.direction[1] * self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm
        self.position += dir * self.speed * dt
        self.focus = self.position + self.forward

class Body:
    def __init__(self, name, position, mass, radius, soi_radius, velocity=None, accel=None):
        self.name = name
        self.position = np.array(position, dtype=float) 
        self.velocity = np.array(velocity, dtype=float) if velocity is not None else np.array([0, 0])
        self.accel = np.array(accel, dtype=float) if accel is not None else np.array([0, 0])
        self.mass = mass
        self.radius = radius
        self.soi_radius = soi_radius


class Ship:
    def __init__(self, position, velocity, radius=0.1, accel = None):
        self.position = np.array(position, dtype= float) 
        self.velocity = np.array(velocity, dtype=float)
        self.accel = np.array(accel, dtype = float) if accel is not None else np.array([0,0])
        self.angle = 0.0
        self.alive = True
        self.radius = radius


G = 1.0
thrust_power = 8.0
time_scale = 1 # multiplicador de velocidad del tiempo


def g_accel(pos, body): 
    r = body.position - pos
    r_mag = max(np.linalg.norm(r), 0.05)
    a = G * body.mass / (r_mag ** 2)
    return (r / r_mag) * a


if __name__ == "__main__":

    controller = Controller(1000, 1000, "Tarea3 - Felipe Cabezas")
    controller.set_exclusive_mouse(True)

    with open(root + "/shaders/color_mesh_lit.vert") as f:
        vert_source = f.read()

    with open(root + "/shaders/color_mesh_lit.frag") as f:
        frag_source = f.read()

    pipeline = ShaderProgram(Shader(vert_source, "vertex"), Shader(frag_source, "fragment"))

    line_vert_source = """
    #version 330
    in vec3 position;
    uniform mat4 u_model = mat4(1.0);
    uniform mat4 u_view = mat4(1.0);
    uniform mat4 u_projection = mat4(1.0);
    void main() {
        gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
    }
    """
    line_frag_source = """
    #version 330
    out vec4 outColor;
    void main() {
        outColor = vec4(0.6, 0.6, 0.6, 0.3);
    }
    """

    sun_vert_source = """
    #version 330

    in vec3 position;

    uniform mat4 u_model = mat4(1.0);
    uniform mat4 u_view = mat4(1.0);
    uniform mat4 u_projection = mat4(1.0);

    void main() {
        gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
    }
    """
    sun_frag_source = """
    #version 330

    out vec4 outColor;

    void main() {
        outColor = vec4(1.0, 0.85, 0.3, 1.0);
    }
    """

    line_pipeline = ShaderProgram(Shader(line_vert_source, "vertex"), Shader(line_frag_source, "fragment"))

    sun_pipeline = ShaderProgram(Shader(sun_vert_source, "vertex"), Shader(sun_frag_source, "fragment"))

    cam = MyCam([0, 20, 22])
    cam.resize(1000, 1000)
    cam.pitch = -0.7
    cam.update()

    orbit_cam = OrbitCamera(25)
    orbit_cam.resize(1000, 1000)
    orbit_cam.phi = 0.0
    orbit_cam.theta = np.pi / 4   

    world = SceneGraph(cam)

    sun = Body("sun", [0, 0], mass=5000, radius=5, soi_radius=9999, velocity=[0, 0])

    def orbital_vel(radius, body):
        return np.sqrt(G * body.mass / radius)

    r1 = 60.0
    v1 = orbital_vel(r1, sun) 
    planet1 = Body("planet1", [r1, 0], mass=400, radius=1.2, soi_radius=15, 
                        velocity=[0, v1])

    r2 = 120.0
    v2 = orbital_vel(r2, sun)
    planet2 = Body("planet2", [r2, 0], mass=600, radius=1.5, soi_radius=25, 
                        velocity=[0, v2])

    r3 = 200.0
    v3 = orbital_vel(r3, sun)
    planet3 = Body("planet3", [r3, 0], mass=1500, radius=2.5, soi_radius=60, 
                        velocity=[0, -v3])

    bodies = [sun, planet1, planet2, planet3]
    for b in bodies[1:]:
        b.accel = g_accel(b.position, sun)

    last_dom = sun

    def get_dom(pos, bod = bodies):
        global last_dom

        blist = [b for b in bod if np.linalg.norm(pos - b.position) < b.soi_radius]

        if not blist:
            last_dom = bod[0]
            return bod[0]

        new_dom = min(blist, key=lambda b: b.soi_radius)

        if last_dom in blist and new_dom != last_dom:
            new_dist = np.linalg.norm(pos - new_dom.position)
            old_dist = np.linalg.norm(pos - last_dom.position)
            if old_dist < new_dist:
                return last_dom

        last_dom = new_dom
        return new_dom

    rship = 80
    vship = orbital_vel(rship, sun)
    ship = Ship(position=[rship, 10], velocity=[3, vship])

    collisions = CollisionManager()
    collisions.add_collider(SphereCollider("ship", ship.radius))
    for b in bodies:
        collisions.add_collider(SphereCollider(b.name, b.radius))

    collisions.set_position("ship", [ship.position[0], 0, ship.position[1]])
    for b in bodies:
        collisions.set_position(b.name, [b.position[0], 0, b.position[1]])


    sphere_list = mesh_from_file(os.path.join(root, "assets", "sphere.obj"))[0]
    sphere = sphere_list["mesh"]
    cow = mesh_from_file(os.path.join(root, "assets", "cow.obj"))[0]["mesh"]


    world.add_node("sun",
                   mesh=sphere, 
                   pipeline=sun_pipeline,
                   position=[sun.position[0], 0, sun.position[1]],
                   #material=Material(ambient = [1, 1, 1],
                   #                  diffuse = [1, 1, 1],
                   #                  specular = [0.5, 0.5, 0.5]),
                   scale=[sun.radius, sun.radius, sun.radius])

    world.add_node("sun_light",
                   pipeline=pipeline,
                   light=PointLight(ambient=[0.5, 0.5, 0.5], 
                                    diffuse=[1, 1, 1],
                                    specular=[1, 1, 1],
                                    constant=1,
                                    linear=0.00001,
                                    quadratic=0.00001), 
                   position=[sun.position[0], 0, sun.position[1]])

    world.add_node("planet1",
                    mesh=sphere, pipeline=pipeline,
                    position=[planet1.position[0], 0, planet1.position[1]],
                    scale=[planet1.radius, planet1.radius, planet1.radius],
                    material=Material(ambient=[0.3, 0.5, 1], 
                                      diffuse=[0.3, 0.5, 1], 
                                      specular=[0.5, 0.5, 0.5]))

    world.add_node("planet2",
                   mesh=sphere, 
                   pipeline=pipeline,
                   position=[planet2.position[0], 0, planet2.position[1]],
                   scale=[planet2.radius, planet2.radius, planet2.radius],
                   material=Material(ambient=[0.8, 0.3, 0.3], 
                                     diffuse=[0.8, 0.3, 0.3], 
                                     specular=[0.5, 0.5, 0.5]))

    world.add_node("planet3",
                   mesh=sphere, 
                   pipeline=pipeline,
                   position=[planet3.position[0], 0, planet3.position[1]],
                   scale=[planet3.radius, planet3.radius, planet3.radius],
                   material=Material(ambient=[0.2, 0.9, 0.2], 
                                     diffuse=[0.2, 0.9, 0.2], 
                                     specular=[0.2, 0.2, 0.2]))

    world.add_node("ship",
                    mesh=cow, pipeline=pipeline,
                    position=[ship.position[0], 0, ship.position[1]],
                    scale=[0.3, 0.3, 0.3],
                    material=Material(ambient=[0.2, 1, 0.2], 
                                      diffuse=[0, 1, 0], 
                                      specular=[1, 1, 1]))

    MAX_TRAIL_POINTS = 1200
    trail_points = []  # lista de [x, 0, z]
    trail_sample_counter = 0
    TRAIL_SAMPLE_EVERY = 1  # frames entre cada punto muestreado

    trail_init_vertices = np.zeros(MAX_TRAIL_POINTS * 3, dtype=np.float32)
    trail_mesh = Model(trail_init_vertices, mode=GL_LINE_STRIP)

    world.add_node("trail_node",
                    mesh=trail_mesh, pipeline=line_pipeline,
                    mode=GL_LINE_STRIP)

    thrust = 0

    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(0.02, 0.02, 0.05, 1.0)
        glEnable(GL_DEPTH_TEST)
        world.draw()

    @controller.event
    def on_key_press(symbol, modifiers):
        global thrust
        global time_scale
        global last_dom

        if symbol == key._1:
            controller.camera_mode = "free"
            world.camera = cam
            print("Camara libre")
        if symbol == key._2:
            controller.camera_mode = "ship"
            world.camera = orbit_cam
            orbit_cam.distance = 10
            orbit_cam.focus = np.array([0, 0, 0], dtype =np.float32)
            print("Siguiendo nave")
        if symbol == key._3:
            controller.camera_mode = "dom"
            world.camera = orbit_cam
            orbit_cam.distance = last_dom.radius + 5
            orbit_cam.focus = np.array([0, 0, 0], dtype =np.float32)
            print("Siguiendo cuerpo dominante")

        if symbol in (key.SPACE, key.UP):
            thrust = 1
        if symbol in (key.LSHIFT, key.DOWN):
            thrust = -1

        if symbol == key.Q: 
            time_scale = max(0.1, time_scale - 0.1)
        if symbol == key.E: 
            time_scale += 0.1

        if symbol == key.W:
            cam.direction[0] = 1
        if symbol == key.S:
            cam.direction[0] = -1
        if symbol == key.A:
            cam.direction[1] = 1
        if symbol == key.D:
            cam.direction[1] = -1

    @controller.event
    def on_key_release(symbol, modifiers):
        global thrust
        if symbol in (key.SPACE, key.UP):
            thrust = 0
        if symbol in (key.LSHIFT, key.DOWN):
            thrust = 0

        if symbol == key.W or symbol == key.S:
            cam.direction[0] = 0
        if symbol == key.A or symbol == key.D:
            cam.direction[1] = 0

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        if controller.camera_mode == "free":
            cam.yaw += dx * .001 
            cam.pitch += dy * .001
            cam.pitch = math.clamp(cam.pitch, -(np.pi / 2 - 0.01), np.pi / 2 - 0.01)
        else:
            orbit_cam.phi -= dx * 0.0025
            orbit_cam.theta += dy * 0.0025

    @controller.event
    def on_mouse_scroll(x, y, dx, dy):
        global last_dom
        if controller.camera_mode != "free":
            orbit_cam.distance = max(1, orbit_cam.distance - dy * 1)
        if controller.camera_mode == "dom":
            orbit_cam.distance = max(last_dom.radius + 1, orbit_cam.distance - dy * 1)


    def update(dt):
        global trail_sample_counter
        global last_dom

        if controller.camera_mode == "free":
            cam.time_update(dt)
        elif controller.camera_mode == "ship":
            if ship.alive:
                orbit_cam.position -= orbit_cam.focus
                orbit_cam.focus = np.array([ship.position[0], 0, ship.position[1]], dtype=np.float32)
                orbit_cam.update()
                orbit_cam.position += orbit_cam.focus

        elif controller.camera_mode == "dom":
            dom = last_dom
            orbit_cam.position -= orbit_cam.focus
            orbit_cam.focus = np.array([dom.position[0], 0, dom.position[1]], dtype=np.float32)
            orbit_cam.update()
            orbit_cam.position += orbit_cam.focus


        world.update()
        #cam.time_update(dt)
        controller.time += dt

        ndt = dt * time_scale

        for body in bodies[1:]:
            body.position = body.position + ndt * body.velocity + (ndt * ndt * body.accel)/2
            accel = g_accel(body.position, sun)
            body.velocity = body.velocity + (ndt/2) * (body.accel + accel)
            body.accel = accel
            
            world[body.name]["position"] = [body.position[0], 0, body.position[1]]
            
            collisions.set_position(body.name, [body.position[0], 0, body.position[1]])

        if ship.alive:

            dom = get_dom(ship.position, bodies)

            rel_vel = ship.velocity - dom.velocity
            rel_vel_mag = np.linalg.norm(rel_vel)

            if rel_vel_mag > 0.0001:
                ship.angle = np.arctan2(rel_vel[1], rel_vel[0])
                thrust_dir = rel_vel / rel_vel_mag
            else:
                thrust_dir = np.array([np.cos(ship.angle), np.sin(ship.angle)])

            ship.position = ship.position + ndt * ship.velocity + (ndt * ndt * ship.accel)/2

            thrust_accel = thrust_dir * thrust_power * thrust 
            gravity_accel = g_accel(ship.position, dom) 

            accel = gravity_accel + thrust_accel + dom.accel


            ship.velocity = ship.velocity + (ndt/2) * (accel + ship.accel)
            ship.accel = accel


            collisions.set_position("ship", [ship.position[0], 0, ship.position[1]])
            hits = collisions.check_collision("ship")
            if hits:
                ship.alive = False
                print(f"Colision con: {hits}")

            world["ship"]["position"] = [ship.position[0], 0, ship.position[1]]
            world["ship"]["rotation"] = [0, ship.angle * 2, 0]

            trail_sample_counter += 1
            if trail_sample_counter >= TRAIL_SAMPLE_EVERY:
                trail_sample_counter = 0

                abs_pos = np.array([ship.position[0], 0.0, ship.position[1]], dtype=np.float32)
                rel_pos = ship.position - dom.position
                trail_points.append({"rel_pos": rel_pos, "body": dom})

                if len(trail_points) > MAX_TRAIL_POINTS:
                    trail_points.pop(0)

                abs_trail = []
                for pt in trail_points:
                    abs_p = pt["rel_pos"] + pt["body"].position
                    abs_trail.append([abs_p[0], 0.0, abs_p[1]])

                flat = np.array(abs_trail, dtype=np.float32).flatten()
                if len(trail_points) < MAX_TRAIL_POINTS:
                    pad = np.tile(flat[:3], MAX_TRAIL_POINTS - len(trail_points))
                    flat = np.concatenate([pad, flat])

                world["trail_node"]["mesh"].gpu_data.position = flat

    clock.schedule_interval(update, 1 / 60)
    run()

