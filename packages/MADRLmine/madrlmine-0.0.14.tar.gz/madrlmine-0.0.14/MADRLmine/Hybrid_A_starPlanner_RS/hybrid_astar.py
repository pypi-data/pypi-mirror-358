"""
Hybrid A*
@author: Huiming Zhou
"""

import os
import sys
import json
import math
import heapq
from heapdict import heapdict
import time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
import matplotlib.pyplot as plt
import scipy.spatial.kdtree as kd
import scipy.ndimage as ndimage
import itertools
from matplotlib.collections import LineCollection
import cvxpy as cp


import Hybrid_A_starPlanner_RS.astar as astar
import Hybrid_A_starPlanner_RS.draw as draw
import Hybrid_A_starPlanner_RS.reeds_shepp as rs



class C:  # Parameter config
    PI = math.pi

    XY_RESO = 1  # [m]
    YAW_RESO = np.deg2rad(15.0)  # [rad]
    MOVE_STEP = 0.6  # [m] path interporate resolution
    N_STEER = 20.0  # steer command number
    COLLISION_CHECK_STEP = 2  # skip number for collision check
    EXTEND_BOUND = 0  # collision check range extended

    GEAR_COST = 1e6  # switch back penalty cost
    BACKWARD_COST = 500.0  # backward penalty cost
    STEER_CHANGE_COST = 1.0  # steer angle change penalty cost
    STEER_ANGLE_COST = 3.0  # steer angle penalty cost
    H_COST = 15.0  # Heuristic cost penalty cost
    EUC_COST_WEIGHT = 40.0 ##欧式距离启发权重
    TIME_LIMIT = 15

    RF = 7.59  # [m] distance from rear to vehicle front end of vehicle
    RB = 2.1  # [m] distance from rear to vehicle back end of vehicle
    W = 3.65  # [m] width of vehicle
    WD = 0.7 * W  # [m] distance between left-right wheels
    WB = 3.5  # [m] Wheel base
    TR = 0.5  # [m] Tyre radius
    TW = 1  # [m] Tyre width
    MAX_STEER = 0.26  # [rad] maximum steering angle
    MAX_C = 1/13.5

    RS_CALL_RANGE = 50.0 #RS调用起点
# ---- 新增 hmap 降采样倍率 ----
    HMAP_SCALE = 3  # 将 hmap 分辨率缩小为原来的 1/4，再插值回去

    PLOT = True  # 总开关：若 False，则不做任何绘图
    ANIMATE = False  # 若 True，则逐步动画，否则只画最终结果

class Node:
    def __init__(self, xind, yind, yawind, direction,
                 x, y, yaw, directions,
                 steer, cost, pind, ind=None, is_rs=False):
        self.xind = xind; self.yind = yind; self.yawind = yawind
        self.direction = direction
        self.x = x; self.y = y; self.yaw = yaw; self.directions = directions
        self.steer = steer; self.cost = cost; self.pind = pind
        self.ind = ind    # 缓存扁平索引
        self.is_rs = is_rs  # ← 新增：标记是否 RS 扩展节点

class Para:
    def __init__(self, minx, miny, minyaw, maxx, maxy, maxyaw,
                 xw, yw, yaww, xyreso, yawreso, ox, oy, kdtree):
        self.minx, self.miny, self.minyaw = minx, miny, minyaw
        self.maxx, self.maxy, self.maxyaw = maxx, maxy, maxyaw
        self.xw, self.yw, self.yaww = xw, yw, yaww
        self.xyreso, self.yawreso = xyreso, yawreso
        self.ox, self.oy, self.kdtree = ox, oy, kdtree

class Path:
    def __init__(self, x, y, yaw, direction, cost, is_rs_list=None,
                 t=None, v=None, a=None, j=None):
        self.x = x
        self.y = y
        self.yaw = yaw
        self.direction = direction
        self.cost = cost
        self.is_rs_list = is_rs_list

        # 以下四个字段用来存放速度规划结果
        self.t = t      # 时间戳 list, len == len(x)
        self.v = v      # 速度 list
        self.a = a      # 加速度 list
        self.j = j      # jerk list

class QueuePrior:
    def __init__(self):
        self.queue = heapdict()
    def empty(self): return len(self.queue)==0
    def put(self, key, pri): self.queue[key] = pri
    def get(self): return self.queue.popitem()[0]

def calc_parameters(ox, oy, xyreso, yawreso, kdtree):
    minx = round(min(ox)/xyreso); maxx = round(max(ox)/xyreso)
    miny = round(min(oy)/xyreso); maxy = round(max(oy)/xyreso)
    xw = maxx - minx + 1; yw = maxy - miny + 1
    minyaw = round(-C.PI/yawreso)-1; maxyaw = round(C.PI/yawreso)
    yaww = maxyaw - minyaw + 1
    return Para(minx, miny, minyaw, maxx, maxy, maxyaw,
                xw, yw, yaww, xyreso, yawreso, ox, oy, kdtree)

