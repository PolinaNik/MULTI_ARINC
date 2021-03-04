"""Скрипт парсинга для КОРИНФ"""

import re
import math
from itertools import groupby
from itertools import chain
from tkinter import filedialog
from tkinter import *
import datetime

import modules
import config


# Создаем окно приложения
root = Tk()
root.withdraw()
root.title("Парсинг для КОРИНФ на АРМах ЗКП")
root.filename = filedialog.askopenfilename(initialdir="%s" % config.arinc_files, title="ВЫБЕРИТЕ ARINC для международных трасс")
begin_time = datetime.datetime.today()

print('_____НАЧАЛО_____Разбор файла ARINC %s' % root.filename)

pat = re.compile(r'(\d+)+?')
version = pat.search(root.filename).group()

# Выбор нужного файла
text = open('%s' % root.filename, 'r', encoding='utf-8').readlines()
all_points = list(modules.get_points(text))

"""Выбор только имени и коррдинаты точки, за исключением точки с координатами Хабаровска 
(это нужно для исключения дальнейших ошибок при рассчетах)"""
points = list(modules.get_data(all_points))

points = list(modules.unique(points))

length = len(points)
print('Найдено %s точек в файле ARINC' % length)

# Сравнение точек из файла ARINC с зоной полигона
inside_points = list(modules.inside_kor(points))

length2 = len(inside_points)
print('Из %s точек ARINC, только %s в зоне ответственности' % (length, length2))

routes = list(modules.get_routes(text))

def get_route_info(list1_r):
    for i in range(len(list1_r)):
        line = list1_r[i]
        name = line[13:18]
        point = line[29:34]
        number = int(line[26:28])
        pat = re.compile(r'[^\s]+')
        s = pat.search(name)
        s2 = pat.search(point)
        name = s.group()
        point = s2.group()
        ind = line[34:36]
        yield name, point, ind, number

int_ = list(get_route_info(routes))

def select_routes(routes, inside_points):
    for i in range(len(routes)):
        line = routes[i]
        route = line[0]
        point = line[1]
        ind = line[2]
        for q in range(len(inside_points)):
            line2 = inside_points[q]
            point2 = line2[0]
            ind2 = line2[2]
            coord = line2[1]
            if point == point2 and ind == ind2:
                yield route, point, ind, coord, line[3]

filtred_routes = list(select_routes(int_, inside_points))
filtred_routes = list(modules.unique(filtred_routes))
filtred_routes = sorted(filtred_routes, key=lambda x: x[0])

filtred_routes = [list(g) for k, g in groupby(filtred_routes, lambda s: s[0])]
more2 = list(modules.count_list(filtred_routes))
more2 = list(chain.from_iterable(more2))

lenght1 = len(int_)
lenght2 = len(filtred_routes)
print('Найдено %s трасс в документе ARINC, только %s находятся в зоне ответсвенности' % (lenght1, lenght2))

def counter_of_points(routes):
    for key, group in groupby(routes, lambda x: x[0]):
        for i,each in enumerate(group, start=1):
            yield "{}".format(key), "{}".format(each[1]), "{}".format(each[2]),"{}".format(i), "{}".format(each[3])

more2 = list(counter_of_points(more2))

#Формируем слой с точками, которые участвуют в трассах (ничего лишнего)
only_in_trass_points = []
for x in more2:
    new = []
    new.append(x[1])
    new.append(x[4])
    new.append(x[2])
    new = tuple(new)
    only_in_trass_points.append(new)
    new = []

only_in_trass_points = list(modules.unique(only_in_trass_points))
add_routes = [list(g) for k, g in groupby(more2, lambda s: s[0])]

def make_pairs(lst):
    for i in range(len(lst)):
        line = lst[i]
        route = line[0][0]
        output = [(route, line[q][1], line[q][4], line[q+1][1], line[q+1][4]) for q in range(len(line)-1)]
        yield output

pairs = list(make_pairs(add_routes))

