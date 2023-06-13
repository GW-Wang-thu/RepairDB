# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import os.path

from django.db import models

NDT_file_dir = r'D:\Codes\RepairDB\RepairDatabase_v2\files\NDT\\'
DMAP_file_dir = r'D:\Codes\RepairDB\RepairDatabase_v2\imgs\DMAP\\'


class JetInfo(models.Model):
    jet_types = (
        (0, "J11"),
        (1, "J11BS"),
        (2, "J16"),
        (3, "d")
    )
    jet_type = models.SmallIntegerField(verbose_name="战机型号", choices=jet_types, default=0)
    jet_serial = models.CharField(verbose_name="战机编号", max_length=255, unique=True)
    jet_serve_region = models.CharField(verbose_name="服役地点", max_length=255)
    jet_service_start_time = models.DateTimeField(verbose_name="战机入列年月日")

    def __str__(self):
        # return "Type: " + self.jet_type_list[self.jet_type][1] + " Serial: " + self.jet_serial
        return "Type:" + self.jet_types[self.jet_type][1] + " Serial:" + self.jet_serial


class DefectInfo(models.Model):
    maintain_rec = models.ForeignKey(verbose_name="维护记录", to="MaintainRecInfo", to_field='id', blank=True,
                                     null=True, on_delete=models.SET_NULL)
    components = [
        (0, "前轮"),
        (1, "挡泥板"),
        (2, "后座"),
        (3, "车把"),
        (4, "刹车")
    ]
    component = models.SmallIntegerField(verbose_name="部件", choices=components)
    parts = [
        (0, "左上壁板"),    # 前轮/后座
        (1, "左下壁板"),
        (2, "右上壁板"),
        (3, "右下壁板"),
        (4, "左左壁板"),    # 挡泥板
        (5, "左右壁板"),
        (6, "右左壁板"),
        (7, "右右壁板"),
        (8, "左左蒙皮"),    # 车把
        (9, "左右蒙皮"),
        (10, "右左蒙皮"),
        (11, "右右蒙皮"),
        (12, "左上盖板"),    # 前轮/后座
        (13, "左下盖板"),
        (14, "右上盖板"),
        (15, "右下盖板"),
    ]
    part = models.SmallIntegerField(verbose_name="零件", choices=parts)
    location_types = [
        (0, "口框区域"),  # 前轮/后座
        (1, "连接区域"),
        (2, "蜂窝区域"),
        (3, "长桁端头"),
        (4, "边缘区域"),
        (5, "其他区域")
    ]
    location_type = models.SmallIntegerField(verbose_name="区域类型", choices=location_types)
    # 前轮：1墙轴线, 2墙轴线, 2墙轴线, 前缘, 后缘
    # 挡泥板：1梁轴线, 2梁轴线, 前缘, 后缘
    # 后座：后墙, 后缘, 后缘
    location_z_refs = [
        (0, "1墙轴线"),
        (1, "2墙轴线"),
        (2, "3墙轴线"),
        (3, "前缘"),
        (4, "后缘"),
        (5, "1梁轴线"),
        (6, "2梁轴线"),
        (7, "梁轴线"),
        (8, "后墙")
    ]
    defect_origins = [
        (0, "原始损伤"),
        (1, "新增损伤"),
        (2, "延续损伤"),
        (3, "扩展损伤")
    ]
    defect_origin = models.SmallIntegerField(verbose_name="损伤起始", choices=defect_origins, blank=True)
    location_z_ref = models.SmallIntegerField(verbose_name="展向基准", choices=location_z_refs)
    location_z_direc = models.BooleanField(verbose_name="相对位置", choices=[(0, "上"), (1, "下")], default=0)
    location_z_dist = models.IntegerField(verbose_name="距离(mm)")
    # 建立不同主结构与次结构的对应关系
    # '后段4肋轴线', '9前肋轴线', '后端17肋轴线', '后段9肋轴线', '后段10肋轴线', '后段12肋轴线', '弦向内侧', '9肋轴线', '10肋轴线',
    # '4肋轴线', '12肋轴线', '2前肋轴线', '1肋轴线', '3肋轴线', '15肋轴线', '后段3肋轴线', '后端13肋轴线', '后段5肋轴线', '7肋轴线'
    # '后段6肋轴线', '后段17肋轴线', '4前肋轴线', '左侧边缘', '6肋轴线', '后段14肋轴线', '后段7肋轴线', '后段1肋轴线', '8肋轴线',
    # '11肋轴线', '后段15肋轴线', '5肋轴线', '后段11肋轴线', '10前肋轴线', '14肋轴线', '后段8肋轴线', '右侧边缘', '17肋轴线',
    # '后段16肋轴线', '13肋轴线', '5前肋轴线', '6前肋轴线', '后段13肋轴线', '2肋轴线'
    location_x_refs = [
        (0, "后段1肋轴线"), (1, "后段2肋轴线"), (2, "后段3肋轴线"), (3, "后段4肋轴线"), (4, "后段5肋轴线"), (5, "后段6肋轴线"),
        (6, "后段7肋轴线"), (7, "后段8肋轴线"), (8, "后段9肋轴线"), (9, "后段10肋轴线"), (10, "后段11肋轴线"), (11, "后段12肋轴线"),
        (12, "后段13肋轴线"), (13, "后段14肋轴线"), (14, "后段15肋轴线"), (15, "后段16肋轴线"), (16, "后段17肋轴线"),
        (17, "1肋轴线"), (18, "2肋轴线"), (19, "3肋轴线"), (20, "4肋轴线"), (21, "5肋轴线"), (22, "6肋轴线"), (23, "7肋轴线"),
        (24, "8肋轴线"), (25, "9肋轴线"), (26, "10肋轴线"), (27, "11肋轴线"), (28, "12肋轴线"), (29, "13肋轴线"), (30, "14肋轴线"),
        (31, "15肋轴线"), (32, "16肋轴线"), (33, "17肋轴线"), (34, "18肋轴线"), (35, "19肋轴线"), (36, "左侧边缘"), (37, "右侧边缘"),
        (38, "1前肋轴线"), (39, "2前肋轴线"), (40, "3前肋轴线"), (41, "4前肋轴线"), (42, "5前肋轴线"), (43, "6前肋轴线"), (44, "7前肋轴线"),
        (45, "8前肋轴线"), (46, "9前肋轴线"), (47, "10前肋轴线"), (48, "11前肋轴线"), (49, "弦向内侧"), (50, "第1隔板轴线"), (51, "第2隔板轴线"), (52, "第3隔板轴线")
    ]

    location_x_ref = models.SmallIntegerField(verbose_name="展向基准", choices=location_z_refs)
    location_x_direc = models.BooleanField(verbose_name="相对位置", choices=[(0, "左"), (1, "右")], default=0)
    location_x_dist = models.IntegerField(verbose_name="距离(mm)")

    location_thickness = models.CharField(verbose_name="厚度分布", max_length=32)

    size_z = models.IntegerField(verbose_name="展向损伤尺度(mm)")     # 最近一次检测检出的最大损伤尺寸
    size_x = models.IntegerField(verbose_name="弦向损伤尺度(mm)")

    defect_types = (
        (0, "分层"),
        (1, "长桁脱粘"),
        (2, "低速冲击损伤（穿透/非穿透型冲击孔）"),
        (3, "高速冲击损伤（穿透/非穿透型冲击孔）"),
        (4, "蜂窝进水（蜂窝结构内部进水）"),
        (5, "表面割裂损伤或深划痕（面板表面若干层被割伤）"),
        (6, "腐蚀/老化（基体或纤维材料老化腐蚀失效）"),
        (7, "雷击损伤"),
        (8, "功能结构损伤（涂层老化脱落等导致的吸波功能减退等）"),
    )
    defect_type = models.SmallIntegerField(verbose_name="缺陷类型", choices=defect_types)

    status = (
        (0, "无需修理"),
        (1, "等待修理"),
        (2, "修理完毕"),
        (3, "等待决策"),
    )

    defect_status = models.SmallIntegerField(verbose_name="缺陷状态", choices=status, default=1)
    defect_ndt_record = models.ForeignKey(verbose_name="缺陷检出的无损检测记录", to="NDTDataInfo", to_field='id', blank=True,
                                          null=True, on_delete=models.CASCADE)
    defect_fix_record = models.ForeignKey(verbose_name="缺陷修复记录", to="REPDataInfo", to_field='id', blank=True,
                                          null=True, on_delete=models.CASCADE)

    pre_defect = models.IntegerField(verbose_name="上一缺陷", default=0, blank=True)
    next_defect = models.IntegerField(verbose_name="下一缺陷", default=0, blank=True)

    def __str__(self):
        return str(self.id) + "-" + self.components[self.component][1] + " 上的 " + self.defect_types[self.defect_type][1]


