from chico_dico.game import CardGame


def test_random():
    """测试一个随机牌组"""

    cg = CardGame()

    # 随机五张牌
    cg.im_feeling_lucky()

    # Chico 给牌排序
    first_four, fifth_card = cg.chico()

    # Dico 根据前四张牌猜第五张
    answer = cg.dico(first_four)

    assert answer == fifth_card