def calc_motion_set():
    s = np.linspace(-C.MAX_STEER, C.MAX_STEER, int(2*C.N_STEER)+1)
    steer = s.tolist()
    direc = [1.0]*len(steer) + [-1.0]*len(steer)
    steer = steer + steer
    return steer, direc

def calc_index(node, P):
    return ((node.yawind - P.minyaw)*P.xw*P.yw +
            (node.yind   - P.miny )*P.xw +
            (node.xind   - P.minx))


def hybrid_astar_planning(sx, sy, syaw,
                          gx, gy, gyaw,
                          ox, oy,
                          xyreso, yawreso,
                          cusp_type,
                          in_path_flag,
                          time_limit=None
                          ):

    # 记录起始时间
    t_start = time.time()
    # 1) 起终点离散化
    sxr, syr = round(sx/xyreso), round(sy/xyreso)
    gxr, gyr = round(gx/xyreso), round(gy/xyreso)
    syawr = round(rs.pi_2_pi(syaw)/yawreso)
    gyawr = round(rs.pi_2_pi(gyaw)/yawreso)

    nstart = Node(sxr, syr, syawr, 1,
                  [sx], [sy], [syaw], [1],
                  0.0, 0.0, -1)
    ngoal  = Node(gxr, gyr, gyawr, 1,
                  [gx], [gy], [gyaw], [1],
                  0.0, 0.0, -1)
    # 缓存目标点的连续坐标，用于欧式距离计算
    goal_x, goal_y = ngoal.x[-1], ngoal.y[-1]

    # 2) KDTree + 参数
    kdtree = kd.KDTree(list(zip(ox, oy)))
    P = calc_parameters(ox, oy, xyreso, yawreso, kdtree)

    # 3) 构造 hmap（粗分辨率 + 线性插值）
    t0 = time.time()
    scale = C.HMAP_SCALE
    if scale > 1:
        h_coarse = np.array(
            astar.calc_holonomic_heuristic_with_obstacle(
                ngoal, P.ox, P.oy, xyreso*scale, C.EXTEND_BOUND))
        hmap = ndimage.zoom(h_coarse, zoom=scale, order=1)
        hmap = hmap[:P.xw, :P.yw]
    else:
        hmap = np.array(
            astar.calc_holonomic_heuristic_with_obstacle(
                ngoal, P.ox, P.oy, xyreso, C.EXTEND_BOUND))
    # print(f"[hmap] shape={hmap.shape}  cost={(time.time()-t0):.3f}s")

    # 4) 扁平化启发式 & 常量
    h_flat = hmap.ravel()
    HW = P.xw * P.yw
    minx, miny = P.minx, P.miny

    # 5) 初始化 open/closed，并把起点加入
    start_id = calc_index(nstart, P)
    nstart.ind = start_id
    # 起点在 h_flat 的索引（仅 x/y，不含 yaw）
    start_xy = (nstart.xind - minx)*P.yw + (nstart.yind - miny)
    open_set, closed_set = {start_id: nstart}, {}
    qp = QueuePrior()
    qp.put(start_id, nstart.cost + C.H_COST * h_flat[start_xy])

    steer_set, direc_set = calc_motion_set()

    # 6) 主循环
    while open_set:
        # —— 超时检测 ——
        if time_limit is not None and time.time() - t_start > time_limit:
            # print(f"[hybrid_astar_planning] time limit {time_limit}s exceeded, abort.")
            return None

        sid = qp.get()
        curr = open_set.pop(sid)
        closed_set[sid] = curr

        # analytic 扩展
        cx, cy = curr.x[-1], curr.y[-1]
        gx, gy = ngoal.x[-1], ngoal.y[-1]
        if math.hypot(cx - gx, cy - gy) <= C.RS_CALL_RANGE:
            update, fpath = update_node_with_analystic_expantion(curr, ngoal, P, cusp_type, in_path_flag)
        else:
            update, fpath = False, None

        if update:
            fnode = fpath
            break

        # 运动原语扩展
        for u, d in zip(steer_set, direc_set):
            nb = calc_next_node(curr, curr.ind, u, d, P)
            if not nb: continue

            nid = calc_index(nb, P)
            nb.ind = nid
            if nid in closed_set: continue

            # 计算对应 x/y 在 h_flat 中的索引
            xyid = (nb.xind - minx)*P.yw + (nb.yind - miny)
            # 新增欧式距离到终点
            dist_to_goal = math.hypot(nb.x[-1] - goal_x, nb.y[-1] - goal_y)
            # 最终 f 值：g + H_COST*h + EUC_COST_WEIGHT*dist
            fcost = (nb.cost + C.H_COST * h_flat[xyid] + C.EUC_COST_WEIGHT * dist_to_goal)

            if nid not in open_set or open_set[nid].cost > nb.cost:
                open_set[nid] = nb
                qp.put(nid, fcost)

    # 7) 回溯路径
    if not update:
        return None
    return extract_path(closed_set, fnode, nstart)