class TemplateInfo(models.Model):
    template_title = models.CharField(verbose_name="模板标题", max_length=255)
    template_types = (
        (0, "无损检测模板"),
        (1, "修复数据模板"),
        (2, "仿真数据模板")
    )
    template_type = models.SmallIntegerField(verbose_name="数据模板类型", choices=template_types, default=0)
    template_description = models.CharField(verbose_name="模板描述", max_length=255, blank=True, null=True)
    template_statuses = (
        (0, "待审"),
        (1, "有效"),
        (2, "作废")
    )
    template_status = models.SmallIntegerField(verbose_name="模板状态", choices=template_statuses)
    template_creator = models.ForeignKey(verbose_name="创建者", blank=True, null=True, to="UserInfo", to_field='id',
                                         on_delete=models.SET_NULL, related_name="template_creator")
    template_approver = models.ForeignKey(verbose_name="审批者", blank=True, null=True, to="UserInfo", to_field='id',
                                          on_delete=models.SET_NULL, related_name="template_approver")
    template_item = models.JSONField(verbose_name="模板条目", blank=True, null=True)

    def __str__(self):
        return self.template_title


class MaintainRecInfo(models.Model):
    record_name = models.CharField(verbose_name="维护名称", max_length=255, unique=True)
    record_types = (
        (0, "大修"),
        (1, "定检"),
        (2, "大过载检修"),
    )
    record_type = models.SmallIntegerField(verbose_name="维护类型", choices=record_types, default=0)
    jet_serial = models.ForeignKey(verbose_name="战机序列号", to="JetInfo", to_field='jet_serial', blank=True,
                                   null=True, on_delete=models.SET_NULL)
    flight_time = models.FloatField(verbose_name="飞行战机时间", default=0.0)
    start_date = models.DateField(verbose_name="维护开始日期")

    def __str__(self):
        return str(self.id) + '-' + self.record_name


