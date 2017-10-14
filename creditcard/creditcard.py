#!/usr/bin/python3
import datetime
import re
import threading
import time

import calendar

ACCOUNT_DATE = calendar.monthrange(datetime.datetime.today().year, datetime.datetime.today().month)[1]
# ACCOUNT_DATE = 30
REPAYMENT_DATE = 10


def is_money(money_str):
    value = re.compile(r'^[0-9]+\.[0-9][0-9]$')
    return value.match(money_str)


class CreditCard:
    def __init__(self, name, card_num, quota=1500.00, over_quota=0.00, avail_credit=0.00):

        self.name = name
        self.card_num = card_num

        self.quota = quota
        self.over_quota = over_quota  # 超限额部分
        self.avail_credit = avail_credit  # 应还款

        self.poundage_rate = 0.05
        self.interest_rate = 0.05

    def drawing(self):

        print("-" * 30)
        money = input("输入q/Q离开，或输入要提款的金额：")

        if money == "q" or money == "Q":
            print("欢迎下次提款")
            return

        if not is_money(money):
            print("违法字符，请重新输入")
            self.drawing()
            return

        money = float(money)
        poundage = money * self.poundage_rate
        money_poundage = money + poundage

        if (self.quota + self.over_quota - self.avail_credit) < money_poundage:
            print("提取金额超过了可用金额")
            self.drawing()
            return

        if self.over_quota >= money_poundage:
            self.over_quota -= money_poundage
        elif self.over_quota != 0:
            self.avail_credit += (money_poundage - self.over_quota)
            self.over_quota = 0
        else:
            self.avail_credit += (money_poundage - self.over_quota)

        account = {"datetime": datetime.datetime.now(), "card_num": self.card_num,
                   "money": -money, "remark": "提款", "name": self.name}
        self.__w_db_account(account)
        account = {"datetime": datetime.datetime.now(), "card_num": self.card_num,
                   "money": -poundage, "remark": "手续费", "name": self.name}
        self.__w_db_account(account)

        print("成功提取 %.2f 元，手续费为 %.2f 元，可用金额为 %.2f 元"
              % (money, poundage, self.quota + self.over_quota - self.avail_credit))

    def repayment(self):

        print("-" * 30)
        money = input("输入q/Q离开，或输入要还款的金额：")

        if money == "q" or money == "Q":
            print("欢迎下次还款")
            return

        if not is_money(money):
            print("违法字符，请重新输入")
            self.drawing()
            return

        money = float(money)

        if self.avail_credit < money:
            self.over_quota += (money - self.avail_credit)
            self.avail_credit = 0
        else:
            self.avail_credit -= money

        account = {"datetime": datetime.datetime.now(), "card_num": self.card_num,
                   "money": money, "remark": "还款", "name": self.name}
        self.__w_db_account(account)

        print("成功还取 %.2f 元，可用金额为 %.2f 元" % (money, self.quota + self.over_quota - self.avail_credit))

    def account_date(self):

        file_name = "%s_%s" % (self.card_num, datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + ".txt")
        dir_name = "./account_lists/"
        account_info = open(dir_name + file_name, mode='a')
        account_file = open("account_list.info")

        account_info.write("本月消费记录如下：\n")
        while True:
            line = account_file.readline()
            if not len(line):
                break
            if line.split()[2] == self.card_num:
                if int(line.split()[0].split(sep="-")[1]) == datetime.datetime.today().month:
                    account_info.write(line)

        account_file.close()
        account_info.close()

    def repayment_date(self):

        interest = self.avail_credit * self.interest_rate
        self.avail_credit += interest
        account = {"datetime": datetime.datetime.now(), "card_num": self.card_num,
                   "money": -interest, "remark": "利息", "name": self.name}
        if interest != 0:
            self.__w_db_account(account)
        print("已计算 %s 的逾期利息，利息为 %.2f 元" % (self.card_num, interest))

    def card_info(self):
        return self.name, self.card_num, self.quota, self.over_quota, self.avail_credit

    @staticmethod
    def __w_db_account(account):
        # 写账单信息
        account_file = open("account_list.info", mode='a')
        account_str = account["datetime"].strftime('%Y-%m-%d %H:%M:%S') + "\t%s\t%.2f\t%s\t%s\n" % (
            account["card_num"], account["money"], account["remark"], account["name"])
        account_file.write(account_str)
        account_file.close()


