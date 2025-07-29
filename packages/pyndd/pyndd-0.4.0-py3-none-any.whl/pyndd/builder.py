from typing import Any
from .parser import parse


class ExpressionBuilder:
    def __init__(self, var_name: str):
        self.var_name = var_name
        self.selectors = []
    
    def attr(self, key: str):
        """속성/키 선택자 추가 (실제로는 변수 키로 처리됨)"""
        self.selectors.append(f":{key}")
        return self
    
    def index(self, idx: int):
        """인덱스 선택자 추가"""
        self.selectors.append(f":[{idx}]")
        return self
    
    def slice(self, start=None, end=None):
        """슬라이스 선택자 추가"""
        start_str = str(start) if start is not None else ""
        end_str = str(end) if end is not None else ""
        self.selectors.append(f":[{start_str}..{end_str}]")
        return self
    
    def multi(self, *selectors):
        """다중 선택자 추가"""
        selector_parts = []
        for sel in selectors:
            if isinstance(sel, str):
                selector_parts.append(sel)
            elif isinstance(sel, int):
                selector_parts.append(str(sel))
        self.selectors.append(f":[{','.join(selector_parts)}]")
        return self
    
    def map_key(self, key: str):
        """맵 키 선택자 추가 (#prefix)"""
        self.selectors.append(f":#{key}")
        return self
    
    def glob(self, pattern: str):
        """글롭 패턴 선택자 추가"""
        self.selectors.append(f":{pattern}")
        return self
    
    def var_keys(self, var_name: str):
        """변수 키 선택자 추가"""
        self.selectors.append(f":{var_name}")
        return self
    
    def at_var(self, var_name: str):
        """@ 변수 선택자 추가"""
        self.selectors.append(f":@{var_name}")
        return self
    
    def build(self) -> str:
        """표현식 문자열 생성"""
        return self.var_name + ''.join(self.selectors)
    
    def parse(self, **kwargs):
        """빌드하고 바로 파싱"""
        return parse(self.build(), **kwargs)
    
    def __str__(self) -> str:
        return self.build()
    
    def __repr__(self) -> str:
        return f"ExpressionBuilder('{self.build()}')"


def expr(var_name: str) -> ExpressionBuilder:
    """표현식 빌더 생성 헬퍼 함수"""
    return ExpressionBuilder(var_name)