class NDTDataInfo(models.Model):
    maintain_rec = models.ForeignKey(verbose_name="维护记录", to="MaintainRecInfo", to_field='id', blank=True,
                                     null=True, on_delete=models.SET_NULL)
    data_creator = models.ForeignKey(verbose_name="数据创建者", to="UserInfo", to_field='id', blank=True, null=True,
                                     on_delete=models.SET_NULL, related_name="ndt_data_creator")

    ndt_methods = (
        (0, "目视检测"),
        (1, "超声C扫+A扫"),
        (2, "主动热成像"),
        (3, "X-CT"),
        (4, "激光剪切散斑"),
        (5, "形貌重建"),
        (6, "其他方法")
    )
    ndt_method = models.SmallIntegerField(verbose_name="无损检测方法", choices=ndt_methods)
    components = [
        (0, "前轮"),
        (1, "挡泥板"),
        (2, "后座"),
        (3, "车把"),
        (4, "刹车")
    ]
    component = models.SmallIntegerField(verbose_name="部件", choices=components)
    parts = [
        (0, "左上壁板"),    # 前轮/后座
        (1, "左下壁板"),
        (2, "右上壁板"),
        (3, "右下壁板"),
        (4, "左左壁板"),    # 挡泥板
        (5, "左右壁板"),
        (6, "右左壁板"),
        (7, "右右壁板"),
        (8, "左左蒙皮"),    # 车把
        (9, "左右蒙皮"),
        (10, "右左蒙皮"),
        (11, "右右蒙皮"),
        (12, "左上盖板"),    # 前轮/后座
        (13, "左下盖板"),
        (14, "右上盖板"),
        (15, "右下盖板"),
    ]
    part = models.SmallIntegerField(verbose_name="零件", choices=parts)
    defect_origins = [
        (0, "原始损伤"),
        (1, "新增损伤"),
        (2, "延续损伤"),
        (3, "扩展损伤")
    ]
    defect_origin = models.SmallIntegerField(verbose_name="损伤起始", choices=defect_origins, blank=True)

    # 1. 原始/新损伤：填写详细位置
    # 2. 延续/扩展：关联已有缺陷，再填写损伤参数

    # 0-原始；1-新增；缺陷填写
    location_types = [
        (0, "口框区域"),  # 前轮/后座
        (1, "连接区域"),
        (2, "蜂窝区域"),
        (3, "长桁端头"),
        (4, "边缘区域"),
        (5, "其他区域")
    ]
    location_type = models.SmallIntegerField(verbose_name="区域类型", choices=location_types)
    # 前轮：1墙轴线, 2墙轴线, 2墙轴线, 前缘, 后缘
    # 挡泥板：1梁轴线, 2梁轴线, 前缘, 后缘
    # 后座：后墙, 后缘, 后缘
    location_z_refs = [
        (0, "1墙轴线"),
        (1, "2墙轴线"),
        (2, "3墙轴线"),
        (3, "前缘"),
        (4, "后缘"),
        (5, "1梁轴线"),
        (6, "2梁轴线"),
        (7, "梁轴线"),
        (8, "后墙")
    ]
    location_z_ref = models.SmallIntegerField(verbose_name="展向基准", choices=location_z_refs)
    location_z_direc = models.BooleanField(verbose_name="相对位置", choices=[(0, "上"), (1, "下")], default=0)
    location_z_dist = models.IntegerField(verbose_name="距离(mm)")
    # 建立不同主结构与次结构的对应关系
    # '后段4肋轴线', '9前肋轴线', '后端17肋轴线', '后段9肋轴线', '后段10肋轴线', '后段12肋轴线', '弦向内侧', '9肋轴线', '10肋轴线',
    # '4肋轴线', '12肋轴线', '2前肋轴线', '1肋轴线', '3肋轴线', '15肋轴线', '后段3肋轴线', '后端13肋轴线', '后段5肋轴线', '7肋轴线'
    # '后段6肋轴线', '后段17肋轴线', '4前肋轴线', '左侧边缘', '6肋轴线', '后段14肋轴线', '后段7肋轴线', '后段1肋轴线', '8肋轴线',
    # '11肋轴线', '后段15肋轴线', '5肋轴线', '后段11肋轴线', '10前肋轴线', '14肋轴线', '后段8肋轴线', '右侧边缘', '17肋轴线',
    # '后段16肋轴线', '13肋轴线', '5前肋轴线', '6前肋轴线', '后段13肋轴线', '2肋轴线'
    location_x_refs = [
        (0, "后段1肋轴线"), (1, "后段2肋轴线"), (2, "后段3肋轴线"), (3, "后段4肋轴线"), (4, "后段5肋轴线"), (5, "后段6肋轴线"),
        (6, "后段7肋轴线"), (7, "后段8肋轴线"), (8, "后段9肋轴线"), (9, "后段10肋轴线"), (10, "后段11肋轴线"), (11, "后段12肋轴线"),
        (12, "后段13肋轴线"), (13, "后段14肋轴线"), (14, "后段15肋轴线"), (15, "后段16肋轴线"), (16, "后段17肋轴线"),
        (17, "1肋轴线"), (18, "2肋轴线"), (19, "3肋轴线"), (20, "4肋轴线"), (21, "5肋轴线"), (22, "6肋轴线"), (23, "7肋轴线"),
        (24, "8肋轴线"), (25, "9肋轴线"), (26, "10肋轴线"), (27, "11肋轴线"), (28, "12肋轴线"), (29, "13肋轴线"), (30, "14肋轴线"),
        (31, "15肋轴线"), (32, "16肋轴线"), (33, "17肋轴线"), (34, "18肋轴线"), (35, "19肋轴线"), (36, "左侧边缘"), (37, "右侧边缘"),
        (38, "1前肋轴线"), (39, "2前肋轴线"), (40, "3前肋轴线"), (41, "4前肋轴线"), (42, "5前肋轴线"), (43, "6前肋轴线"), (44, "7前肋轴线"),
        (45, "8前肋轴线"), (46, "9前肋轴线"), (47, "10前肋轴线"), (48, "11前肋轴线"), (49, "弦向内侧"), (50, "第1隔板轴线"), (51, "第2隔板轴线"), (52, "第3隔板轴线")
    ]
    location_x_ref = models.SmallIntegerField(verbose_name="展向基准", choices=location_z_refs)
    location_x_direc = models.BooleanField(verbose_name="相对位置", choices=[(0, "左"), (1, "右")], default=0)
    location_x_dist = models.IntegerField(verbose_name="距离(mm)")
    location_thickness = models.CharField(verbose_name="厚度分布", max_length=32)

    # 2-扩展；3-延续 缺陷填写
    defect_item = models.ForeignKey(verbose_name="关联已有缺陷", to="DefectInfo", to_field='id',
                                  blank=True, null=True, on_delete=models.CASCADE)

    # 0-原始；1-新增；2-扩展；缺陷填写
    size_z = models.IntegerField(verbose_name="展向损伤尺度(mm)")  # 最近一次检测检出的最大损伤尺寸
    size_x = models.IntegerField(verbose_name="弦向损伤尺度(mm)")
    defect_types = (
        (0, "分层"),
        (1, "长桁脱粘"),
        (2, "低速冲击损伤（穿透/非穿透型冲击孔）"),
        (3, "高速冲击损伤（穿透/非穿透型冲击孔）"),
        (4, "蜂窝进水（蜂窝结构内部进水）"),
        (5, "表面割裂损伤或深划痕（面板表面若干层被割伤）"),
        (6, "腐蚀/老化（基体或纤维材料老化腐蚀失效）"),
        (7, "雷击损伤"),
        (8, "功能结构损伤（涂层老化脱落等导致的吸波功能减退等）"),
    )
    defect_type = models.SmallIntegerField(verbose_name="缺陷类型", choices=defect_types)

    attachment_file_path = models.FileField(upload_to=NDT_file_dir + '%Y/%m/%d/', blank=True)

    def __str__(self):
        return str(self.maintain_rec) + "无损检测记录" + str(self.id)


