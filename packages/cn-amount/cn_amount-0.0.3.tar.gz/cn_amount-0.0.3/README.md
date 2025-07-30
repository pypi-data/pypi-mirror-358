# 金额转中文大写
`作者： 李聚升`

## 特性

- 人民币金额大写规范中规定了的最高单位为千亿。
- 本包默认支持亿以上单位："兆", "京", "垓", "姊", "穰", "沟", "涧", "正", "载"； 举例：10千亿=1兆。
- 亿以上单位支持自定义
- 超出范围 抛 CNAmountOutOfRangeException 异常

## 使用

安装
```sh
pip install cn-amount
```
使用示例
```python
from cn_amount import CNAmount

# 按《孙子算经》的规则 最高单位为“载”，一般长度的数字都可以正常转换
print(CNAmount().amount_to_chinese(999999999999999999999999999.99))

try:
    # 最高单位为亿，会抛出异常
    print(CNAmount(use_default_extend_units=False).amount_to_chinese(999999999999.99 + 0.01))
except CNAmountOutOfRangeException as e:
    print(e)

# 最高单位为兆
print(CNAmount(extend_units=["兆"], use_default_extend_units=False).amount_to_chinese(999999999999.99 + 0.01))
```
