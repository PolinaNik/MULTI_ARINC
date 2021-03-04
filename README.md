# Настройка MULTI_ARINC

Перед первым запуском работы программы необходимо выполнить следующие шаги:
1) создать папку "MULTI_ARINC";
2) в папке MULTI_ARINC создать 5 папок: "СИНТЕЗ", "КОРИНФ", "ОРЛ_А", "Файлы для парсинга", "program_files";
3) в папку "program_files" поместить всё содержимое репозитория;
4) в папке MULTI_ARINC/program_files открыть файл "config.py" любым редактором и прописать адреса к созданным папкам

#Описание работы MULTI_ARINC

Чтобы запустить программу, нужно выполнить скрипт "start_parsing.py". Для удобства можно создать ярлык этого скрипта, переменовать и поместить на рабочий стол.

После запуска скрипта появится окно с возможностью выбора 5 опций: 
1) прочесть инструкцию;
2) проверить документ ARINC на наличие ошибок в нумерации точек;
3) сделать разбор для СИНТЕЗА;
4) сделать разбор для КОРИНФ;
5) сделать разбор для ОРЛ-А.

Результаты разбора будут находиться в одноименных папках в MULTI_ARINC.

#Какие сторонные модули должны быть установлены для работы скрипта?
1) shapely
2) numpy
3) geog
4) transliterate
5) xlwt