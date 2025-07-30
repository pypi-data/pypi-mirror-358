import random

from .magic import Magic
from .poker import PokeMapper


class CardGame:
    """提供交互函数"""

    def __init__(self, nums: list = []):
        if nums:
            # nums 非空时检查
            if len(nums) != 5:
                raise ValueError("nums must contain exactly 5 cards")
            if len(set(nums)) != 5:
                raise ValueError("nums must be unique")

            for num in nums:
                if not (1 <= num <= 52):
                    raise ValueError(f'num must be between [1, 52]. Invalid num: {num}')

        self.nums = nums
        self.magic = Magic()
        self.poker = PokeMapper()

    def im_feeling_lucky(self):
        """随机取5张牌"""
        self.nums = random.sample(range(1, 53), 5)

    def display_cards(self, nums):
        """展示牌面"""
        res = []
        for i in nums:
            res.append(self.poker.num_to_card(i))
        return ' '.join(res)

    def chico(self):
        """Chico按特定方法排序"""
        nums = self.magic.encoder(self.nums)
        first_four, fifth_card = self.magic.reverse(nums)
        return first_four, fifth_card

    def dico(self, first_four):
        """dico从排序中解码第五张牌"""
        fifth_card = self.magic.decoder(first_four)
        return fifth_card