class REPDataInfo(models.Model):
    data_title = models.CharField(verbose_name='数据标题', max_length=255)
    data_description = models.TextField(verbose_name="数据描述", null=True, blank=True)
    defect = models.ForeignKey(verbose_name="针对缺陷", to="DefectInfo", to_field="id", blank=True, null=True,
                                  on_delete=models.SET_NULL, limit_choices_to={'defect_status': 1})
    data_creator = models.ForeignKey(verbose_name="数据创建者", to="UserInfo", to_field='id', blank=True, null=True,
                                     on_delete=models.SET_NULL, related_name="rep_data_creator")
    data_approver = models.ForeignKey(verbose_name="数据审批者", to="UserInfo", to_field='id', blank=True, null=True,
                                      on_delete=models.SET_NULL, related_name="rep_data_approver")
    rep_methods = (
        (0, "复合材料结构挖补修复"),
        (1, "复合材料结构贴补修复"),
        (2, "螺栓补板修复"),
        (3, "零备件更换")
    )
    rep_method = models.SmallIntegerField(verbose_name="无损检测方法", choices=rep_methods)
    data_statuses = (
        (0, "待审"),
        (1, "有效"),
        (2, "作废")
    )
    data_status = models.SmallIntegerField(verbose_name="数据状态", choices=data_statuses)
    img_path = models.CharField(verbose_name='图片文件名', max_length=255)
    data_template = models.ForeignKey(verbose_name="数据模板", to="TemplateInfo", to_field='id', blank=True,
                                      null=True, on_delete=models.SET_NULL, limit_choices_to={'template_type': 1, 'template_status': 1})
    data_item_all = models.JSONField(verbose_name="数据内容")


