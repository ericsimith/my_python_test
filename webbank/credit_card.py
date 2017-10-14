

class CreditCard:
    def __init__(self, card_num, card_class="A", ):
        self.card_num = card_num

        # tod 这个卡的类型要放到文件中去
        cards_class = {"A": (1500.00, 0.05), "B": (1600.00, 0.05)}
        self.quota, self.rate = cards_class[card_class]

    def draw_cash(self):
        pass

    def pay(self):
        pass

    def repay(self):
        pass

    def check_balance(self):
        pass
