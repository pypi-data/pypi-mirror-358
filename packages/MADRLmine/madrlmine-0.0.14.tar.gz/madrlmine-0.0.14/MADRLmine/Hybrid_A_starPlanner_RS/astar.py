import heapq
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import binary_dilation


class Node:
    def __init__(self, x, y, cost, pind):
        self.x = x  # x position of node
        self.y = y  # y position of node
        self.cost = cost  # g cost of node
        self.pind = pind  # parent index of node


class Para:
    def __init__(self, minx, miny, maxx, maxy, xw, yw, reso, motion):
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
        self.xw = xw
        self.yw = yw
        self.reso = reso  # resolution of grid world
        self.motion = motion  # motion set


def astar_planning(sx, sy, gx, gy, ox, oy, reso, rr):
    """
    return path of A*.
    :param sx: starting node x [m]
    :param sy: starting node y [m]
    :param gx: goal node x [m]
    :param gy: goal node y [m]
    :param ox: obstacles x positions [m]
    :param oy: obstacles y positions [m]
    :param reso: xy grid resolution
    :param rr: robot radius
    :return: path
    """

    n_start = Node(round(sx / reso), round(sy / reso), 0.0, -1)
    n_goal = Node(round(gx / reso), round(gy / reso), 0.0, -1)

    ox = [x / reso for x in ox]
    oy = [y / reso for y in oy]

    P, obsmap = calc_parameters(ox, oy, rr, reso)

    open_set, closed_set = dict(), dict()
    open_set[calc_index(n_start, P)] = n_start

    q_priority = []
    heapq.heappush(q_priority,
                   (fvalue(n_start, n_goal), calc_index(n_start, P)))

    while True:
        if not open_set:
            break

        _, ind = heapq.heappop(q_priority)
        n_curr = open_set[ind]
        closed_set[ind] = n_curr
        open_set.pop(ind)

        for i in range(len(P.motion)):
            node = Node(n_curr.x + P.motion[i][0],
                        n_curr.y + P.motion[i][1],
                        n_curr.cost + u_cost(P.motion[i]), ind)

            if not check_node(node, P, obsmap):
                continue

            n_ind = calc_index(node, P)
            if n_ind not in closed_set:
                if n_ind in open_set:
                    if open_set[n_ind].cost > node.cost:
                        open_set[n_ind].cost = node.cost
                        open_set[n_ind].pind = ind
                else:
                    open_set[n_ind] = node
                    heapq.heappush(q_priority,
                                   (fvalue(node, n_goal), calc_index(node, P)))

    pathx, pathy = extract_path(closed_set, n_start, n_goal, P)

    return pathx, pathy


import heapq
import numpy as np

def calc_holonomic_heuristic_with_obstacle(node, ox, oy, reso, rr):
    """
    在栅格上做 8 连通 Dijkstra，返回 hmap.tolist()
    node: 目标 Node，ox/oy: 障碍物世界坐标列表，
    reso: 栅格分辨率，rr: 机器人半径（用于障碍膨胀）
    """
    # 1) 障碍物 & 目标点 转栅格坐标
    xs = np.array(ox, dtype=np.float32) / reso
    ys = np.array(oy, dtype=np.float32) / reso
    gx = int(round(node.x[-1] / reso))
    gy = int(round(node.y[-1] / reso))

    # 2) 计算边界 & 分配数组
    x_min, x_max = math.floor(xs.min()), math.ceil(xs.max())
    y_min, y_max = math.floor(ys.min()), math.ceil(ys.max())
    W, H = x_max - x_min + 1, y_max - y_min + 1

    # 3) 构建二值障碍栅格并膨胀
    occ = np.zeros((W, H), dtype=bool)
    ix = np.clip((xs - x_min).astype(int), 0, W - 1)
    iy = np.clip((ys - y_min).astype(int), 0, H - 1)
    occ[ix, iy] = True
    if rr > 0:
        rad = int(math.ceil(rr / reso))
        occ = binary_dilation(occ, structure=np.ones((2*rad+1,2*rad+1)))

    # 4) 初始化 cost 与 visited
    INF = np.inf
    cost = np.full((W, H), INF, dtype=np.float32)
    vis  = np.zeros((W, H), dtype=bool)
    sgx, sgy = gx - x_min, gy - y_min
    cost[sgx, sgy] = 0.0

    # 8 连通 & 对角线权值
    motions = [
        ( 1, 0, 1.0), (-1, 0, 1.0),
        ( 0, 1, 1.0), ( 0,-1, 1.0),
        ( 1, 1, math.sqrt(2)), ( 1,-1, math.sqrt(2)),
        (-1, 1, math.sqrt(2)), (-1,-1, math.sqrt(2))
    ]
    hq = [(0.0, sgx, sgy)]

    # 5) Dijkstra 波前传播
    while hq:
        c, x, y = heapq.heappop(hq)
        if vis[x, y]:
            continue
        vis[x, y] = True

        for dx, dy, dc in motions:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < W and 0 <= ny < H):
                continue
            if occ[nx, ny]:
                continue
            nc = c + dc
            if nc < cost[nx, ny]:
                cost[nx, ny] = nc
                heapq.heappush(hq, (nc, nx, ny))

    # 6) 转回 Python list of list
    return cost.tolist()