def calculate_midpoint(lst):
    for i in range(len(lst)):
        line = lst[i]
        for q in range(len(line)):
            info = line[q]
            route = info[0]
            f1 = math.radians(int(info[2][1:3]) + int(info[2][3:5]) / 60 + int(info[2][5:7]) / 3600)
            f2 = math.radians(int(info[4][1:3]) + int(info[4][3:5]) / 60 + int(info[4][5:7]) / 3600)
            l1 = math.radians(int(info[2][10:13]) + int(info[2][13:15]) / 60 + int(info[2][15:17]) / 3600)
            l2 = math.radians(int(info[4][10:13]) + int(info[4][13:15]) / 60 + int(info[4][15:17]) / 3600)
            dl = l2 - l1
            Bx = math.cos(f2) * math.cos(dl)
            By = math.cos(f2) * math.sin(dl)
            fm = math.atan2(math.sin(f1) + math.sin(f2), math.sqrt((math.cos(f1) + Bx) ** 2 + By ** 2))
            lm = l1 + math.atan2(By, math.cos(f1) + Bx)
            yield route, f1, l1, fm, lm
            yield route, fm, lm, f2, l2


midpoints = list(calculate_midpoint(pairs))

def more_midpoints(lst):
    for i in range(len(lst)):
        line = lst[i]
        f1 = line[1]
        l1 = line[2]
        f2 = line[3]
        l2 = line[4]
        dl = l2 - l1
        Bx = math.cos(f2) * math.cos(dl)
        By = math.cos(f2) * math.sin(dl)
        fm = math.atan2(math.sin(f1) + math.sin(f2), math.sqrt((math.cos(f1) + Bx) ** 2 + By ** 2))
        lm = l1 + math.atan2(By, math.cos(f1) + Bx)
        yield line[0], f1, l1, fm, lm
        yield line[0], fm, lm, f2, l2

midpoints2 = list(more_midpoints(midpoints))
midpoints3 = list(more_midpoints(midpoints2))
midpoints4 = list(more_midpoints(midpoints3))
midpoints5 = list(more_midpoints(midpoints4))

def transform_coord(f,l):
    f = math.degrees(f)
    l = math.degrees(l)
    f_gr = math.trunc(f)
    l_gr = math.trunc(l)
    f_min = math.trunc((f - f_gr) * 60)
    l_min = math.trunc((l - l_gr) * 60)
    f_sec = math.trunc(((f - f_gr) * 60 - f_min) * 60)
    l_sec = math.trunc(((l - l_gr) * 60 - l_min) * 60)
    f_gr = str(f_gr).rjust(2, '0')
    l_gr = str(l_gr).rjust(3, '0')
    f_min = str(f_min).rjust(2, '0')
    l_min = str(l_min).rjust(2, '0')
    f_sec = str(f_sec).rjust(2, '0')
    l_sec = str(l_sec).rjust(2, '0')
    f = f_gr + f_min + f_sec + 'N'
    l = l_gr + l_min + l_sec + 'E'
    coord = f + ' ' + l
    return coord

def destination_point(f1, l1, az, d):
    rad = 6372795
    b = d/rad
    f2 = math.asin(math.sin(f1)*math.cos(b)+math.cos(f1)*math.sin(b)*math.cos(az))
    l2 = l1 + math.atan2(math.sin(az)*math.sin(b)*math.cos(f1), math.cos(b)-math.sin(f1)*math.sin(f2))
    return transform_coord(f2, l2)


def calculate_coridors(lst):
    for i in range(len(lst)):
        line = lst[i]
        rad = 6372795
        b = 5000/rad
        f1 = line[1]
        l1 = line[2]
        f2 = line[3]
        l2 = line[4]
        y = math.sin(l2 - l1) * math.cos(f2)
        x = math.cos(f1) * math.sin(f2) - math.sin(f1) * math.cos(f2) * math.cos(l2 - l1)
        az = math.degrees(math.atan2(y, x))
        front = math.radians(((az-90)+360)%360)
        back = math.radians(((az+90)+360)%360)
        yield line[0], destination_point(f1, l1, front, 5000), destination_point(f2, l2, front, 5000), destination_point(f2, l2, back, 5000), destination_point(f1,l1, back, 5000)


coridors = list(calculate_coridors(midpoints3))
coridors = [list(g) for k, g in groupby(coridors, lambda s: s[0])]

def gen_names(lst):
    for i in range(len(lst)):
        line = lst[i]
        for q in range(len(line)):
            info = line[q]
            points = info[1:]
            for t in range(len(points)):
                coord = points[t]
                name = 'p_'+str(i)+'_'+str(q)+'_'+str(t)
                string = '1 ' + name + ' 0 ' + coord
                yield string

