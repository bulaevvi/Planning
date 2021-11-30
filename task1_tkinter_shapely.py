from tkinter import *
import math
from shapely.geometry import Polygon
import heapq

# Дискрет, с которым двигаемся в пространстве поиска
# Чем больше дискрет, тем быстрее работает алгоритм, но точность снижается
DISCRETE = 40
# Гиперпараметр для эвристики
ANGLE_COEF = 400 # гиперпараметр для эвристики

"""================= Your classes and methods ================="""

# These functions will help you to check collisions with obstacles

def rotate(points, angle, center):
    angle = math.radians(angle)
    cos_val = math.cos(angle)
    sin_val = math.sin(angle)
    cx, cy = center
    new_points = []

    for x_old, y_old in points:
        x_old -= cx
        y_old -= cy
        x_new = x_old * cos_val - y_old * sin_val
        y_new = x_old * sin_val + y_old * cos_val
        new_points.append((x_new + cx, y_new + cy))

    return new_points

def get_polygon_from_position(position):
    x, y, yaw = position
    points = [(x - 50, y - 100), (x + 50, y - 100), (x + 50, y + 100), (x - 50, y + 100)]
    # new_points = rotate(points, yaw, (x,y))
    # Согласно посту в дискорде от Dasha Pankratova
    new_points = rotate(points, yaw * 180 / math.pi, (x, y))
    return Polygon(new_points)

def get_polygon_from_obstacle(obstacle):
    points = [(obstacle[0], obstacle[1]), (obstacle[2], obstacle[3]), (obstacle[4], obstacle[5]), (obstacle[6], obstacle[7])] 
    return Polygon(points)

def collides(position, obstacle):
    return get_polygon_from_position(position).intersection(get_polygon_from_obstacle(obstacle))

# Очередь с приоритетом (будет использоваться в алгоритме построения траектории)
# Модификация этого кода https://programmathically.com/priority-queue-and-heapq-in-python/
class PriorityQueue:
    def __init__(self):
        self.elements = []
        self.length = 0

    def isEmpty(self):
        return len(self.elements) == 0    

    def push(self, element, priority):
        data = (priority, self.length, element)
        self.length += 1
        heapq.heappush(self.elements, data)

    def pop(self):
        (_, _, element) = heapq.heappop(self.elements)
        return element

# Эвристика, которая будет использоваться в алгоритме построения траектории
def heuristic(position, target_position):
    current_x, current_y, current_yaw = position    
    target_x, target_y, target_yaw = target_position
    diff_x, diff_y = target_x - current_x, target_y - current_y
    # С Манхэттонской метрикой более прямолинейная траектория, но с ней тяжелее вписываться в повороты
    #distance = abs(diff_x) + abs(diff_y)
    # С Евклидовой метрикой получается более естественная сглаженная траектория, но она чуть длиннее
    distance = math.hypot(diff_x, diff_y)
    if diff_y == 0:
        if diff_x >= 0:
            angle = math.pi
        else:
            angle = -math.pi
    else:
        angle = math.atan(abs(diff_x / diff_y))
        if (diff_x >= 0) and (diff_y >= 0):
            angle = math.pi - angle
        elif (diff_x < 0) and (diff_y >= 0):
            angle = angle - math.pi
        elif (diff_x >= 0) and (diff_y < 0):
            angle = angle
        else:
            angle = -angle
    kappa = abs(angle - target_yaw)
    if kappa > math.pi:
        kappa = abs(kappa - 2 * math.pi)
    return ANGLE_COEF * kappa + distance
   


