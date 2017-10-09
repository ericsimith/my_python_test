USER_LOCK_TIMES = 3


class CheckLogin(object):
    def __init__(self, user_file="users.info"):

        self.__user_file = user_file

        self.__users_info = []
        self.__tmp_name = ""
        self.__tmp_password = ""
        self.__user = {}
        self.__read_user_info()
        self.tag = 0
        self.tag_list = ["登录成功", "用户不存在，请先注册！", "用户已锁定，请联系管理员！",
                         "密码已达到 %d 次，用户被锁定" % USER_LOCK_TIMES, "错误密码,已错误输入 %d 次"]

    def __read_user_info(self):

        users_file = open(self.__user_file)

        while True:
            text = users_file.readline()

            if not text:
                break

            user_info_list = text.split()
            user = {"name": user_info_list[0], "password": user_info_list[1],
                    "error": int(user_info_list[2]), "lock": (user_info_list[3] == "True")}
            self.__users_info.append(user)

        users_file.close()

    def __write_user_info(self):

        users_file = open(self.__user_file, mode="w")

        for user in self.__users_info:
            users_file.write("%s\t%s\t%d\t%r\n"
                             % (user["name"], user["password"], user["error"], user["lock"]))

        users_file.close()

    def __check_user_name(self):

        for user in self.__users_info:
            if user["name"] == self.__tmp_name:
                self.__user = user
                # self.tag_list[0] = user
                return True
        return False

    def __check_user_lock(self):

        if self.__user["lock"]:
            return True
        return False

    def __check_user_error(self):

        if self.__user["error"] == USER_LOCK_TIMES:
            self.__user["lock"] = True
            return True
        self.tag_list[4] = "错误密码,已错误输入 %d 次" % self.__user["error"]
        return False

    def __check_user_password(self):

        if self.__user["password"] == self.__tmp_password:
            self.__user["error"] = 0
            return True
        self.__user["error"] += 1
        return False

    def __check_info(self):

        if not self.__check_user_name():
            return 1
        if self.__check_user_lock():
            return 2
        if self.__check_user_password():
            return 0
        if self.__check_user_error():
            return 3
        else:
            return 4

    def check_login(self, name, password):
        self.__tmp_name = name
        self.__tmp_password = password

        self.tag = self.__check_info()
        self.__write_user_info()

        return self.tag, self.tag_list[self.tag]


def is_login():
    while True:
        do_login = input("你要登录吗？y/n[y] :")
        if do_login == "y" or do_login == "Y" or len(do_login) == 0:
            break
        elif do_login == "n" or do_login == "N":
            return False
        else:
            print("输入错误请重新输入！")
    return True


def login():
    cl = CheckLogin("users.info")

    while True:
        print("=" * 50)

        if not is_login():
            print("谢谢，再见")
            exit()

        print("-" * 50)
        tmp_name = input("请输入用户名：")
        tmp_password = input("请输入密码：")
        print("-" * 50)

        tag, tag_str = cl.check_login(tmp_name, tmp_password)
        print(tag_str)

        if tag != 0:
            continue

        print("=" * 50)
        return tmp_name
