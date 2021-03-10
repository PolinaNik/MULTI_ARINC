"""Скрипт парсинга для СИНТЕЗА"""

import re
import os
import math
import logging
from itertools import groupby
from itertools import chain
from tkinter import filedialog
from tkinter import *
import transliterate
import xlwt
import datetime
import copy

import modules
import values
import config
import operator

# Пишем в лог
logging.basicConfig(format='%(asctime)s %(message)s', filename='%s/arinc.log' % config.sintez_files,
                    filemode='a')

# Создаем окно приложения
root = Tk()
root.withdraw()
root.title("Парсинг для SINTEZ")
root.filename1 = filedialog.askopenfilename(initialdir="%s" % config.arinc_files, title="ВЫБЕРИТЕ ARINC для международных трасс")
root.filename2 = filedialog.askopenfilename(initialdir="%s" % config.arinc_files, title="ВЫБЕРИТЕ ARINC для МВЛьных трасс трасс")
root.filename3 = filedialog.askopenfilename(initialdir="%s" % config.arinc_files, title="ВЫБЕРИТЕ mysqldump")
begin_time = datetime.datetime.today()

pat = re.compile(r'(\d+)+?')
version = pat.search(root.filename1).group()


# Выбор нужного файла
text1 = open('%s' % root.filename1, 'r', encoding='utf-8').readlines()
text2 = open('%s' % root.filename2, 'r', encoding='utf-8').readlines()
text3 = open('%s' % root.filename3, 'r', encoding='utf-8').readlines()

logging.warning('_____НАЧАЛО_____Разбор файла ARINC %s и %s' % (root.filename1, root.filename2))
print('_____НАЧАЛО_____Разбор файла ARINC %s и %s' % (root.filename1, root.filename2))


frame1 = Frame(root)
frame1.pack()
label1 = Label(frame1, text='TESTTESTTEST')
label1.pack()


# Поиск всех точек в файле ARINC
all_points1 = list(modules.get_points(text1))
all_points2 = list(modules.get_points(text2))

"""Выбор только имени и коррдинаты точки, за исключением точки с координатами Хабаровска 
(это нужно для исключения дальнейших ошибок при рассчетах)"""
points1 = list(modules.get_data(all_points1))
points2 = list(modules.get_data(all_points2))

points1 = list(modules.unique(points1))
points2 = list(modules.unique(points2))

points = points1 + points2

points = list(modules.unique(points))
length = len(points)
logging.warning('Найдено %s точек в файле ARINC' % length)
print('Найдено %s точек в файле ARINC' % length)

# Сравнение точек из файла ARINC с зоной полигона
inside_points = list(modules.inside(points))
inside_for_cartography = copy.deepcopy(inside_points)

length2 = len(inside_points)
logging.warning('Из %s точек ARINC, только %s в зоне ответственности' % (length, length2))
print('Из %s точек ARINC, только %s в зоне ответственности' % (length, length2))

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

# Получение координат точек для дальнешего сравнения с базой
arinc = list(modules.data(inside_points))

output = list(modules.listTosring(arinc_duplicates))
output = list(modules.unique(output))

with open('%s/4.duplicates.txt' % config.sintez_files, 'w') as file2:
    for item in output:
        file2.write("%s\n" % item)

#Получение точек из базы
for x in text3:
    pat = re.compile(r'(INSERT INTO `point` VALUES).+')
    s = pat.search(x)
    if s:
        points_base = s.group()

#Получение трасс из базы
for x in text3:
    pat = re.compile(r'(INSERT INTO `_trass` VALUES).+')
    s = pat.search(x)
    if s:
        trass_base = s.group()

#Получение трасс и точек из базы
for x in text3:
    pat = re.compile(r'(INSERT INTO `_trass_point` VALUES).+')
    s = pat.search(x)
    if s:
        trass_point_base = s.group()

#Приведение к нужному виду
pat = re.compile(r'\((.*?)\)')
points_base = pat.findall(points_base)
trass_base = pat.findall(trass_base)
trass_point_base = pat.findall(trass_point_base)

def make_list(lst):
    for x in lst:
        new = x.split(',')
        yield new

def delete_quotes(lst):
    pat = re.compile(r'[^"\']+')
    for i in range(len(lst)):
        line = lst[i]
        new_line = []
        for q in range(len(line)):
            elem = line[q]
            s = pat.search(elem)
            if s:
                new = s.group()
                new_line.append(new)
            else:
                new_line.append(elem)
        yield new_line


points_base = points_base[1:]
points_base = list(make_list(points_base))
points_base = list(delete_quotes(points_base))
trass_base = list(make_list(trass_base))
trass_base = list(delete_quotes(trass_base))
trass_point_base = list(make_list(trass_point_base))
trass_point_base = list(delete_quotes(trass_point_base))

points_names_from_base = []
pat = re.compile(r'(?=[^0-9]+$)(?:\w+)')
pat2 = re.compile(r'(?=[^0-9]{5})(?:\w+)')

for x in points_base:
    s = pat.search(x[0])
    if s:
        new = s.group()
        if len(new) == 2 or len(new) == 3 or len(new) == 5:
            points_names_from_base.append(s.group())

length = len(points_names_from_base)
logging.warning('Найдено %s точек в базе данных' % length)
print('Найдено %s точек в базе данных' % length)

#Отбор точек на кириллице из базы данных
def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))

#Отбор точек на на латинице из базы данных
def has_latin(text):
    return bool(re.search('[A-Z]', text))

rus_points_from_base = []
eng_points_from_base = []
for x in points_names_from_base:
    if has_cyrillic(x) is True:
        rus_points_from_base.append(x)
    if has_latin(x) is True:
        eng_points_from_base.append(x)


length1 = len(rus_points_from_base)
length2 = len(eng_points_from_base)
logging.warning('Найдено %s точек на кириллице и %s точек на латинице в базе данных' % (length1, length2))
print('Найдено %s точек на кириллице и %s точек на латинице в базе данных' % (length1, length2))

#Нахождение общих точек на латинице с документом аринк
arinc_names = list(modules.names(inside_points))
eng_common_points = list(modules.find(eng_points_from_base, arinc_names))
eng_not_common_points = list(modules.compare(eng_points_from_base, eng_common_points))
length3 = len(eng_not_common_points)
logging.warning('Из базы нужно удалить %s точек на кириллице и %s старых точек на латинице. Список старых точек на латинице: %s' %(length1, length3, eng_not_common_points))
print('Из базы нужно удалить %s точек на кириллице и %s старых точек на латинице. Список старых точек на латинице: %s' %(length1, length3, eng_not_common_points))

#Формирвоание запроса на удаление точек на кириллице из базы и удаление старых точек на латинице:
def create_quotes(lst):
    for x in lst:
        new="'"+x+"'"
        yield new

rus_points_from_base = list(create_quotes(rus_points_from_base))
rus_points_from_base = ', '.join(rus_points_from_base)
eng_not_common_points = list(create_quotes(eng_not_common_points))
eng_not_common_points = ', '.join(eng_not_common_points)

query_01A_delete_rus_points = "DELETE FROM `point` WHERE PN_NAME IN (" + rus_points_from_base+");"
query_01B_delete_rus_points = "DELETE FROM `point_mag` WHERE PN_NAME IN (" + rus_points_from_base+");"

query_01C_delete_eng_old_points = "DELETE FROM `point` WHERE PN_NAME IN (" + eng_not_common_points+");"
query_01D_delete_eng_old_points = "DELETE FROM `point_mag` WHERE PN_NAME IN (" + eng_not_common_points+");"

query_01_delete_points = query_01A_delete_rus_points + query_01C_delete_eng_old_points + query_01B_delete_rus_points + query_01D_delete_eng_old_points

if not os.path.exists('%s1.Запросы' %config.sintez_files):
    os.makedirs('%s1.Запросы' %config.sintez_files)

with open('%s1.Запросы/01_delete_points.sql' % config.sintez_files, 'w') as file1:
    file1.write(query_01_delete_points)


