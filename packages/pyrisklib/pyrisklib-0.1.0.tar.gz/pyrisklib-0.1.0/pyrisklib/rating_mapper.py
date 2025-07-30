# your_module/rating_mapper.py
import numpy as np
import pandas as pd
import re
from typing import Union, List, Dict, Any

from .rating_agency import RatingAgencyManager

class RatingMapper:
    def __init__(self, system_manager: RatingAgencyManager = None):
        """初始化评级映射器。
        
        Args:
            system_manager: RatingAgencyManager实例，如果为None则创建新实例
        """
        self.system_manager = system_manager if system_manager is not None else RatingAgencyManager()

    def map_rating(self, rating: str, agency) -> Union[int, float]:
        """将单个评级映射到其在评级系统中的位置（从1开始）
        
        Args:
            rating: 要映射的评级
            agency: 评级机构
            
        Returns:
            int: 评级在评级系统中的位置（从1开始），如果找不到则返回NaN
        """
        agency_name = self.system_manager.get_agency_name(agency)
        if agency_name not in self.system_manager.rating_systems:
            return f"Unsupported rating agency: {agency_name}"

        rating_cleaned = str(rating).strip()
        rating_list = self.system_manager.rating_systems[agency_name]
        try:
            index = rating_list.index(rating_cleaned)
            return index + 1
        except ValueError:
            return np.nan

    def map_ratings(self, rating_list: List[str], agency) -> List[Union[int, float]]:
        """将多个评级映射到其在评级系统中的位置
        
        Args:
            rating_list: 要映射的评级列表
            agency: 评级机构
            
        Returns:
            List: 评级在评级系统中的位置列表
        """
        return [self.map_rating(r, agency) for r in rating_list]

    def map_dataframe(self, df: pd.DataFrame, agency, exclude_cols: List[str] = None) -> pd.DataFrame:
        """将DataFrame中的评级列映射到其在评级系统中的位置
        
        Args:
            df: 包含评级的DataFrame
            agency: 评级机构
            exclude_cols: 需要排除的列名列表
            
        Returns:
            pd.DataFrame: 包含映射结果的DataFrame
        """
        exclude_cols = exclude_cols or []
        
        def map_col(col):
            if col.name in exclude_cols:
                return col
            return col.apply(lambda x: self.map_rating(x, agency))
        
        return df.apply(map_col)

    def filter_unrated_entities(self, df: pd.DataFrame, rating_years: List[str], suffix: str = '_num', id_col: str = 'company') -> pd.DataFrame:
        """过滤掉所有年份都没有评级的实体
        
        Args:
            df: 包含评级数据的DataFrame
            rating_years: 包含年份的列表
            suffix: 年份列名的后缀
            id_col: 实体ID列的名称
            
        Returns:
            pd.DataFrame: 只包含有评级记录的实体的DataFrame
        """
        rating_cols = [f"{y}{suffix}" for y in rating_years]
        
        def is_all_missing(row):
            return all(pd.isna(row[col]) or isinstance(row[col], str) for col in rating_cols)
        
        valid_entities = df[~df.apply(is_all_missing, axis=1)][id_col].unique()
        return df[df[id_col].isin(valid_entities)]

    def get_pure_ratings(self, ratings: Union[str, pd.Series, pd.DataFrame]) -> Union[str, pd.Series, pd.DataFrame]:
        """移除评级观察、展望等与实际评级无关的信息
        
        Args:
            ratings: 包含原始评级信息的数据，可以是字符串、Series或DataFrame
            
        Returns:
            Union[str, pd.Series, pd.DataFrame]: 清理后的评级数据
        """
        # 后缀清理：移除结尾的 pi、展望等后缀以及(Developing)、(CwPositive)、*+等特殊后缀
        rating_suffix_pattern = re.compile(r'(pi|outlook|watch|u|U|p|P|Developing|CwPositive|\*+)\b', re.IGNORECASE)
        
        # 新增模式：匹配并移除括号及其内容，如(Developing)或(CwPositive)
        bracket_pattern = re.compile(r'$$[^)]*$$')
        
        # 新增模式：匹配并移除末尾的 *- 或 *+ 等特殊符号
        special_suffix_pattern = re.compile(r'\s*\*+\+|\s*\*-\s*$')

        def clean_single_rating(rating: str) -> str:
            """清理单个评级"""
            if pd.isna(rating):
                return rating
                
            # 转换为字符串处理但不改变大小写
            rating_str = str(rating)
            
            # 移除括号及其内容，如(Developing)或(CwPositive)
            rating_str = bracket_pattern.sub('', rating_str)
            
            # 移除特殊后缀如 *- 或 *+
            rating_str = special_suffix_pattern.sub('', rating_str)
            
            # 移除所有非评级后缀，包括*+等
            rating_str = rating_suffix_pattern.sub('', rating_str)
            
            # 去除多余空格和特殊字符(不改变大小写)
            rating_str = rating_str.strip()
            
            # 去除评级观察后缀如 (p), (P) 等(虽然前面已经移除了括号内容，但这里再确保一次)
            rating_str = rating_str.removeprefix("(p)").removeprefix("(P)")
            rating_str = rating_str.rstrip("uU")
            
            return rating_str

        if isinstance(ratings, str):
            return clean_single_rating(ratings)
        
        elif isinstance(ratings, pd.Series):
            isstring = ratings.apply(type).eq(str)
            ratings[isstring] = ratings[isstring].str.replace(bracket_pattern, '', regex=True)
            ratings[isstring] = ratings[isstring].str.replace(special_suffix_pattern, '', regex=True)
            ratings[isstring] = ratings[isstring].str.replace(rating_suffix_pattern, '', regex=True)
            ratings[isstring] = ratings[isstring].apply(clean_single_rating)
            ratings.name = f"{ratings.name}_clean"
            return ratings
        
        elif isinstance(ratings, pd.DataFrame):
            return pd.concat(
                [self.get_pure_ratings(ratings[col]) for col in ratings.columns],
                axis=1
            )
