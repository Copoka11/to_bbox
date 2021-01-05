supervisely to bbox convert

скрипт supervisely_to_bbox.py  берет координаты точек supervisely ("geometryType": "polygon") и переводит в формат pascal_voc для детектора (выделяет bounding boxы правой и левой руки)

supervisely_to_bbox.py переводит в формат:

      | left      | top       | right     | bottom
------|-----------|-----------|-----------|---------
класс | мин(х)    | мин(у)    | макс(х)   | макс(у)
------|-----------|-----------|-----------|---------
0     | 50        | 60        | 100       | 120

класс RHand - 0, LHahs - 1