def extract_path(closed, ngoal, nstart):
    rx, ry, ryaw, direc, is_rs = [], [], [], [], []
    cost = 0.0
    node = ngoal

    while True:
        # 逆序累加当前节点的所有点和它的 is_rs 标记
        rx += node.x[::-1]
        ry += node.y[::-1]
        ryaw += node.yaw[::-1]
        direc += node.directions[::-1]
        # node.is_rs 是一个标记，把它复制 len(node.x) 次
        is_rs += [node.is_rs] * len(node.x)

        cost += node.cost
        if is_same_grid(node, nstart):
            break
        node = closed[node.pind]

    # 正序
    rx = rx[::-1]
    ry = ry[::-1]
    ryaw = ryaw[::-1]
    direc = direc[::-1]
    is_rs = is_rs[::-1]

    # 修正第一个方向
    direc[0] = direc[1]

    path = Path(rx, ry, ryaw, direc, cost, is_rs)
    return path

def calc_next_node(n_curr, c_id, u, d, P):
    step = C.XY_RESO * 2

    nlist = math.ceil(step / C.MOVE_STEP)
    xlist = [n_curr.x[-1] + d * C.MOVE_STEP * math.cos(n_curr.yaw[-1])]
    ylist = [n_curr.y[-1] + d * C.MOVE_STEP * math.sin(n_curr.yaw[-1])]
    yawlist = [rs.pi_2_pi(n_curr.yaw[-1] + d * C.MOVE_STEP / C.WB * math.tan(u))]

    for i in range(nlist - 1):
        xlist.append(xlist[i] + d * C.MOVE_STEP * math.cos(yawlist[i]))
        ylist.append(ylist[i] + d * C.MOVE_STEP * math.sin(yawlist[i]))
        yawlist.append(rs.pi_2_pi(yawlist[i] + d * C.MOVE_STEP / C.WB * math.tan(u)))

    xind = round(xlist[-1] / P.xyreso)
    yind = round(ylist[-1] / P.xyreso)
    yawind = round(yawlist[-1] / P.yawreso)

    if not is_index_ok(xind, yind, xlist, ylist, yawlist, P):
        return None

    cost = 0.0

    if d > 0:
        direction = 1
        cost += abs(step)
    else:
        direction = -1
        cost += abs(step) * C.BACKWARD_COST

    if direction != n_curr.direction:  # switch back penalty
        cost += C.GEAR_COST

    cost += C.STEER_ANGLE_COST * abs(u)  # steer angle penalyty
    cost += C.STEER_CHANGE_COST * abs(n_curr.steer - u)  # steer change penalty
    cost = n_curr.cost + cost

    directions = [direction for _ in range(len(xlist))]

    node = Node(
        xind, yind, yawind, direction,
        xlist, ylist, yawlist, directions,
        u, cost, c_id,
        ind=None,
        is_rs=False  # ← 普通扩展
    )

    return node


def is_index_ok(xind, yind, xlist, ylist, yawlist, P):
    # （1）原有的地图边界检查
    if xind <= P.minx or xind >= P.maxx or \
       yind <= P.miny or yind >= P.maxy:
        return False

    # （3）原有的碰撞检查
    ind = range(0, len(xlist), C.COLLISION_CHECK_STEP)
    nodex = [xlist[k] for k in ind]
    nodey = [ylist[k] for k in ind]
    nodeyaw = [yawlist[k] for k in ind]
    if is_collision(nodex, nodey, nodeyaw, P):
        return False

    return True


def update_node_with_analystic_expantion(n_curr, ngoal, P, cusp_type, in_path_flag):
    path = analystic_expantion(n_curr, ngoal, P, cusp_type, in_path_flag)  # rs path: n -> ngoal

    if not path:
        return False, None

    fx = path.x[1:-1]
    fy = path.y[1:-1]
    fyaw = path.yaw[1:-1]
    fd = path.directions[1:-1]

    cost = calc_rs_path_cost(path)
    fcost = n_curr.cost + cost
    fpind = calc_index(n_curr, P)
    fsteer = 0.0

    fpath = Node(
        n_curr.xind, n_curr.yind, n_curr.yawind, n_curr.direction,
        fx, fy, fyaw, fd,
        fsteer, fcost, fpind,
        ind=None,
        is_rs=True  # ← RS 扩展
    )

    return True, fpath

def angle_difference(rad1, rad2):
    # 将角度归一化到 [-pi, pi) 区间
    rad1_normalized = (rad1 + np.pi) % (2 * np.pi) - np.pi
    rad2_normalized = (rad2 + np.pi) % (2 * np.pi) - np.pi

    # 计算差异并取模 2pi，然后取最小的绝对值差异
    diff = (rad1_normalized - rad2_normalized) % (2 * np.pi)
    return min(diff, 2 * np.pi - diff)