class DMAPDataInfo(models.Model):
    data_title = models.CharField(verbose_name='数据标题', max_length=255)
    data_description = models.TextField(verbose_name="数据描述", null=True, blank=True)
    structure_types = (
        (0, "层合板"),
        (1, "蜂窝结构"),
        (2, "加筋结构"),
        (3, "挖补/贴补/螺栓修复结构")
    )
    structure_type = models.SmallIntegerField(verbose_name="损伤结构", choices=structure_types)
    ndt_methods = (
        (0, "目视检测"),
        (1, "超声C扫+A扫"),
        (2, "主动热成像"),
        (3, "X-CT"),
        (4, "激光剪切散斑"),
        (5, "形貌重建"),
        (6, "其他方法")
    )
    ndt_method = models.SmallIntegerField(verbose_name="无损检测方法", choices=ndt_methods)
    damage_types = [
        (0, '蒙皮分层（可能由于制造原因、载荷集中、低速冲击、老化疲劳等导致的不明原因分层）'),
        (1, '长桁分层（可能由于制造原因、载荷集中、低速冲击、老化疲劳等导致的长桁分层）'),
        (2, '蒙皮-芯材/长桁/筋条胶接面脱粘（蜂窝或加筋结构蒙皮-芯材/筋连接处脱粘）'),
        (3, '蜂窝进水（蜂窝结构内部进水）'),
        (4, '表面割裂损伤或深划痕（面板表面若干层被割伤）'),
        (5, '腐蚀/老化（蜂窝芯，或基体、纤维材料老化腐蚀失效）'),
        (6, '雷击损伤'),
        (7, '功能损伤（涂层老化脱落等导致的吸波功能减退等）'),
        (8, '制造缺陷（夹杂、纤维堆叠、褶皱等）'),
        (9, '过载断裂（超载、碰撞等局部应力过大导致的断裂）'),
        (10, '低速冲击损伤（表面凹痕、内部分层及裂纹）'),
        (11, '高速冲击损伤（穿透/非穿透型冲击孔）'),
        (12, '其他损伤'),
    ]
    damage_type = models.SmallIntegerField(verbose_name="损伤类型", choices=damage_types)
    img = models.ImageField(verbose_name="损伤图片", upload_to='DMAP', height_field=None, width_field=None, max_length=100)


