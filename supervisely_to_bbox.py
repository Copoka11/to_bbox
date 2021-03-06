import cv2
import json
import os
import zlib
import base64
import numpy as np
import time

def base64_2_mask(s):
    z = zlib.decompress(base64.b64decode(s))
    n = np.fromstring(z, np.uint8)
    mask = cv2.imdecode(n, cv2.IMREAD_UNCHANGED)[:, :, 3].astype(bool)
    return mask

# def mask_2_base64(mask):
#     img_pil = Image.fromarray(np.array(mask, dtype=np.uint8))
#     img_pil.putpalette([0,0,0,255,255,255])
#     bytes_io = io.BytesIO()
#     img_pil.save(bytes_io, format='PNG', transparency=0, optimize=0)
#     bytes = bytes_io.getvalue()
#     return base64.b64encode(zlib.compress(bytes)).decode('utf-8')

# def get_ds_names(folder_name):
#     try:
#         namelist = os.listdir(os.path.join("data", folder_name))
#         print(namelist)
#         paths = []
#         for name in namelist:
#             cur_path = os.path.join("data", folder_name, name)
#             if os.path.isdir(cur_path):
#                 paths.append(cur_path)
#         return paths
#     except:     # ValueError
#         print("Folder not exist")

# def get_masks_from_json(json_path):
#     # try:
#     ret_masks = [] # {filename, width, hight, number, label, mask}
#     filename = json_path
#     with open(json_path, "r") as read_file:
#         data = json.load(read_file)
#         h = data["size"]["height"]
#         w = data["size"]["width"]
#         print(w, h)
#         objects = data["objects"]
#         print(objects)
#         objects_dict = {}
#         for object in objects:
#             key = object["key"]
#             label = object["classTitle"]
#             objects_dict[key] = label
#         print(objects_dict)
        
#         frames = data["frames"]
#         for frame in frames:
#             number = frame["index"]
#             figures = frame["figures"]
#             for figure in figures:
#                 label_key = figure["objectKey"]
#                 label = "unknown"
#                 if label_key in objects_dict:
#                     label = objects_dict[label_key]
#                 left, top = figure["geometry"]["bitmap"]["origin"]
#                 base64_data = figure["geometry"]["bitmap"]["data"]
#                 mask = base64_2_mask(base64_data)
#                 mask_full = np.zeros((h, w), dtype=bool)
#                 mask_full[top: (top + mask.shape[0]), left: (left + mask.shape[1])] = mask
#                 print(mask_full.shape)
#                 ret_masks.append({"filename": filename,
#                                     "width": w,
#                                     "heigh": h,
#                                     "number": number,
#                                     "label": label,
#                                     "mask": mask_full,
#                                     "left": left,
#                                     "top": top})
#     return ret_masks

def get_points_from_json(json_path):
    # try:
    ret_points = [] # {filename, width, hight, number, label, mask}
    filename = json_path
    with open(json_path, "r") as read_file:
        data = json.load(read_file)
        h = data["size"]["height"]
        w = data["size"]["width"]
        print(w, h)
        objects = data["objects"]
        print(objects)
        objects_dict = {}
        for cur_object in objects:
            class_name = cur_object["classTitle"]
            points = cur_object["points"]["exterior"] 
            # points.extend(cur_object["points"]["interior"])
            objects_dict[class_name] = points
        print(objects_dict)
        ret_points = objects_dict
    return ret_points, h, w

# def get_frames_from_video(video_path):
#     ret_frames = []
#     cap = cv2.VideoCapture(video_path)
#     ret, image = cap.read()
   
#     while ret:
#         ret_frames.append(image)
#         ret, image = cap.read()
#     return ret_frames

def get_bbox(points):
    xs, ys = [], []
    for point in points:
        xs.append(point[0])
        ys.append(point[1])
    left = min(xs)
    top = min(ys)
    right = max(xs)
    bottom = max(ys)    
    return left, top, right, bottom

# print("test_started")
# paths = get_ds_names("test_rsl")
# print(paths)

def coords_to_yolo_coords(left, top, right, bottom, h, w):
    xc = ((left + right) / 2) / w 
    yc = ((top + bottom) / 2) / h
    box_w = (right - left) / w
    box_h = (bottom - top) / h
    return xc, yc, box_w, box_h

path = ".."

path_ann = os.path.join(path, "ann")
ann_files = os.listdir(path_ann)
ann_files.sort()