def analystic_expantion(node, ngoal, P, cusp_type, in_path_flag):
    sx, sy, syaw = node.x[-1], node.y[-1], node.yaw[-1]
    gx, gy, gyaw = ngoal.x[-1], ngoal.y[-1], ngoal.yaw[-1]

    maxc = math.tan(C.MAX_STEER) / C.WB
    paths = rs.calc_all_paths(
        sx, sy, syaw, gx, gy, gyaw, maxc, step_size=C.MOVE_STEP)

    if not paths:
        return None

    pq = QueuePrior()
    for path in paths:
        # 如果对人字尖朝向有限制，那么先检测人字尖朝向是否符合要求
        if in_path_flag and cusp_type != "both":
            cusp_idx = 0
            change_gear = 0
            for i in range(len(path.directions) - 1):
                if path.directions[i] * path.directions[i + 1] < 0.0:
                    cusp_idx = i
                    change_gear += 1
            if change_gear > 1:
                continue
            end_x, end_y, end_yaw = path.x[-1], path.y[-1], path.yaw[-1]
            cusp_x, cusp_y = path.x[cusp_idx], path.y[cusp_idx]
            # 计算终点指向人字尖的向量角度，(-pi, pi],atan2会自动处理x坐标相同的问题
            end_toward_cusp_yaw = math.atan2((cusp_y-end_y), (cusp_x-end_x))
            # 终点左前方45度,并统一到(-pi, pi]
            end_left_front_yaw = (end_yaw + np.pi/4 + np.pi) % (2 * np.pi) - np.pi
            end_left_front_yaw = np.pi if end_left_front_yaw==-np.pi else end_left_front_yaw
            # 终点右前方45度,并统一到(-pi, pi]
            end_right_front_yaw = (end_yaw - np.pi/4 + np.pi) % (2 * np.pi) - np.pi
            end_right_front_yaw = np.pi if end_right_front_yaw==-np.pi else end_right_front_yaw

            if angle_difference(end_left_front_yaw, end_toward_cusp_yaw) < angle_difference(end_right_front_yaw, end_toward_cusp_yaw):
                actual_cusp_type = "left"
            else:
                actual_cusp_type = "right"
            if actual_cusp_type != cusp_type:
                continue
        cost = calc_rs_path_cost(path)
        pq.put(path, cost)


    while not pq.empty():
        path = pq.get()
        ind = range(0, len(path.x), C.COLLISION_CHECK_STEP)
        pathx = [path.x[k] for k in ind]
        pathy = [path.y[k] for k in ind]
        pathyaw = [path.yaw[k] for k in ind]

        # 碰撞过滤
        if is_collision(pathx, pathy, pathyaw, P):
            continue

        # 既不碰撞，也都在可行驶区，接受这条 RS 解
        return path

    return None


def is_collision(x, y, yaw, P):
    for ix, iy, iyaw in zip(x, y, yaw):
        d = 1
        dl = (C.RF - C.RB) / 2.0
        r = (C.RF + C.RB) / 2.0 + d

        cx = ix + dl * math.cos(iyaw)
        cy = iy + dl * math.sin(iyaw)

        ids = P.kdtree.query_ball_point([cx, cy], r)

        if not ids:
            continue

        for i in ids:
            xo = P.ox[i] - cx
            yo = P.oy[i] - cy
            dx = xo * math.cos(iyaw) + yo * math.sin(iyaw)
            dy = -xo * math.sin(iyaw) + yo * math.cos(iyaw)

            if abs(dx) < r and abs(dy) < C.W / 2 + d:
                return True

    return False


def calc_rs_path_cost(rspath):
    cost = 0.0

    for lr in rspath.lengths:
        if lr >= 0:
            cost += 1
        else:
            cost += abs(lr) * C.BACKWARD_COST

    for i in range(len(rspath.directions) - 1):
        if rspath.directions[i] * rspath.directions[i + 1] < 0.0:
            cost += C.GEAR_COST

    for ctype in rspath.ctypes:
        if ctype != "S":
            cost += C.STEER_ANGLE_COST * abs(C.MAX_STEER)

    nctypes = len(rspath.ctypes)
    ulist = [0.0 for _ in range(nctypes)]

    for i in range(nctypes):
        if rspath.ctypes[i] == "R":
            ulist[i] = -C.MAX_STEER
        elif rspath.ctypes[i] == "WB":
            ulist[i] = C.MAX_STEER

    for i in range(nctypes - 1):
        cost += C.STEER_CHANGE_COST * abs(ulist[i + 1] - ulist[i])

    return cost


def calc_hybrid_cost(node, hmap, P):
    cost = node.cost + \
           C.H_COST * hmap[node.xind - P.minx][node.yind - P.miny]

    return cost


