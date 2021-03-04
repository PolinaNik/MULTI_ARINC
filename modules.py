"""Файл со всеми программными функциями"""

import re
import math
from shapely.geometry import Point
from collections import defaultdict
from itertools import groupby
from itertools import chain
import config

#Поиск всех точек в файле ARINC
def get_points(list):
    for i in range(len(list)):
        line = list[i]
        pat1 = re.compile(r'^(SEEUP ).+')
        pat2 = re.compile(r'^(TEEUD).+')
        pat3 = re.compile(r'^(SPACP ).+')
        pat4 = re.compile(r'^(SEEUU).+')
        pat5 = re.compile(r'^(SEEUP).+')
        pat6 = re.compile(r'^(SEEUP UH).+')
        pat7 = re.compile(r'(?=[^0-9]{5})(?:.+)')
        s1 = pat1.search(line)
        s2 = pat2.search(line)
        s3 = pat3.search(line)
        s4 = pat4.search(line)
        s5 = pat5.search(line)
        s6 = pat6.search(line)
        name = line[13:18]
        s7 = pat7.search(name)
        if len(line) >= 41:
            if line[32] == 'N' and line[41] == 'E' and not s1 \
                    and not s2 and not s3 and not s4 and not s5:
                yield line
            if line[32] == 'N' and line[41] == 'E' and s6 and s7:
                pat8 = re.compile(r'\s|\S+')
                s8 = pat8.search(name)
                point = s8.group()
                if len(point) == 5:
                    yield line

"""Выбор только имени и коррдинаты точки, за исключением точки с координатами Хабаровска 
(это нужно для исключения дальнейших ошибок при рассчетах)"""
def get_data(file):
    for i in range(len(file)):
        line = file[i]
        name = line[13:18]
        coord = line[32:51]
        N = line[32]
        E = line[41]
        pat = re.compile(r'\s|\S+')
        s = pat.search(name)
        ind = line[19:21]
        pat2 = re.compile(r'[0-9]+')
        s2 = pat2.search(name)
        if s and N == 'N' and E == 'E' and coord != 'N48314100E135111700' and not s2:
            point = s.group()
            if len(point) > 1:
                yield point, coord, ind

def get_line(file):
    for i in range(len(file)):
        line = file[i]
        name = line[13:18]
        coord = line[32:51]
        N = line[32]
        E = line[41]
        pat = re.compile(r'\s|\S+')
        s = pat.search(name)
        ind = line[19:21]
        pat2 = re.compile(r'[0-9]+')
        s2 = pat2.search(name)
        if s and N == 'N' and E == 'E' and coord != 'N48314100E135111700' and not s2:
            point = s.group()
            if len(point) > 1:
                yield line

#Получение координат точек для дальнешего сравнения с базой
def data(points):
    for i in range(len(points)):
        line = points[i]
        name = line[0]
        lat = line[1][5:7]
        lon = line[1][15:17]
        yield name, lat, lon


#Полигон для Синтеза
poly = config.poly_sintez

