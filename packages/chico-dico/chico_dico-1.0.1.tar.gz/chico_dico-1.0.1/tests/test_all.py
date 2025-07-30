import itertools

from chico_dico.magic import Magic


def test_all():
    """测试所有牌组"""
    magic = Magic()
    combinations = itertools.combinations(range(1, 53), 5)

    for combo in combinations:
        nums = list(combo)
        first_four, fifth_card = magic.reverse(magic.encoder(nums))
        guess_fifth_card = magic.decoder(first_four)
        assert fifth_card == guess_fifth_card
