"""
Lexicon 词库系统模块

三级分类体系：
- 一级：domain（领域）→ 51个领域，按用户意图组织
- 二级：type（类型）→ knowledge/pattern/principle/law/paradigm
- 三级：attribute（属性）→ verified/hypothesis/deprecated
"""

from .lexicon_categories import (
    LexiconCategoryRegistry,
    DOMAINS,
    TYPES,
    ATTRIBUTES,
    get_categories,
    get_subcategories,
    add_category,
    categorize_concept,
    default_registry,
)

__all__ = [
    "LexiconCategoryRegistry",
    "DOMAINS",
    "TYPES",
    "ATTRIBUTES",
    "get_categories",
    "get_subcategories",
    "add_category",
    "categorize_concept",
    "default_registry",
]
