import random
from typing import Tuple


class PokeMapper:
    """数字和扑克牌的双向映射"""

    def __init__(self):
        self.suits = ['♠', '♥', '♦', '♣']  # 黑桃 红心 方块 梅花
        self.ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

        self._num_to_card = dict()
        self._card_to_num = dict()

        num = 1
        for suit in self.suits:
            for rank in self.ranks:
                card = f'{suit}{rank}'
                self._num_to_card[num] = card
                self._card_to_num[card] = num
                num += 1

    def num_to_card(self, num: int) -> str:
        """将1-52的数字转换为扑克牌"""
        if not (1 <= num <= 52):
            raise ValueError(f'num must be between [1, 52]. Invalid num: {num}')
        return self._num_to_card[num]

    def card_to_num(self, card: str) -> int:
        """将扑克牌转换为1-52的数字"""
        if card not in self._card_to_num:
            raise ValueError(f'Invalid card: {card}')
        return self._card_to_num[card]

    def get_suit_and_rank(self, num: int) -> Tuple[str, str]:
        """根据指定的数字分别获取花色和点数"""
        if not (1 <= num <= 52):
            raise ValueError(f'num must be between [1, 52]. Invalid num: {num}')

        suit_index = (num - 1) // 13
        rank_index = (num - 1) % 13
        return self.suits[suit_index], self.ranks[rank_index]

    def is_card(self, card: str) -> bool:
        return (card in self._card_to_num)

    def random_n_cards(self, n: int = 5):
        assert 1 <= n <= len(self._card_to_num)
        n_cards = random.sample(self._card_to_num.keys(), n)
        return ' '.join(n_cards)

    def display_all_mapping(self):
        """显示所有数字到扑克牌的映射"""
        print('数字 -> 扑克牌：')
        for i in range(1, 53):
            suit, rank = self.get_suit_and_rank(i)
            print(f'{i:2d} -> {suit}{rank}')


if __name__ == '__main__':
    pm = PokeMapper()
    print(pm.card_to_num('♠4'))
