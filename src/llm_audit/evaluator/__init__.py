"""评估引擎模块"""

from .base import BaseEvaluator, EvalResult
from .heuristic import HeuristicEvaluator
from .regex_evaluator import RegexEvaluator

__all__ = ["BaseEvaluator", "EvalResult", "HeuristicEvaluator", "RegexEvaluator"]


def get_evaluator(method: str = "heuristic") -> BaseEvaluator:
    """获取评估器实例"""
    evaluators = {
        "heuristic": HeuristicEvaluator,
        "regex": RegexEvaluator,
    }
    if method not in evaluators:
        raise ValueError(f"不支持的评估方法: {method}，可选: {list(evaluators.keys())}")
    return evaluators[method]()