def gen_routes(lst):
    for i in range(len(lst)):
        line = lst[i]
        for q in range(len(line)):
            info = line[q]
            points = info[1:]
            for t in range(len(points)):
                coord = points[t]
                name = 'p_'+str(i)+'_'+str(q)+'_'+str(t)
                yield q, name

list_points= list(gen_names(coridors))
list_routes = list(gen_routes(coridors))
list_routes = [list(g) for k, g in groupby(list_routes, lambda s: s[0])]

def create_polygons(lst):
    for i in range(len(lst)):
        line = lst[i]
        start1 = 'Полигон (индекс 6)'
        start2 = '6 0 128 128 128 128 128 128 0'
        yield start1
        yield start2
        for q in range(len(line)):
            info = line[q]
            marker = '7 '+info[1]
            yield marker

polygon_all = list(create_polygons(list_routes))

def add_coridor(lst):
    for i in range(len(lst)):
        line = lst[i]
        string1 = '2 ' +line[0][1]+ ' ' + line[1][1]+' 0 11'
        string2 = '2 ' + line[2][1] + ' ' + line[3][1] + ' 0 11'
        yield string1
        yield string2

coridor_all = list(add_coridor(list_routes))

def write_trass(lst):
    for i in range(len(lst)):
        line = lst[i]
        for q in range(len(line)):
            info = line[q]
            string = '2 '+info[1]+' '+info[3]+' 2 12'
            yield string


trass_all = list(write_trass(pairs))

trass_info = '0 Трассы\nЛиний 227; ПОДов 0; дуг 0; окружностей 0\nЛинии(индекс 2): всего 227\nID(2) начало конец тип цвет\n'

RZ_info = open('%ssamples/sample_RZ.txt' %config.program_files, 'r', encoding='utf-8')
RZ_info = RZ_info.readlines()

with open('%sexport.all' %config.korinf_files, 'w', encoding='cp1251') as one:
    for i in RZ_info:
        one.write(i)


with open('%sexport.all' %config.korinf_files, 'a+', encoding='cp1251') as one:
    one.write(trass_info)