def calc_motion_set():
    s = np.arange(C.MAX_STEER / C.N_STEER,
                  C.MAX_STEER, C.MAX_STEER / C.N_STEER)

    steer = list(s) + [0.0] + list(-s)
    direc = [1.0 for _ in range(len(steer))]
    steer = steer

    return steer, direc


def is_same_grid(node1, node2):
    if node1.xind != node2.xind or \
            node1.yind != node2.yind or \
            node1.yawind != node2.yawind:
        return False

    return True


def calc_index(node, P):
    ind = (node.yawind - P.minyaw) * P.xw * P.yw + \
          (node.yind - P.miny) * P.xw + \
          (node.xind - P.minx)

    return ind


def calc_parameters(ox, oy, xyreso, yawreso, kdtree):
    minx = round(min(ox) / xyreso)
    miny = round(min(oy) / xyreso)
    maxx = round(max(ox) / xyreso)
    maxy = round(max(oy) / xyreso)

    xw, yw = maxx - minx, maxy - miny

    minyaw = round(-C.PI / yawreso) - 1
    maxyaw = round(C.PI / yawreso)
    yaww = maxyaw - minyaw

    return Para(minx, miny, minyaw, maxx, maxy, maxyaw,
                xw, yw, yaww, xyreso, yawreso, ox, oy, kdtree)


def draw_car(x, y, yaw, steer, color='black'):
    car = np.array([[-C.RB, -C.RB, C.RF, C.RF, -C.RB],
                    [C.W / 2, -C.W / 2, -C.W / 2, C.W / 2, C.W / 2]])

    wheel = np.array([[-C.TR, -C.TR, C.TR, C.TR, -C.TR],
                      [C.TW / 4, -C.TW / 4, -C.TW / 4, C.TW / 4, C.TW / 4]])

    rlWheel = wheel.copy()
    rrWheel = wheel.copy()
    frWheel = wheel.copy()
    flWheel = wheel.copy()

    Rot1 = np.array([[math.cos(yaw), -math.sin(yaw)],
                     [math.sin(yaw), math.cos(yaw)]])

    Rot2 = np.array([[math.cos(steer), math.sin(steer)],
                     [-math.sin(steer), math.cos(steer)]])

    frWheel = np.dot(Rot2, frWheel)
    flWheel = np.dot(Rot2, flWheel)

    frWheel += np.array([[C.WB], [-C.WD / 2]])
    flWheel += np.array([[C.WB], [C.WD / 2]])
    rrWheel[1, :] -= C.WD / 2
    rlWheel[1, :] += C.WD / 2

    frWheel = np.dot(Rot1, frWheel)
    flWheel = np.dot(Rot1, flWheel)

    rrWheel = np.dot(Rot1, rrWheel)
    rlWheel = np.dot(Rot1, rlWheel)
    car = np.dot(Rot1, car)

    frWheel += np.array([[x], [y]])
    flWheel += np.array([[x], [y]])
    rrWheel += np.array([[x], [y]])
    rlWheel += np.array([[x], [y]])
    car += np.array([[x], [y]])

    plt.plot(car[0, :], car[1, :], color)
    plt.plot(frWheel[0, :], frWheel[1, :], color)
    plt.plot(rrWheel[0, :], rrWheel[1, :], color)
    plt.plot(flWheel[0, :], flWheel[1, :], color)
    plt.plot(rlWheel[0, :], rlWheel[1, :], color)
    draw.Arrow(x, y, yaw, C.WB * 0.8, color)


def read_grid_map(json_file_path):
    """读取地图数据并生成障碍物字典"""
    obstacles = {}
    # 读取JSON文件
    with open(json_file_path, 'r') as file:
        data = json.load(file)

        # 提取地图信息
        width = data['metadata']['dimensions']['width']
        height = data['metadata']['dimensions']['height']

        # 初始化地图数据数组
        map_data = np.zeros((width, height), dtype=int)

        # 填充地图数据
        for index in data['data']:
            # 计算二维数组的坐标
            x = index % width  # 余数，列位置
            y = index // width
            map_data[x, y] = 1  # 将障碍物标记为1
            obstacles[(x, y)] = True

    return map_data, height, width, obstacles


