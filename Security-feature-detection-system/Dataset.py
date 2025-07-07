class Dataset:
    # 数据结构存储
    categories = {
        '外勤人员': ['戴威', '陈嘉屹'],
        '验断电监管人员': ['梁城斌'],
        '验断电操作人员': ['刘曦远']
    }
    modelsfeature = {
        # 外勤人员总类别 '外勤人员': ['head', 'helmet', 'reflective_clothes', 'other_clothes', 'watch'],
        # 外勤人员正确包含 '外勤人员': ['helmet', 'reflective_clothes','watch'],
        '外勤人员': ['head', 'other_clothes', 'watch'], # 用于我测试
        '验断电监管人员': ['badge', 'person'],
        # '验电操作人员': ['badge', 'person', 'glove', 'powerchecker', 'operatingbar']
        '验电操作人员': ['person', 'glove', 'powerchecker']
    }

    # 函数来检索成员所属的类别
    def find_category(member, categories):
        for category, members in categories.items():
            if member in members:
                return category
        return "成员不存在"
    # # 测试用例
    # print(find_category('戴威', categories))  # 应当输出: 外勤人员
    # print(find_category('梁城斌', categories))  # 应当输出: 验断电监管人员
    # print(find_category('刘曦远', categories))  # 应当输出: 验断电操作人员
    # print(find_category('刘星雨', categories))  # 应当输出: 成员不存在

    def contains_all_items(input_string, items):
        """
        判断input_string是否包含items列表中的所有项。

        :param input_string: 主字符串
        :param items: 需要检查的子字符串列表
        :return: 如果所有子字符串都在主字符串中，则返回True，否则返回False
        """
        return all(item in input_string for item in items)
    # # 测试用例
    # # 子字符串列表
    # items_to_check = ['head', 'helmet', 'reflective_clothes', 'other_clothes', 'watch']
    # # 测试字符串
    # test_string = "This text includes head, helmet, reflective_clothes, other_clothes, and watch."
    # # 调用函数并打印结果
    # result = contains_all_items(test_string, items_to_check)
    # print("Does the test string contain all items? ", result)


