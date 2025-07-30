# your_module/rating_agency.py
from typing import Dict, List

class RatingAgency:
    """枚举式评级机构常量类，支持多种写法和别名映射。"""
    StandardPoor = 'StandardPoor'
    Moody = 'Moody'
    Fitch = 'Fitch'
    DBRS = 'DBRS'
    Bloomberg = 'Bloomberg'
    RatingMatrix = 'RatingMatrix'

class RatingAgencyManager:
    def __init__(self):
        self.rating_systems = {
            'StandardPoor': ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'BB-',
                             'B+', 'B', 'B-', 'CCC+', 'CCC', 'CCC-', 'CC', 'C', 'D'],
            'Moody': ['Aaa', 'Aa1', 'Aa2', 'Aa3', 'A1', 'A2', 'A3', 'Baa1', 'Baa2', 'Baa3', 'Ba1', 'Ba2', 'Ba3', 'B1',
                      'B2', 'B3', 'Caa1', 'Caa2', 'Caa3', 'Ca', 'C', 'D'],
            'Fitch': ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'BB-', 'B+', 'B',
                      'B-', 'CCC+', 'CCC', 'CCC-', 'CC', 'C', 'D'],
            'DBRS': ['AAA', 'AAH', 'AA', 'AAL', 'AH', 'A', 'AL', 'BBBH', 'BBB', 'BBBL', 'BBH', 'BB', 'BBL', 'BH', 'B',
                     'BL', 'CCCH', 'CCC', 'CCCL', 'CC', 'C', 'DDD'],
            'Bloomberg': ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'BB-', 'B+',
                          'B', 'B-', 'CCC+', 'CCC', 'CCC-', 'CC', 'C', 'D'],
            'RatingMatrix': ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'CC', 'C', 'D'],
        }
        self.aliases = {'SP': 'StandardPoor', 'M': 'Moody'}

    def add_rating_system(self, agency_name: str, rating_list: List[str]) -> None:
        """添加或更新一个评级系统"""
        if agency_name in self.rating_systems:
            print(f"Warning: Rating agency '{agency_name}' already exists and will be overwritten.")
        
        # 动态添加进 RatingAgency
        setattr(RatingAgency, agency_name.replace(' ', ''), agency_name)
        
        # 存储评级符号列表
        self.rating_systems[agency_name] = [r.upper() for r in rating_list]

    def get_agency_name(self, agency) -> str:
        """获取评级机构名称"""
        if hasattr(agency, '__class__') and agency.__class__.__name__ == 'type':
            return agency.value if hasattr(agency, 'value') else agency.name
        elif isinstance(agency, str):
            return self.aliases.get(agency, agency)
        else:
            raise ValueError(f"Unsupported rating agency input: {repr(agency)}")
