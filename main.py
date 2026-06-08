# 这是一个示例 Python 脚本。

# 按 Ctrl+F5 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import random

num = random.randint(1, 100)
print(num)

name = '123456789'
print(len(name))

# pws=input('请输入密码')
# print(pws)

isShow = False
print(isShow)

myList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 1]
print(myList)

count = [i for i, x in enumerate(myList) if x == 1]
print(count)

myList.insert(0, 'e')
print(myList)

myList.append('0123')
print(myList)

myList.extend(['a', 'b', 'c'])
print(myList)

del myList[len(myList) - 1]
print(myList)

myList.pop(1)
print(myList)

while num < 50:
    print(num, '-----')
    break

list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 1]


def testFun():
    sumValue = 0
    for i in list:
        if i < 50:
            sumValue += i
    return sumValue


print(testFun(), '=---')

data_list = [{"value": 100, "num": 5}, {"value": 99, "num": 2}]

# 获取字典里 value 的值
for data in data_list:
    print(data['value'])
    print(data['num'])
