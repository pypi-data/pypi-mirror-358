# -*- coding: utf-8 -*-

"""
Gradio Encoder APP
"""

from .gradio_ui import create_ui
from .magic_max import MagicMax
from .poker import PokeMapper


def check_card(cards: list, pm: PokeMapper) -> str:
    """
    验证卡面是否符合以下条件：
    - 包含 5 个卡面
    - 每个卡面都由合法的花色和数字组成
    - 每个卡面各不相同
    """

    # 检查列表长度是否为 5
    if len(cards) != 5:
        return f"提示：当前牌组长度为{len(cards)}，请输入 5 张卡面"

    # 检查卡面是否符合要求
    for card in cards:
        if not pm.is_card(card):
            return f"提示：卡面 {card} 解析失败"

    # 检查是否有重复元素
    if len(set(cards)) != len(cards):
        return "提示：牌组中存在重复卡面"

    # 验证通过：列表符合所有条件
    return None


def check_list(parsed_list: list) -> str:
    """
    验证列表是否符合以下条件：
    - 包含 5 个元素
    - 每个元素都是 1-52 之间的整数
    - 每个元素各不相同
    """

    # 检查列表长度是否为 5
    if len(parsed_list) != 5:
        return f"提示：当前列表长度为{len(parsed_list)}，请输入 5 个元素的列表"

    # 检查每个元素是否为整数
    for i, element in enumerate(parsed_list):
        if not isinstance(element, int):
            return f"提示：第 {i+1} 个元素 {element} 不是整数"

    # 检查每个元素是否在 1-52 范围内
    for i, element in enumerate(parsed_list):
        if element < 1 or element > 52:
            return f"提示：第 {i+1} 个元素 {element} 不在 [1, 52] 范围内"

    # 检查是否有重复元素
    if len(set(parsed_list)) != len(parsed_list):
        return "提示：列表中存在重复元素"

    # 验证通过：列表符合所有条件
    return None


def bot(messages: list) -> str:
    card_str = messages[-1].get('content')

    # 解析 card_str
    try:
        cards = card_str.strip().split(' ')
        cards = [e.strip() for e in cards]
    except Exception as e:
        return f"错误：解析错误 - {e}"

    # 实例化卡片映射器
    pm = PokeMapper()

    # 检查卡面是否符合条件
    hint = check_card(cards, pm)
    if hint is not None:
        return hint

    # 将卡面解析为数字编码
    parsed_list = [pm.card_to_num(e) for e in cards]

    n, k = 52, 5
    magic = MagicMax(n, k)
    first_four, fifth_card = magic.reverse(magic.encoder(parsed_list))

    # 将数字编码转换为卡面
    first_four_str = ' '.join([pm.num_to_card(e) for e in first_four])
    fifth_card_str = pm.num_to_card(fifth_card)

    return (
        "五张扑克牌被 Chico 分为两堆：\n"
        f"- 前四张牌：{first_four_str}\n"
        f"- 第五张牌：{fifth_card_str}\n"
        "将前四张牌告诉 Dico 吧！他可以据此猜出第五张"
    )


def generate_response(message, history):
    if not message.strip():
        return message, history

    messages = [{'role': 'user', 'content': message}]
    response = bot(messages)

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response.strip()})
    return "", history


# 初始提示消息处理函数
def initial_message(chat_history):
    """在界面加载时添加初始提示消息"""
    pm = PokeMapper()

    initial_prompt = '\n'.join([
        "这里是 Chico！请抽取 5 张牌，每张牌由【花色】和【数字】组成。",
        "可选的花色: ♠ ♥ ♦ ♣",
        "可选的数字: A 2 3 4 5 6 7 8 9 10 J Q K",
        f"选好五张牌后告诉 Chico 哦，比如: {pm.random_n_cards()}"
    ])
    chat_history.append({"role": "assistant", "content": initial_prompt})
    return chat_history


def webui(port=7870):
    demo = create_ui(llm_func=generate_response,
                     tab_name="Chico & Dico - Encoder",
                     main_title="Chico & Dico's Magic",
                     sub_title="我是 Chico ฅ( ̳• ◡ • ̳)ฅ",
                     assistant_avatar=None,  # "/img/chico.png",
                     initial_message_fn=initial_message)
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        show_api=False,
        share=False
    )


if __name__ == "__main__":
    webui()