class Blank:
    def __init__(self, cards_file="cards.info"):
        self.cards_file_name = cards_file

        self.cards_num = 0
        self.cards_list = []
        self.__r_db_cards()

        self.account_tag = True
        self.repayment_tag = True

        self.thread = threading.Thread(target=self.__server)
        self.thread.setDaemon(True)

    def __r_db_cards(self):

        # 读取卡信息
        self.cards_file = open(self.cards_file_name)
        while True:
            line = self.cards_file.readline()
            if not len(line):
                break
            self.cards_list.append([self.cards_num, CreditCard(line.split()[0],
                                                               line.split()[1],
                                                               float(line.split()[2]),
                                                               float(line.split()[3]),
                                                               float(line.split()[4]))])
            self.cards_num += 1
        self.cards_file.close()

    def w_db_cards(self):


        self.cards_file = open(self.cards_file_name, mode='w')
        for card in self.cards_list:
            self.cards_file.write("%s\t%s\t%.2f\t%.2f\t%.2f\n" % card[-1].card_info())
        self.cards_file.close()

    def create_card(self, name):
        card_num = "%08d" % self.cards_num
        self.cards_num += 1
        self.cards_list.append([self.cards_num, CreditCard(name, card_num=card_num)])
        print("已经为用户 %s 创办一张 %s 的信用卡，欢迎您使用" % (name, card_num))

    def __server(self):

        while True:

            if self.repayment_tag:
                if datetime.datetime.now().day == REPAYMENT_DATE:
                    print("开始repayment")
                    for card in self.cards_list:
                        card[1].repayment_date()
                    print("结束repayment")
                    self.repayment_tag = False
                else:
                    self.repayment_tag = True

            if self.account_tag:
                if datetime.datetime.now().day == ACCOUNT_DATE:
                    print("开始account")
                    for card in self.cards_list:
                        card[1].account_date()
                    print("结束account")
                    self.account_tag = False
                else:
                    self.account_tag = True

            time.sleep(2)

    def drawing(self):

        tag = True
        while tag:
            card_num = input("请输入要操作的卡号：")
            for card in self.cards_list:
                if card[0] == int(card_num):
                    card[1].drawing()
                    tag = False
            if tag:
                print("没有找到相应的卡号%s" % card_num)

    def repayment(self):

        tag = True
        while tag:
            card_num = input("请输入要操作的卡号：")
            for card in self.cards_list:
                if card[0] == int(card_num):
                    card[1].repayment()
                    tag = False
            if tag:
                print("没有找到相应的卡号%s" % card_num)


def jm_help():
    print("*" * 35)
    print("create:\t\t创建新的信用卡\n"
          "drawing:\t提款\n"
          "repayment:\t还款\n"
          "help:\t\t显示菜单提示\n"
          "quit:\t\t离开软件")
    print("*" * 35)


def start(a):

    a.thread.start()
    time.sleep(1)

    while True:
        print("=" * 50)
        jm_help()
        key = input("请输入要操作符：")
        if key == "quit":
            a.w_db_cards()
            return
        elif key == "create":
            a.create_card(input("请输入用户名："))
        elif key == "drawing":
            a.drawing()
        elif key == "repayment":
            a.repayment()
        elif key == "help":
            jm_help()
        else:
            print("输入错误，请重新输入。")


if __name__ == "__main__":
    a = Blank()
    start(a)