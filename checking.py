"""Скрипт проверки файла ARINC на порядок нумерации"""

import re
import math
from itertools import groupby
from itertools import chain
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
import datetime
import os

import modules
import config


# Создаем окно приложения
root = Tk()
root.withdraw()

root.title("Проверка ARINC")
root.filename = filedialog.askopenfilename(initialdir="%s" % config.arinc_files, title="ВЫБЕРИТЕ ARINC для международных трасс")
begin_time = datetime.datetime.today()


pat = re.compile(r'(\d+)+?')
version = pat.search(root.filename).group()

# Выбор нужного файла
text = open('%s' % root.filename, 'r', encoding='utf-8').readlines()
all_points = list(modules.get_points(text))

"""Выбор только имени и коррдинаты точки, за исключением точки с координатами Хабаровска 
(это нужно для исключения дальнейших ошибок при рассчетах)"""
points = list(modules.get_data(all_points))

points = list(modules.unique(points))

# Сравнение точек из файла ARINC с зоной полигона
inside_points = list(modules.inside(points))

# Получение имен точек
arinc_names = list(modules.names(inside_points))

# Нахождение дубликатов точек ARINC, которые попали в полигон
dup = {}
gen = sorted(modules.list_duplicates(arinc_names))

for x in gen:
    dup.update(x)

# Нахождение индексов дубликатов
list_of_index = list(modules.sep(dup))

indexes = []

for sublist in list_of_index:
    for item in sublist:
        indexes.append(item)

arinc_duplicates = list(modules.sep2(inside_points, indexes))

# Убираем дубликаты по номеру индекса из списка точек ARINC
for element in arinc_duplicates:
    inside_points.remove(element)


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
            yield "{}".format(key), "{}".format(each[1]), "{}".format(each[2]),"{}".format(i), "{}".format(each[3]), "{}".format(each[4])

more2 = list(counter_of_points(more2))
more2 = [list(g) for k, g in groupby(more2, lambda s: s[0])]


def checking_number(lst):
    for i in range(len(lst)):
        line = lst[i]
        out = [(line[q+1][-1], line[q][-1]) for q in range(len(line)-1)]
        out = list(out)
        for r in range(len(out)):
            compare = out[r]
            res = int(compare[0])-int(compare[1])
            if res > 4 and r != len(out)-1:
                yield line[0][0]

res = list(checking_number(more2))

delete_rows = []

for y in more2:
    for x in y:
        if x[0] in res:
            delete_rows.append(x)

delete_rows2 = []
for x in delete_rows:
    lst = []
    if x[2] == 'ZY' or x[5] == 'P' or x[5] == 'PA' or x[5] == 'RJ' or x[5] == 'RK':
        lst.append(x[0])
        lst.append(x[1])
        delete_rows2.append(lst)


text_mes = 'В трассе: %s в середине маршрута нарушена нумерация точек.\nНеобходимо удалить часть маршрута: %s' % (res, delete_rows2)

head, tail = os.path.split(root.filename)

if not res:
    messagebox.showinfo(title='Результат проверки %s' %tail, message='Проблем с нумерацией нет.\nМожно начинать разбор')
else:
    messagebox.showerror(title='Результат проверки %s' %tail, message=text_mes)

root.destroy()