def resample_path(path, N, preserve_shifts=True):
    """
    将原始 path 重采样为恰好 N 个点。
    如果 preserve_shifts=True，则强制保留每个 direction 切换处的原始点。
    path 必须带有 .x, .y, .yaw, .direction, .is_rs_list 属性。
    """
    # 原始路径数据
    x = np.array(path.x)
    y = np.array(path.y)
    yaw = np.array(path.yaw)
    direction = np.array(path.direction)
    is_rs = np.array(path.is_rs_list, dtype=bool)

    # 1) 计算累积弧长 s
    dx = np.diff(x)
    dy = np.diff(y)
    ds = np.hypot(dx, dy)
    s = np.concatenate(([0.], np.cumsum(ds)))  # len = M

    s_total = s[-1]
    if s_total == 0:
        raise ValueError("路径长度为0，无法重采样。")

    # 2) 找到所有 gear-shift 处的 s_shift
    #    切换发生在 i->i+1，取 i+1 处的 s 值
    idx = np.where(direction[:-1] != direction[1:])[0] + 1
    s_shift = s[idx] if preserve_shifts else np.empty(0)
    M_shift = len(s_shift)

    if preserve_shifts and M_shift >= N:
        raise ValueError(f"N={N} 太小，无法同时保留 {M_shift} 个切换点。")

    # 3) 在剩余弧长上等距取点
    N_uniform = N - M_shift if preserve_shifts else N
    s_uniform = np.linspace(0, s_total, N_uniform)

    # 4) 合并、去重、排序
    if preserve_shifts:
        s_new = np.concatenate((s_uniform, s_shift))
    else:
        s_new = s_uniform
    s_new = np.unique(s_new)
    # 如果去重后少于 N，补齐端点附近的点
    if len(s_new) < N:
        extra = np.linspace(0, s_total, N - len(s_new))
        s_new = np.unique(np.concatenate((s_new, extra)))
    # 最后再截断到前 N 个
    s_new = np.sort(s_new)[:N]

    # 5) 插值 x,y
    x_new = np.interp(s_new, s, x)
    y_new = np.interp(s_new, s, y)

    # 6) 插值 yaw：先 unwrap 再 wrap
    yaw_un = np.unwrap(yaw)
    yaw_i  = np.interp(s_new, s, yaw_un)
    yaw_new = (yaw_i + np.pi) % (2*np.pi) - np.pi

    # 7) 离散量 direction / is_rs 最近邻
    #    查找每个 s_new 对应的原始索引
    idx_nn = np.searchsorted(s, s_new, side='right') - 1
    idx_nn = np.clip(idx_nn, 0, len(direction)-1)
    dir_new   = direction[idx_nn].tolist()
    is_rs_new = is_rs[idx_nn].tolist()

    # 8) 检查：如果最终点数不是 N，就抛错
    final_len = len(x_new)
    if final_len != N or len(yaw_new) != N or len(dir_new) != N or len(is_rs_new) != N:
        raise ValueError(
            f"重采样失败：期望点数 {N}，但得到 {final_len} (dir={len(dir_new)}, is_rs={len(is_rs_new)})"
        )

    # 8) 返回新的 Path（复用原 cost）
    return Path(
        x_new.tolist(),
        y_new.tolist(),
        yaw_new.tolist(),
        dir_new,
        path.cost,
        is_rs_new
    )

import numpy as np

def speed_profile_with_asymmetric_limits(
    path,
    v_max_global: float,
    a_lat_max: float,
    a_acc_max: float,   # 最大加速能力 [m/s²]
    a_dec_max: float,   # 最大制动能力 [m/s²]（取正值）
    j_max: float = None, # 新增：最大 jerk [m/s³]，不限制时传 None
    gamma: float = 1e-2  # 提升速度的线性权重，越大速度提升越多
):
    import numpy as np
    import cvxpy as cp

    # 1) 提取数据
    x = np.array(path.x);   y = np.array(path.y)
    yaw = np.array(path.yaw)
    direction = np.array(path.direction, dtype=int)
    N = len(x)
    assert N > 2, "点太少"

    # 2) 等弧长 Δs
    ds = np.hypot(x[1]-x[0], y[1]-y[0])

    # 3) 曲率限速
    kappa = np.zeros(N)
    kappa[1:-1] = np.abs((yaw[2:] - yaw[:-2]) / (2*ds))
    kappa[0], kappa[-1] = kappa[1], kappa[-2]
    v_max_curve = np.sqrt(a_lat_max/np.maximum(kappa, 1e-6))
    v_ub = np.minimum(v_max_curve, v_max_global)

    # 4) 换档点
    shift_idx = np.where(direction[:-1]!=direction[1:])[0] + 1
    shift_idx = shift_idx[(shift_idx>0)&(shift_idx<N-1)]

    # 5) 优化变量
    v = cp.Variable(N)

    # 6) 目标：jerk 二次项 - γ·sum(v)
    dv2 = v[2:] - 2*v[1:-1] + v[:-2]  # 离散二阶差分
    obj = cp.Minimize(cp.sum_squares(dv2) - gamma*cp.sum(v))

    # 7) 约束集合
    cons = []
    # 7.1 速度上下限
    cons += [v >= 0, v <= v_ub]
    # 7.2 起终点、换档点 v=0
    cons += [v[0]==0, v[-1]==0]
    for idx in shift_idx:
        cons += [v[idx]==0]
    # 7.3 区分加速 & 制动
    for i in range(1, N):
        cons += [v[i] - v[i-1] <= a_acc_max * ds]
        cons += [v[i-1] - v[i] <= a_dec_max * ds]

    # 7.4 （可选）jerk 上下限
    if j_max is not None:
        # j ≈ dv2 / ds^2，因此 |dv2| ≤ j_max * ds^2
        cons += [ dv2 <=  j_max * ds**2 ]
        cons += [ dv2 >= -j_max * ds**2 ]

    # 8) 求解
    prob = cp.Problem(obj, cons)
    prob.solve(solver=cp.OSQP)

    # 9) 导出结果
    v_opt = np.maximum(v.value, 0)
    v_safe = np.maximum(v_opt, 1e-3)
    v_front = v_safe[:-1]
    v_latter = v_safe[1:]
    v_used_for_calc_t = (v_front + v_latter)/2
    dt = ds / v_used_for_calc_t
    # 避免某些情况点与点之间的时间间隔过大的问题，限制点与点之间时间间隔最大为3s
    dt = np.minimum(dt, 3)
    t = np.concatenate(([0.], np.cumsum(dt[:])))
    a = np.zeros_like(v_opt)
    a[1:] = (v_opt[1:] - v_opt[:-1]) / dt[:]
    j = np.zeros_like(v_opt)
    j[2:] = (a[2:]     - a[1:-1])  / dt[1:]
    # # —9— 打印统计信息
    # print(f"[speed_profile] speed: min={v_opt.min():.3f}, max={v_opt.max():.3f}")
    # print(f"[speed_profile] accel: min={a.min():.3f}, max={a.max():.3f}, |a|_max={np.abs(a).max():.3f}")
    # print(f"[speed_profile] jerk:  min={j.min():.3f}, max={j.max():.3f}, |j|_max={np.abs(j).max():.3f}")

    path.t = t.tolist()
    path.v = v_opt.tolist()
    path.a = a.tolist()
    path.j = j.tolist()
    return path