#Сравнение точек из файла ARINC с зоной полигона для СИНТЕЗА
def inside(points):
    for i in range(len(points)):
        line = points[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        lat = gr_lat + min_lat/60 + sec_lat/3600
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        lon = gr_lon + min_lon/60 + sec_lon/3600
        lat = lat*math.pi/180
        lon = lon*math.pi/180
        p = Point(lat, lon)
        if poly.contains(p):
            yield line


poly2 = config.poly_radar
#Сравнение точек из файла ARINC с зоной полигона для локатора
def inside_radar(points):
    for i in range(len(points)):
        line = points[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        lat = gr_lat + min_lat/60 + sec_lat/3600
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        lon = gr_lon + min_lon/60 + sec_lon/3600
        p = Point(lon, lat)
        if poly2.contains(p):
            yield line

poly3 = config.poly_kor
#Сравнение точек из файла ARINC с зоной полигона для КОРИНФ
def inside_kor(points):
    for i in range(len(points)):
        line = points[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        lat = gr_lat + min_lat/60 + sec_lat/3600
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        lon = gr_lon + min_lon/60 + sec_lon/3600
        p = Point(lon, lat)
        if poly3.contains(p):
            yield line

def inside_line(points):
    for i in range(len(points)):
        line = points[i]
        gr_lat = int(line[33:35])
        min_lat = int(line[35:37])
        sec_lat = int(line[37:39])
        lat = gr_lat + min_lat/60 + sec_lat/3600
        gr_lon = int(line[42:45])
        min_lon = int(line[45:47])
        sec_lon = int(line[47:49])
        lon = gr_lon + min_lon/60 + sec_lon/3600
        lat = lat*math.pi/180
        lon = lon*math.pi/180
        p = Point(lat, lon)
        if poly.contains(p):
            yield line

#Получение имен точек
def names(points):
    for i in range(len(points)):
        line = points[i]
        name = line[0]
        yield name

#Выбираем только уникальные названия
def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    for x in unique_list:
        yield x

#Конвертация списка к нужному формату
def convert_to_list(func):
    for i in range(len(func)):
        line = func[i]
        a = line[0]
        pat = re.compile(r'\d+')
        b = pat.search(line[1][4:6])
        c = pat.search(line[2][5:7])
        lat = b.group()
        lon = c.group()
        yield a, lat, lon

#Преобразуем строки в список
def conver_to_list2(db2):
    for i in range(len(db2)):
        line = db2[i]
        name = line[0]
        yield name

def convert_to_list3(func):
    for i in range(len(func)):
        line = func[i]
        route = line[0]
        point = line[1]
        id = line[2]
        mah = line[3]
        yield route, point, id, mah


#Нахождение дубликатов точек ARINC, которые попали в полигон
def list_duplicates(seq):
    tally = defaultdict(list)
    for i, item in enumerate(seq):
        tally[item].append(i)
    yield ((key, locs) for key,locs in tally.items()
        if len(locs)>1)

#Нахождение индексов дубликатов
def sep(dup):
    for key in dup:
        index = dup[key]
        yield index

def sep2(list, indexes):
    for item in indexes:
        line = list[item]
        yield line

#Устанавливаем ключи к одинаковым названиям
def dup_numbers(list1):
    for i in range(len(list1)):
        line = list1[i]
        if line[2] == 'UH':
            name1 = line[0]+'1'
            yield name1, line[1], line[2]
        if line[2] == 'UE':
            name2 = line[0]+'2'
            yield name2, line[1], line[2]
        if line[2] == 'ZY':
            name3 = line[0]+'3'
            yield name3, line[1], line[2]
        if line[2] == 'UI':
            name4 = line[0]+'4'
            yield name4, line[1], line[2]
        if line[2] != 'UH' and line[2] != 'UE' and line[2] != 'ZY' and line[2] != 'UI':
            yield line[0], line[1], line[2]

# def dup_numbers2(list1):
#     for i in range(len(list1)):
#         line = list1[i]
#         if line[2] == 'UH':
#             name1 = line[0]+'1'
#             yield name1, line[1], line[2], line[3]
#         if line[2] == 'UE':
#             name2 = line[0]+'2'
#             yield name2, line[1], line[2], line[3]
#         if line[2] == 'ZY':
#             name3 = line[0]+'3'
#             yield name3, line[1], line[2], line[3]
#         if line[2] == 'UI':
#             name4 = line[0]+'4'
#             yield name4, line[1], line[2], line[3]
#         if line[2] != 'UH' and line[2] != 'UE' and line[2] != 'ZY' and line[2] != 'UI':
#             yield line[0], line[1], line[2], line[3]


#Преобразуем спиок в строки
def listTosring(arinc_duplicates):
    for i in range(len(arinc_duplicates)):
        line = arinc_duplicates[i]
        str1 = " "
        yield str1.join(line)

#Преобразуем спиок в строки
def listTosring2(list1):
    for i in range(len(list1)):
        line = list1[i]
        str1 = ", "
        yield str1.join(line)

#Заполняем файл POINTS_W.sld
def filling1(list, type):
    for i in range(len(list)):
        line = list[i]
        point = line[0]
        coord = line[1]
        if len(point) == 3:
            str1 = 'S: "6" <R4> '+ coord
            str2 = 'T: <R2> '+coord + ' / '+ point + ' / '
            yield str1, str2
        if len(point) == 2:
            str1 = 'S: "1" <R1> '+ coord
            str2 = 'T: <R2> '+coord+' / '+ point + ' / '
            str3 = 'S: "9" <R3> '+coord
            yield str1, str2, str3, str2
        if len(point) != 2 and len(point) != 3 and point not in type:
            str1 = 'S: "1" <R1> '+coord
            str2 = 'T: <R2> ' +coord+ ' / '+point + ' / '
            yield str1, str2
        if len(point) != 2 and len(point) != 3 and point in type:
            str1 = 'S: "2" <R1> '+coord
            str2 = 'T: <R2> ' +coord+ ' / '+point + ' / '
            yield str1, str2

def filling1_1(lst, type):
    for i in range(len(lst)):
        line = lst[i]
        point = line[0]
        coord = line[1]
        if len(point) == 3:
            str0 = 'SD: 0.0, -1.0'
            str1 = 'S: "6" <R4> '+ coord
            str2 = 'T: <R2> '+coord + ' / '+ point + ' / '
            yield str0, str1, str2
        if len(point) == 2:
            str0 = 'SD: 0.0, -1.0'
            str1 = 'S: "1" <R1> '+ coord
            str2 = 'T: <R2> '+coord+ ' / '+ point + ' / '
            str3 = 'S: "9" <R3> '+coord
            yield str0, str1, str2, str0, str3, str2
        if len(point) != 2 and len(point) != 3 and point not in type:
            str0 = 'SD: 0.0, -1.0'
            str1 = 'S: "1" <R1> '+coord
            str2 = 'T: <R2> ' +coord+ ' / '+point + ' / '
            yield str0, str1, str2
        if len(point) != 2 and len(point) != 3 and point in type:
            str0 = 'SD: 0.0, -1.0'
            str1 = 'S: "2" <R1> '+coord
            str2 = 'T: <R2> ' +coord+ ' / '+point + ' / '
            yield str0, str1, str2

def filling2(list):
    for i in range(len(list)):
        line = list[i]
        point = line[0]
        coord = line[1]
        str0 = 'SD: 0.0, 0.0'
        str1 = 'S: "9" <R1, BLACK> '+coord
        str2 = 'T: <BLACK, R1> ' +coord+ ' / '+point + ' / '
        yield str0, str1, str2

def filling2_1(lst):
    for i in range(len(lst)):
        line = lst[i]
        point = line[0]
        coord = line[1]
        str0 = 'SD: 0.0, -1.0'
        str1 = 'S: "9" <R1, BLACK> '+ coord
        str2 = 'T: <BLACK, R1> '+coord + ' / '+ point + ' / '
        yield str0, str1, str2

#Нахождение трасс в документе ARINC
def get_routes(file):
    for i in range(len(file)):
        line = file[i]
        pat1 = re.compile(r'^(SEEUER ).+')
        pat2 = re.compile(r'^(SPACER ).+')
        pat3 = re.compile(r'^(SCANER ).+')
        s1 = pat1.search(line)
        s2 = pat2.search(line)
        s3 = pat3.search(line)
        if s1:
            points = s1.group()
            yield points
        if s2:
            points = s2.group()
            yield points
        if s3:
            points = s3.group()
            yield points

#Формируем список, отсекая лишнюю информацию из строк, и, оставляя названия трасс и точек
def get_position1_r(list1_r):
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

#Список, в котором содержаться только точки (названия трасс отсекаем)
def get_second_part(routes):
    for i in range(len(routes)):
        line = routes[i]
        point = line[1]
        ind = line[2]
        yield point, ind

#Список, в котором содержаться только точки и идентификаторы(названия координаты отсекаем)
def get_second_part2(list1):
    for i in range(len(list1)):
        line = list1[i]
        point = line[0]
        ind = line[2]
        yield point, ind

#Функция сравнения
def find(new, old):
    for element in new:
        if element in old:
            yield element

#Создаем лист с дубликатами a_doubles(ARINC) и b_doubles(база), для дальнейшего сранения координат
def select(doubles, func):
    for i in range(len(func)):
        line = func[i]
        name = line[0]
        for q in range(len(doubles)):
            name2 = doubles[q]
            if name == name2:
                yield line

#Сравнение совпавших по имени точек по координатам
def compare(a_doubles, b_doubles):
    for element in a_doubles:
        if element not in b_doubles:
            yield element

#Нахождение точек с разницей в координатах больше 10 географических секунд
def diff(new_coord, old_coord):
    for i in range(len(new_coord)):
        line1 = new_coord[i]
        line2 = old_coord[i]
        lat1 = int(line1[1])
        lat2 = int(line2[1])
        lon1 = int(line1[2])
        lon2 = int(line2[2])
        if abs(lat1-lat2) > 10 or abs(lon1-lon2) > 10:
            yield line2

#Получаем координаты для точек из "списка на добавление"
def get_coordinates(add_list, points):
    for i in range(len(points)):
        line = points[i]
        name = line[0]
        for q in range(len(add_list)):
            name2 = add_list[q]
            if name == name2:
                yield line

#Перерасчет географических координат в прямоугольной системе координат с центром в точке HBR
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
            yield line[0], shir, dolg, x, y
        if x<-1000 and -1000<y<1000:
            k = x/250
            x = round(x+k, 3)
            yield line[0], shir, dolg, x, y
        if x>1000 and y>1000:
            k = x/250
            x = round(x+k, 3)
            k2 = y/250
            y = round(y+k2, 3)
            yield line[0], shir, dolg, x, y
        if x<-1000 and y>1000:
            k = x/250
            x = round(x+k, 3)
            k2 = y/250
            y = round(y+k2, 3)
            yield line[0], shir, dolg, x, y
        if x>1000 and y<-1000:
            k = x/250
            x = round(x+k, 3)
            k2 = y/250
            y = round(y+k2, 3)
            yield line[0], shir, dolg, x, y
        if x<-1000 and y<-1000:
            k = x/250
            x = round(x+k, 3)
            k2 = y/250
            y = round(y+k2, 3)
            yield line[0], shir, dolg, x, y
        if -1000<x<1000:
            yield line[0], shir, dolg, x, y

#Запрос на получение уже имеющейся информации о точках
def info_points(lst1, lst2):
    for i in range(len(lst1)):
        line = lst1[i]
        name1 = line[0]
        for q in range(len(lst2)):
            name2 = lst2[q]
            if name1 == name2:
                yield line

"""Соединение имеющейся информации из базы с обновленной координатной частью"""
def mixing(lst1, lst2):
    for i in range(len(lst1)):
        line = lst1[i]
        name = line[0]
        for q in range(len(lst2)):
            line2 = lst2[q]
            name2 = line2[0]
            if name == name2:
                yield name, line2[1], line2[2], line2[3], line2[4], line[5], line[6], line[7], line[8], line[9], line[10], line[11], line[12], line[13], line[14], line[15]

#Создание заспроса на добавление точек
def query(coordinates):
    for i in range(len(coordinates)):
        line = coordinates[i]
        PN_NAME = line[0]
        PN_LAT = line[1]
        PN_LON = line[2]
        PN_X = round(line[3], 2)
        PN_Y = round(line[4], 2)
        query = """INSERT IGNORE INTO point (PN_NAME, PN_LAT, PN_LON, PN_X, PN_Y, P_RP) VALUES ('%s', '%s', '%s', %s, %s, 1);"""
        yield query % (PN_NAME, PN_LAT, PN_LON, PN_X, PN_Y)

#Запрос на модифицирование точек
def query2(update_points):
    for i in range(len(update_points)):
        line = update_points[i]
        PN_NAME = line[0]
        PN_LAT = line[1]
        PN_LON = line[2]
        PN_X = line[3]
        PN_Y = line[4]
        PN_FNAME = line[5]
        PN_NUM = line[6]
        P_RP = line[7]
        P_ACT = line[8]
        P_STATE = line[9]
        P_FIR = line[10]
        P_TMA = line[11]
        P_AOR = line[12]
        P_SECTOR = line[13]
        P_ZONE = line[14]
        PN_CAPTION = line[15]
        query = """UPDATE point set PN_NAME = '%s', PN_LAT = '%s', PN_LON = '%s', PN_X = %s, PN_Y = %s, PN_FNAME = '%s', PN_NUM = %s, P_RP = %s, P_ACT = %s, P_STATE = %s, P_FIR = %s, P_TMA = %s, P_AOR = %s, P_SECTOR = %s, P_ZONE = %s, PN_CAPTION = '%s' WHERE PN_NAME = '%s';"""
        yield query % (PN_NAME, PN_LAT, PN_LON, PN_X, PN_Y, PN_FNAME, PN_NUM, P_RP, P_ACT, P_STATE, P_FIR, P_TMA, P_AOR, P_SECTOR, P_ZONE, PN_CAPTION, PN_NAME)


#Исходя из совпавших точек, выбираем трассы из ARINC
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

def select_routes2(routes, both_points):
    for i in range(len(routes)):
        line = routes[i]
        point1 = line[1]
        ind1 = line[2]
        for q in range(len(both_points)):
            line2 = both_points[q]
            point2 = line2[0]
            ind2 = line2[1]
            if point1 == point2 and ind1 == ind2:
                yield line

#Считаем трассы, где точек больше двух
def count_list(list1):
    for i in range(len(list1)):
        line = list1[i]
        len1 = len(line)
        if len1 > 1:
            yield line

#Установка порядковых номеров точек на маршруте
def counter_of_points(routes):
    for key, group in groupby(routes, lambda x: x[0]):
        for i,each in enumerate(group, start=1):
            yield "{}".format(key), "{}".format(each[1]), "{}".format(each[2]),"{}".format(i), "{}".format(each[3])

#Установка порядковых номеров точек на маршруте2
def counter_of_points_arinc(routes):
    for key, group in groupby(routes, lambda x: x[0]):
        for i,each in enumerate(group, start=1):
            yield "{}".format(key), "{}".format(each[1]), "{}".format(i)

#Находим только МВЛьные трассы
def find_rus(list):
    for i in range(len(list)):
        name = list[i]
        one = name[0]
        if one == 'А' or one == 'Б' or one == 'В' or one == 'Г' or one == 'Д' or one == 'Е' or one == 'Ж' or one == 'З' or one == 'И' or one == 'К' or one == 'Л' or one == 'М' or one == 'Н' or one == 'О' or one == 'П' or one == 'Р' or one == 'С' or one == 'Т' or one == 'У' or one == 'Ф' or one == 'Х' or one == 'Ц' or one == 'Ч' or one == 'Ш' or one == 'Щ' or one == 'Э' or one == 'Ю' or one == 'Я':
            yield name

def find_rus2(list):
    for i in range(len(list)):
        line = list[i]
        name = line[0]
        one = name[0]
        if one == 'А' or one == 'Б' or one == 'В' or one == 'Г' or one == 'Д' or one == 'Е' or one == 'Ж' or one == 'З' or one == 'И' or one == 'К' or one == 'Л' or one == 'М' or one == 'Н' or one == 'О' or one == 'П' or one == 'Р' or one == 'С' or one == 'Т' or one == 'У' or one == 'Ф' or one == 'Х' or one == 'Ц' or one == 'Ч' or one == 'Ш' or one == 'Щ' or one == 'Э' or one == 'Ю' or one == 'Я':
            yield line

#Транслитерация кириллицы на латиницу.
def transliterate(name):
   slovar = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
      'ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
      'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h',
      'ц':'c','ч':'cz','ш':'sh','щ':'scz','ъ':'','ы':'y','ь':'','э':'e',
      'ю':'u','я':'ja', 'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'E',
      'Ж':'ZH','З':'Z','И':'I','Й':'I','К':'K','Л':'L','М':'M','Н':'N',
      'О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'H',
      'Ц':'C','Ч':'CZ','Ш':'SH','Щ':'SCH','Ъ':'','Ы':'Y','Ь':'','Э':'E',
      'Ю':'U','Я':'YA',',':'','?':'',' ':'_','~':'','!':'','@':'','#':'',
      '$':'','%':'','^':'','&':'','*':'','(':'',')':'','-':'','=':'','+':'',
      ':':'',';':'','<':'','>':'','\'':'','"':'','\\':'','/':'','№':'',
      '[':'',']':'','{':'','}':'','ґ':'','ї':'', 'є':'','Ґ':'g','Ї':'i',
      'Є':'e', '—':''}
   for key in slovar:
      name = name.replace(key, slovar[key])
   return name

#Делаем транслит на латиницу МВЛьных трасс из базы
def translit(rus):
    for i in range(len(rus)):
        line = rus[i]
        new = transliterate(line)
        yield new

def translit2(rus):
    for i in range(len(rus)):
        line = rus[i]
        trass = transliterate(line[0])
        point = transliterate(line[1])
        yield trass, point, line[2], line[3]

def translit3(rus):
    for i in range(len(rus)):
        line = rus[i]
        trass = transliterate(line[0])
        yield trass, line[1], line[2], line[3], line[4]


#Пересчитываем градусы в радианы
def gradus(list1):
    for i in range(len(list1)):
        line = list1[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        mili_lat = int(line[1][7:9])
        lat = gr_lat + min_lat/60 + sec_lat/3600 + mili_lat/216000
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        mili_lon = int(line[1][17:19])
        lon = gr_lon + min_lon/60 + sec_lon/3600 + mili_lon/216000
        yield line[0], lat, lon

def gradus2(point):
    gr_lat = int(point[1:3])
    min_lat = int(point[3:5])
    sec_lat = int(point[5:7])
    lat = gr_lat + min_lat / 60 + sec_lat / 3600
    gr_lon = int(point[10:13])
    min_lon = int(point[13:15])
    sec_lon = int(point[15:17])
    lon = gr_lon + min_lon / 60 + sec_lon / 3600
    return lat, lon

#Нахождение дубликатов - вторая часть. Дубли МВЛьные
def latin_rus(distinct, rus):
    for i in range(len(distinct)):
        line = distinct[i]
        name_id = line[0:2]
        name_num = line[2:]
        for q in range(len(rus)):
            line2 = rus[q]
            name_id2 = line2[0:2]
            name_num2 = line2[2:]
            if name_id == 'KD' and name_id2 == 'КД' and name_num == name_num2:
                yield line2
            if name_id == 'KI' and name_id2 == 'КИ' and name_num == name_num2:
                yield line2
            if name_id == 'KR' and name_id2 == 'КР' and name_num == name_num2:
                yield line2
            if name_id == 'KT' and name_id2 == 'КТ' and name_num == name_num2:
                yield line2

def get_doubles(rus_new3, doubles3):
    for i in range(len(rus_new3)):
        line = rus_new3[i]
        name = line[0]
        for q in range(len(doubles3)):
            name2 = doubles3[q]
            if name == name2:
                yield line

def add_values(non_doubles):
    for i in range(len(non_doubles)):
        name = non_doubles[i]
        p1 = 'NULL'
        p2 = 'NULL'
        p3 = 'NULL'
        p4 = 'NULL'
        yield name, p1, p2, p3, p4

def add_query1(new):
    for i in range(len(new)):
        line = new[i]
        name = line[0]
        p1 = line[1]
        p2 = line[2]
        p3 = line[3]
        p4 = line[4]
        query = """INSERT IGNORE INTO _trass (T_NAME, T_DIR, T_DEST1, T_DEST2, T_DESCR) VALUES ('%s', '%s', '%s', '%s', '%s');"""
        yield query % (name, p1, p2, p3, p4)


#Объединяем отфильтрованные трассы и точки с ключами
def combine_names(list1, dup_dict):
    new = list(chain.from_iterable(list1))
    for i in range(len(new)):
        line = new[i]
        name = line[1]
        ind = line[2]
        if name in dup_dict.keys() and ind == dup_dict[name][1]:
            new = dup_dict[name][0]
            yield line[0], new, ind, line[3], line[4]
        else:
            yield line

# def combine_names(list1, list2):
#     new = list(chain.from_iterable(list1))
#     for i in range(len(new)):
#         line = new[i]
#         name = line[1]
#         ind = line[2]
#         for q in range(len(list2)):
#             line2 = list2[q]
#             pat = re.compile(r'[A-Z].+')
#             s = pat.search(line2[0])
#             name2 = s.group()
#             if name == name2 and ind == line2[2]:
#                 yield line[0], line2[0], line[2], line[3]
#             if name != name2 and ind != line2[2]:
#                 yield line

#Убираем номера точек
def delete_numbers(list1):
    for i in range(len(list1)):
        line = list1[i]
        for q in range(len(line)):
            line2 = line[q]
            route = line2[0]
            point = line2[1]
            yield route, point

def delete_numbers2(list1):
    for i in range(len(list1)):
        line = list1[i]
        for q in range(len(line)):
            line2 = line[q]
            route = line2[0]
            point = line2[1]
            ind = line2[2]
            yield route, point, ind

#Формируем нужную последовательность
def right_order(list_1):
    for i in range(len(list_1)):
        line = list_1[i]
        new = list(chain.from_iterable(line))
        new = list(dict.fromkeys(new))
        yield new

#Формируем нужную последовательность
def right_order2(list_1):
    for i in range(len(list_1)):
        line = list_1[i]
        for w in range(len(line)):
            line2 = line[w]
            route = line[0]
            points = line[1:]
            yield line2, points


#Перерасчет координат
def transform(points):
    for i in range(len(points)):
        line = points[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        mili_lat = int(line[1][7:9])
        lat = gr_lat + min_lat/60 + sec_lat/3600 + mili_lat/216000
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        mili_lon = int(line[1][17:19])
        lon = gr_lon + min_lon/60 + sec_lon/3600 + mili_lon/216000
        yield line[0], line[2], lat, lon

#Привести трассы и точки к нужному виду для дальнейших расчетов
def ordered2(list1):
    for i in range(len(list1)):
        line = list1[i]
        route = line[0]
        points = line[1:]
        yield route, points


#________________MAH. Получение разрешенных высот из БД и соотношение их с трассами и точками из документа ARINC______________________________
def select_mah(full):
    for i in range(len(full)):
        line = full[i]
        mah = str(line[3])
        pat = re.compile(r'(MAH).+')
        s = pat.search(mah)
        if s:
            yield line[0], line[1], line[3]

#Соединение разрешенных высот с трассами и точками из документа ARINC
def combine(all, mah):
    for i in range(len(all)):
        line = all[i]
        trass = line[0]
        point = line[1]
        for q in range(len(mah)):
            line2 = mah[q]
            trass2 = line2[0]
            point2 = line2[1]
            if trass == trass2 and point == point2:
                yield trass, point, line[2], line2[2]

def separate(new_list_with_mah):
    for i in range(len(new_list_with_mah)):
        line = new_list_with_mah[i]
        yield line[0], line[1], line[2]

def add_null(new_list_without_mah):
    for i in range(len(new_list_without_mah)):
        line = new_list_without_mah[i]
        new = 'NULL'
        yield line[0], line[1], line[2], new

def parameters(add_trass_final):
    for i in range(len(add_trass_final)):
        line = add_trass_final[i]
        yield line[0], line[1], int(line[2]), line[3]

#Находим трассы, где точек больше 40
def excess(add_trass_final):
    for i in range(len(add_trass_final)):
        line = add_trass_final[i]
        number = int(line[2])
        if number > 40:
            yield line[0]

#Формируем список с трассами, где больше 40 точек
def over_40(add_trass_final, excess_routes):
    for i in range(len(add_trass_final)):
        line = add_trass_final[i]
        name = line[0]
        for q in range(len(excess_routes)):
            line1 = excess_routes[q]
            if name == line1:
                yield line

#Формируем список с трассами, где меньше или равно 40 точек
def less_40(add_trass_final, excess_routes):
    for i in range(len(add_trass_final)):
        line = add_trass_final[i]
        name = line[0]
        for q in range(len(excess_routes)):
            line1 = excess_routes[q]
            if name != line1:
                yield line

#Создание запроса на добавление трасс и точек
def add_query_over40(routes):
    for i in range(len(routes)):
        line = routes[i]
        route = line[0]
        point = line[1]
        number = line[2]
        mah = line[3]
        query = """#INSERT IGNORE INTO _trass_point (T_NAME, TP_NUM, PN_NAME, TP_ID, T_DESIGNATION, T_LENGTH, T_WIDTH, T_FL, T_FLAGS) VALUES ('%s', %s, '%s', NULL, NULL, NULL, NULL, NULL, '%s');"""
        yield query % (route, number, point, mah)

def add_query_less40(routes):
    for i in range(len(routes)):
        line = routes[i]
        route = line[0]
        point = line[1]
        number = line[2]
        mah = line[3]
        query = """INSERT IGNORE INTO _trass_point (T_NAME, TP_NUM, PN_NAME, TP_ID, T_DESIGNATION, T_LENGTH, T_WIDTH, T_FL, T_FLAGS) VALUES ('%s', %s, '%s', NULL, NULL, NULL, NULL, NULL, '%s');"""
        yield query % (route, number, point, mah)


#Сопоставление трасс и точек с перерасчитанными координатами
def desw(list1, list2):
    for i in range(len(list1)):
        line = list1[i]
        for q in range(len(line)):
            info = line[q]
            route = info[0]
            point = info[1]
            ind = info[2]
            for w in range(len(list2)):
                line2 = list2[w]
                name = line2[0]
                ind2 = line2[1]
                if point == name and ind == ind2:
                    yield route, line2
#
#Заполнение файла с маршрутами
def fill_routes(list):
    for i in range(len(list)):
        line = list[i]
        route = line[0]
        points = line[1]
        str1 = ", "
        points = str1.join(points)
        info = "L: " + "*" + route + "* " + points
        yield info

#Представление в нужном формате
def delta_lat(list1):
    for i in range(len(list1)):
        line = list1[i]
        output = [(line[q][1][0], line[q+1][1][0], line[q][1][2], line[q][1][3], line[q+1][1][2], line[q+1][1][3], line[q][0]) for q in range(len(line) - 1)]
        yield output

#Измерение расстояние между точками
def distance(list1):
    for i in range(len(list1)):
        line = list1[i]
        route = line[6]
        r = 6372795
        f1 = math.radians(line[2])
        f2 = math.radians(line[4])
        l1 = math.radians(line[3])
        l2 = math.radians(line[5])
        df = f2-f1
        dl = l2-l1
        a = ((math.sin(df/2))**2)+(math.cos(f1)*math.cos(f2)*(math.sin(dl/2))**2)
        c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = r*c
        yield line[0], line[2], line[3], line[1], line[4], line[5], d, route

def midpoint(list1):
    for i in range(len(list1)):
        line = list1[i]
        d = line[6]
        f1 = math.radians(line[1])
        l1 = math.radians(line[2])
        f2 = math.radians(line[4])
        l2 = math.radians(line[5])
        dl = l2-l1
        # if d >= 60000:
        Bx = math.cos(f2)*math.cos(dl)
        By = math.cos(f2)*math.sin(dl)
        fm = math.atan2(math.sin(f1)+math.sin(f2), math.sqrt((math.cos(f1)+Bx)**2+By**2))
        lm = l1+math.atan2(By, math.cos(f1)+Bx)
        yield line[1], line[2], math.degrees(fm), math.degrees(lm), line[7]
            # yield math.degrees(fm), math.degrees(lm), line[4], line[5], line[7]

def midpoint2(list1):
    for i in range(len(list1)):
        line = list1[i]
        d = line[6]
        f1 = math.radians(line[1])
        l1 = math.radians(line[2])
        f2 = math.radians(line[4])
        l2 = math.radians(line[5])
        dl = l2-l1
        if d >= config.d:
            Bx = math.cos(f2)*math.cos(dl)
            By = math.cos(f2)*math.sin(dl)
            fm = math.atan2(math.sin(f1)+math.sin(f2), math.sqrt((math.cos(f1)+Bx)**2+By**2))
            lm = l1+math.atan2(By, math.cos(f1)+Bx)
            yield line[1], line[2], math.degrees(fm), math.degrees(lm), line[7]
            # yield math.degrees(fm), math.degrees(lm), line[4], line[5], line[7]

#Расчитываем азимут между соседними точками
def azimut_between(lst):
    for i in range(len(lst)):
        line = lst[i]
        f1 = math.radians(line[0])
        l1 = math.radians(line[1])
        f2 = math.radians(line[2])
        l2 = math.radians(line[3])
        y = math.sin(l2-l1)*math.cos(f2)
        x = math.cos(f1)*math.sin(f2)-math.sin(f1)*math.cos(f2)*math.cos(l2-l1)
        az = math.degrees(math.atan2(y,x))
        az = (az+360)%360
        Bx = math.cos(f2)*math.cos(l2-l1)
        By = math.cos(f2)*math.sin(l2-l1)
        fm = math.atan2(math.sin(f1)+math.sin(f2), math.sqrt((math.cos(f1)+Bx)**2+By**2))
        lm = l1+math.atan2(By, math.cos(f1)+Bx)
        fm = math.degrees(fm)
        lm = math.degrees(lm)
        yield line[2], line[3], az, line[4]
        # yield fm, lm, az, line[4]

#Перарасчитываем кординаты точек десигнатов
def transform2(points):
    for i in range(len(points)):
        rad = 6372795
        line = points[i]
        lat2 = math.radians(line[0])
        lon2 = math.radians(line[1])
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
        angledeg = (anglerad2*180)/math.pi
        x = round(((math.sin(anglerad2)*dist)/1000), 3)
        y = round(((math.cos(anglerad2)*dist)/1000), 3)
        yield line[0], line[1], line[2], line[3], x, y

#Меняем угол надписи
def change_angle(list1):
    for i in range(len(list1)):
        line = list1[i]
        a = line[2]
        x = line[4]
        y = line[5]
        k = (abs(x)/300+abs(y)/600)*2.5
        if a < 90 and -300<x<300:
            new = 90-a
            yield line[0], line[1], line[3], a, new
        if a < 90 and -3000<x<-300:
            new = 90-a-k
            yield line[0], line[1], line[3], a, new
        if a < 90 and 300 < x < 3000:
            new = 90 - a+k
            yield line[0], line[1], line[3], a, new
        if a > 90 and a < 180 and -300<x<300:
            new = 270+(180-a)
            yield line[0], line[1], line[3], a, new
        if a > 90 and a < 180 and -3000<x<-300:
            new = 270+(180-a)-k
            yield line[0], line[1], line[3], a, new
        if a > 90 and a < 180 and 300<x<3000:
            new = 270+(180-a)+k
            yield line[0], line[1], line[3], a, new
        if a > 180 and a < 270 and -300<x<300:
            new = 90-(a-180)
            yield line[0], line[1], line[3], a, new
        if a > 180 and a < 270 and -3000<x<-300:
            new = 90-(a-180)-k
            yield line[0], line[1], line[3], a, new
        if a > 180 and a < 270 and 300<x<3000:
            new = 90-(a-180)+k
            yield line[0], line[1], line[3], a, new
        if a > 270 and a < 360 and -300<x<300:
            new = 270+(360-a)
            yield line[0], line[1], line[3], a, new
        if a > 270 and a < 360 and -3000<x<-300:
            new = 270+(360-a)-k
            yield line[0], line[1], line[3], a, new
        if a > 270 and a < 360 and 300<x<3000:
            new = 270+(360-a)+k
            yield line[0], line[1], line[3], a, new

#Перевод десятичных градусов в градусы, минуты и секунды
def minutes(list1):
    for i in range(len(list1)):
        line = list1[i]
        f = float(line[0])
        l = float(line[1])
        f_gr = math.trunc(f)
        l_gr = math.trunc(l)
        f_min = math.trunc((f - f_gr)*60)
        l_min = math.trunc((l-l_gr)*60)
        f_sec = math.trunc(((f - f_gr)*60-f_min)*60)
        l_sec = math.trunc(((l-l_gr)*60-l_min)*60)
        f_mili = math.ceil((((f-f_gr)*60-f_min)*60-f_sec)*60)
        l_mili = math.ceil((((l-l_gr)*60-l_min)*60-l_sec)*60)
        f_gr = str(f_gr).rjust(2, '0')
        l_gr = str(l_gr).rjust(3, '0')
        f_min = str(f_min).rjust(2, '0')
        l_min = str(l_min).rjust(2, '0')
        f_sec = str(f_sec).rjust(2, '0')
        l_sec = str(l_sec).rjust(2, '0')
        f_mili = str(f_mili).rjust(2, '0')
        l_mili = str(l_mili).rjust(2, '0')
        f = 'N'+f_gr+f_min+f_sec+f_mili
        l = 'E'+l_gr+l_min+l_sec+l_mili
        coord = f+l
        yield line[2], coord, line[3], line[4]

#Создание списка с десигнаторов
def make_desw(list1):
    for i in range(len(list1)):
        line = list1[i]
        route = line[0]
        sa = str(round(line[3], 1))
        coord = line[1]
        a = line[2]
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


def make_desw2(list1, list2):
    for i in range(len(list1)):
        line = list1[i]
        line2 = list2[i]
        route = line[0]
        route2 = line2[0]
        sa = str(round(line[3], 1))
        coord = line[1]
        a = line[2]
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


#Разбиваем на части
def chunks(lst, n):
    for q in range(len(lst)):
        line = lst[q]
        for i in range(0, len(line), n):
            yield line[i:i + n]

#Отбираем пары точек
def check_pairs(lst):
    for i in range(len(lst)):
        line = lst[i]
        list_1 = []
        list_1.append(line[0])
        list_1.append(line[1])
        yield list_1


def from_even(lst, d):
    for i in range(len(lst)):
        line = lst[i]
        coord = line[1]
        lat1 = math.radians(int(coord[1:3])+ int(coord[3:5])/60 + int(coord[5:7])/3600)
        lon1 = math.radians(int(coord[10:13]) + int(coord[13:15])/60 + int(coord[15:17])/3600)
        az = line[2]
        rad = 6371
        b = d/rad
        if az < 180:
            new_az = az+90
            az_r = math.radians(new_az)
            lat2 = math.asin(math.sin(lat1)*math.cos(b)+math.cos(lat1)*math.sin(b)*math.cos(az_r))
            lon2 = lon1 + math.atan2(math.sin(az_r)*math.sin(b)*math.cos(lat1), math.cos(b)-math.sin(lat1)*math.sin(lat2))
            lat2 = math.degrees(lat2)
            lon2 = math.degrees(lon2)
            yield lat2, lon2, line[0], line[2], line[3]
        if 180<az<360:
            new_az = az-90
            az_r = math.radians(new_az)
            lat2 = math.asin(math.sin(lat1)*math.cos(b)+math.cos(lat1)*math.sin(b)*math.cos(az_r))
            lon2 = lon1 + math.atan2(math.sin(az_r)*math.sin(b)*math.cos(lat1), math.cos(b)-math.sin(lat1)*math.sin(lat2))
            lat2 = math.degrees(lat2)
            lon2 = math.degrees(lon2)
            yield lat2, lon2, line[0], line[2], line[3]

#Проверяем на наложение
def only_coords(lst):
    for i in range(len(lst)):
        line = lst[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        lat = gr_lat + min_lat / 60 + sec_lat / 3600
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        lon = gr_lon + min_lon / 60 + sec_lon / 3600
        p = Point(lat, lon)
        yield line[0], p, line[2], lat, lon, line[1]

def check(output, sec):
    for i in range(len(output)):
        line = output[i]
        sec1 = sec/3600
        poly = line[0].buffer(sec1)
        point = line[1]
        if poly.contains(point):
            yield line[2], line[3], line[4], line[5], line[6]
            yield line[7], line[8], line[9], line[10], line[11]

def get_same(lst1, lst2):
    for i in range(len(lst2)):
        line2 = lst2[i]
        name2 = line2[0]
        ind2 = line2[1]
        for q in range(len(lst1)):
            line = lst1[q]
            name = line[0]
            ind = line[2]
            if name == name2 and ind ==ind2:
                yield line


#Формируем список, отсекая лишнюю информацию из строк, и, оставляя названия трасс и точек
def get_position2(list1_r):
    for i in range(len(list1_r)):
        line = list1_r[i]
        name = line[13:18]
        point = line[29:34]
        min = line[83:88]
        max = line[93:98]
        pat = re.compile(r'[^\s]+')
        s = pat.search(name)
        s2 = pat.search(point)
        name = s.group()
        point = s2.group()
        ind = line[34:36]
        yield name, point, ind, min, max

#Сопоставление трасс и точек с перерасчитанными координатами
def desw2(list1, list2):
    for i in range(len(list1)):
        line = list1[i]
        route = line[0]
        point = line[1]
        ind = line[2]
        for w in range(len(list2)):
            line2 = list2[w]
            name = line2[0]
            ind2 = line2[1]
            if point == name and ind == ind2:
                yield route, point, line2[2], line2[3], line[3], line[4]

"""Отбор трасс с больше, чем одной тоской на маршруте"""
def long_FL(lst):
    for i in range(len(lst)):
        line = lst[i]
        if len(line)>1:
            yield line

#Представление в нужном формате
def delta_lat2(list1):
    for i in range(len(list1)):
        line = list1[i]
        output = [(line[q][1], line[q+1][1], line[q][2], line[q][3], line[q+1][2], line[q+1][3], line[q][0], line[q][4], line[q][5]) for q in range(len(line) - 1)]
        yield output


#Измерение расстояние между точками
def distance2(list1):
    for i in range(len(list1)):
        line = list1[i]
        route = line[6]
        min = line[7]
        max = line[8]
        r = 6372795
        f1 = math.radians(line[2])
        f2 = math.radians(line[4])
        l1 = math.radians(line[3])
        l2 = math.radians(line[5])
        df = f2-f1
        dl = l2-l1
        a = ((math.sin(df/2))**2)+(math.cos(f1)*math.cos(f2)*(math.sin(dl/2))**2)
        c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = r*c
        yield line[0], line[2], line[3], line[1], line[4], line[5], d, route, min, max


def midpoint_FL(list1):
    for i in range(len(list1)):
        line = list1[i]
        d = line[6]
        f1 = math.radians(line[1])
        l1 = math.radians(line[2])
        f2 = math.radians(line[4])
        l2 = math.radians(line[5])
        dl = l2-l1
        # if d >= 60000:
        Bx = math.cos(f2)*math.cos(dl)
        By = math.cos(f2)*math.sin(dl)
        fm = math.atan2(math.sin(f1)+math.sin(f2), math.sqrt((math.cos(f1)+Bx)**2+By**2))
        lm = l1+math.atan2(By, math.cos(f1)+Bx)
        yield line[1], line[2], math.degrees(fm), math.degrees(lm), line[7], line[8], line[9]
            # yield math.degrees(fm), math.degrees(lm), line[4], line[5], line[7], line[8], line[9]

def midpoint2_FL(list1):
    for i in range(len(list1)):
        line = list1[i]
        d = line[6]
        f1 = math.radians(line[1])
        l1 = math.radians(line[2])
        f2 = math.radians(line[4])
        l2 = math.radians(line[5])
        dl = l2-l1
        if d >= config.d:
            Bx = math.cos(f2)*math.cos(dl)
            By = math.cos(f2)*math.sin(dl)
            fm = math.atan2(math.sin(f1)+math.sin(f2), math.sqrt((math.cos(f1)+Bx)**2+By**2))
            lm = l1+math.atan2(By, math.cos(f1)+Bx)
            yield line[1], line[2], math.degrees(fm), math.degrees(lm), line[7], line[8], line[9]

#Расчитываем азимут между соседними точками
def azimut_between2(lst):
    for i in range(len(lst)):
        line = lst[i]
        rad = 6372795
        f1 = math.radians(line[0])
        l1 = math.radians(line[1])
        f2 = math.radians(line[2])
        l2 = math.radians(line[3])
        y = math.sin(l2-l1)*math.cos(f2)
        x = math.cos(f1)*math.sin(f2)-math.sin(f1)*math.cos(f2)*math.cos(l2-l1)
        az = math.degrees(math.atan2(y,x))
        az = (az+360)%360
        if 0 < az < 180:
            az=az+180
            az = math.radians(az)
            b = 10000/rad
            f_s = math.asin(math.sin(f2)*math.cos(b)+math.cos(f2)*math.sin(b)*math.cos(az))
            l_s = l2+math.atan2(math.sin(az)*math.sin(b)*math.cos(f2), math.cos(b)-math.sin(f2)*math.sin(f_s))
            yield math.degrees(f_s), math.degrees(l_s), math.degrees(az), line[4], line[5], line[6]
        if 180 < az < 360:
            az = math.radians(az)
            b = 10000/rad
            f_s = math.asin(math.sin(f2)*math.cos(b)+math.cos(f2)*math.sin(b)*math.cos(az))
            l_s = l2+math.atan2(math.sin(az)*math.sin(b)*math.cos(f2), math.cos(b)-math.sin(f2)*math.sin(f_s))
            yield math.degrees(f_s), math.degrees(l_s), math.degrees(az), line[4], line[5], line[6]

#Перарасчитываем кординаты точек десигнатов
def transform2_FL(points):
    for i in range(len(points)):
        rad = 6372795
        line = points[i]
        lat2 = math.radians(line[0])
        lon2 = math.radians(line[1])
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
        yield line[0], line[1], line[2], line[3], line[4], line[5], x, y

#Меняем угол надписи
def change_angle2(list1):
    for i in range(len(list1)):
        line = list1[i]
        a = line[2]
        x = line[6]
        y = line[7]
        k = (abs(x)/300+abs(y)/600)*2.5
        if a < 90 and -300<x<300:
            new = 90-a
            yield line[0], line[1], line[3], a, new, line[4], line[5]
        if a < 90 and -3000<x<-300:
            new = 90-a-k
            yield line[0], line[1], line[3], a, new, line[4], line[5]
        if a < 90 and 300 < x < 3000:
            new = 90 - a+k
            yield line[0], line[1], line[3], a, new, line[4], line[5]
        if a > 90 and a < 180 and -300<x<300:
            new = 270+(180-a)
            yield line[0], line[1], line[3], a, new, line[4], line[5]
        if a > 90 and a < 180 and -3000<x<-300:
            new = 270+(180-a)-k
            yield line[0], line[1], line[3], a, new, line[4], line[5]
        if a > 90 and a < 180 and 300<x<3000:
            new = 270+(180-a)+k
            yield line[0], line[1], line[3], a, new, line[4], line[5]
        if a > 180 and a < 270 and -300<x<300:
            new = 90-(a-180)
            yield line[0], line[1], line[3], a, new, line[4], line[5]
        if a > 180 and a < 270 and -3000<x<-300:
            new = 90-(a-180)-k
            yield line[0], line[1], line[3], a, new, line[4], line[5]
        if a > 180 and a < 270 and 300<x<3000:
            new = 90-(a-180)+k
            yield line[0], line[1], line[3], a, new, line[4], line[5]
        if a > 270 and a < 360 and -300<x<300:
            new = 270+(360-a)
            yield line[0], line[1], line[3], a, new, line[4], line[5]
        if a > 270 and a < 360 and -3000<x<-300:
            new = 270+(360-a)-k
            yield line[0], line[1], line[3], a, new, line[4], line[5]
        if a > 270 and a < 360 and 300<x<3000:
            new = 270+(360-a)+k
            yield line[0], line[1], line[3], a, new, line[4], line[5]


#Перевод десятичных градусов в градусы, минуты и секунды
def minutes2(list1):
    for i in range(len(list1)):
        line = list1[i]
        f = float(line[0])
        l = float(line[1])
        f_gr = math.trunc(f)
        l_gr = math.trunc(l)
        f_min = math.trunc((f - f_gr)*60)
        l_min = math.trunc((l-l_gr)*60)
        f_sec = math.trunc(((f - f_gr)*60-f_min)*60)
        l_sec = math.trunc(((l-l_gr)*60-l_min)*60)
        f_mili = math.ceil((((f-f_gr)*60-f_min)*60-f_sec)*60)
        l_mili = math.ceil((((l-l_gr)*60-l_min)*60-l_sec)*60)
        f_gr = str(f_gr).rjust(2, '0')
        l_gr = str(l_gr).rjust(3, '0')
        f_min = str(f_min).rjust(2, '0')
        l_min = str(l_min).rjust(2, '0')
        f_sec = str(f_sec).rjust(2, '0')
        l_sec = str(l_sec).rjust(2, '0')
        f_mili = str(f_mili).rjust(2, '0')
        l_mili = str(l_mili).rjust(2, '0')
        f = 'N'+f_gr+f_min+f_sec+f_mili
        l = 'E'+l_gr+l_min+l_sec+l_mili
        coord = f+l
        yield line[2], coord, line[3], line[4], line[5], line[6]

#Создание списка с десигнаторов
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

def make_desw2_FL(list1):
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

def connecting(chained_minutes, zon):
    for i in range(len(chained_minutes)):
        line = chained_minutes[i]
        for q in range(len(zon)):
            if zon[q] == line[0]:
                yield line

def desw_pairs(list):
    for i in range(len(list)-1):
        line = list[i]
        line2 = list[i+1]
        if line[1]==line2[1]:
            yield line, line2

def combine_coord(list1, list2):
    for i in range(len(list1)):
        line1 = list1[i]
        name1 = line1[0]
        coord1 = line1[1]
        for q in range(len(list2)):
            line2 = list2[q]
            route = line2[0]
            points = line2[1:]
            for w in range(len(points)):
                point = points[w]
                if name1 == point:
                    yield route, name1, coord1

def route_coord(ordered, new):
    for i in range(len(ordered)):
        line = ordered[i]
        route = line[0]
        points = line[1:]
        for w in range(len(points)):
            point = points[w]
            for e in range(len(new)):
                line2 = new[e]
                route2 = line2[0]
                point2 = line2[1]
                coord = line2[2]
                if route == route2 and point == point2:
                    yield route, point, coord


def make_seq(list):
    for i in range(len(list)):
        line = list[i]
        route = line[0][0]
        new = []
        for q in range(len(line)):
            info = line[q]
            point = info[2]
            new.append(point)
            yield route, new

def delete_zero_int(list):
    for i in range(len(list)):
        line = list[i]
        min = line[4]
        max = line[5]
        if min[0:2] != 'FL' and max[0:2] != 'FL' and max != 'UNLTD' and min != '     ' and min !='' and max !='':
            min = int(min)
            max = int(max)
            yield line[0], line[1], line[2], line[3], min, max
        if min[0:2] != 'FL' and max == 'UNLTD' and min !='':
            min = int(line[4])
            max = line[5]
            yield line[0], line[1], line[2], line[3], min, max
        if line[4][0:2] != 'FL' and line[5][0:2] == 'FL' and min !='':
            min = int(line[4])
            max = line[5]
            yield line[0], line[1], line[2], line[3], min, max
        if line[4][0:2] == 'FL' and line[5][0:2] == 'FL':
            yield line[0], line[1], line[2], line[3], line[4], line[5]
        if line[4][0:2] == 'FL' and line[5] == 'UNLTD':
            yield line[0], line[1], line[2], line[3], line[4], line[5]
        if min == '' and max == '':
            yield line[0], line[1], line[2], line[3], line[4], line[5]

def make_metr_mvl(list):
    for i in range(len(list)):
        line = list[i]
        min = int(round(int(line[4])*0.3048*2, -2) // 2)
        max = int(round(int(line[5])*0.3048*2, -2) // 2)
        yield line[0], line[1], line[2], line[3], min, max


def find_disorder(list):
    for i in range(len(list)):
        line = list[i]
        for q in range(len(line)-1):
            number1 = int(line[q][4])
            number2 = int(line[q+1][4])
            if number2-number1 != 1:
                yield line[q], line[q+1]


def for_log_points(non_common, inside_points):
    for i in range(len(non_common)):
        point = non_common[i]
        for q in range(len(inside_points)):
            line = inside_points[q]
            point2 = line[0]
            if point == point2:
                yield line

def compare_new_points_and_routes(filtred_routes_num,test):
    for i in range(len(filtred_routes_num)):
        line = filtred_routes_num[i]
        point = line[1]
        ind = line[2]
        for q in range(len(test)):
            line2 = test[q]
            point2 = line2[0]
            ind2 = line2[2]
            if point == point2 and ind ==ind2:
                yield line[0], line[1], line2[1], line[3]


def make_tab(tab):
    for i in range(tab.nrows):
        list = []
        for q in range(tab.ncols):
            list.append(tab.cell_value(i, q))
            yield list

def more3(lst):
    for i in range(len(lst)):
        line = lst[i]
        if len(line)>2:
            yield line[0], line[1:]

def paires_points(lst):
    for i in range(len(lst)):
        line = lst[i]
        route = line[0]
        points = line[1]
        output = [(route, points[q], points[q+1]) for q in range(len(points)-1)]
        yield output

def midpoint_del_routes(lst):
    for i in range(len(lst)):
        line = lst[i]
        f1 = math.radians(line[1])
        l1 = math.radians(line[2])
        f2 = math.radians(line[3])
        l2 = math.radians(line[4])
        dl = l2-l1
        Bx = math.cos(f2)*math.cos(dl)
        By = math.cos(f2)*math.sin(dl)
        fm = math.atan2(math.sin(f1)+math.sin(f2),math.sqrt((math.cos(f1)+Bx))**2+By**2)
        lm = l1 + math.atan2(By, math.cos(f1)+Bx)
        y = math.sin(dl)*math.cos(f2)
        x = math.cos(f1)*math.sin(f2)-math.sin(f1)*math.cos(f2)*math.cos(dl)
        az = math.degrees(math.atan2(y,x))
        az = (az+360)%360
        yield line[0], math.degrees(fm), math.degrees(lm), az

#Перарасчитываем кординаты точек десигнатов
def transform3(points):
    for i in range(len(points)):
        rad = 6372795
        line = points[i]
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
        angledeg = (anglerad2*180)/math.pi
        x = round(((math.sin(anglerad2)*dist)/1000), 3)
        y = round(((math.cos(anglerad2)*dist)/1000), 3)
        yield line[0], line[1], line[2], line[3], x, y

#Меняем угол надписи
def del_change_angle(list1):
    for i in range(len(list1)):
        line = list1[i]
        a = line[3]
        x = line[4]
        y = line[5]
        k = (abs(x)/300+abs(y)/600)*2.5
        if a < 90 and -300<x<300:
            new = 90-a
            yield line[0], line[1], line[2], a, new
        if a < 90 and -3000<x<-300:
            new = 90-a-k
            yield line[0], line[1], line[2], a, new
        if a < 90 and 300 < x < 3000:
            new = 90 - a+k
            yield line[0], line[1], line[2], a, new
        if a > 90 and a < 180 and -300<x<300:
            new = 270+(180-a)
            yield line[0], line[1], line[2], a, new
        if a > 90 and a < 180 and -3000<x<-300:
            new = 270+(180-a)-k
            yield line[0], line[1], line[2], a, new
        if a > 90 and a < 180 and 300<x<3000:
            new = 270+(180-a)+k
            yield line[0], line[1], line[2], a, new
        if a > 180 and a < 270 and -300<x<300:
            new = 90-(a-180)
            yield line[0], line[1], line[2], a, new
        if a > 180 and a < 270 and -3000<x<-300:
            new = 90-(a-180)-k
            yield line[0], line[1], line[2], a, new
        if a > 180 and a < 270 and 300<x<3000:
            new = 90-(a-180)+k
            yield line[0], line[1], line[2], a, new
        if a > 270 and a < 360 and -300<x<300:
            new = 270+(360-a)
            yield line[0], line[1], line[2], a, new
        if a > 270 and a < 360 and -3000<x<-300:
            new = 270+(360-a)-k
            yield line[0], line[1], line[2], a, new
        if a > 270 and a < 360 and 300<x<3000:
            new = 270+(360-a)+k
            yield line[0], line[1], line[2], a, new

#Перевод десятичных градусов в градусы, минуты и секунды
def del_minutes(list1):
    for i in range(len(list1)):
        line = list1[i]
        f = float(line[1])
        l = float(line[2])
        f_gr = math.trunc(f)
        l_gr = math.trunc(l)
        f_min = math.trunc((f - f_gr)*60)
        l_min = math.trunc((l-l_gr)*60)
        f_sec = math.trunc(((f - f_gr)*60-f_min)*60)
        l_sec = math.trunc(((l-l_gr)*60-l_min)*60)
        f_mili = math.ceil((((f-f_gr)*60-f_min)*60-f_sec)*60)
        l_mili = math.ceil((((l-l_gr)*60-l_min)*60-l_sec)*60)
        f_gr = str(f_gr).rjust(2, '0')
        l_gr = str(l_gr).rjust(3, '0')
        f_min = str(f_min).rjust(2, '0')
        l_min = str(l_min).rjust(2, '0')
        f_sec = str(f_sec).rjust(2, '0')
        l_sec = str(l_sec).rjust(2, '0')
        f_mili = str(f_mili).rjust(2, '0')
        l_mili = str(l_mili).rjust(2, '0')
        f = 'N'+f_gr+f_min+f_sec+f_mili
        l = 'E'+l_gr+l_min+l_sec+l_mili
        coord = f+l
        yield line[0], coord, line[3], line[4]

def del_make_desw2(list1, list2):
    for i in range(len(list1)):
        line = list1[i]
        for q in range(len(list2)):
            line2 = list2[q]
            route = line[0]
            route2 = line2[0]
            sa = str(round(line[3], 1))
            coord = line[1]
            a = line[2]
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

#testtesttest