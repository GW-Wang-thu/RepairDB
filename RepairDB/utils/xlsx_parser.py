# coding = gbk
import xlrd
import os
import re
import shutil
import datetime


def read_xlsx(file_name, st_row=0, st_line=0, mode=0):
    if mode == 0:
        kws = file_name.split("\\")[-1].split("-")
        j_rep_code = [kws[0] + kws[1] + kws[2]]
        data = xlrd.open_workbook(file_name)
    else:
        st_row = 3
        st_line = 0
        data = xlrd.open_workbook(file_contents=file_name.read())
    j_type = []
    j_id = []
    serve_area = []     # 0
    #
    component = []          # 1
    part = []               # 2
    detect_stage = []       # 3
    detect_file = []        # 4
    serve_time = []         # 5
    detect_method = []      # 6
    detector = []           # 7
    date = []               # 8
    defect_id = []          # 9
    defect_origin = []      # 10
    defect_type = []        # 11
    location_type = []      # 12
    location_z_ref = []     # 13
    location_z_dir = []     # 14
    location_z_dis = []     # 15
    location_x_ref = []     # 13
    location_x_dir = []     # 14
    location_x_dis = []     # 15
    location_depth = []     # 16
    size_z = []             # 17
    size_x = []             # 18
    prev_size_depth = []    # 19
    prev_size_z = []        # 20
    prev_size_x = []        # 21

    component_dict = {
        "前轮": 0,
        "挡泥板": 1,
        "后座": 2,
        "车把": 3,
        "刹车": 4
    }
    part_dict = {
        "左上壁板": 0,
        "左下壁板": 1,
        "右上壁板": 2,
        "右下壁板": 3,
        "左左壁板": 4,
        "左右壁板": 5,
        "右左壁板": 6,
        "右右壁板": 7,
        "左左蒙皮": 8,
        "左右蒙皮": 9,
        "右左蒙皮": 10,
        "右右蒙皮": 11,
        "左上盖板": 12,
        "左下盖板": 13,
        "右上盖板": 14,
        "右下盖板": 15,
    }
    location_types = {
        "口框区域": 0,  # 前轮/后座
        "连接区域": 1,
        "蜂窝区域": 2,
        "长桁端头": 3,
        "边缘区域": 4,
        "其他区域": 5
    }
    location_z_refs = {
        "1墙轴线": 0,
        "2墙轴线": 1,
        "3墙轴线": 2,
        "前缘": 3,
        "后缘": 4,
        "1梁轴线": 5,
        "2梁轴线": 6,
        "梁轴线": 7,
        "后墙": 8,
    }
    location_z_dirs = {
        "上": 0,
        "下": 1
    }
    location_x_refs = {
        "后段1肋轴线":0, "后段2肋轴线":1, "后段3肋轴线":2, "后段4肋轴线":3, "后段5肋轴线":4, "后段6肋轴线":5,
        "后段7肋轴线":6, "后段8肋轴线":7, "后段9肋轴线":8, "后段10肋轴线":9, "后段11肋轴线":10, "后段12肋轴线":11,
        "后段13肋轴线":12, "后段14肋轴线":13, "后段15肋轴线":14, "后段16肋轴线":15, "后段17肋轴线":16,
        "1肋轴线":17, "2肋轴线":18, "3肋轴线":19, "4肋轴线":20, "5肋轴线":21, "6肋轴线":22, "7肋轴线":23,
        "8肋轴线":24, "9肋轴线":25, "10肋轴线":26, "11肋轴线":27, "12肋轴线":28, "13肋轴线":29, "14肋轴线":30,
        "15肋轴线":31, "16肋轴线":32, "17肋轴线":33, "18肋轴线":34, "19肋轴线":35, "左侧边缘":36, "右侧边缘":37,
        "1前肋轴线":38, "2前肋轴线":39, "3前肋轴线":40, "4前肋轴线":41, "5前肋轴线":42, "6前肋轴线":43, "7前肋轴线":44,
        "8前肋轴线": 45, "9前肋轴线": 46, "10前肋轴线": 47, "11前肋轴线": 48, "弦向内侧": 49, "第1隔板轴线": 50, "第2隔板轴线": 51, "第3隔板轴线": 52
    }
    location_x_dirs = {
        "左": 0,
        "右": 1
    }
    defect_types = {
        "分层损伤":0,
        "长桁脱粘":1,
        "低速冲击损伤（穿透/非穿透型冲击孔）":2,
        "高速冲击损伤（穿透/非穿透型冲击孔）":3,
        "蜂窝进水（蜂窝结构内部进水）":4,
        "表面割裂损伤或深划痕（面板表面若干层被割伤）":5,
        "腐蚀/老化（基体或纤维材料老化腐蚀失效）":6,
        "雷击损伤":7,
        "功能结构损伤（涂层老化脱落等导致的吸波功能减退等）":8,
    }
    defect_origins = {
        "原始损伤":0,
        "新增损伤":1,
        "延续损伤":2,
        "扩展损伤":3
    }

    for j in range(data.nsheets):
        table = data.sheets()[j]
        for i in range(table.nrows - st_row):
            if j == 0:
                row = i + st_row
            else:
                row = i
            # 首先根据关键列判断是否为有效数据
            flag = True
            if (table.cell_value(row, st_line + 11) == "") +\
                (table.cell_value(row, st_line + 12) == "") +\
                (table.cell_value(row, st_line + 13) == "") +\
                (table.cell_value(row, st_line + 14) == "") +\
                (table.cell_value(row, st_line + 15) == "") +\
                (table.cell_value(row, st_line + 16) == "") +\
                (table.cell_value(row, st_line + 17) == "") +\
                (table.cell_value(row, st_line + 18) == "") +\
                (table.cell_value(row, st_line + 19) == "") +\
                (table.cell_value(row, st_line + 20) == "") +\
                (table.cell_value(row, st_line + 21) == "") +\
                (table.cell_value(row, st_line + 22) == "") +\
                (table.cell_value(row, st_line + 23) == ""):
                flag = False

            # 如果是有效数据，填入列表中，后期存入MySQL数据库中
            if flag:
                # try:
                if table.cell_value(row, st_line).replace(" ", "") == "":
                    j_type.append(j_type[-1])
                else:
                    j_type.append(table.cell_value(row, st_line))

                if table.cell_value(row, st_line + 1) == "":
                    j_id.append(j_id[-1])
                else:
                    j_id.append(table.cell_value(row, st_line + 1))

                if table.cell_value(row, st_line + 2).replace(" ", "") == "":
                    serve_area.append(serve_area[-1])
                else:
                    serve_area.append(table.cell_value(row, st_line + 2))

                if table.cell_value(row, st_line + 3).replace(" ", "") == "":
                    component.append(component[-1])
                else:
                    component.append(component_dict[table.cell_value(row, st_line + 3)])

                if table.cell_value(row, st_line + 4).replace(" ", "") == "":
                    part.append(part[-1])
                else:
                    part.append(part_dict[table.cell_value(row, st_line + 4)])

                if table.cell_value(row, st_line + 5).replace(" ", "") == "":
                    detect_stage.append(detect_stage[-1])
                else:
                    detect_stage.append(table.cell_value(row, st_line + 5))

                if table.cell_value(row, st_line + 6).replace(" ", "") == "":
                    if len(detect_file) > 0:
                        detect_file.append(detect_file[-1])
                    else:
                        detect_file.append("")
                else:
                    detect_file.append(table.cell_value(row, st_line + 6))
                # 1250.2h/1543.2
                if type(table.cell_value(row, st_line + 7)) == type(""):
                    if table.cell_value(row, st_line + 7).replace(" ", "") == "":
                        serve_time.append(serve_time[-1])
                    else:
                        serve_time.append(float(table.cell_value(row, st_line + 7)[:-1]))
                else:
                    if table.cell_value(row, st_line + 7) == "":
                        serve_time.append(serve_time[-1])
                    else:
                        serve_time.append(float(table.cell_value(row, st_line + 7)))

                if table.cell_value(row, st_line + 8).replace(" ", "") == "":
                    detect_method.append(detect_method[-1])
                else:
                    detect_method.append(table.cell_value(row, st_line + 8))

                if table.cell_value(row, st_line + 9).replace(" ", "") == "":
                    if len(detect_file) > 0:
                        detector.append(detect_file[-1])
                    else:
                        detector.append("")
                else:
                    detector.append(table.cell_value(row, st_line + 9))

                if table.cell_value(row, st_line + 10).replace(" ", "") == "":
                    date.append(date[-1])
                else:
                    date.append(datetime.datetime.strptime(table.cell_value(row, st_line + 10), '%Y.%m.%d'))

                defect_id.append(int(table.cell_value(row, st_line + 11)))
                defect_origin.append(defect_origins[table.cell_value(row, st_line + 12)])
                defect_type.append(defect_types[table.cell_value(row, st_line + 13)])
                location_type.append(location_types[table.cell_value(row, st_line + 14)])
                location_z_ref.append(location_z_refs[table.cell_value(row, st_line + 15)])
                location_z_dir.append(location_z_dirs[table.cell_value(row, st_line + 16)])
                location_z_dis.append(table.cell_value(row, st_line + 17))
                location_x_ref.append(location_x_refs[table.cell_value(row, st_line + 18)])
                location_x_dir.append(location_x_dirs[table.cell_value(row, st_line + 19)])
                location_x_dis.append(table.cell_value(row, st_line + 20))
                location_depth.append(table.cell_value(row, st_line + 21))
                size_z.append(table.cell_value(row, st_line + 22))
                size_x.append(table.cell_value(row, st_line + 23))
                prev_size_depth.append(table.cell_value(row, st_line + 24))
                prev_size_z.append(table.cell_value(row, st_line + 25))
                prev_size_x.append(table.cell_value(row, st_line + 26))
                # except:
                #     continue

    # 集合去重
    set_component = set(component)
    set_part = set(part)
    set_detect_stage = set(detect_stage)
    set_serve_time = set(serve_time)
    set_defect_origin = set(defect_origin)
    set_defect_type = set(defect_type)
    set_location_type = set(location_type)
    set_location_z_ref = set(location_z_ref)
    set_location_x_ref = set(location_x_ref)
    print(set_component, set_part, set_detect_stage, set_serve_time, set_defect_origin, set_defect_type, set_location_type, set_location_z_ref, set_location_x_ref)
    return [j_id, component, part, location_type,
            location_z_ref, location_z_dir, location_z_dis,
            location_x_ref, location_x_dir, location_x_dis,
            location_depth, size_z, size_x, defect_origin,
            defect_type, detect_stage, serve_time]


if __name__ == '__main__':
    file_name = r"E:\Data\JetDamageCollection\qtf清华合作资料\a-1-4-0001-无密.xlsx"
    read_xlsx(file_name, st_row=3, st_line=0)