def check_node(node, P, obsmap):
    if node.x <= P.minx or node.x >= P.maxx or \
            node.y <= P.miny or node.y >= P.maxy:
        return False

    if obsmap[node.x - P.minx][node.y - P.miny]:
        return False

    return True


def u_cost(u):
    return math.hypot(u[0], u[1])


def fvalue(node, n_goal):
    return node.cost + h(node, n_goal)


def h(node, n_goal):
    return math.hypot(node.x - n_goal.x, node.y - n_goal.y)


def calc_index(node, P):
    return (node.y - P.miny) * P.xw + (node.x - P.minx)


def calc_parameters(ox, oy, rr, reso):
    minx, miny = round(min(ox)), round(min(oy))
    maxx, maxy = round(max(ox)), round(max(oy))
    xw, yw = maxx - minx, maxy - miny

    motion = get_motion()
    P = Para(minx, miny, maxx, maxy, xw, yw, reso, motion)
    obsmap = calc_obsmap(ox, oy, rr, P)

    return P, obsmap


def calc_obsmap(ox, oy, rr, P):
    obsmap = [[False for _ in range(P.yw)] for _ in range(P.xw)]

    for x in range(P.xw):
        xx = x + P.minx
        for y in range(P.yw):
            yy = y + P.miny
            for oxx, oyy in zip(ox, oy):
                if math.hypot(oxx - xx, oyy - yy) <= rr / P.reso:
                    obsmap[x][y] = True
                    break

    return obsmap


def extract_path(closed_set, n_start, n_goal, P):
    pathx, pathy = [n_goal.x], [n_goal.y]
    n_ind = calc_index(n_goal, P)

    while True:
        node = closed_set[n_ind]
        pathx.append(node.x)
        pathy.append(node.y)
        n_ind = node.pind

        if node == n_start:
            break

    pathx = [x * P.reso for x in reversed(pathx)]
    pathy = [y * P.reso for y in reversed(pathy)]

    return pathx, pathy


def get_motion():
    motion = [[-1, 0], [-1, 1], [0, 1], [1, 1],
              [1, 0], [1, -1], [0, -1], [-1, -1]]

    return motion


def get_env():
    ox, oy = [], []

    for i in range(60):
        ox.append(i)
        oy.append(0.0)
    for i in range(60):
        ox.append(60.0)
        oy.append(i)
    for i in range(61):
        ox.append(i)
        oy.append(60.0)
    for i in range(61):
        ox.append(0.0)
        oy.append(i)
    for i in range(40):
        ox.append(20.0)
        oy.append(i)
    for i in range(40):
        ox.append(40.0)
        oy.append(60.0 - i)

    return ox, oy


def main():
    sx = 10.0  # [m]
    sy = 10.0  # [m]
    gx = 50.0  # [m]
    gy = 50.0  # [m]

    robot_radius = 2.0
    grid_resolution = 1.0
    ox, oy = get_env()

    pathx, pathy = astar_planning(sx, sy, gx, gy, ox, oy, grid_resolution, robot_radius)

    plt.plot(ox, oy, 'sk')
    plt.plot(pathx, pathy, '-r')
    plt.plot(sx, sy, 'sg')
    plt.plot(gx, gy, 'sb')
    plt.axis("equal")
    plt.show()


if __name__ == '__main__':
    main()
