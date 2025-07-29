from .base import zut_mcp
from fuzzywuzzy import process
import pandas as pd
import json
import os
print('加载-餐饮数据-中...')
food_path = os.environ.get("ZUT_FOOD_PATH", "")
df = pd.read_csv(food_path)

@zut_mcp.tool()
def get_Zut_food(query:str, column:str="name", debug:bool=False, top_k:int=5):
    """
    仅当你需要查询中原工学院周围的餐饮信息时使用这个工具函数!
    在数据库的column列中, 查询与query最相似的菜品, 并返回top_k个结果.
    参数:
        query (str): 用户输入的菜品或店铺名称，用于模糊匹配查找最相似的餐饮店。
        df (DataFrame): 包含餐饮店信息的数据表，需包含指定的列。
        column (str, 可选): 用于匹配的列名，默认为 "name"。 Choice("name"店名, "tag"出售种类的标签)
        debug (bool, 可选): 是否打印调试信息，默认为 False。
        top_k (int, 可选): 返回最相似的前 top_k 个结果，默认为 5。

    返回:
        list[dict]: 包含 top_k 个最相似餐饮店信息的字典列表，每个字典的 key 为数据表的列名，value 为对应的值。

    用途:
        该工具用于根据用户输入的关键词，在餐饮数据库中查找最相似的餐饮店或菜品，并返回详细信息，适合智能问答、推荐等场景。
    """
    choices = df[column].tolist()
    most_similar = process.extract(query, choices, limit=top_k)
    # 提取匹配到的菜品名
    matched_names = [item[0] for item in most_similar]
    result_df = df[df[column].isin(matched_names)].drop_duplicates(subset=['address'])[:top_k]
    if debug:
        print('query:', query)
        print('most_similar:', most_similar)
    return json.dumps(result_df.to_dict(orient="records"))