with open('%sexport.all' % config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in trass_all:
        one.write('%s\n' %i)

coridor_info1 = '0 Коридоры\nЛиний 1275; ПОДов 0; дуг 0; окружностей 0\nЛинии(индекс 2): всего 1275\nID(2) начало конец тип цвет\n'

with open('%sexport.all' %config.korinf_files, 'a+', encoding='cp1251') as one:
    one.write(coridor_info1)

with open('%sexport.all' % config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in coridor_all:
        one.write('%s\n' %i)

polygon_info = '0 Коридоры заштрихованные\nЛиний 0; ПОДов 0; дуг 0; окружностей 0\n'

with open('%sexport.all' %config.korinf_files, 'a+', encoding='cp1251') as one:
    one.write(polygon_info)

with open('%sexport.all' % config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in polygon_all:
        one.write('%s\n' %i)

aero_info = open('%ssamples/sample_aero.txt' %config.program_files, 'r')
aero_info = aero_info.readlines()

with open('%sexport.all' % config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in aero_info:
        one.write(i)

VC_info = open('%ssamples/sample_VC.txt' %config.program_files, 'r')
VC_info = VC_info.readlines()

with open('%sexport.all' % config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in VC_info:
        one.write(i)

routes_info = open('%ssamples/sample_routes.txt' %config.program_files, 'r')
routes_info = routes_info.readlines()

with open('%sexport.all' % config.program_files, 'a+', encoding='cp1251') as one:
    for i in routes_info:
        one.write(i)

points_info = 'Точки(индекс 1): всего 1714\nID(1) имя тип широта долгота\n'

def trass_points(lst):
    for i in range(len(lst)):
        line = lst[i]
        for q in range(len(line)):
            info = line[q]
            point1 = info[1]
            coord1 = info[2][1:7]+'N '+info[2][10:17]+'E'
            string1 = '1 '+point1+' 6 '+coord1
            point2 = info[3]
            coord2 = info[4][1:7] + 'N ' + info[4][10:17] + 'E'
            string2 = '1 ' + point2 + ' 6 ' + coord2
            yield string1
            yield string2

all_points_add = list(trass_points(pairs))
all_points_add = list(modules.unique(all_points_add))


# # Точки ПОД и ПДЗ
# pod = config.pod
# pdz = config.pdz
#
# pod_points = []
# for x in inside_points:
#     if x[0] in pod:
#         pod_points.append(x)
#
# pdz_points = []
# for x in inside_points:
#     if x[0] in pdz:
#         pdz_points.append(x)

pod_info = '0 Точки\nЛиний 0; ПОДов 175; дуг 0; окружностей 0\nПОДы(индекс 3): всего 175\nID(3) имя флаг цвет x-смещение y-смещение имя2\n'
pod_info2 = '0 Названия точек\nЛиний 0; ПОДов 176; дуг 0; окружностей 0\nПОДы(индекс 3): всего 176\nID(3) имя флаг цвет x-смещение y-смещение имя2\n'

def add_pod_points(lst):
    for i in range(len(lst)):
        line = lst[i]
        string = '3 '+line[0]+' 0 11 0 0 '+line[0]
        yield string

def add_pod_points2(lst):
    for i in range(len(lst)):
        line = lst[i]
        string = '3 '+line[0]+' 1 11 0 0 '+line[0]
        yield string

pod_points_list = list(add_pod_points(inside_points))
pod_points_list2 = list(add_pod_points2(inside_points))

# pdz_points_list = list(add_pod_points(pdz_points))
# pdz_points_list2 = list(add_pod_points2(pdz_points))

with open('%sexport.all' %config.korinf_files, 'a+', encoding='cp1251') as one:
    one.write(pod_info)

with open('%sexport.all' %config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in pod_points_list:
        one.write('%s\n' %i)

# with open('%sexport.all' %config.korinf_map, 'a+', encoding='cp1251') as one:
#     for i in pdz_points_list:
#         one.write('%s\n' %i)

with open('%sexport.all' %config.korinf_files, 'a+', encoding='cp1251') as one:
    one.write(pod_info2)

with open('%sexport.all' %config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in pod_points_list2:
        one.write('%s\n' %i)

# with open('%sexport.all' %config.korinf_map, 'a+', encoding='cp1251') as one:
#     for i in pdz_points_list:
#         one.write('%s\n' %i)

with open('%sexport.all' %config.korinf_files, 'a+', encoding='cp1251') as one:
    one.write(points_info)

with open('%sexport.all' % config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in list_points:
        one.write('%s\n' %i)

with open('%sexport.all' % config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in all_points_add:
        one.write('%s\n' %i)

def get_pod_coords(lst):
    for i in range(len(lst)):
        line = lst[i]
        string = '1 '+line[0]+' 6 '+line[1][1:7]+'N '+line[1][10:17]+'E'
        yield string

def get_pdz_coords(lst):
    for i in range(len(lst)):
        line = lst[i]
        string = '1 '+line[0]+' 5 '+line[1][1:7]+'N '+line[1][10:17]+'E'
        yield string

pod_coords = list(get_pod_coords(inside_points))
# pdz_coords = list(get_pod_coords(pdz_points))

with open('%sexport.all' % config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in pod_coords:
        one.write('%s\n' %i)

# pdz_coords = list(get_pdz_coords(pdz_points))

# with open('%sexport.all' % config.korinf_map, 'a+', encoding='cp1251') as one:
#     for i in pdz_coords:
#         one.write('%s\n' %i)

RZ_points = open('%ssamples/sample_RZ_points.txt' %config.program_files, 'r')
RZ_points = RZ_points.readlines()

with open('%sexport.all' %config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in RZ_points:
        one.write(i)

aero_points = open('%ssamples/sample_aero_points.txt' %config.program_files, 'r')
aero_points = aero_points.readlines()

with open('%sexport.all' %config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in aero_points:
        one.write(i)

VC_points = open('%ssamples/sample_VC_points.txt' %config.program_files, 'r')
VC_points = VC_points.readlines()

with open('%sexport.all' %config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in VC_points:
        one.write(i)

routes_points = open('%ssamples/sample_routes_points.txt' %config.program_files, 'r')
routes_points = routes_points.readlines()

with open('%sexport.all' %config.korinf_files, 'a+', encoding='cp1251') as one:
    for i in routes_points:
        one.write(i)

print('Файл с картографией для КОРИНФ сформирован')

root.destroy()