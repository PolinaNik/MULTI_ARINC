"""Скрипт парсинга для ОРЛ-А"""

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

root.title("Парсинг для ОРЛ-А")
root.filename = filedialog.askopenfilename(initialdir="/", title="ВЫБЕРИТЕ ARINC для международных трасс")
begin_time = datetime.datetime.today()

print('_____НАЧАЛО_____Разбор файла ARINC %s' % root.filename1)

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
inside_points = list(modules.inside_radar(points))

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

def counter_of_points(routes):
    for key, group in groupby(routes, lambda x: x[0]):
        for i,each in enumerate(group, start=1):
            yield "{}".format(key), "{}".format(each[1]), "{}".format(each[2]),"{}".format(i), "{}".format(each[3])

more2 = list(counter_of_points(more2))

lenght1 = len(int_)
lenght2 = len(more2)
print('Найдено %s трасс в документе ARINC, только %s находятся в зоне ответсвенности' % (lenght1, lenght2))


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

new = []
for x in add_routes:
    test = []
    test.append(x[0][0])
    for i in x:
        test.append(i[4])
        test.append(i[1])
    new.append(test)

routes_add = []
for x in new:
    test = []
    names = x[2::2]
    points = x[1::2]
    test.append("# N1 K1 L2 C25 O1 S1 W3 F7 A25 %s;\n" % x[0])
    for q in range(len(names)):
        name= names[q]
        point = points[q]
        coord = '<' + point[1:3] + ' ' + point[3:5] + ' ' + point[5:7] +', ' + point[10:13] + ' ' + point[13:15] + ' ' + point[15:17] + "'%s'" %name+'>\n'
        test.append(coord)
    routes_add.append(test)

test = []
for i in range(len(routes_add)):
    line = routes_add[i]
    new = ''.join(line)
    test.append(new)

sample = config.sample
sample = sample.readlines()

now = datetime.datetime.now()
now = now.strftime("%d.%m.%Y")
filename = 'map_'+now+'.mp'

with open('%s%s' % (config.locator_map, filename), 'w', encoding="cp1251") as r:
    for item in sample:
        r.write('%s' %item)


with open('%s%s' % (config.locator_map, filename), 'a+', encoding='cp1251') as r:
    for item in test:
        r.write('%s\n' %item)

points_add = []

for x in only_in_trass_points:
    test = []
    test.append("# N4 K1 L0 C25 O1 S4 W1 F0 A25 ' %s;\n" %x[0])
    coord = '<' + x[1][1:3] + ' ' + x[1][3:5] + ' ' + x[1][5:7] +', ' + x[1][10:13] + ' ' + x[1][13:15] + ' ' + x[1][15:17] + '>\n'
    test.append(coord)
    test.append("# N5 K1 L0 C25 O1 S4 W1 F0 A25 ;\n")
    test.append(coord)
    points_add.append(test)

test = []

for i in range(len(points_add)):
    line = points_add[i]
    new = ''.join(line)
    test.append(new)

with open('%s%s' % (config.locator_map, filename), 'a+', encoding='cp1251') as r:
    for item in test:
        r.write('%s\n' %item)

print('Файл с картографией для ОРЛ-А сформирован')

root.destroy()