#Перерасчет координат точек из документа аринк в прямоугольной системе координат
def transform_arinc(points):
    for i in range(len(points)):
        rad = 6372795
        line = points[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        lat = gr_lat + min_lat/60 + sec_lat/3600
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        lon = gr_lon + min_lon/60 + sec_lon/3600
        hab_lat = 48 + 31/60 + 41/3600
        hab_lon = 135 + 11/60 + 17/3600
        lat1 = hab_lat*math.pi/180
        lon1 = hab_lon*math.pi/180
        lat2 = lat*math.pi/180
        lon2 = lon*math.pi/180
        cl1 = math.cos(lat1)
        cl2 = math.cos(lat2)
        sl1 = math.sin(lat1)
        sl2 = math.sin(lat2)
        delta = lon2 - lon1
        cdelta = math.cos(delta)
        sdelta = math.sin(delta)
        y = math.sqrt(math.pow(cl2*sdelta,2)+math.pow(cl1*sl2-sl1*cl2*cdelta,2))
        x = sl1*sl2+cl1*cl2*cdelta
        ad = math.atan2(y,x)
        dist = ad*rad
        x = (cl1*sl2) - (sl1*cl2*cdelta)
        y = sdelta*cl2
        z = math.degrees(math.atan(-y/x))
        if (x < 0):
            z = z+180
        z2 = (z+180.) % 360. - 180
        z2 = - math.radians(z2)
        anglerad2 = z2 - ((2*math.pi)*math.floor((z2/(2*math.pi))) )
        angledeg = (anglerad2*180)/math.pi
        x = round(((math.sin(anglerad2)*dist)/1000), 3)
        y = round(((math.cos(anglerad2)*dist)/1000), 3)
        shir = line[1][1:7]
        shir = shir + 'N'
        dolg = line[1][10:17]
        dolg = dolg + 'E'
        if x>1000 and -1000<y<1000:
            k = x/250
            x = round(x+k, 3)
            yield line[0], shir, dolg, x, y, line[2]
        if x<-1000 and -1000<y<1000:
            k = x/250
            x = round(x+k, 3)
            yield line[0], shir, dolg, x, y, line[2]
        if x>1000 and y>1000:
            k = x/250
            x = round(x+k, 3)
            k2 = y/250
            y = round(y+k2, 3)
            yield line[0], shir, dolg, x, y, line[2]
        if x<-1000 and y>1000:
            k = x/250
            x = round(x+k, 3)
            k2 = y/250
            y = round(y+k2, 3)
            yield line[0], shir, dolg, x, y, line[2]
        if x>1000 and y<-1000:
            k = x/250
            x = round(x+k, 3)
            k2 = y/250
            y = round(y+k2, 3)
            yield line[0], shir, dolg, x, y, line[2]
        if x<-1000 and y<-1000:
            k = x/250
            x = round(x+k, 3)
            k2 = y/250
            y = round(y+k2, 3)
            yield line[0], shir, dolg, x, y, line[2]
        if -1000<x<1000:
            yield line[0], shir, dolg, x, y, line[2]

arinc_transformed = list(transform_arinc(inside_points))
arinc_transformed2 = list(transform_arinc(inside_for_cartography))

#Сравнение совпаших точек на латинице
eng_common_points_base = []
for x in points_base:
    pat_space = re.compile(r'[^\s]+')
    pat_search = pat_space.search(x[0])
    without_space = pat_search.group()
    if without_space in eng_common_points:
        eng_common_points_base.append(x)

eng_common_points_arinc = []
for x in arinc_transformed:
    if x[0] in eng_common_points:
        eng_common_points_arinc.append(x)

eng_common_points_base=sorted(eng_common_points_base)
eng_common_points_arinc = sorted(eng_common_points_arinc)

#Нахождение совпаших точек, у которых разница в координатах более 10 сек
def compare_coordinates(arinc, base):
    for i in range(len(arinc)):
        if len(base[i][1]) == 7 and len(base[i][2])== 8:
            lat_ar = int(arinc[i][1][0:6])
            lon_ar = int(arinc[i][2][0:7])
            lat_base = int(base[i][1][0:6])
            lon_base = int(base[i][2][0:7])
            if abs(lat_ar-lat_base) > 10 or abs(lon_ar-lon_base) > 10:
                yield base[i], arinc[i]
        else:
            yield base[i], arinc[i]

update_points = list(compare_coordinates(eng_common_points_arinc, eng_common_points_base))

def update_query(lst):
    for i in range(len(lst)):
        line = lst[i]
        queryA = "UPDATE point set PN_NAME = '%s', PN_LAT = '%s', PN_LON = '%s', PN_X = %s, PN_Y = %s, PN_FNAME = %s, PN_NUM = %s, P_RP = %s, P_ACT = %s, P_STATE = %s, P_FIR = %s, P_TMA = %s, P_AOR = %s, P_SECTOR = %s, P_ZONE = %s, PN_CAPTION = '%s' WHERE PN_NAME = '%s';" %(line[0][0], line[1][1], line[1][2], line[1][3], line[1][4], line[0][5], line[0][6], line[0][7], line[0][8], line[0][9], line[0][10], line[0][11], line[0][12], line[0][13], line[0][14], line[0][15], line[0][0])
        queryB = "UPDATE point_mag set PN_NAME = '%s', PN_LAT = '%s', PN_LON = '%s', PN_X = %s, PN_Y = %s, PN_FNAME = %s, PN_NUM = %s, P_RP = %s, P_ACT = %s, P_STATE = %s, P_FIR = %s, P_TMA = %s, P_AOR = %s, P_SECTOR = %s, P_ZONE = %s, PN_CAPTION = '%s' WHERE PN_NAME = '%s';" % (
        line[0][0], line[1][1], line[1][2], line[1][3], line[1][4], line[0][5], line[0][6], line[0][7], line[0][8],
        line[0][9], line[0][10], line[0][11], line[0][12], line[0][13], line[0][14], line[0][15], line[0][0])
        yield queryA
        yield queryB


updated_points = list(update_query(update_points))

with open('%s1.Запросы/02_update_points.sql' % config.sintez_files, 'w') as file1:
    for item in updated_points:
        file1.write("%s\n" % item)

#Создание запроса на добавление новых точек
common_points_names = list(modules.names(eng_common_points_arinc))

points_add = copy.deepcopy(arinc_transformed)
for x in arinc_transformed:
    if x[0] in common_points_names:
        points_add.remove(x)

length = len(points_add)
logging.warning('В базу нужно добавить %s новых точек из документа ARINC' %length)
print('В базу нужно добавить %s новых точек из документа ARINC' %length)

points_add = sorted(points_add)

def query_03_add_points(lst):
    for i in range(len(lst)):
        line = lst[i]
        query = "('%s', '%s', '%s', %s, %s, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL ) \n" % (line[0], line[1], line[2], str(line[3]), str(line[4]))
        yield query

points_add_list = list(query_03_add_points(points_add))
points_add_list = ','.join(points_add_list)

query_03A_add_points= "INSERT IGNORE INTO `point` (`PN_NAME`, `PN_LAT`, `PN_LON`, `PN_X`, `PN_Y`, `PN_FNAME`, `PN_NUM`, `P_RP`, `P_ACT`, `P_STATE`, `P_FIR`, `P_TMA`, `P_AOR`, `P_SECTOR`, `P_ZONE`, `PN_CAPTION`) VALUES "+points_add_list+';'
query_03B_add_points = "INSERT IGNORE INTO `point_mag` (`PN_NAME`, `PN_LAT`, `PN_LON`, `PN_X`, `PN_Y`, `PN_FNAME`, `PN_NUM`, `P_RP`, `P_ACT`, `P_STATE`, `P_FIR`, `P_TMA`, `P_AOR`, `P_SECTOR`, `P_ZONE`, `PN_CAPTION`) VALUES "+points_add_list+';'

with open('%s1.Запросы/03_add_points.sql' % config.sintez_files, 'w') as file1:
    file1.write(' \n'+query_03A_add_points)

with open('%s1.Запросы//03_add_points_mag.sql' % config.sintez_files, 'w') as file1:
    file1.write(' \n'+query_03B_add_points)

# ______________________АНАЛИЗ ТРАСС_______________________________________

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
        min = line[83:88]
        max = line[93:98]
        yield name, point, ind, number, min, max

routes1 = list(modules.get_routes(text1))
routes2 = list(modules.get_routes(text2))
routes = routes1 + routes2
routes = list(get_route_info(routes))

int_ = list(get_route_info(routes1))
mvl = list(get_route_info(routes2))

# Получаем список с трассами, которые лежат в зоне ответсвенности из ARINC
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
                yield route, point, ind, coord, line[3], line[4], line[5]

def select_routes_lines(routes, inside_points):
    for i in range(len(routes)):
        line = routes[i]
        route = line[13:18]
        point = line[29:34]
        ind = line[34:36]
        pat = re.compile(r'[^\s]+')
        s = pat.search(route)
        s2 = pat.search(point)
        route = s.group()
        point = s2.group()
        for q in range(len(inside_points)):
            line2 = inside_points[q]
            point2 = line2[0]
            ind2 = line2[2]
            coord = line2[1]
            if point == point2 and ind == ind2:
                yield line

filtred_routes = list(select_routes(routes, inside_points))
filtred_routes = list(modules.unique(filtred_routes))
filtred_routes = sorted(filtred_routes, key=lambda x: x[0])

filtred_int = list(select_routes(int_, inside_points))
filtred_int = list(modules.unique(filtred_int))
filtred_int = sorted(filtred_int, key=lambda x: x[0])

filtred_mvl = list(select_routes(mvl, inside_points))
filtred_mvl = list(modules.unique(filtred_mvl))
filtred_mvl = sorted(filtred_mvl, key=lambda x: x[0])

# Сортировка трасс, где мало точек
filtred_routes = [list(g) for k, g in groupby(filtred_routes, lambda s: s[0])]

filtred_int = [list(g) for k, g in groupby(filtred_int, lambda s: s[0])]
filtred_mvl = [list(g) for k, g in groupby(filtred_mvl, lambda s: s[0])]

more2 = list(modules.count_list(filtred_routes))
more2 = list(chain.from_iterable(more2))

more2_int = list(modules.count_list(filtred_int))
more2_int = list(chain.from_iterable(more2_int))

more2_mvl = list(modules.count_list(filtred_mvl))
more2_mvl = list(chain.from_iterable(more2_mvl))

def counter_of_points(routes):
    for key, group in groupby(routes, lambda x: x[0]):
        for i,each in enumerate(group, start=1):
            yield "{}".format(key), "{}".format(each[1]), "{}".format(each[2]),"{}".format(i), "{}".format(each[3]), "{}".format(each[5]), "{}".format(each[6]), "{}".format(each[4])

more2 = list(counter_of_points(more2))
more2_int = list(counter_of_points(more2_int))
more2_mvl = list(counter_of_points(more2_mvl))

#Формируем слой с точками, которые участвуют в трассах (ничего лишнего)
only_in_trass_points = []
for x in more2_int:
    new = []
    new.append(x[1])
    new.append(x[4])
    new.append(x[2])
    new = tuple(new)
    only_in_trass_points.append(new)
    new = []

only_in_trass_points = list(modules.unique(only_in_trass_points))

names_trass_points = list(modules.names(only_in_trass_points))
add_points_trass = []
for x in points_add:
    if x[0] in names_trass_points:
        add_points_trass.append(x)

points_add_list_trass = list(query_03_add_points(add_points_trass))
points_add_list_trass = ','.join(points_add_list_trass)

query_03A_add_points_trass= "INSERT IGNORE INTO `point` (`PN_NAME`, `PN_LAT`, `PN_LON`, `PN_X`, `PN_Y`, `PN_FNAME`, `PN_NUM`, `P_RP`, `P_ACT`, `P_STATE`, `P_FIR`, `P_TMA`, `P_AOR`, `P_SECTOR`, `P_ZONE`, `PN_CAPTION`) VALUES "+points_add_list_trass+';'
query_03B_add_points_trass = "INSERT IGNORE INTO `point_mag` (`PN_NAME`, `PN_LAT`, `PN_LON`, `PN_X`, `PN_Y`, `PN_FNAME`, `PN_NUM`, `P_RP`, `P_ACT`, `P_STATE`, `P_FIR`, `P_TMA`, `P_AOR`, `P_SECTOR`, `P_ZONE`, `PN_CAPTION`) VALUES "+points_add_list_trass+';'

with open('%s1.Запросы/03_add_points_only.sql' % config.sintez_files, 'w') as file1:
    file1.write(' \n'+query_03A_add_points_trass)

with open('%s1.Запросы/03_add_points_mag_only.sql' % config.sintez_files, 'w') as file1:
    file1.write(' \n'+query_03B_add_points_trass)

# Пересчитываем координаты точек в радианы
transformed = list(modules.gradus(inside_points))

# Получаем только навания трасс (отсекаем точки) из ARINC (для лога)
names_routes = list(modules.names(more2))
names_routes = list(modules.unique(names_routes))

# Формируем список с названиями трасс из базы (для лога)
all_routes_names = list(modules.names(routes))

# для лога
all_routes_unique = list(modules.unique(all_routes_names))

length1 = len(all_routes_unique)
length3 = len(names_routes)
logging.warning('Найдено %s трасс в документе ARINC, только %s находятся в зоне ответсвенности' % (length1, length3))
print('Найдено %s трасс в документе ARINC, только %s находятся в зоне ответсвенности' % (length1, length3))

names_routes_int = list(modules.names(more2_int))
names_routes_mvl = list(modules.names(more2_mvl))

names_routes_int = list(modules.unique(names_routes_int))
names_routes_mvl = list(modules.unique(names_routes_mvl))

# Установка порядковых номеров точек на маршруте
list_of_routes_with_points = list(modules.counter_of_points_arinc(more2))

print('В базе найдено %s трасс' %len(trass_base))

rus = []
international = []
for x in trass_base:
    if has_cyrillic(x[0]) is True:
        rus.append(x)
    else:
        international.append(x)

for x in rus:
    x[0] = transliterate.translit(x[0], 'ru', reversed=True)

# Формируем новый список с трассами из базы
old = rus+international
old_names = list(modules.names(old))
# Нахождение дубликатов - первая часть. Дубли международные
doubles = list(modules.find(names_routes, old_names))
#Создание запроса на добавление трасс c учетом уже имеющихся данных в базе
old_doubles_names = []
for x in doubles:
    if x in old_names:
        old_doubles_names.append(x)

old_doubles = []
for x in old:
    if x[0] in old_doubles_names:
        old_doubles.append(x)

new_routes = []
for x in names_routes:
    if x not in old_doubles_names:
        new_routes.append(x)

#Находим новые трассы
rus_names = list(modules.names(rus))
international_names = list(modules.names(international))

#Для картографиии
new_routes_int = sorted(list(set(names_routes_int) - set(international_names)))
new_routes_mvl = sorted(list(set(names_routes_mvl) - set(rus_names)))

if not os.path.exists('%s3.Таблицы/' %config.sintez_files):
    os.makedirs('%s3.Таблицы/' %config.sintez_files)

with open('%s3.Таблицы/new_routes_international.txt' % config.sintez_files, 'w') as output:
    for item in new_routes_int:
        output.write("%s\n\n" % item)

with open('%s3.Таблицы/new_routes_mvl.txt' % config.sintez_files, 'w') as output:
    for item in new_routes_mvl:
        output.write("%s\n\n" % item)

del_routes_int = sorted(list(set(international_names) - set(names_routes_int)))
del_routes_mvl = sorted(list(set(rus_names) - set(names_routes_mvl)))

with open('%s3.Таблицы/old_routes_international.txt' % config.sintez_files, 'w') as output:
    for item in del_routes_int:
        output.write("%s\n\n" % item)

with open('%s3.Таблицы/old_routes_mvl.txt' % config.sintez_files, 'w') as output:
    for item in del_routes_mvl:
        output.write("%s\n\n" % item)

#Формируем запрос
new_routes_add_null =[]
for x in new_routes:
    lst =[]
    lst.append(x)
    lst.append('NULL')
    lst.append('NULL')
    lst.append('NULL')
    lst.append('NULL')
    new_routes_add_null.append(lst)

add_routes = sorted(new_routes_add_null+old_doubles)
def add_quotes(lst):
    for i in range(len(lst)):
        line = lst[i]
        new = []
        for x in line:
            if x != 'NULL' and x != "''":
                new_x = "'"+x+"'"
                new.append(new_x)
            if x == "''":
                new_x = 'NULL'
                new.append(new_x)
            if x == 'NULL':
                new.append(x)
        yield new

add_routes = list(add_quotes(add_routes))

def query_04_add_trass(lst):
    for i in range(len(lst)):
        line = lst[i]
        route = line[0]
        t_dir = line[1]
        t_dest1 = line[2]
        t_dest2= line[3]
        t_descr = line[4]
        query = "(%s, %s, %s, %s, %s)\n" %(route, t_dir, t_dest1, t_dest2, t_descr)
        yield query

query_04 = ','.join(list(query_04_add_trass(add_routes)))
query_04 = "INSERT IGNORE INTO _trass (T_NAME, T_DIR, T_DEST1, T_DEST2, T_DESCR) VALUES "+query_04+';'

with open('%s1.Запросы/04_add_trass.sql' % config.sintez_files, 'w') as file1:
    file1.write(" \n"+query_04)

# ________________MAH. Получение разрешенных высот из БД и соотношение их с трассами и точками из документа ARINC______________________________
rus_trass_point = []
international_trass_point = []
copy_base = copy.deepcopy(trass_point_base)

for x in copy_base:
    if has_cyrillic(x[0]) is True:
        rus_trass_point.append(x)
    else:
        international_trass_point.append(x)

for x in rus_trass_point:
    x[0]= transliterate.translit(x[0], 'ru', reversed=True)
    x[2] = transliterate.translit(x[2], 'ru', reversed=True)

base_trass_point = sorted(rus_trass_point+international_trass_point)
get_mah = []
for x in base_trass_point:
    if x[8] != "''" and x[8] != 'NULL':
        if x[0] in old_doubles_names:
            get_mah.append(x)

def compare_mah(base, arinc):
    for x in range(len(base)):
        line = base[x]
        route = line[0]
        point = line[2]
        for y in range(len(arinc)):
            line2 = arinc[y]
            route2 = line2[0]
            point2 = line2[1]
            if route == route2 and point ==point2:
                yield line2, line[8]

sorted_more2 = list(compare_mah(get_mah, more2))

s = set([x[0] for x in sorted_more2])
new_more = [x for x in more2 if x not in s]

more_not_mah = []
for x in new_more:
    new = list(x)
    new.append('NULL')
    more_not_mah.append(new)

more_with_mah = []
for x in sorted_more2:
    new = list(x[0])
    new.append(x[1])
    more_with_mah.append(new)

#Важдный лист для работы со слоями
add_routes_points = sorted((more_not_mah+more_with_mah), key=operator.itemgetter(0, 3))

#Группируем с целью выделить трассы с более чем 40 точками
grouped_routes = [list(g) for k, g in groupby(add_routes_points, lambda s: s[0])]
def find_more40(lst):
    for i in range(len(lst)):
        line = lst[i]
        if len(line) > 40:
            new = sorted(line, key=lambda s: int(s[3]))
            yield new

more40 = list(find_more40(grouped_routes))
more40 = list(chain.from_iterable(more40))

add_routes_points_limited = copy.copy(add_routes_points)
for x in more40:
    add_routes_points_limited.remove(x)

def add_quotes2(lst):
    for i in range(len(lst)):
        line = lst[i]
        new = []
        name = "'"+line[0]+"'"
        point = "'"+line[1]+"'"
        num = line[3]
        if line[8]=='NULL':
            mah = line[8]
            new.append(name)
            new.append(point)
            new.append(num)
            new.append(mah)
        if line[8] != 'NULL':
            mah1 = "'"+line[8]+"'"
            new.append(name)
            new.append(point)
            new.append(num)
            new.append(mah1)
        yield new

add_routes_points_quotes = list(add_quotes2(add_routes_points))
add_routes_points_quotes_limited = list(add_quotes2(more40))

def query_05_add_routes_points(lst):
    for i in range(len(lst)):
        line = lst[i]
        query = "(%s, %s, %s, NULL, NULL, NULL, NULL, NULL, %s) \n" %(line[0], line[2], line[1], line[3])
        yield query

query_05 = list(query_05_add_routes_points(add_routes_points_quotes))
query_05 = ','.join(query_05)

query_05_limited = list(query_05_add_routes_points(add_routes_points_quotes_limited))
query_05_limited = ','.join(query_05_limited)

query_05 = "INSERT IGNORE INTO _trass_point (T_NAME, TP_NUM, PN_NAME, TP_ID, T_DESIGNATION, T_LENGTH, T_WIDTH, T_FL, T_FLAGS) VALUES "+query_05+';'
query_05_limited = "#INSERT IGNORE INTO _trass_point (T_NAME, TP_NUM, PN_NAME, TP_ID, T_DESIGNATION, T_LENGTH, T_WIDTH, T_FL, T_FLAGS) VALUES "+query_05_limited+';'

with open('%s1.Запросы/05_add_trass_point.sql' % config.sintez_files, 'w') as file1:
    file1.write(" \n"+query_05)

with open('%s1.Запросы/05_add_trass_point_limited.sql' % config.sintez_files, 'w') as file1:
    file1.write(" \n"+query_05_limited)

#____________________КАРТОГРАФИЯ________________________________
# Определяем принадлежит ли точка полигону
arinc_int = list(modules.inside(points1))
arinc_mvl = list(modules.inside(points2))

# Проверяем на наложение
coords_int = list(modules.only_coords(arinc_int))
coords_mvl = list(modules.only_coords(arinc_mvl))

coords_int = sorted(coords_int, key=operator.itemgetter(3, 4))
coords_mvl = sorted(coords_mvl, key=operator.itemgetter(3, 4))

output_int = [(coords_int[q][1], coords_int[q + 1][1], coords_int[q + 1][0], coords_int[q + 1][2], coords_int[q + 1][3],
               coords_int[q + 1][4], coords_int[q + 1][5], coords_int[q][0], coords_int[q][2], coords_int[q][3],
               coords_int[q][4], coords_int[q][5]) for q in range(len(coords_int) - 1)]
output_mvl = [(coords_mvl[q][1], coords_mvl[q + 1][1], coords_mvl[q + 1][0], coords_mvl[q + 1][2], coords_mvl[q + 1][3],
               coords_mvl[q + 1][4], coords_mvl[q + 1][5], coords_mvl[q][0], coords_mvl[q][2], coords_mvl[q][3],
               coords_mvl[q][4], coords_mvl[q][5]) for q in range(len(coords_mvl) - 1)]

results1 = list(modules.check(output_int, 30))
results2 = list(modules.check(output_mvl, 30))

Name = values.params[0]

from_app = '***' + str(Name) + ' ' + str(datetime.datetime.today().year) + '-' + str(
    datetime.datetime.today().month) + '-' + str(datetime.datetime.today().day) + ' ' + str(
    datetime.datetime.today().hour) + ':' + str(datetime.datetime.today().minute) + ' Версия ARINC ' + version + '***'
author = []
author.append(from_app)

# Точки ПОД и ПДЗ

pod = config.pod
pdz = config.pdz

"""Формируем список: первой строкой будет указан автор, затем пойдут точки"""

# Убираем наложение точек
def find_coord_trass_points(trass_points, coords):
    for i in range(len(trass_points)):
        line = trass_points[i]
        point = line[0]
        ind = line[2]
        for q in range(len(coords)):
            line2 = coords[q]
            point2 = line2[0]
            ind2 = line2[2]
            if point == point2 and ind == ind2:
                yield point, line2[1], ind

only_in_trass = list(find_coord_trass_points(only_in_trass_points, inside_for_cartography))
only_in_trass = list(modules.unique(only_in_trass))

same_as1 = list(modules.get_same(arinc_int, results1))
same_as2 = list(modules.get_same(arinc_mvl, results2))
same_as_only = list(modules.get_same(only_in_trass, results1))

ar1 = copy.copy(arinc_int)
ar2 = copy.copy(arinc_mvl)

ar_only = copy.copy(only_in_trass)

# Формируем список без наложения
without_overlay1 = []
for x in ar1:
    if x not in same_as1:
        without_overlay1.append(x)

without_overlay2 = []
for x in ar2:
    if x not in same_as2:
        without_overlay2.append(x)

without_overlay_only = []
for x in ar_only:
    if x not in same_as_only:
        without_overlay_only.append(x)

for x in same_as1:
    if x in ar1:
        ar1.remove(x)

for x in same_as2:
    if x in ar2:
        ar2.remove(x)

for x in same_as_only:
    if x in ar_only:
        ar_only.remove(x)

points_list = list(modules.filling1(ar1, pdz))
points_list2 = list(modules.filling2(ar2))
points_list_only = list(modules.filling1(ar_only, pdz))

odd_s1 = same_as1[1::2]
even_s1 = same_as1[0::2]

odd_s2 = same_as2[1::2]
even_s2 = same_as2[0::2]

odd_s_only = same_as_only[1::2]
even_s_only = same_as_only[0::2]

points_list_1 = list(modules.filling1(odd_s1, pdz))
points_list_1_2 = list(modules.filling1_1(even_s1, pdz))

points_list_only2 = list(modules.filling1(odd_s_only, pdz))
points_list_only3 = list(modules.filling1_1(even_s_only, pdz))

points_list2_1 = list(modules.filling2(odd_s2))
points_list_2_2 = list(modules.filling2_1(even_s2))

first1 = ['N: "points" * points - Habarovsk Zonal Center *']
first2 = ['N: "local points"']
first3 = ['N: "points 3" * points - Habarovsk Zonal Center ONLY IN TRASS*']
second = ['L: <BLACK>']

points_list = list(chain.from_iterable(points_list))
points_list_1 = list(chain.from_iterable(points_list_1))
points_list_1_2 = list(chain.from_iterable(points_list_1_2))

points_list_only = list(chain.from_iterable(points_list_only))
points_list_only2 = list(chain.from_iterable(points_list_only2))
points_list_only3 = list(chain.from_iterable(points_list_only3))

po1 = points_list + points_list_1 + points_list_1_2
po1 = list(modules.unique(po1))

po1_only = points_list_only + points_list_only2 + points_list_only3
po1_only = list(modules.unique(po1_only))

points_list = author + first1 + second + po1

points_list_only = author + first3 + second + po1_only

points_list2 = list(chain.from_iterable(points_list2))
points_list2_1 = list(chain.from_iterable(points_list2_1))
points_list_2_2 = list(chain.from_iterable(points_list_2_2))

po2 = points_list2 + points_list2_1 + points_list_2_2
po2 = list(modules.unique(po2))
points_list2 = author + first2 + second + po2

if not os.path.exists('%s2.Картография/' %config.sintez_files):
    os.makedirs('%s2.Картография/' %config.sintez_files)

with open('%s2.Картография/POINTS_W_AUTO.SLD' % config.sintez_files, 'w') as output2:
    for item in points_list:
        output2.write("%s\n" % item)

with open('%s2.Картография/POINTS_W_ONLY_AUTO.SLD' % config.sintez_files, 'w') as output2:
    for item in points_list_only:
        output2.write("%s\n" % item)

with open('%s2.Картография/HB_LOC_P_AUTO.SLD' % config.sintez_files, 'w') as output2:
    for item in points_list2:
        output2.write("%s\n" % item)

print('Слои с точками созданы')

"""Формируем слои с трассами"""
save_more2_int = copy.copy(more2_int)
on_agr = []
for x in more2_int:
    if x[0] in config.routes:
        on_agr.append(x)

for x in on_agr:
    if x in more2_int:
        more2_int.remove(x)

new_routes_int_cart = []
for x in more2_int:
    if x[0] in new_routes_int:
        new_routes_int_cart.append(x)

new_routes_mvl_cart = []
for x in more2_mvl:
    if x[0] in new_routes_mvl:
        new_routes_mvl_cart.append(x)

grouped_routes_int = [list(g) for k, g in groupby(more2_int, lambda s: s[0])]
grouped_routes_agr = [list(g) for k, g in groupby(on_agr, lambda s: s[0])]
grouped_routes_mvl = [list(g) for k, g in groupby(more2_mvl, lambda s: s[0])]
grouped_routes_int_new = [list(g) for k, g in groupby(new_routes_int_cart, lambda s: s[0])]
grouped_routes_mvl_new = [list(g) for k, g in groupby(new_routes_mvl_cart, lambda s: s[0])]


def create_order_route(lst):
    for i in range(len(lst)):
        line = lst[i]
        route = line[0][0]
        coords = []
        for q in range(len(line)):
            par = line[q]
            coord = par[4]
            coords.append(coord)
        yield route, coords

cart_trass_int = list(create_order_route(grouped_routes_int))
cart_trass_agr = list(create_order_route(grouped_routes_agr))
cart_trass_mvl = list(create_order_route(grouped_routes_mvl))
cart_trass_int_new = list(create_order_route(grouped_routes_int_new))
cart_trass_mvl_new = list(create_order_route(grouped_routes_mvl_new))

routes_to_file_int = list(modules.fill_routes(cart_trass_int))
routes_to_file_agr = list(modules.fill_routes(cart_trass_agr))
routes_to_file_mvl = list(modules.fill_routes(cart_trass_mvl))
routes_to_file_int_new = list(modules.fill_routes(cart_trass_int_new))
routes_to_file_mvl_new = list(modules.fill_routes(cart_trass_mvl_new))

# Укорачиваем длину строки
long_int = []
for x in routes_to_file_int:
    if len(x) > 140:
        long_int.append(x)

long_mvl = []
for x in routes_to_file_mvl:
    if len(x) > 140:
        long_mvl.append(x)

long_agr = []
for x in routes_to_file_agr:
    if len(x) > 140:
        long_agr.append(x)

long_int_new = []
for x in routes_to_file_int_new:
    if len(x) > 140:
        long_int_new.append(x)

long_mvl_new = []
for x in routes_to_file_mvl_new:
    if len(x) > 140:
        long_mvl_new.append(x)

short_int = []
for x in routes_to_file_int:
    if x not in long_int:
        short_int.append(x)

short_mvl = []
for x in routes_to_file_mvl:
    if x not in long_mvl:
        short_mvl.append(x)

short_agr = []
for x in routes_to_file_agr:
    if x not in long_agr:
        short_agr.append(x)

short_int_new = []
for x in routes_to_file_int_new:
    if x not in long_int_new:
        short_int_new.append(x)

short_mvl_new = []
for x in routes_to_file_mvl_new:
    if x not in long_mvl_new:
        short_mvl_new.append(x)

# Разбиваем на части
parts_int = []
for x in long_int:
    k = x.split(', ')
    parts_int.append(k)

parts_mvl = []
for x in long_mvl:
    k = x.split(', ')
    parts_mvl.append(k)

parts_agr = []
for x in long_agr:
    k = x.split(', ')
    parts_agr.append(k)

parts_int_new = []
for x in long_int_new:
    k = x.split(', ')
    parts_int_new.append(k)

parts_mvl_new = []
for x in long_mvl_new:
    k = x.split(', ')
    parts_mvl_new.append(k)

all_parts_int = list(modules.chunks(parts_int, 3))
all_parts_mvl = list(modules.chunks(parts_mvl, 3))
all_parts_agr = list(modules.chunks(parts_agr, 3))
all_parts_int_new = list(modules.chunks(parts_int_new, 3))
all_parts_mvl_new = list(modules.chunks(parts_mvl_new, 3))

for x in all_parts_int:
    if len(x[0]) <= 20:
        t = ',' + x[0]
        x[0] = t

for x in all_parts_mvl:
    if len(x[0]) <= 20:
        t = ',' + x[0]
        x[0] = t

for x in all_parts_agr:
    if len(x[0]) <= 20:
        t = ',' + x[0]
        x[0] = t

for x in all_parts_int_new:
    if len(x[0]) <= 20:
        t = ',' + x[0]
        x[0] = t

for x in all_parts_mvl_new:
    if len(x[0]) <= 20:
        t = ',' + x[0]
        x[0] = t

list_routes_int = list(modules.listTosring2(all_parts_int))
list_routes_mvl = list(modules.listTosring2(all_parts_mvl))
list_routes_agr = list(modules.listTosring2(all_parts_agr))
list_routes_int_new = list(modules.listTosring2(all_parts_int_new))
list_routes_mvl_new = list(modules.listTosring2(all_parts_mvl_new))

agr = ['L: <BROWN,ff00,full>']
add_routes_agr = agr + short_agr + list_routes_agr
add_routes_int = short_int + list_routes_int
add_routes_mvl = short_mvl + list_routes_mvl

first = ['N: "routes" * routes - Habarovsk Zonal Center *']
first_sw = ['N: "scaled routes" * scaled routes - Habarovsk Zonal Center *']
second = ['L: <BROWN,ffff,full>']

add_routes_osn = author + first + second + add_routes_int + add_routes_agr
add_routes_sw = author + first_sw + second + add_routes_int + add_routes_agr

first2 = ['N: "local routes"']
add_routes2 = author + first2 + second + add_routes_mvl

first_int = ['N: "routes 10" * routes - Habarovsk Zonal Center *']
first_mvl = ['N: "routes 11" * routes - Habarovsk Zonal Center *']

add_routes_int_ = author + first_int + second + short_int_new + list_routes_int_new
add_routes_mvl_ = author + first_mvl + second + short_mvl_new + list_routes_mvl_new

with open('%s2.Картография/ROUTES_W_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in add_routes_osn:
        output3.write("%s\n" % item)

with open('%s2.Картография/ROUT_S_W_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in add_routes_sw:
        output3.write("%s\n" % item)

with open('%s2.Картография/HB_LOC_R_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in add_routes2:
        output3.write("%s\n" % item)

with open('%s2.Картография/NEW_ROUTES_INT_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in add_routes_int_:
        output3.write("%s\n" % item)

with open('%s2.Картография/NEW_ROUTES_MVL_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in add_routes_mvl_:
        output3.write("%s\n" % item)

print('Слои с трассами созданы')

# Сопоставление трасс и точек с перерасчитанными координатами
def combine_coords(trass, coords):
    for i in range(len(trass)):
        line = trass[i]
        point = line[1]
        ind = line[2]
        for q in range(len(coords)):
            line2 = coords[q]
            point2 = line2[0]
            ind2 = line2[5]
            if point == point2 and ind ==ind2:
                yield line[0], point, line[4], line[5], line[6]


together_int = list(combine_coords(save_more2_int, arinc_transformed2))
together_mvl = list(combine_coords(more2_mvl, arinc_transformed2))
together_int_new = list(combine_coords(new_routes_int_cart, arinc_transformed2))
together_mvl_new = list(combine_coords(new_routes_mvl_cart, arinc_transformed2))

together_int = [list(g) for k, g in groupby(together_int, lambda s: s[0])]
together_mvl = [list(g) for k, g in groupby(together_mvl, lambda s: s[0])]
together_int_new = [list(g) for k, g in groupby(together_int_new, lambda s: s[0])]
together_mvl_new = [list(g) for k, g in groupby(together_mvl_new, lambda s: s[0])]

#Представление в нужном формате
def delta_lat(list1):
    for i in range(len(list1)):
        line = list1[i]
        output = [(line[q][1], line[q][2], line[q][3], line[q][4], line[q+1][1], line[q+1][2], line[q+1][3], line[q+1][4], line[q][0]) for q in range(len(line) - 1)]
        yield output

right_order_int = list(delta_lat(together_int))
right_order_mvl = list(delta_lat(together_mvl))
right_order_int_new = list(delta_lat(together_int_new))
right_order_mvl_new = list(delta_lat(together_mvl_new))

right_order_int = list(chain.from_iterable(right_order_int))
right_order_mvl = list(chain.from_iterable(right_order_mvl))
right_order_int_new = list(chain.from_iterable(right_order_int_new))
right_order_mvl_new = list(chain.from_iterable(right_order_mvl_new))

#Измерение расстояния и угла между точками и нахождение координаты серединной точки
def distance_and_angle(list1):
    for i in range(len(list1)):
        line = list1[i]
        route = line[8]
        r = 6372795
        f1 = math.radians(int(line[1][1:3]) + int(line[1][3:5])/60 + int(line[1][5:7])/3600)
        f2 = math.radians(int(line[5][1:3]) + int(line[5][3:5])/60 + int(line[5][5:7])/3600)
        l1 = math.radians(int(line[1][10:13]) + int(line[1][13:15])/60 + int(line[1][15:17])/3600)
        l2 = math.radians(int(line[5][10:13]) + int(line[5][13:15]) / 60 + int(line[5][15:17]) / 3600)
        df = f2-f1
        dl = l2-l1
        a = ((math.sin(df/2))**2)+(math.cos(f1)*math.cos(f2)*(math.sin(dl/2))**2)
        c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = r*c
        y = math.sin(l2 - l1) * math.cos(f2)
        x = math.cos(f1) * math.sin(f2) - math.sin(f1) * math.cos(f2) * math.cos(l2 - l1)
        az = math.degrees(math.atan2(y, x))
        az = (az + 360) % 360
        Bx = math.cos(f2) * math.cos(l2 - l1)
        By = math.cos(f2) * math.sin(l2 - l1)
        fm = math.degrees(math.atan2(math.sin(f1) + math.sin(f2), math.sqrt((math.cos(f1) + Bx) ** 2 + By ** 2)))
        lm = math.degrees(l1 + math.atan2(By, math.cos(f1) + Bx))
        f = float(fm)
        l = float(lm)
        f_gr = math.trunc(f)
        l_gr = math.trunc(l)
        f_min = math.trunc((f - f_gr) * 60)
        l_min = math.trunc((l - l_gr) * 60)
        f_sec = math.trunc(((f - f_gr) * 60 - f_min) * 60)
        l_sec = math.trunc(((l - l_gr) * 60 - l_min) * 60)
        f_mili = math.ceil((((f - f_gr) * 60 - f_min) * 60 - f_sec) * 60)
        l_mili = math.ceil((((l - l_gr) * 60 - l_min) * 60 - l_sec) * 60)
        f_gr = str(f_gr).rjust(2, '0')
        l_gr = str(l_gr).rjust(3, '0')
        f_min = str(f_min).rjust(2, '0')
        l_min = str(l_min).rjust(2, '0')
        f_sec = str(f_sec).rjust(2, '0')
        l_sec = str(l_sec).rjust(2, '0')
        f_mili = str(f_mili).rjust(2, '0')
        l_mili = str(l_mili).rjust(2, '0')
        f = 'N' + f_gr + f_min + f_sec + f_mili
        l = 'E' + l_gr + l_min + l_sec + l_mili
        coord = f + l
        yield route, fm, lm, coord, d, az, line[2], line[3]


def distance_and_angle2(list1):
    for i in range(len(list1)):
        line = list1[i]
        route = line[8]
        r = 6372795
        f1 = math.radians(int(line[1][1:3]) + int(line[1][3:5])/60 + int(line[1][5:7])/3600)
        f2 = math.radians(int(line[5][1:3]) + int(line[5][3:5])/60 + int(line[5][5:7])/3600)
        l1 = math.radians(int(line[1][10:13]) + int(line[1][13:15])/60 + int(line[1][15:17])/3600)
        l2 = math.radians(int(line[5][10:13]) + int(line[5][13:15]) / 60 + int(line[5][15:17]) / 3600)
        df = f2-f1
        dl = l2-l1
        a = ((math.sin(df/2))**2)+(math.cos(f1)*math.cos(f2)*(math.sin(dl/2))**2)
        c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = r*c
        y = math.sin(l2 - l1) * math.cos(f2)
        x = math.cos(f1) * math.sin(f2) - math.sin(f1) * math.cos(f2) * math.cos(l2 - l1)
        az = math.degrees(math.atan2(y, x))
        az = (az + 360) % 360
        Bx = math.cos(f2) * math.cos(l2 - l1)
        By = math.cos(f2) * math.sin(l2 - l1)
        fm = math.degrees(math.atan2(math.sin(f1) + math.sin(f2), math.sqrt((math.cos(f1) + Bx) ** 2 + By ** 2)))
        lm = math.degrees(l1 + math.atan2(By, math.cos(f1) + Bx))
        if d > config.d:
            f = float(fm)
            l = float(lm)
            f_gr = math.trunc(f)
            l_gr = math.trunc(l)
            f_min = math.trunc((f - f_gr) * 60)
            l_min = math.trunc((l - l_gr) * 60)
            f_sec = math.trunc(((f - f_gr) * 60 - f_min) * 60)
            l_sec = math.trunc(((l - l_gr) * 60 - l_min) * 60)
            f_mili = math.ceil((((f - f_gr) * 60 - f_min) * 60 - f_sec) * 60)
            l_mili = math.ceil((((l - l_gr) * 60 - l_min) * 60 - l_sec) * 60)
            f_gr = str(f_gr).rjust(2, '0')
            l_gr = str(l_gr).rjust(3, '0')
            f_min = str(f_min).rjust(2, '0')
            l_min = str(l_min).rjust(2, '0')
            f_sec = str(f_sec).rjust(2, '0')
            l_sec = str(l_sec).rjust(2, '0')
            f_mili = str(f_mili).rjust(2, '0')
            l_mili = str(l_mili).rjust(2, '0')
            f = 'N' + f_gr + f_min + f_sec + f_mili
            l = 'E' + l_gr + l_min + l_sec + l_mili
            coord = f + l
            yield route, fm, lm, coord, d, az, line[2], line[3]

params_int = list(distance_and_angle(right_order_int))
params_mvl = list(distance_and_angle(right_order_mvl))
params_int_new = list(distance_and_angle(right_order_int_new))
params_mvl_new = list(distance_and_angle(right_order_mvl_new))
params_sloy = list(distance_and_angle2(right_order_mvl))

def transform_params(lst):
    for i in range(len(lst)):
        rad = 6372795
        line = lst[i]
        lat2 = math.radians(line[1])
        lon2 = math.radians(line[2])
        lat1 = math.radians(48 + 31/60 + 41/3600)
        lon1 = math.radians(135 + 11/60 + 17/3600)
        cl1 = math.cos(lat1)
        cl2 = math.cos(lat2)
        sl1 = math.sin(lat1)
        sl2 = math.sin(lat2)
        delta = lon2 - lon1
        cdelta = math.cos(delta)
        sdelta = math.sin(delta)
        y = math.sqrt(math.pow(cl2*sdelta,2)+math.pow(cl1*sl2-sl1*cl2*cdelta,2))
        x = sl1*sl2+cl1*cl2*cdelta
        ad = math.atan2(y,x)
        dist = ad*rad
        x = (cl1*sl2) - (sl1*cl2*cdelta)
        y = sdelta*cl2
        z = math.degrees(math.atan(-y/x))
        if (x < 0):
            z = z+180
        z2 = (z+180.) % 360. - 180
        z2 = - math.radians(z2)
        anglerad2 = z2 - ((2*math.pi)*math.floor((z2/(2*math.pi))) )
        x = round(((math.sin(anglerad2)*dist)/1000), 3)
        y = round(((math.cos(anglerad2)*dist)/1000), 3)
        yield line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], x, y

params_int = list(transform_params(params_int))
params_mvl = list(transform_params(params_mvl))
params_int_new = list(transform_params(params_int_new))
params_mvl_new = list(transform_params(params_mvl_new))
params_sloy = list(transform_params(params_sloy))

def change_angle(list1):
    for i in range(len(list1)):
        line = list1[i]
        a = line[5]
        x = line[8]
        y = line[9]
        k = (abs(x)/300+abs(y)/600)*2.5
        if a < 90 and -300<x<300:
            new = 90-a
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a < 90 and -3000<x<-300:
            new = 90-a-k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a < 90 and 300 < x < 3000:
            new = 90 - a+k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 90 and a < 180 and -300<x<300:
            new = 270+(180-a)
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 90 and a < 180 and -3000<x<-300:
            new = 270+(180-a)-k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 90 and a < 180 and 300<x<3000:
            new = 270+(180-a)+k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 180 and a < 270 and -300<x<300:
            new = 90-(a-180)
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 180 and a < 270 and -3000<x<-300:
            new = 90-(a-180)-k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 180 and a < 270 and 300<x<3000:
            new = 90-(a-180)+k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 270 and a < 360 and -300<x<300:
            new = 270+(360-a)
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 270 and a < 360 and -3000<x<-300:
            new = 270+(360-a)-k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]
        if a > 270 and a < 360 and 300<x<3000:
            new = 270+(360-a)+k
            yield line[0], line[1], line[2], line[3], a, new, line[6], line[7]

params_int = list(change_angle(params_int))
params_mvl = list(change_angle(params_mvl))
params_int_new = list(change_angle(params_int_new))
params_mvl_new = list(change_angle(params_mvl_new))
params_sloy = list(change_angle(params_sloy))

coords_int = []
for x in params_int:
    coords_int.append(x[3])

coords_mvl = []
for x in params_mvl:
    coords_mvl.append(x[3])

coords_int_new = []
for x in params_int_new:
    coords_int_new.append(x[3])

coords_mvl_new = []
for x in params_mvl_new:
    coords_mvl_new.append(x[3])


coords_sloy = []
for x in params_sloy:
    coords_sloy.append(x[3])

# Находим дубликаты пар
dup_int = {}
gen = sorted(modules.list_duplicates(coords_int))
for x in gen:
    dup_int.update(x)

dup_mvl = {}
gen = sorted(modules.list_duplicates(coords_mvl))
for x in gen:
    dup_mvl.update(x)

dup_int_new = {}
gen = sorted(modules.list_duplicates(coords_int_new))
for x in gen:
    dup_int_new.update(x)

dup_mvl_new = {}
gen = sorted(modules.list_duplicates(coords_mvl_new))
for x in gen:
    dup_mvl_new.update(x)

dup_sloy = {}
gen = sorted(modules.list_duplicates(coords_sloy))
for x in gen:
    dup_sloy.update(x)

list_of_index_int = list(modules.sep(dup_int))
list_of_index_mvl = list(modules.sep(dup_mvl))
list_of_index_int_new = list(modules.sep(dup_int_new))
list_of_index_mvl_new = list(modules.sep(dup_mvl_new))
list_of_index_sloy = list(modules.sep(dup_sloy))

indexes_int = []
for sublist in list_of_index_int:
    for item in sublist:
        indexes_int.append(item)

indexes_mvl = []
for sublist in list_of_index_mvl:
    for item in sublist:
        indexes_mvl.append(item)

indexes_int_new = []
for sublist in list_of_index_int_new:
    for item in sublist:
        indexes_int_new.append(item)

indexes_mvl_new = []
for sublist in list_of_index_mvl_new:
    for item in sublist:
        indexes_mvl_new.append(item)

indexes_sloy = []
for sublist in list_of_index_sloy:
    for item in sublist:
        indexes_sloy.append(item)

duplicates_int = []
for x in indexes_int:
    ele = params_int[x]
    duplicates_int.append(ele)

duplicates_mvl = []
for x in indexes_mvl:
    ele = params_mvl[x]
    duplicates_mvl.append(ele)

duplicates_int_new = []
for x in indexes_int_new:
    ele = params_int_new[x]
    duplicates_int_new.append(ele)

duplicates_mvl_new = []
for x in indexes_mvl_new:
    ele = params_mvl_new[x]
    duplicates_mvl_new.append(ele)

duplicates_sloy = []
for x in indexes_sloy:
    ele = params_sloy[x]
    duplicates_sloy.append(ele)

# Убираем дубликаты из общего списка
for x in duplicates_int:
    if x in params_int:
        params_int.remove(x)

for x in duplicates_mvl:
    if x in params_mvl:
        params_mvl.remove(x)

for x in duplicates_int_new:
    if x in params_int_new:
        params_int_new.remove(x)

for x in duplicates_mvl_new:
    if x in params_mvl_new:
        params_mvl_new.remove(x)

for x in duplicates_sloy:
    if x in params_sloy:
        params_sloy.remove(x)

# Формируем два списка с повторами (одинаковые пары точек, но разные трассы)
odd_int = duplicates_int[1::2]
even_int = duplicates_int[0::2]
odd_mvl = duplicates_mvl[1::2]
even_mvl = duplicates_mvl[0::2]
odd_sloy = duplicates_sloy[1::2]
even_sloy = duplicates_sloy[0::2]

odd_int_new = duplicates_int_new[1::2]
even_int_new = duplicates_int_new[0::2]
odd_mvl_new = duplicates_mvl_new[1::2]
even_mvl_new = duplicates_mvl_new[0::2]


# Создание списка с десигнаторами
def make_desw(list1):
    for i in range(len(list1)):
        line = list1[i]
        route = line[0]
        sa = str(round(line[5], 1))
        coord = line[3]
        a = line[4]
        first = 'SA: '+sa
        third = 'T: <* BLACK * GREEN, R1> '+coord+' / '+route+' /'
        if a < 90:
            b = a*(math.pi/180)
            dx = str(round(math.cos(b) * (-0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: '+ dx', 0.0'
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 180 < a < 270:
            b = (a-180)*(math.pi/180)
            dx = str(round(math.cos(b) * (-0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 90 < a < 180:
            b = (180-a)*(math.pi/180)
            dx = str(round(math.cos(b) * (0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 270 < a < 360:
            b = (360-a)*(math.pi/180)
            dx = str(round(math.cos(b) * (0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third

desw_int = list(make_desw(params_int))
desw_mvl = list(make_desw(params_mvl))
desw_int_new = list(make_desw(params_int_new))
desw_mvl_new = list(make_desw(params_mvl_new))
desw_sloy = list(make_desw(params_sloy))

def make_desw2(list1, list2):
    for i in range(len(list1)):
        line = list1[i]
        line2 = list2[i]
        route = line[0]
        route2 = line2[0]
        sa = str(round(line[5], 1))
        coord = line[3]
        a = line[4]
        first = 'SA: '+sa
        third = 'T: <* BLACK * GREEN, R1> '+coord+' / '+route+'-'+route2+' /'
        if a < 90:
            b = a*(math.pi/180)
            dx = str(round(math.cos(b) * (-0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: '+ dx', 0.0'
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 180 < a < 270:
            b = (a-180)*(math.pi/180)
            dx = str(round(math.cos(b) * (-0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 90 < a < 180:
            b = (180-a)*(math.pi/180)
            dx = str(round(math.cos(b) * (0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 270 < a < 360:
            b = (360-a)*(math.pi/180)
            dx = str(round(math.cos(b) * (0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third

desw_int2 = list(make_desw2(even_int, odd_int))
desw_mvl2 = list(make_desw2(even_mvl, odd_mvl))
desw_int_new2 = list(make_desw2(even_int_new, odd_int_new))
desw_mvl_new2 = list(make_desw2(even_mvl_new, odd_mvl_new))
desw_sloy2 = list(make_desw2(even_sloy, odd_sloy))

first_int = ['N: "designators" * route designators - Habarovsk *']
first_int_new = ['N: "designators 20" * route designators - Habarovsk *']
first_mvl_new = ['N: "designators 21" * route designators - Habarovsk *']
first_mvl = ['N: "MVLD0"']
first_sloy = ['N: "MVLD1"']
first_mvl2 = ['N: "bl - loc. des." * local route designators - Habarovsk *']

for_desw_int = author + first_int + desw_int + desw_int2
for_desw_mvl = author + first_mvl + desw_mvl + desw_mvl2
for_desw_int_new = author + first_int_new + desw_int_new + desw_int_new2
for_desw_mvl_new = author + first_mvl_new + desw_mvl_new + desw_mvl_new2
for_desw_sloy = author + first_sloy+ desw_sloy + desw_sloy
for_desw_mvl2 = author + first_mvl2+ desw_mvl + desw_mvl2

with open('%s2.Картография/DESW_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in for_desw_int:
        output3.write("%s\n" % item)

with open('%s2.Картография/HB_LOC_D_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in for_desw_mvl2:
        output3.write("%s\n" % item)

with open('%s2.Картография/HABMVLD0_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in for_desw_mvl:
        output3.write("%s\n" % item)

with open('%s2.Картография/HABMVLD1_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in for_desw_sloy:
        output3.write("%s\n" % item)

with open('%s2.Картография/NEW_DESW_INT_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in for_desw_int_new:
        output3.write("%s\n" % item)

with open('%s2.Картография/NEW_DESW_MVL_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in for_desw_mvl_new:
        output3.write("%s\n" % item)

print('Слои с десигнаторами созданы')

#Формирование слоев с эшелонами
def delete_zero_int(list):
    for i in range(len(list)):
        line = list[i]
        min = line[6]
        max = line[7]
        if min[0:2] != 'FL' and max[0:2] != 'FL' and max != 'UNLTD' and min != '     ' and min !='' and max !='':
            min = int(min)
            max = int(max)
            yield line[0], line[3], line[4], line[5], min, max
        if min[0:2] != 'FL' and max == 'UNLTD' and min !='':
            min = int(line[6])
            max = line[7]
            yield line[0], line[3], line[4], line[5], min, max
        if line[6][0:2] != 'FL' and line[7][0:2] == 'FL' and min !='':
            min = int(line[6])
            max = line[7]
            yield line[0], line[3], line[4], line[5], min, max
        if line[6][0:2] == 'FL' and line[7][0:2] == 'FL':
            yield line[0], line[3], line[4], line[5], line[6], line[7]
        if line[6][0:2] == 'FL' and line[7] == 'UNLTD':
            yield line[0], line[3], line[4], line[5], line[6], line[7]
        if min == '' and max == '':
            yield line[0], line[3], line[4], line[5], line[6], line[7]

params_int_FL = list(delete_zero_int(params_int))
odd_int_FL = list(delete_zero_int(odd_int))
even_int_FL = list(delete_zero_int(even_int))


def make_metr_mvl(list):
    for i in range(len(list)):
        line = list[i]
        min = int(round(int(line[6])*0.3048*2, -2) // 2)
        max = int(round(int(line[7])*0.3048*2, -2) // 2)
        yield line[0], line[3], line[4], line[5], min, max

params_mvl_FL = list(make_metr_mvl(params_mvl))
odd_mvl_FL = list(make_metr_mvl(odd_mvl))
even_mvl_FL = list(make_metr_mvl(even_mvl))

def make_desw_FL(list1):
    for i in range(len(list1)):
        line = list1[i]
        route = line[0]
        min = str(line[4])
        max = str(line[5])
        height = route+':'+min+'-'+max
        sa = str(round(line[3], 1))
        coord = line[1]
        a = line[2]
        first = 'SA: '+sa
        third = 'T: <* BLACK * GREEN, R1> '+coord+' / '+height+' /'
        if a < 90:
            b = a*(math.pi/180)
            dx = str(round(math.cos(b) * (-0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: '+ dx', 0.0'
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 180 < a < 270:
            b = (a-180)*(math.pi/180)
            dx = str(round(math.cos(b) * (-0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 90 < a < 180:
            b = (180-a)*(math.pi/180)
            dx = str(round(math.cos(b) * (0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 270 < a < 360:
            b = (360-a)*(math.pi/180)
            dx = str(round(math.cos(b) * (0.2), 1))
            dy = str(round(math.sin(b) * (0.2), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third

int_FL_desw = list(make_desw_FL(params_int_FL))
mvl_FL_desw = list(make_desw_FL(params_mvl_FL))

def make_desw2_FL(list1, list2):
    for i in range(len(list1)):
        line = list1[i]
        line2 = list2[i]
        route = line[0]
        route2 = line2[0]
        min = str(line[4])
        max = str(line[5])
        min2 = str(line2[4])
        max2 = str(line2[5])
        height = route+':'+min+'-'+max
        height2 = route2+':'+min2+'-'+max2
        sa = str(round(line[3], 1))
        coord = line[1]
        a = line[2]
        first = 'SA: '+sa
        third = 'T: <* BLACK * GREEN, R1> '+coord+' / '+height+'; '+height2 +'/'
        if a < 90:
            b = a*(math.pi/180)
            dx = str(round(math.cos(b) * (1.5), 1))
            dy = str(round(math.sin(b) * (-1.5), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: '+ dx', 0.0'
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 180 < a < 270:
            b = (a-180)*(math.pi/180)
            dx = str(round(math.cos(b) * (1.5), 1))
            dy = str(round(math.sin(b) * (-1.5), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 90 < a < 180:
            b = (a-90)*(math.pi/180)
            dx = str(round(math.cos(b) * (-1.5), 1))
            dy = str(round(math.sin(b) * (-1.5), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third
        if 270 < a < 360:
            b = (a-270)*(math.pi/180)
            dx = str(round(math.cos(b) * (-1.5), 1))
            dy = str(round(math.sin(b) * (-1.5), 1))
            second = 'SD: ' + dx + ', ' + dy
            # second = 'SD: 0.0, 0.0'
            yield first
            yield second
            yield third

int_FL_desw2 = list(make_desw2_FL(odd_int_FL, even_int_FL))
mvl_FL_desw2 = list(make_desw2_FL(odd_mvl_FL, even_mvl_FL))

first = ['N: "designators 16" * route designators - Habarovsk *']
first2 = ['N: "designators 17" * mvl designators - Habarovsk *']

desw_FL_int = author + first + int_FL_desw + int_FL_desw2
desw_FL_mvl = author + first2 + mvl_FL_desw + mvl_FL_desw2

with open('%s2.Картография/HEIGHT_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in desw_FL_int:
        output3.write("%s\n" % item)

with open('%s2.Картография/HEIGHT_MVL_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in desw_FL_mvl:
        output3.write("%s\n" % item)

# Находим зональные трассы
zon = open('%ssamples/ROUTES_ZON_DOP.SLD' % config.program_files, 'r', encoding='koi8-r')
zon = zon.readlines()

zones = []
for x in zon:
    if len(x) > 10:
        if x[3] == '*' and x[10] == '*':
            new = x[5:9]
            zones.append(new)

zon = list(modules.unique(zones))
#zon = set(zon)

chained_zon = []

int_FL = params_int_FL+odd_int_FL

for x in range(len(int_FL)):
    line = int_FL[x]
    route = line[0]
    if route in zon:
        chained_zon.append(line)

chained_zon = list(modules.connecting(int_FL, zon))
# Отбираем пары точек
coords_zon = []
for x in chained_zon:
    coords_zon.append(x[1])

# Находим дубликаты пар
dup3 = {}
gen = sorted(modules.list_duplicates(coords_zon))
for x in gen:
    dup3.update(x)

list_of_index3 = list(modules.sep(dup3))

indexes3 = []
for sublist in list_of_index3:
    for item in sublist:
        indexes3.append(item)

duplicates3 = []
for x in indexes3:
    ele = chained_zon[x]
    duplicates3.append(ele)

# Убираем дубликаты из общего списка
for x in duplicates3:
    if x in chained_zon:
        chained_zon.remove(x)

# Формируем два списка с повторами (одинаковые пары точек, но разные трассы)
odd = duplicates3[1::2]
even = duplicates3[0::2]

chained_zon = chained_zon + odd

for_desw_zon1 = list(make_desw_FL(chained_zon))
for_desw_zon2 = list(make_desw2_FL(odd, even))

first3 = ['N: "designators 19" * zon designators - Habarovsk *']

for_desw3_zon = author + first3 + for_desw_zon1 + for_desw_zon2

with open('%s2.Картография/HEIGHT_ZON_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in for_desw3_zon:
        output3.write("%s\n" % item)

print('Слои с эшелонами созданы')

# Формируем лог для диспетчеров
rus_inside_points = []
for x in arinc_names:
    new = transliterate.translit(x, 'ru')
    rus_inside_points.append(new)

rus_common_points = list(modules.find(rus_inside_points, points_names_from_base))
rus_common_eng = []

for x in rus_common_points:
    new = transliterate.translit(x, 'ru', reversed=True)
    rus_common_eng.append(new)

common_points = rus_common_eng + eng_common_points
non_common = list(modules.compare(arinc_names, common_points))

non_common = list(modules.unique(non_common))
test = list(modules.for_log_points(non_common, inside_points))
test = list(modules.unique(test))
test = sorted(test, key=lambda s: s[0])

common_routes = list(modules.compare_new_points_and_routes(more2, test))
common_routes = list(modules.unique(common_routes))

all_routes = list(modules.compare_new_points_and_routes(more2, inside_points))
all_routes = list(modules.unique(all_routes))

non_common_routes = list(modules.compare(all_routes, common_routes))
non_common_routes = list(modules.unique(non_common_routes))

filename = xlwt.Workbook()
sheet = filename.add_sheet('Routes and points')
style = xlwt.easyxf('pattern: pattern solid, fore_color orange; font: color black;')

for i, l in enumerate(all_routes):
    if l not in common_routes:
        for j, col in enumerate(l):
            sheet.write(i, j, col)
    if l in common_routes:
        for j, col in enumerate(l):
            sheet.write(i, j, col, style)

filename.save('%s3.Таблицы/new_points_in_routes.xls' % config.sintez_files)

t = []
l = []
for x in common_routes:
    l.append(x[1])
    l.append(x[2])
    t.append(l)
    l = []

t = list(modules.unique(t))
t = sorted(t, key=lambda s: s[0])

first = [('Новая точка', 'Координаты')]
new_points = first + t
filename = xlwt.Workbook()
sheet = filename.add_sheet('New_points')

for i, l in enumerate(new_points):
    for j, col in enumerate(l):
        sheet.write(i, j, col)

filename.save('%s3.Таблицы/new_points.xls' % config.sintez_files)

print('Таблицы Excel с отчетом о новых точках и трассах созданы')

new_layer = list(modules.filling1(t, pdz))
first1 = ['N: "points 2" * points - Habarovsk Zonal Center *']
second = ['L: <RED>']

new_layer = list(chain.from_iterable(new_layer))

sticker = 'Cartography is created in ' + str(datetime.datetime.today().year) + '-' + str(
    datetime.datetime.today().month) + '-' + str(datetime.datetime.today().day) + ' ' + str(
    datetime.datetime.today().hour) + ':' + str(
    datetime.datetime.today().minute) + ' Version of ARINC ' + version + '***'
start_point = ['S: "1" <R1> N46120000E131100000']
start_point2 = ['T: <R2> N46120000E131100000 /%s /' % sticker]

layer = author + first1 + second + new_layer + start_point + start_point2

with open('%s2.Картография/NEW_LAYER_AUTO.SLD' % config.sintez_files, 'w') as output:
    for item in layer:
        output.write("%s\n" % item)

#Работаем с удаленными трассами
del_routes_int_finded = []
for x in trass_point_base:
    if x[0] in del_routes_int:
        del_routes_int_finded.append(x)

del_routes_int_finded = sorted(del_routes_int_finded, key=operator.itemgetter(0, 1))

rus_del_routes_mvl = []
for x in del_routes_mvl:
    k = transliterate.translit(x, 'ru')
    rus_del_routes_mvl.append(k)

del_routes_mvl_finded = []
for x in trass_point_base:
    if x[0] in rus_del_routes_mvl:
        del_routes_mvl_finded.append(x)

del_routes_mvl_finded = sorted(del_routes_mvl_finded, key=operator.itemgetter(0, 1))

only_del_points_int =[]
for x in del_routes_int_finded:
    only_del_points_int.append(x[2])

only_del_points_int=list(modules.unique(only_del_points_int))

only_del_points_mvl =[]
for x in del_routes_mvl_finded:
    only_del_points_mvl.append(x[2])

only_del_points_mvl=list(modules.unique(only_del_points_mvl))

del_points_coods_int = []
for x in points_base:
    if x[0] in only_del_points_int:
        l = []
        l.append(x[0])
        l.append(x[1])
        l.append(x[2])
        del_points_coods_int.append(l)

del_points_coods_mvl = []
for x in points_base:
    t = transliterate.translit(x[0], 'ru', reversed=True)
    if x[0] in only_del_points_mvl:
        l = []
        l.append(x[0])
        l.append(x[1])
        l.append(x[2])
        del_points_coods_mvl.append(l)
    if t in only_del_points_mvl:
        l = []
        l.append(t)
        l.append(x[1])
        l.append(x[2])
        del_points_coods_mvl.append(l)

def combine_coords_and_routes(lst1, lst2):
    for i in range(len(lst1)):
        line = lst1[i]
        route = line[0]
        point = line[2]
        for q in range(len(lst2)):
            line2 = lst2[q]
            point2 = line2[0]
            if point == point2:
                yield route, point, line2[1], line2[2], line[1]

del_routes_int_ = list(combine_coords_and_routes(del_routes_int_finded, del_points_coods_int))
del_routes_mvl_ = list(combine_coords_and_routes(del_routes_mvl_finded, del_points_coods_mvl))

def right_format(lst1):
    for i in range(len(lst1)):
        line = lst1[i]
        coord1 = line[2]
        coord2 = line[3]
        if len(coord1) == 7 and len(coord2) == 8:
            if coord1[4:6] == '60' and coord2[5:7] == '60':
                lst = []
                lst.append(line[0])
                coord1 = coord1[0:4] + '59'
                coord2 = coord2[0:5] + '59'
                coord = 'N' + coord1 + '00' + 'E' + coord2 + '00'
                lst.append(coord)
                lst.append(int(line[4]))
                yield lst
            if coord1[4:6] == '60' and coord2[5:7] != '60':
                lst = []
                lst.append(line[0])
                coord1 = coord1[0:4] + '59'
                coord = 'N' + coord1 + '00' + 'E' + coord2[0:7] + '00'
                lst.append(coord)
                lst.append(int(line[4]))
                yield lst
            if coord1[4:6] != '60' and coord2[5:7] == '60':
                lst = []
                lst.append(line[0])
                coord2 = coord2[0:5] + '59'
                coord = 'N' + coord1[0:6] + '00' + 'E' + coord2 + '00'
                lst.append(coord)
                lst.append(int(line[4]))
                yield lst
            if coord1 != '60' and coord2[5:7] != '60':
                lst = []
                lst.append(line[0])
                coord = 'N' + coord1[0:6] + '00' + 'E' + coord2[0:7] + '00'
                lst.append(coord)
                lst.append(int(line[4]))
                yield lst


del_routes_int_1 = list(right_format(del_routes_int_))
del_routes_mvl_1 = list(right_format(del_routes_mvl_))
del_routes_int_1 = list(modules.unique(del_routes_int_1))
del_routes_mvl_1 = list(modules.unique(del_routes_mvl_1))
del_routes_int_1 = sorted(del_routes_int_1, key=operator.itemgetter(0, 2))
del_routes_mvl_1 = sorted(del_routes_mvl_1, key=operator.itemgetter(0, 2))

for x in del_routes_mvl_1:
    x[0] = transliterate.translit(x[0], 'ru', reversed=True)

grouped_del_routes_int = [list(g) for k, g in groupby(del_routes_int_1, lambda s: s[0])]
grouped_del_routes_mvl = [list(g) for k, g in groupby(del_routes_mvl_1, lambda s: s[0])]

more2_del_int = []
for x in grouped_del_routes_int:
    if len(x) >= 2:
        more2_del_int.append(x)

more2_del_mvl = []
for x in grouped_del_routes_mvl:
    if len(x) >= 2:
        more2_del_mvl.append(x)

def make_trass_order(lst1):
    for i in range(len(lst1)):
        line = lst1[i]
        lst = []
        for q in range(len(line)):
            info = line[q]
            lst.append(info[1])
        yield line[0][0], lst

ordered_del_int = list(make_trass_order(more2_del_int))
ordered_del_mvl = list(make_trass_order(more2_del_mvl))

routes_to_file_int_del = list(modules.fill_routes(ordered_del_int))
routes_to_file_mvl_del = list(modules.fill_routes(ordered_del_mvl))

# Укорачиваем длину строки
long_int_del = []
for x in routes_to_file_int_del:
    if len(x) > 140:
        long_int_del.append(x)

long_mvl_del = []
for x in routes_to_file_mvl_del:
    if len(x) > 140:
        long_mvl_del.append(x)

short_int_del = []
for x in routes_to_file_int_del:
    if x not in long_int_del:
        short_int_del.append(x)

short_mvl_del = []
for x in routes_to_file_mvl_del:
    if x not in long_mvl_del:
        short_mvl_del.append(x)

# Разбиваем на части
parts_int_del = []
for x in long_int_del:
    k = x.split(', ')
    parts_int_del.append(k)

parts_mvl_del = []
for x in long_mvl_del:
    k = x.split(', ')
    parts_mvl_del.append(k)

all_parts_int_del = list(modules.chunks(parts_int_del, 3))
all_parts_mvl_del = list(modules.chunks(parts_mvl_del, 3))

for x in all_parts_int_del:
    if len(x[0]) <= 20:
        t = ',' + x[0]
        x[0] = t

for x in all_parts_mvl_del:
    if len(x[0]) <= 20:
        t = ',' + x[0]
        x[0] = t

list_routes_int_del = list(modules.listTosring2(all_parts_int_del))
list_routes_mvl_del = list(modules.listTosring2(all_parts_mvl_del))

del_first_int = ['N: "routes 12" * routes - Habarovsk Zonal Center *']
del_first_mvl = ['N: "routes 13" * routes - Habarovsk Zonal Center *']
second = ['L: <BROWN,ff00,full>']

del_add_routes_int = author + del_first_int + second + short_int_del + list_routes_int_del
del_add_routes_mvl = author + del_first_mvl + second + short_mvl_del + list_routes_mvl_del

with open('%s2.Картография/DEL_ROUTES_INT_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in del_add_routes_int:
        output3.write("%s\n" % item)

with open('%s2.Картография/DEL_ROUTES_MVL_AUTO.SLD' % config.sintez_files, 'w') as output3:
    for item in del_add_routes_mvl:
        output3.write("%s\n" % item)

print('Слои с удаленными трассами созданы')

# Делаем десигнаторы
def create_order_for_del(lst1):
    for i in range(len(lst1)):
        line = lst1[i]
        output = [(line[q][1], line[q+1][1], line[q][0]) for q in range(len(line)-1)]
        yield output

pairs_del_int = list(create_order_for_del(more2_del_int))
pairs_del_mvl = list(create_order_for_del(more2_del_mvl))
pairs_del_int = list(chain.from_iterable(pairs_del_int))
pairs_del_mvl = list(chain.from_iterable(pairs_del_mvl))

def midpoint_del(lst1):
    for i in range(len(lst1)):
        r = 6372795
        line = lst1[i]
        f1 = math.radians(int(line[0][1:3]) + int(line[0][3:5]) / 60 + int(line[0][5:7]) / 3600)
        l1 = math.radians(int(line[0][10:13]) + int(line[0][13:15]) / 60 + int(line[0][15:17]) / 3600)
        f2 = math.radians(int(line[1][1:3]) + int(line[1][3:5]) / 60 + int(line[1][5:7]) / 3600)
        l2 = math.radians(int(line[1][10:13]) + int(line[1][13:15]) / 60 + int(line[1][15:17]) / 3600)
        df = f2 - f1
        dl = l2 - l1
        a = ((math.sin(df / 2)) ** 2) + (math.cos(f1) * math.cos(f2) * (math.sin(dl / 2)) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = r * c
        y = math.sin(l2 - l1) * math.cos(f2)
        x = math.cos(f1) * math.sin(f2) - math.sin(f1) * math.cos(f2) * math.cos(l2 - l1)
        az = math.degrees(math.atan2(y, x))
        az = (az + 360) % 360
        Bx = math.cos(f2) * math.cos(l2 - l1)
        By = math.cos(f2) * math.sin(l2 - l1)
        fm = math.degrees(math.atan2(math.sin(f1) + math.sin(f2), math.sqrt((math.cos(f1) + Bx) ** 2 + By ** 2)))
        lm = math.degrees(l1 + math.atan2(By, math.cos(f1) + Bx))
        if d > config.d:
            f = float(fm)
            l = float(lm)
            f_gr = math.trunc(f)
            l_gr = math.trunc(l)
            f_min = math.trunc((f - f_gr) * 60)
            l_min = math.trunc((l - l_gr) * 60)
            f_sec = math.trunc(((f - f_gr) * 60 - f_min) * 60)
            l_sec = math.trunc(((l - l_gr) * 60 - l_min) * 60)
            f_mili = math.ceil((((f - f_gr) * 60 - f_min) * 60 - f_sec) * 60)
            l_mili = math.ceil((((l - l_gr) * 60 - l_min) * 60 - l_sec) * 60)
            f_gr = str(f_gr).rjust(2, '0')
            l_gr = str(l_gr).rjust(3, '0')
            f_min = str(f_min).rjust(2, '0')
            l_min = str(l_min).rjust(2, '0')
            f_sec = str(f_sec).rjust(2, '0')
            l_sec = str(l_sec).rjust(2, '0')
            f_mili = str(f_mili).rjust(2, '0')
            l_mili = str(l_mili).rjust(2, '0')
            f = 'N' + f_gr + f_min + f_sec + f_mili
            l = 'E' + l_gr + l_min + l_sec + l_mili
            coord = f + l
            yield line[2], fm, lm, coord, d, az


pairs_del_int_mid = list(midpoint_del(pairs_del_int))
pairs_del_mvl_mid = list(midpoint_del(pairs_del_mvl))

#Перевод в прямоугольную систему координат
def transform_arinc_del(points):
    for i in range(len(points)):
        rad = 6372795
        line = points[i]
        lat1 = math.radians(48 + 31/60 + 41/3600)
        lon1 = math.radians(135 + 11/60 + 17/3600)
        lat2 = math.radians(line[1])
        lon2 = math.radians(line[2])
        cl1 = math.cos(lat1)
        cl2 = math.cos(lat2)
        sl1 = math.sin(lat1)
        sl2 = math.sin(lat2)
        delta = lon2 - lon1
        cdelta = math.cos(delta)
        sdelta = math.sin(delta)
        y = math.sqrt(math.pow(cl2*sdelta,2)+math.pow(cl1*sl2-sl1*cl2*cdelta,2))
        x = sl1*sl2+cl1*cl2*cdelta
        ad = math.atan2(y,x)
        dist = ad*rad
        x = (cl1*sl2) - (sl1*cl2*cdelta)
        y = sdelta*cl2
        z = math.degrees(math.atan(-y/x))
        if (x < 0):
            z = z+180
        z2 = (z+180.) % 360. - 180
        z2 = - math.radians(z2)
        anglerad2 = z2 - ((2*math.pi)*math.floor((z2/(2*math.pi))) )
        #angledeg = (anglerad2*180)/math.pi
        x = round(((math.sin(anglerad2)*dist)/1000), 3)
        y = round(((math.cos(anglerad2)*dist)/1000), 3)
        if x>1000 and -1000<y<1000:
            k = x/250
            x = round(x+k, 3)
            yield line[0], line[1], line[2], line[3], line[5], x, y
        if x<-1000 and -1000<y<1000:
            k = x/250
            x = round(x+k, 3)
            yield line[0], line[1], line[2], line[3], line[5], x, y
        if x>1000 and y>1000:
            k = x/250
            x = round(x+k, 3)
            k2 = y/250
            y = round(y+k2, 3)
            yield line[0], line[1], line[2], line[3], line[5], x, y
        if x<-1000 and y>1000:
            k = x/250
            x = round(x+k, 3)
            k2 = y/250
            y = round(y+k2, 3)
            yield line[0], line[1], line[2], line[3], line[5], x, y
        if x>1000 and y<-1000:
            k = x/250
            x = round(x+k, 3)
            k2 = y/250
            y = round(y+k2, 3)
            yield line[0], line[1], line[2], line[3], line[5], x, y
        if x<-1000 and y<-1000:
            k = x/250
            x = round(x+k, 3)
            k2 = y/250
            y = round(y+k2, 3)
            yield line[0], line[1], line[2], line[3], line[5], x, y
        if -1000<x<1000:
            yield line[0], line[1], line[2], line[3], line[5], x, y


transform_del_int = list(transform_arinc_del(pairs_del_int_mid))
transform_del_mvl = list(transform_arinc_del(pairs_del_mvl_mid))

#Меняем угол надписи
def del_change_angle(list1):
    for i in range(len(list1)):
        line = list1[i]
        a = line[4]
        x = line[5]
        y = line[6]
        k = (abs(x)/300+abs(y)/600)*2.5
        if a < 90 and -300<x<300:
            new = 90-a
            yield line[0], line[3], a, new
        if a < 90 and -3000<x<-300:
            new = 90-a-k
            yield line[0], line[3], a, new
        if a < 90 and 300 < x < 3000:
            new = 90 - a+k
            yield line[0], line[3], a, new
        if a > 90 and a < 180 and -300<x<300:
            new = 270+(180-a)
            yield line[0], line[3], a, new
        if a > 90 and a < 180 and -3000<x<-300:
            new = 270+(180-a)-k
            yield line[0], line[3], a, new
        if a > 90 and a < 180 and 300<x<3000:
            new = 270+(180-a)+k
            yield line[0], line[3], a, new
        if a > 180 and a < 270 and -300<x<300:
            new = 90-(a-180)
            yield line[0], line[3], a, new
        if a > 180 and a < 270 and -3000<x<-300:
            new = 90-(a-180)-k
            yield line[0], line[3], a, new
        if a > 180 and a < 270 and 300<x<3000:
            new = 90-(a-180)+k
            yield line[0], line[3], a, new
        if a > 270 and a < 360 and -300<x<300:
            new = 270+(360-a)
            yield line[0], line[3], a, new
        if a > 270 and a < 360 and -3000<x<-300:
            new = 270+(360-a)-k
            yield line[0], line[3], a, new
        if a > 270 and a < 360 and 300<x<3000:
            new = 270+(360-a)+k
            yield line[0], line[3], a, new

changed_del_int=list(del_change_angle(transform_del_int))
changed_del_mvl=list(del_change_angle(transform_del_mvl))

# Отбираем пары точек
del_coords_int = []
for x in changed_del_int:
    del_coords_int.append(x[1])

del_coords_mvl = []
for x in changed_del_mvl:
    del_coords_mvl.append(x[1])

# Находим дубликаты пар
del_dup_int = {}
gen = sorted(modules.list_duplicates(del_coords_int))
for x in gen:
    del_dup_int.update(x)

del_dup_mvl = {}
gen = sorted(modules.list_duplicates(del_coords_mvl))
for x in gen:
    del_dup_mvl.update(x)

del_list_of_index_int = list(modules.sep(del_dup_int))
del_list_of_index_mvl = list(modules.sep(del_dup_mvl))

indexes_int = []
for sublist in del_list_of_index_int:
    for item in sublist:
        indexes_int.append(item)

indexes_mvl = []
for sublist in del_list_of_index_mvl:
    for item in sublist:
        indexes_mvl.append(item)

duplicates_int = []
for x in indexes_int:
    ele = changed_del_int[x]
    duplicates_int.append(ele)

duplicates_mvl = []
for x in indexes_mvl:
    ele = changed_del_mvl[x]
    duplicates_mvl.append(ele)

for x in duplicates_int:
    if x in changed_del_int:
        changed_del_int.remove(x)

for x in duplicates_mvl:
    if x in changed_del_mvl:
        changed_del_mvl.remove(x)

odd_int = duplicates_int[1::2]
even_int = duplicates_int[0::2]
odd_mvl = duplicates_mvl[1::2]
even_mvl = duplicates_mvl[0::2]

del_desw_int = list(modules.make_desw(changed_del_int))
del_desw_mvl = list(modules.make_desw(changed_del_mvl))

del_desw_mvl2 = list(modules.del_make_desw2(even_mvl, odd_mvl))

del_desw_mvl2 = list(modules.unique(del_desw_mvl2))
first_del_int = ['N: "designators 22" * route designators - Habarovsk *']
first_del_mvl = ['N: "designators 23" * route designators - Habarovsk *']

del_desw_int = author + first_del_int + del_desw_int
del_desw_mvl = author + first_del_mvl + del_desw_mvl + del_desw_mvl2

with open('%s2.Картография/DEL_DESW_INT_AUTO.SLD' % config.sintez_files, 'w', encoding='utf-8') as output3:
    for item in del_desw_int:
        output3.write("%s\n" % item)

with open('%s2.Картография/DEL_DESW_MVL_AUTO.SLD' % config.sintez_files, 'w', encoding='utf-8') as output3:
    for item in del_desw_mvl:
        output3.write("%s\n" % item)

end_time = datetime.datetime.today()

root.destroy()