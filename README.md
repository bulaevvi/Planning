# MADE "Введение в мобильную робототехнику"  
## ДЗ №5 - Построение траектории  

### Выполнил: студент группы DS-32 Булаев Владимир  

Внимание:  
- в зависимости ок количества препятствий расчет траектории может длиться очень долго (десятки минут - единицы часов). 
Поэтому по совету коллег был создан альтернативный скрипт `task1_tkinter_shapely.py`, в котором для расчета полигонов используется библиотека `Shapely`. 
Это позволило ускорить расчеты на несколько порядков.  
- Чем больше препятствий и чем сложнее конфигурация, тем дольше идут расчеты.  
- Если необходимо построить траектории несколько раз, то надо перезапускать скрипт заново.  

Установка бибилиотеки Shapely:
`pip install Shapely`  

Запуск быстрого скрипта: `python task1_tkinter_shapely.py`  

Запуск базового скрипта: `python task1_tkinter_sympy.py` - не рекомендуется, т.к. работает очень долго.  

В работе опробовались несколько вариантов эвристик: манхеттенское и евклидово расстояние. Первое позволяет строить более короткие пути, 
но на мой взгляд они более рискованные с точки зрения "вписывания" в повороты. Поэтому в итоге я отдал предпочтение евклидовой метрике.
Не смотря на то, что с ней расстояние получается больше, траектории получаются более плавные и естественные.  

Для ускорения поиска в скрипте используется параметр `DISCRETE` - размер шага поиска.  Чем больше это значение, тем быстрее идет поиск траектории,
но тем ниже точность (и наоборот). При значениях `DISCRETE` менее 20 в сложных конфигурациях построение траектории может занять демятки минут в быстром 
варианте и несколько часов в базовом скрипте, поэтому будьте осторожны с этим параметром.  

Пример работы скрипта приведен в скриншоте `example.png`
