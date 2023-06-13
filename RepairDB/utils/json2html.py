import json


def json2html(json_item):
    return str_html


if __name__ == '__main__':
    str = '''
    {
    "title": "演示数据模板",
    "description": "这是一个用于演示的数据模板，包含了三个字段，含有文件、input、下拉框类型的数据",
    "num_key": 3,
    "content": {
        "1": {
            "name": "填空框",
            "type": 1,
            "default": "",
            "required": false
        },
        "2": {
            "name": "文件型填空框",
            "type": 2,
            "default": "",
            "required": false,
            "file_type": [".bmp", ".jpg"]
        },
        "3": {
            "name": "下拉选择框",
            "type": 3,
            "default": "",
            "required": true,
            "choices":{
                "0": "选项1",
                "2": "选项2",
                "3": "选项3"
            }
        }
    }
}'''
    json2html(str)