def hybrid_Astar_with_speed(
    sx, sy, syaw,
    gx, gy, gyaw,
    ox, oy,
    xyreso=C.XY_RESO,
    yawreso=C.YAW_RESO,
    time_limit=C.TIME_LIMIT,
    # 重采样参数
    N_resample=128,
    preserve_shifts=True,
    # 速度规划参数
    v_max_global=8.0,
    a_lat_max=0.8,
    a_acc_max=0.8,
    a_dec_max=2.0,
    j_max=2.0,
    gamma=1e-2
):
    """
    一步完成：
      1) 调用 hybrid_astar_planning 获得初步轨迹
      2) 调用 resample_path 重采样到 N_resample 点
      3) 调用 speed_profile_with_asymmetric_limits 做速度规划

    返回：带时间、速度、加速度、jerk 的 Path 对象，失败返回 None。
    """
    # 1) Hybrid A* 规划
    path = hybrid_astar_planning(
        sx, sy, syaw,
        gx, gy, gyaw,
        ox, oy,
        xyreso, yawreso,
        time_limit=time_limit
    )
    if path is None:
        # print("[plan_with_speed] Hybrid A* 规划失败")
        return None

    # 2) 重采样
    try:
        path = resample_path(path, N_resample, preserve_shifts=preserve_shifts)
    except Exception as e:
        # print(f"[plan_with_speed] 重采样失败: {e}")
        return None

    # 3) 速度规划
    path = speed_profile_with_asymmetric_limits(
        path,
        v_max_global=v_max_global,
        a_lat_max=a_lat_max,
        a_acc_max=a_acc_max,
        a_dec_max=a_dec_max,
        j_max=j_max,
        gamma=gamma
    )
    return path

