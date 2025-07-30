# -*- coding: utf-8 -*-

def factorial(n):
    """计算n的阶乘"""
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)


class Magic:
    """Chico 和 Dico 的魔术"""

    @staticmethod
    def reverse(cards):
        """翻转牌组，分出前四张牌"""
        reversed_cards = cards[::-1]
        return reversed_cards[:-1], reversed_cards[-1]

    @staticmethod
    def encoder(cards):
        """将第五张牌的牌面信息编码到前四张的顺序中"""
        res = []
        cards = sorted(cards)
        s = sum(cards) % factorial(5)

        q = s
        for i in range(5, 0, -1):
            q, r = divmod(q, i)
            res.append(cards.pop(r))
        return res

    @staticmethod
    def decoder(first_four):
        """将第五张牌的牌面信息从前四张牌的排列信息中解码出来"""
        # 逆向求解编码过程
        q, r = 0, 0
        for i in range(1, 5):
            q = i * q + r

            if i < 4:  # 前3步需要计算余数
                r = sorted(first_four[:i+1]).index(first_four[i])

        # 判断模 5! 的偏离量 t
        sum_first_four = sum(first_four)
        for t in range(3):
            v_min = 5 * q + t * 120 - sum_first_four
            v_max = 5 * q + t * 120 - sum_first_four
            if v_min >= 1 and v_max <= 52:
                break

        for r in range(5):
            # 线索1：牌组总和为 s + 120 * t
            s = 5 * q + r
            v = s + 120 * t - sum_first_four
            # 线索2：第五张牌的值 v 放入牌组中获得正确的余数 r
            if 1 <= v <= 52 and v not in first_four:
                real_r = sorted(first_four + [v]).index(v)
                if real_r == r:
                    return v