class SIMUDataInfo(models.Model):
    data_title = models.CharField(verbose_name='数据标题', max_length=255)
    data_description = models.TextField(verbose_name="数据描述", null=True, blank=True)
    data_creator = models.ForeignKey(verbose_name="数据创建者", to="UserInfo", to_field='id', blank=True, null=True,
                                     on_delete=models.SET_NULL, related_name="simu_data_creator")
    apps = (
        (0, "Abaqus"),
        (1, "Adams"),
        (2, "Fluent"),
        (3, "COMSOL"),
        (4, "其他"),
    )
    simulation_software = models.SmallIntegerField(verbose_name="仿真软件", choices=apps)
    structure_objects = (
        (0, "层合板"),
        (1, "蜂窝结构"),
        (2, "加筋结构"),
        (3, "吸波结构")
    )
    structure_object = models.SmallIntegerField(verbose_name="模拟对象", choices=structure_objects)
    structure_types = [
        (0, "完好结构"),
        (1, "贴补/挖补修复结构"),
        (2, "螺栓修复结构"),
        (3, "预置缺陷结构"),
    ]
    structure_type = models.SmallIntegerField(verbose_name="结构类型", choices=structure_types)
    load_types = (
        (0, "单拉（典型拉伸载荷）"),
        (1, "单压（典型压缩载荷）"),
        (2, "弯曲（三点弯、四点弯、面内静水压强等）"),
        (3, "剪切（面内剪切）"),
        (4, "低速冲击（落锤冲击损伤仿真）"),
        (5, "高速冲击（高速冲击损伤仿真）"),
        (6, "固化工艺仿真（固化热动力学仿真）"),
        (7, "加工工艺仿真（钻孔、打磨、钉铆等工艺仿真）"),
        (8, "混合型载荷（拉压弯扭剪等耦合，CAI模拟等）"),
        (9, "功能结构仿真（电磁特性仿真等）"),
        (10, "热仿真"),
        (11, "其他")
    )
    load_type = models.SmallIntegerField(verbose_name="载荷类型", choices=load_types)
    demo_img = models.ImageField(verbose_name="示例图片", upload_to='SIMUMAP/IMGS', height_field=None, width_field=None, max_length=100)
    demo_video = models.FileField(verbose_name="结果视频", upload_to='SIMUMAP/VIDEO', max_length=100, blank=True, null=True)
    origin_file = models.FileField(verbose_name="仿真文件", upload_to='SIMUMAP/ATTACH', max_length=100, blank=True, null=True)


