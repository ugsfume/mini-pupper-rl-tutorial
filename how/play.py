# SPDX-License-Identifier: Apache-2.0
"""Drive a Mini Pupper v4 walking policy in a MuJoCo window, on the processor (no NVIDIA card needed).

    .venv/bin/python play.py                                   # the released walker
    .venv/bin/python play.py --policy runs/exports/high   # one of your own
    .venv/bin/python play.py --simple                          # simple shapes, for slow computers

Keys:  up / down     walk faster forward / backward        6 / 7   walk to the left / right
       left / right  turn left / right                     Enter   stop and stand
       8             give the robot a shove                9       start again

One robot on a flat floor, without the random variations that training and evaluation add, so it's for looking at a
policy. Use the evaluation scripts to measure one. Walking policies for the SKU2 only.
"""
import argparse
import sys
import time
from pathlib import Path

import mujoco
import numpy as np
from mp4_sim import paths
from mp4_sim.actuators import bank, choice, fits
from mp4_sim.calibration import Contract
from mp4_sim.robot import model as robot_model

from mp4_rl.common import policy as P
from mp4_rl.common.policy_file import NumpyPolicy

CONTROL_DT = 0.02           # the policy decides 50 times a second
SUBSTEPS = 20               # and the physics takes 1 ms steps in between
DELAY_MS = 13               # the middle of the 8 to 19 ms that training draws from
MOTORS = {"abd": "md300_id_1_m6.json", "hip": "md300_id_2_m6.json", "knee": "md300_id_3_m6.json"}
LEGS = ("FR", "FL", "RR", "RL")


