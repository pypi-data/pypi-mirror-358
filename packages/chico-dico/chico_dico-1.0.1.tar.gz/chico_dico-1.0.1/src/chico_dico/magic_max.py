# -*- coding: utf-8 -*-

def factorial(n):
    """计算n的阶乘"""
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)


class MagicMax:
    """Chico 和 Dico 的魔术 - 推广版"""

    def __init__(self, n, k):
        assert 3 <= n < factorial(k) + k
        assert 3 <= k
        self.n = n  # 整个牌组有多少牌
        self.k = k  # 从牌组中抽几张牌

    @staticmethod
    def reverse(cards):
        """翻转牌组，分出前 k - 1 张牌"""
        reversed_cards = cards[::-1]
        return reversed_cards[:-1], reversed_cards[-1]

    def encoder(self, cards):
        """将第 k 张牌的牌面信息编码到前 k-1 张的顺序中"""
        res = []
        cards = sorted(cards)
        s = sum(cards) % factorial(self.k)

        q = s
        for i in range(self.k, 0, -1):
            q, r = divmod(q, i)
            res.append(cards.pop(r))
        return res

    def decoder(self, visible_cards):
        """将第 k 张牌的牌面信息从前 k-1 张牌的排列信息中解码出来"""
        # 逆向求解编码过程
        q, r = 0, 0
        for i in range(1, self.k):
            q = i * q + r

            if i < self.k - 1:  # 前 k-2 步需要计算余数
                r = sorted(visible_cards[:i+1]).index(visible_cards[i])

        # 判断模 k! 的偏离量 t
        sum_visible_cards = sum(visible_cards)
        factorial_k = factorial(self.k)

        epoch = sum([self.n - i for i in range(self.k)]) // factorial_k
        for t in range(epoch+1):
            v_min = self.k * q + t * factorial_k - sum_visible_cards
            v_max = self.k * q + t * factorial_k - sum_visible_cards
            if v_min >= 1 and v_max <= self.n:
                break

        for r in range(self.k):
            # 线索1：牌组总和为 s + k! * t
            s = self.k * q + r
            v = s + factorial_k * t - sum_visible_cards
            # 线索2：第 k 张牌的值 v 放入牌组中获得正确的余数 r
            if 1 <= v <= self.n and v not in visible_cards:
                real_r = sorted(visible_cards + [v]).index(v)
                if real_r == r:
                    return v