class Window:

    """================= Your Main Function ================="""

    def go(self, event):
        # Write your code here
        print("Start position:", self.get_start_position())
        print("Target position:", self.get_target_position())
        print("Obstacles:", self.get_obstacles())
        
        # Example of collision calculation
        number_of_collisions = 0
        for obstacle in self.get_obstacles() :
            if collides(self.get_start_position(), obstacle) :
                number_of_collisions += 1
        print("Start position collides with", number_of_collisions, "obstacles")

        # Запускаем поиск
        print('Calculating in progress...')        
        route = self.route_planning([self.get_start_position()], DISCRETE)
        # Визуализируем результат
        for i in range(1, len(route)):
            self.canvas.create_line(route[i][0], route[i][1], route[i - 1][0], route[i - 1][1], fill="yellow", width = 4)
        self.canvas.create_text(860, 30, anchor=W, font="Arial", fill = "yellow", text = "Маршрут построен")
        print('Calculation is done!')

    # Алгоритм планирования траектории
    def route_planning(self, route, discrete):
        alternatives = 3
        target_position = self.get_target_position()
        steps = set()
        queue = PriorityQueue()
        queue.push((route[-1], route), heuristic(route[-1], target_position))
        
        while not queue.isEmpty():
            element = queue.pop()
            if (heuristic(element[0], target_position) < discrete + 1):
                route[-1] = target_position
                break
            x, y, yaw = element[0]
            beam_width = math.pi * discrete / 180
            temp = [beam_width / alternatives * i for i in range(alternatives)]
            angles = [x - beam_width / alternatives * ((alternatives - 1) / 2) for x in temp]
            results = []
            
            for angle in angles:
                result_yaw = angle + yaw
                result_x = x + discrete * math.sin(result_yaw)
                result_y = y - discrete * math.cos(result_yaw)
                collisions = 0
                for obstacle in self.get_obstacles():
                    if collides([result_x, result_y, result_yaw], obstacle):
                        collisions += 1
                if collisions > 0:
                    continue
                results.append([result_x, result_y, result_yaw])
            
            for step in results:
                if (round(step[0], 1), round(step[1], 1), round(step[2], 1)) in steps:
                    continue
                route = element[1][:]
                route.append(step)
                steps.add((round(step[0], 1), round(step[1], 1), round(step[2], 1)))
                priority = discrete * (len(route) + 1) + heuristic(step, target_position)
                queue.push((step, route), priority)
        
        return route


    """================= Interface Methods ================="""

    def get_obstacles(self):
        obstacles = []
        potential_obstacles = self.canvas.find_all()
        for i in potential_obstacles:
            if (i > 2):
                coords = self.canvas.coords(i)
                if coords:
                    obstacles.append(coords)
        return obstacles

    def get_start_position(self):
        x,y = self.get_center(2)  # Purple block has id 2
        yaw = self.get_yaw(2)
        return x,y,yaw

    def get_target_position(self):
        x, y = self.get_center(1)  # Green block has id 1
        yaw = self.get_yaw(1)
        return x, y, yaw

    def get_center(self, id_block):
        coords = self.canvas.coords(id_block)
        center_x, center_y = ((coords[0] + coords[4]) / 2, (coords[1] + coords[5]) / 2)
        return [center_x, center_y]

    def get_yaw(self, id_block):
        center_x, center_y = self.get_center(id_block)
        first_x = 0.0
        first_y = -1.0
        second_x = 1.0
        second_y = 0.0
        points = self.canvas.coords(id_block)
        end_x = (points[0] + points[2]) / 2
        end_y = (points[1] + points[3]) / 2
        direction_x = end_x - center_x
        direction_y = end_y - center_y
        length = math.hypot(direction_x, direction_y)
        unit_x = direction_x / length
        unit_y = direction_y / length
        cos_yaw = unit_x * first_x + unit_y * first_y
        sign_yaw = unit_x * second_x + unit_y * second_y
        if (sign_yaw) >= 0:
            return math.acos(cos_yaw)
        else:
            return -math.acos(cos_yaw)

    def get_vertices(self, id_block):
        return self.canvas.coords(id_block)

    """=================================================="""

    def rotate(self, points, angle, center):
        angle = math.radians(angle)
        cos_val = math.cos(angle)
        sin_val = math.sin(angle)
        cx, cy = center
        new_points = []

        for x_old, y_old in points:
            x_old -= cx
            y_old -= cy
            x_new = x_old * cos_val - y_old * sin_val
            y_new = x_old * sin_val + y_old * cos_val
            new_points.append(x_new + cx)
            new_points.append(y_new + cy)

        return new_points

    def start_block(self, event):
        widget = event.widget
        widget.start_x = event.x
        widget.start_y = event.y

    def in_rect(self, point, rect):
        x_start, x_end = min(rect[::2]), max(rect[::2])
        y_start, y_end = min(rect[1::2]), max(rect[1::2])

        if x_start < point[0] < x_end and y_start < point[1] < y_end:
            return True

    def motion_block(self, event):
        widget = event.widget

        for i in range(1, 10):
            if widget.coords(i) == []:
                break
            if self.in_rect([event.x, event.y], widget.coords(i)):
                coords = widget.coords(i)
                id = i
                break

        res_cords = []
        try:
            coords
        except:
            return

        for ii, i in enumerate(coords):
            if ii % 2 == 0:
                res_cords.append(i + event.x - widget.start_x)
            else:
                res_cords.append(i + event.y - widget.start_y)

        widget.start_x = event.x
        widget.start_y = event.y
        widget.coords(id, res_cords)
        widget.center = ((res_cords[0] + res_cords[4]) / 2, (res_cords[1] + res_cords[5]) / 2)

    def draw_block(self, points, color):
        x = self.canvas.create_polygon(points, fill=color)
        return x

    def distance(self, x1, y1, x2, y2):
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def set_id_block(self, event):
        widget = event.widget

        for i in range(1, 10):
            if widget.coords(i) == []:
                break
            if self.in_rect([event.x, event.y], widget.coords(i)):
                coords = widget.coords(i)
                id = i
                widget.id_block = i
                break

        widget.center = ((coords[0] + coords[4]) / 2, (coords[1] + coords[5]) / 2)

    def rotate_block(self, event):
        angle = 0
        widget = event.widget

        if widget.id_block == None:
            for i in range(1, 10):
                if widget.coords(i) == []:
                    break
                if self.in_rect([event.x, event.y], widget.coords(i)):
                    coords = widget.coords(i)
                    id = i
                    widget.id_block == i
                    break
        else:
            id = widget.id_block
            coords = widget.coords(id)

        wx, wy = event.x_root, event.y_root
        try:
            coords
        except:
            return

        block = coords
        center = widget.center
        x, y = block[2], block[3]

        cat1 = self.distance(x, y, block[4], block[5])
        cat2 = self.distance(wx, wy, block[4], block[5])
        hyp = self.distance(x, y, wx, wy)

        if wx - x > 0: angle = math.acos((cat1**2 + cat2**2 - hyp**2) / (2 * cat1 * cat2))
        elif wx - x < 0: angle = -math.acos((cat1**2 + cat2**2 - hyp**2) / (2 * cat1 * cat2))

        new_block = self.rotate([block[0:2], block[2:4], block[4:6], block[6:8]], angle, center)
        self.canvas.coords(id, new_block)

    def delete_block(self, event):
        widget = event.widget.children["!canvas"]

        for i in range(1, 10):
            if widget.coords(i) == []:
                break
            if self.in_rect([event.x, event.y], widget.coords(i)):
                widget.coords(i, [0, 0])
                break

    def create_block(self, event):
        block = [[0, 100], [100, 100], [100, 300], [0, 300]]

        id = self.draw_block(block, "black")

        self.canvas.tag_bind(id, "<Button-1>", self.start_block)
        self.canvas.tag_bind(id, "<Button-3>", self.set_id_block)
        self.canvas.tag_bind(id, "<B1-Motion>", self.motion_block)
        self.canvas.tag_bind(id, "<B3-Motion>", self.rotate_block)

    def make_draggable(self, widget):
        widget.bind("<Button-1>", self.drag_start)
        widget.bind("<B1-Motion>", self.drag_motion)

    def drag_start(self, event):
        widget = event.widget
        widget.start_x = event.x
        widget.start_y = event.y

    def drag_motion(self, event):
        widget = event.widget
        x = widget.winfo_x() - widget.start_x + event.x + 200
        y = widget.winfo_y() - widget.start_y + event.y + 100
        widget.place(rely=0.0, relx=0.0, x=x, y=y)

    def create_button_create(self):
        button = Button(text="New", bg="#555555", activebackground="blue", borderwidth=0)

        button.place(rely=0.0, relx=0.0, x=200, y=100, anchor=SE, width=200, height=100)
        button.bind("<Button-1>", self.create_block)

    def create_green_block(self, center_x):
        block = [[center_x - 50, 100],
                 [center_x + 50, 100],
                 [center_x + 50, 300],
                 [center_x - 50, 300]]

        id = self.draw_block(block, "green")
        self.canvas.tag_bind(id, "<Button-1>", self.start_block)
        self.canvas.tag_bind(id, "<Button-3>", self.set_id_block)
        self.canvas.tag_bind(id, "<B1-Motion>", self.motion_block)
        self.canvas.tag_bind(id, "<B3-Motion>", self.rotate_block)

    def create_purple_block(self, center_x, center_y):
        block = [
                [center_x - 50, center_y - 300],
                [center_x + 50, center_y - 300],
                [center_x + 50, center_y - 100],
                [center_x - 50, center_y - 100]]
        id = self.draw_block(block, "purple")
        self.canvas.tag_bind(id, "<Button-1>", self.start_block)
        self.canvas.tag_bind(id, "<Button-3>", self.set_id_block)
        self.canvas.tag_bind(id, "<B1-Motion>", self.motion_block)
        self.canvas.tag_bind(id, "<B3-Motion>", self.rotate_block)

    def create_button_go(self):
        button = Button(text="Go", bg="#555555", activebackground="blue", borderwidth=0)
        button.place(rely=0.0, relx=1.0, x=0, y=200, anchor=SE, width=100, height=200)
        button.bind("<Button-1>", self.go)

    def run(self):
        root = self.root
        self.create_button_create()
        self.create_button_go()
        self.create_green_block(self.width / 2)
        self.create_purple_block(self.width / 2, self.height)
        root.bind("<Delete>", self.delete_block)
        root.mainloop()

    def __init__(self):
        self.root = Tk()
        self.root.title("")
        self.width  = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.root.geometry("{}x{}".format(self.width, self.height))
        self.canvas = Canvas(self.root, bg="#777777", height=self.height, width=self.width)
        self.canvas.pack()
        # self.points = [0, 500, 500/2, 0, 500, 500]

if __name__ == "__main__":
    run = Window()
    run.run()
