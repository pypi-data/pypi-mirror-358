import chico_dico


# 指定五张牌
nums = [2, 4, 41, 29, 33]
cg = chico_dico.CardGame(nums)

# 随机五张牌
# cg.im_feeling_lucky()

# 展示当前牌面
cards = cg.display_cards(cg.nums)
print(f'当前牌面：{cards}')

# Chico 给牌排序
first_four, fifth_card = cg.chico()
print(f'前四张牌：{cg.display_cards(first_four)}')

# Dico 根据前四张牌猜第五张
answer = cg.dico(first_four)
print(f'Dico 认为第五张牌是：{cg.display_cards([answer])}')
print(f'实际第五张牌是：{cg.display_cards([fifth_card])}')