class UserInfo(models.Model):
    ecard_id = models.CharField(verbose_name="工号", max_length=20, null=True, blank=True)
    username = models.CharField(verbose_name="用户名", max_length=255)
    mail = models.CharField(verbose_name="邮箱", max_length=255)
    passwd = models.CharField(verbose_name="密码", max_length=64)
    user_authorities = (
        (0, "基本游客权限"),
        (1, "检测数据创建"),
        (2, "修复数据创建"),
        (3, "检测数据审核"),
        (4, "修理数据审核"),
        (5, "检测数据模板创建"),
        (6, "修复数据模板创建"),
        (7, "检测数据模板审核"),
        (8, "修复数据模板审核"),
        (9, "检测数据访问"),
        (10, "修复数据访问"),
        (11, "外联模块审核"),
        (12, "外联模块访问"),
        (13, "权限申请的审批"),
    )
    rights = models.CharField(verbose_name="用户权限", max_length=255, default="0,")
    join_date = models.DateTimeField(verbose_name="注册时间")
    task_numbers = models.IntegerField(verbose_name="待处理任务数量", default=0)
    applying_tasks = models.CharField(verbose_name="正在申请的事项", max_length=255, default='')
    approving_tasks = models.CharField(verbose_name="正在处理的事项", max_length=255, default='')
    finished_tasks = models.CharField(verbose_name="处理完毕的事项", max_length=255, default='')

    def __str__(self):
        return self.username


class Logininfo(models.Model):
    ''' 记录登录信息的表格 '''
    user = models.ForeignKey(verbose_name="用户名", to="UserInfo", to_field='id', blank=True, null=True,
                             on_delete=models.SET_NULL)
    date_time = models.DateTimeField(verbose_name="登录日期")
    login_ip = models.CharField(verbose_name="登录ip", max_length=255, blank=True, null=True)


class Taskinfo(models.Model):
    task_types = (
        (0, "数据上传"),
        (1, "数据上传审核"),
        (2, "用户权限申请"),
        (3, "用户权限申请审核"),
        (4, "数据模板创建申请"),
        (5, "数据模板审核"),
        (6, "数据使用申请"),
        (7, "数据使用审核"),
    )
    task_statuses = (
        (0, "处理中"),
        (1, "审批通过"),
        (2, "申请被驳回"),
        (3, "用户撤销申请"),
        (4, "待提交"),
        (5, "超时未处理驳回"),
    )
    task_type = models.SmallIntegerField(verbose_name="任务类别", choices=task_types)
    task_status = models.SmallIntegerField(verbose_name="任务状态", choices=task_statuses)
    task_applier = models.ForeignKey(verbose_name="创建者", blank=True, null=True, to="UserInfo", to_field='id',
                                     on_delete=models.SET_NULL, related_name="task_creator")
    task_approver = models.ForeignKey(verbose_name="审批者", blank=True, null=True, to="UserInfo", to_field='id',
                                      on_delete=models.SET_NULL, related_name="task_approver")
    task_title = models.CharField(verbose_name="任务标题", max_length=255)
    task_description = models.CharField(verbose_name="任务描述", max_length=255, blank=True, null=True)
    task_create_time = models.DateTimeField(verbose_name="任务创建时间")
    task_decision_time = models.DateTimeField(verbose_name="任务完成时间", blank=True, null=True)
    task_content = models.JSONField(verbose_name="任务信息")

    def __str__(self):
        return self.task_title