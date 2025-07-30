from typing import List, Optional, Union
NUMS = "零壹贰叁肆伍陆柒捌玖"


class CNAmountOutOfRangeException(Exception):
    """ 金额超出范围的异常。 """
    def __init__(self, error_info=f"金额超出范围，最大值为：999999999999.99。"):
        """
        :param error_info: 错误提示信息
        """
        super().__init__(self)
        self.error_info = error_info

    def __str__(self):
        return self.error_info


class CNAmount:
    """ 金额转中国大写。 """
    def __init__(self, extend_units: Optional[List[str]] = None, use_default_extend_units=True):
        """
        :param extend_units: 错误提示信息
        """
        self.units = []
        self.main_units = ["元", "万", "亿"]
        self.common_units = ["拾", "佰", "仟"]
        self.units_size = 0
        if use_default_extend_units:
            extend_units = ["兆", "京", "垓", "姊", "穰", "沟", "涧", "正", "载"]
        self.generate_units(extend_units)

    def generate_units(self, extend_units: Optional[List[str]]):
        """
        写入self.units中 需要的单位
        :param extend_units: 扩展的单位，比如 ["兆", "京", "垓", "姊", "穰", "沟", "涧", "正", "载"], 默认为None即可
        :return: None
        """
        if extend_units:
            self.main_units.extend(extend_units)
        for _ in self.main_units:
            self.units.append("")
            for common_unit in self.common_units:
                self.units.append(common_unit)
        self.units_size = len(self.units)

    @staticmethod
    def decimal_part(num: Union[int, float]) -> str:
        """
        小数部分转金融中文大写
        :param num:
        :return:
        """
        decimal_str_two = f"{num:.2f}".split(".")[1]
        if decimal_str_two == "00":
            return "整"

        def one_decimal(char_s, unit="角", zero="零"):
            result = []
            if char_s != "0":
                result.append(NUMS[int(char_s)] + unit)
            else:
                result.append(zero)
            return "".join(result)
        return "".join([one_decimal(decimal_str_two[0]), one_decimal(decimal_str_two[1], unit="分", zero="")])

    def integer_part(self, num: Union[int, float]):
        """
        整数部分转金融中文大写
        :param num:
        :return:
        """
        if int(num) < 1:
            return "零元"
        num_str = f"{int(num):0{self.units_size}}"[::-1]
        unit_list, zero_count = [], 0
        for out_index, unit in enumerate(self.main_units):
            for inner_index in range(4):
                unit_index = out_index * 4 + inner_index
                if num_str[unit_index] == "0":
                    zero_count += 1
                    unit_list.append("")
                else:
                    if zero_count > 0:
                        unit_list[-1] = NUMS[0]
                    zero_count = 0
                    unit_list.append(NUMS[int(num_str[unit_index])]+self.units[unit_index])
            for i in range(4):
                if unit_list[i - 4] and unit_list[i - 4] != "零":
                    unit_list[i - 4] += unit
                    break
        cn_amount = "".join(unit_list[::-1])
        cn_amount = cn_amount[:-1] if cn_amount.endswith("零") else cn_amount
        return cn_amount if cn_amount.endswith("元") else f"{cn_amount}元"

    def amount_to_chinese(self, num: Union[int, float]):
        if num >= 10 ** self.units_size:
            raise CNAmountOutOfRangeException(f"金额超出范围，最大值为：{10 ** self.units_size - 0.01}。")
        integer_part_big = self.integer_part(num)
        decimal_part_big = self.decimal_part(num)
        return decimal_part_big if integer_part_big == "零元" and decimal_part_big != "整" else \
            integer_part_big + decimal_part_big