def HA_path(map_path, test_start_list, test_goal_list, in_path_flags, path_fig_dir, cusp_type, need_plot=False):
    print("start!") 

    # 读取地图数据
    _, height, width, obstacles = read_grid_map(map_path)
    print("height:", height)
    print("width:", width)
    print("maxc:", math.tan(C.MAX_STEER) / C.WB)
    print("max_steer:", np.arctan(C.MAX_C*C.WB))

    # 生成障碍物点列表
    ox, oy = [], []
    for (x, y) in obstacles.keys():
        ox.append(x)
        oy.append(y)
    #增加地图边界
    for i in range(width):
        ox.append(i)
        oy.append(0)
        ox.append(i)
        oy.append(height-1)
    for i in range(height):
        ox.append(0)
        oy.append(i)
        ox.append(width-1)
        oy.append(i)

    paths = []

    for idx, (start, goal) in enumerate(zip(test_start_list, test_goal_list)):
        print(f"Test case {idx} ")

        sx, sy, syaw0 = start
        gx, gy, gyaw0 = goal

        t0 = time.time()
        path = hybrid_astar_planning(
            sx, sy, syaw0, gx, gy, gyaw0,
            ox, oy, C.XY_RESO, C.YAW_RESO,cusp_type=cusp_type,
            in_path_flag = in_path_flags[idx], time_limit = C.TIME_LIMIT
        )
        if not path:
            print(f"Test case {idx} fail")
            continue
        path = resample_path(path, N=128, preserve_shifts=True)

        t1 = time.time()

        # 2) 做速度规划（传入物理限幅参数）
        path = speed_profile_with_asymmetric_limits(
            path,
            v_max_global=6.0,
            a_lat_max=4.0,
            a_acc_max=2.0,
            a_dec_max=2.0,
            j_max=2.0,
            gamma=5e-1
        )

        print("running T:", t1 - t0)
        paths.append(path)
        print("Done!")
        if not path:
            print("  Searching failed!")
            continue

        x, y, yaw, direction, t = path.x, path.y, path.yaw, path.direction, path.t

        if not need_plot:
            continue

        # 2) 外部可视化
        if C.ANIMATE:
            # 动画模式：逐步显示
            for k in range(len(x)):
                plt.cla()
                # 绘制障碍物
                plt.plot(ox, oy, "sk", markersize=2)
                # 绘制全路径
                plt.plot(x, y, "o", markersize=1.5)

                # 计算当前舵角
                if k < len(x) - 2:
                    dy = (yaw[k + 1] - yaw[k]) / C.MOVE_STEP
                    steer = rs.pi_2_pi(math.atan2(-C.WB * dy, direction[k]))
                else:
                    steer = 0.0

                # 画终点与车辆
                draw_car(gx, gy, gyaw0, 0.0, 'dimgray')
                draw_car(x[k], y[k], yaw[k], steer)
                plt.title(f"Hybrid A* - Case {idx + 1}")
                plt.axis("equal")
                plt.pause(0.0001)

            # plt.show()

        else:
            # 假设已有以下变量：
            # ox, oy      障碍物坐标列表
            # x, y, yaw   路径点坐标与航向（弧度制）
            # path.v      速度列表

            # 1) 静态图 + 速度色带
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.plot(ox, oy, "sk", markersize=1)

            v = np.array(path.v)  # len == len(x)
            points = np.vstack([x, y]).T  # shape (N,2)
            segs = np.concatenate([points[:-1, None, :],
                                   points[1:, None, :]],
                                  axis=1)  # (N-1, 2, 2)

            lc = LineCollection(segs,
                                cmap="viridis",
                                norm=plt.Normalize(v.min(), v.max()),
                                linewidth=1.5)
            lc.set_array(v[:-1])
            ax.add_collection(lc)

            cbar = fig.colorbar(lc, ax=ax)
            cbar.set_label("Speed [m/s]")

            # # 2) 航向箭头 (quiver) 其实是车头朝向
            # # 每隔 step 个点画一个箭头，避免过密
            # step = max(1, len(x) // 20)
            # # 箭头方向由 yaw 给出，长度 scale 可调
            # ax.quiver(
            #     x[::step],  # 起点 x
            #     y[::step],  # 起点 y
            #     np.cos(yaw[::step]),  # 箭头在 x 方向的分量
            #     np.sin(yaw[::step]),  # 箭头在 y 方向的分量
            #     color="red",
            #     width=0.005,
            #     scale=20,
            #     label="heading"
            # )

            draw_car(gx, gy, gyaw0, 0.0, color="dimgray")
            draw_car(x[-1], y[-1], yaw[-1], 0.0, color="black")

            ax.set_title(f"Hybrid A* — idx {idx}, path_time:{path.t[-1]} ")
            ax.set_aspect('equal', 'datalim')
            ax.set_xlabel("X [m]")
            ax.set_ylabel("Y [m]")

            savefig_path = os.path.join(path_fig_dir, f"hybrid_a_star_case_{idx}_yaw.png")
            plt.savefig(savefig_path, dpi=300)
            plt.close()
            # plt.show()

        t1 = time.time()
        print("running T:", t1 - t0)
    
    return paths


if __name__ == '__main__':
    dir_parent = os.path.dirname(os.path.dirname(__file__))
    map_path = os.path.join(dir_parent, 'MVTP_2.json')
    path_fig_dir = os.path.join(dir_parent, 'path_figs')
    # 限制人字尖点方向, left为左前方、right为右前方、both为不限制
    cusp_type = "left"
    # 定义测试起点和终点
    test_start_list = [
        [240.0,60.0,np.deg2rad(180.0)],
        [52.0,60.0,np.deg2rad(0.0)]
    ]

    test_goal_list = [
        [52.0,70.0,np.deg2rad(0.0)],
        [250.0, 50.0, np.deg2rad(0.0)]
    ]
    in_path_flags = [True, False]

    paths = HA_path(map_path, test_start_list, test_goal_list, in_path_flags, path_fig_dir, cusp_type, need_plot=False)