class Robot:
    """The simulated robot, its motors and the policy that drives it."""

    def __init__(self, policy_dir, simple=False):
        self.policy = NumpyPolicy(Path(policy_dir) / "policy.npz")
        meta = self.policy.meta
        if P.policy_kind(meta) != "walk" or (meta.get("robot") or "sku2") != "sku2":
            sys.exit("play.py runs walking policies for the SKU2 only.")

        # the motors: the model fitted to the real ones
        motors = bank.load_models({role: paths.ACTUATOR_PARAMS / "md300" / f for role, f in MOTORS.items()})
        for motor in motors.values():
            choice.apply_md300_firmware(motor.actuator, choice.MD300_FIRMWARE)

        # the robot, a floor and some light
        spec = robot_model.get_spec(strip_visuals=simple, self_collision=True, limits=True, foot_solref=(0.01, 1.0))
        bank.add_servos(spec, motors)
        if not simple:
            self.add_looks(spec)
        spec.add_texture(name="grid", type=mujoco.mjtTexture.mjTEXTURE_2D, builtin=mujoco.mjtBuiltin.mjBUILTIN_CHECKER,
                         rgb1=[.82, .84, .86], rgb2=[.74, .76, .79], width=300, height=300)
        mat = spec.add_material(name="grid", texrepeat=[10, 10], texuniform=True)
        mat.textures[mujoco.mjtTextureRole.mjTEXROLE_RGB] = "grid"
        spec.add_texture(name="sky", type=mujoco.mjtTexture.mjTEXTURE_SKYBOX,
                         builtin=mujoco.mjtBuiltin.mjBUILTIN_GRADIENT, rgb1=[.55, .68, .82], rgb2=[.9, .93, .96],
                         width=256, height=256)
        spec.worldbody.add_geom(name="floor", type=mujoco.mjtGeom.mjGEOM_PLANE, size=[0, 0, .05], material="grid",
                                contype=2, conaffinity=1)
        spec.worldbody.add_light(pos=[0, 0, 3], dir=[0, 0, -1], type=mujoco.mjtLightType.mjLIGHT_DIRECTIONAL)
        self.m = spec.compile()
        self.m.opt.timestep = fits.PHYSICS_DT
        self.m.opt.iterations, self.m.opt.ls_iterations = 10, 20
        if simple:                                  # show the collision shapes instead of the meshes
            self.m.geom_group[:] = 0
            for i in range(self.m.ngeom):
                body = self.m.body(self.m.geom_bodyid[i]).name
                if body != "world":
                    self.m.geom_rgba[i] = (.95, .8, .1, 1) if body == "base" else (.15, .15, .15, 1)
            self.m.light_castshadow[:] = 0
        self.d = mujoco.MjData(self.m)
        self.bank = bank.BamServoBank(self.m, self.d, motors, extra_lag_steps=DELAY_MS)

        # what turns the policy's output into motor targets, the same code as on the robot
        self.c = Contract.load()
        self.decoder = P.ActionDecoder(self.c, self.policy.scale, band_deg=P.policy_band_deg(meta),
                                       bounds=P.policy_bounds(meta),
                                       stand_offset_abd_deg=P.policy_stand_offset_deg(meta),
                                       filter_alpha=P.policy_filter_alpha(meta))
        self.stand = np.asarray(self.c.stand_rel_rad)
        coefs = self.c.meta["tendon_coefs"]
        self.knee = np.array([[coefs[g][f"{g}_thigh"], coefs[g][f"{g}_calf"]] for g in LEGS])
        self.qadr = np.array([self.m.joint(f"{g}_{j}").qposadr[0] for g in LEGS for j in ("hip", "thigh", "calf")])
        self.gyro = self.m.sensor("imu_ang_vel").adr[0]
        self.imu = self.m.site("imu").id
        self.command = np.zeros(3)                  # forward m/s, left m/s, turn left rad/s
        self.reset()

    @staticmethod
    def add_looks(spec):
        """The display and the Raspberry Pi. They have no effect on the walking, so the simulator leaves them out."""
        full = mujoco.MjSpec.from_file(str(robot_model.Legs().xml))
        folder = robot_model.Legs().xml.parent / full.meshdir
        spec.add_texture(name="face", type=mujoco.mjtTexture.mjTEXTURE_2D, file=str(folder / "screen_face.png"))
        spec.add_material(name="face", emission=0.5).textures[mujoco.mjtTextureRole.mjTEXROLE_RGB] = "face"
        for g in full.body("base").geoms:
            if g.meshname in robot_model.ACCESSORY_MESHES and not g.meshname.startswith("acc_lidar"):
                mesh = full.mesh(g.meshname)
                spec.add_mesh(name=g.meshname, file=str(folder / mesh.file), inertia=mesh.inertia)
                spec.body("base").add_geom(type=mujoco.mjtGeom.mjGEOM_MESH, meshname=g.meshname, material=g.material,
                                           pos=g.pos, quat=g.quat, contype=0, conaffinity=0, density=0, group=2)

    def reset(self):
        mujoco.mj_resetData(self.m, self.d)
        self.decoder.reset()
        target = (self.decoder.physical(np.zeros(12)) + self.stand).reshape(4, 3)
        q = target.copy()
        q[:, 2] = (target[:, 2] - self.knee[:, 0] * target[:, 1]) / self.knee[:, 1]
        self.d.qpos[:3] = 0, 0, robot_model.init_base_z()
        self.d.qpos[3:7] = 1, 0, 0, 0
        self.d.qpos[self.qadr] = q.ravel()
        mujoco.mj_forward(self.m, self.d)
        self.bank.reset()
        self.bank.set_targets(target.ravel())
        self.history = P.HistoryStacker(int(self.policy.meta.get("history") or 1))
        self.velocity = P.VelocityFilter()
        self.command[:] = 0

    def joints(self):
        """The twelve motor angles, as the robot's sensors report them."""
        q = self.d.qpos[self.qadr].reshape(4, 3).copy()
        q[:, 2] = (q[:, 1:] * self.knee).sum(1)
        return q.ravel() - self.stand

    def step(self):
        """One decision of the policy: observe, choose, and let 20 ms of physics happen."""
        up = self.d.site_xmat[self.imu].reshape(3, 3)[2]
        self.velocity.hist is None and self.velocity.push(self.joints())
        obs = P.assemble_observation(self.d.sensordata[self.gyro:self.gyro + 3], -up, self.command,
                                     self.joints() - self.decoder.obs_offset, self.velocity.velocity(),
                                     self.decoder.prev_action)
        action = self.policy(self.history(obs))
        self.bank.set_targets(self.decoder(action)["rel"] + self.stand)
        for i in range(SUBSTEPS):
            self.bank.update()
            mujoco.mj_step(self.m, self.d)
            if i % 5 == 4:
                self.velocity.push(self.joints())

    def shove(self, speed=0.6):
        angle = np.random.uniform(0, 2 * np.pi)
        self.d.qvel[:2] += speed * np.cos(angle), speed * np.sin(angle)

    def speeds(self):
        """Forward and sideways speed (m/s) and turning speed (rad/s) as the robot sees them."""
        R = self.d.body("base").xmat.reshape(3, 3)
        yaw = np.arctan2(R[1, 0], R[0, 0])
        vx, vy = self.d.qvel[:2]
        return np.cos(yaw) * vx + np.sin(yaw) * vy, -np.sin(yaw) * vx + np.cos(yaw) * vy, self.d.qvel[5]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--policy", default="mp4_rl/skills/walker/policies/sku2", help="a folder with a policy.npz")
    ap.add_argument("--simple", action="store_true", help="simple shapes, for slow computers")
    a = ap.parse_args()
    import mujoco.viewer

    robot = Robot(a.policy, a.simple)
    limits = np.array([0.20, 0.20, 2.0])
    moves = {265: (0, +.05), 264: (0, -.05), ord("6"): (1, +.05), ord("7"): (1, -.05), 263: (2, +.5), 262: (2, -.5)}
    todo = []                                       # the window has its own thread: keys wait here for the loop

    with mujoco.viewer.launch_passive(robot.m, robot.d, key_callback=todo.append, show_left_ui=False,
                                      show_right_ui=False) as window:
        window.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
        window.cam.trackbodyid = robot.m.body("base").id
        window.cam.distance, window.cam.elevation, window.cam.azimuth = 0.6, -18, 140
        print(__doc__.split("\n\n")[2])
        mean, steps, start, clock = np.zeros(3), 0, time.time(), time.time()
        while window.is_running():
            for key in todo[:]:
                todo.remove(key)
                if key in moves:
                    axis, change = moves[key]
                    robot.command[axis] = np.clip(round(robot.command[axis] + change, 2), -limits[axis], limits[axis])
                elif key == 257:
                    robot.command[:] = 0
                elif key == ord("8"):
                    robot.shove()
                elif key == ord("9"):
                    robot.reset()
            robot.step()
            mean += 0.05 * (np.array(robot.speeds()) - mean)
            steps += 1
            window.sync()
            if steps % 10 == 0:
                print("\rasked: forward %+.2f left %+.2f m/s turn %+.1f rad/s | doing: %+.2f %+.2f %+.1f   "
                      % (*robot.command, *mean), end="", flush=True)
            clock += CONTROL_DT
            wait = clock - time.time()
            if wait > 0:
                time.sleep(wait)
            else:
                clock = time.time()                 # too slow to keep up: carry on from here
    print()


if __name__ == "__main__":
    main()