path_img = os.path.join(path, "img")
img_files = os.listdir(path_img)
img_files.sort()


json_file_path = os.path.join(path_ann, ann_files[2000])
print(json_file_path)

img_file_path = os.path.join(path_img, img_files[2000])
print(img_file_path)


points_dict, h, w = get_points_from_json(json_file_path)

cv2.namedWindow("img", cv2.WINDOW_NORMAL)  
cv2.resizeWindow("img", 800, 450)
cv2.namedWindow("RHand", cv2.WINDOW_NORMAL)  
cv2.resizeWindow("RHand", 800, 450)
cv2.namedWindow("LHand", cv2.WINDOW_NORMAL)  
cv2.resizeWindow("LHand", 800, 450)

points = points_dict["RHand"]
print(img_file_path)
print(points)
img = cv2.imread(img_file_path)


for point in points:
    print(point)
    img = cv2.circle(img, tuple(point), 2, (0,255,0), 2)

cv2.imshow("img", img)

#####################################################################

class_dict = {"RHand":0, "LHand":1}

for i, a in zip(img_files, ann_files):
    # print(i, a)
    i_path = os.path.join(path_img, i)
    a_path = os.path.join(path_ann, a)
    # print(i_path, a_path)

    k = cv2.waitKey(1) & 0xff
    if k == ord('q') or k == 27:
        break

    cur_img = cv2.imread(i_path)
    cur_img_draw = np.copy(cur_img)

    points_dict, h, w = get_points_from_json(a_path)
    # print(points_dict.items())
    strings = []

    for hand in points_dict.items():
        class_name = hand[0]
        points = hand[1]
        left, top, right, bottom = get_bbox(points)
        bbox_width = right - left
        bbox_height = bottom - top

        if (bbox_height < 40) or (bbox_width < 40): 
            
            font = cv2.FONT_HERSHEY_SIMPLEX 
            cur_img_draw = cv2.putText(cur_img_draw, 'BAD', (100,100), font,  
                            3, (255,0,0), 2, cv2.LINE_AA) 
            cv2.imshow("img", cur_img_draw)
            continue    
            #time.sleep(3)

        else:
            class_coords = str(class_dict[class_name]) + " " + str(left) + " " + str(top) + " " + str(right) + " " + str(bottom) + "\n"
            strings.append(class_coords)

            # создаем папку с Правыми руками (right), | папку с левыми, но отраженными руками (left_flip).
            # файлы имя_изобр.jpg и имя_изобр.txt     | файлы имя_изобр_flip.jpg и имя_изобр_flip.txt  
            if class_name == "RHand":
                cv2.imwrite("./right/"+ i, cur_img)

                text_file = open('./right/' + i[:-4] + ".txt", "w")
                xc, yc, box_w, box_h = coords_to_yolo_coords(left, top, right, bottom, h, w)
                cur_string = "0 " + str(xc) + " " + str(yc) + " " + str(box_w) + " " + str(box_h)
                text_file.write(cur_string)
                text_file.close()
                cur_img_draw = cv2.rectangle(cur_img_draw, (left, top), (right, bottom), (0,0,255), 3) 
                cv2.imshow("RHand", cur_img_draw)

            elif class_name == "LHand":
                cur_img_flip = cv2.flip(cur_img, 1)
                cv2.imwrite("./left_flip/"+ i, cur_img_flip)

                text_file = open('./left_flip/' + i[:-4] + ".txt", "w")

                xc, yc, box_w, box_h = coords_to_yolo_coords(left, top, right, bottom, h, w)
                xc = 1 - xc
                cur_string = "0 " + str(xc) + " " + str(yc) + " " + str(box_w) + " " + str(box_h)
                text_file.write(cur_string)
                text_file.close()
                cur_img_flip = cv2.rectangle(cur_img_flip, (w-left, top), (w-right, bottom), (0,0,255), 3) 
                cv2.imshow("LHand", cur_img_flip)

            else:
                pass

        for point in points:
            # print(point)
            cur_img_draw = cv2.circle(cur_img_draw, tuple(point), 2, (0,255,0), 2)
        cur_img_draw = cv2.rectangle(cur_img_draw, (left, top), (right, bottom), (0,0,255), 3) 
        
    if len(strings) > 0:
        
        text_file = open('pascal_voc_txt/'+str(i)+".txt", "w")
        text_file.writelines(strings)
        text_file.close()

    cv2.imshow("img", cur_img_draw)    

cv2.waitKey(0)




