import re


def bold(matched):
    return "\033[1;32m" + matched.group() + "\033[0m"


def contact_file(find_str, file_str):
    file = open(file_str, mode="r")

    while True:

        line = file.readline()

        if not len(line):
            break

        if re.search(find_str, line) is not None:
            print(re.sub(find_str, bold, line), end="")

    file.close()


def contact():
    file = "contact_list.txt"

    while True:
        find = input("请输入要查找的字符串：")
        if len(find):
            break

    contact_file(find, file)


contact()
