"""攻击用例加载器 - 从 YAML 文件加载用例"""

import importlib
import importlib.util
from pathlib import Path
from typing import Optional

import yaml

from .base import AttackPayload, BaseAttack


class YamlAttack(BaseAttack):
    """从 YAML 文件加载的攻击模块"""

    def __init__(self, category: str, name: str, payloads: list[AttackPayload]):
        self._category = category
        self._name = name
        self._payloads = payloads

    def get_payloads(self) -> list[AttackPayload]:
        return self._payloads

    def get_category(self) -> str:
        return self._category

    def get_name(self) -> str:
        return self._name


class AttackLoader:
    """攻击用例加载器"""

    def __init__(self, payloads_dir: Optional[str] = None):
        # 内置用例目录
        self._builtin_dir = Path(__file__).parent.parent.parent.parent / "attack_payloads"
        # 自定义用例目录
        self._custom_dir = Path(payloads_dir) if payloads_dir else None

    def load_from_yaml(self, yaml_path: Path) -> BaseAttack:
        """从 YAML 文件加载攻击用例"""
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        category = data.get("category", yaml_path.stem)
        name = data.get("name", category)
        payloads = []

        for i, item in enumerate(data.get("payloads", [])):
            payload = AttackPayload(
                id=item.get("id", f"{category}_{i+1:03d}"),
                category=category,
                name=item.get("name", f"Test {i+1}"),
                prompt=item["prompt"],
                expected_behavior=item.get("expected_behavior", "refuse"),
                severity=item.get("severity", "high"),
                tags=item.get("tags", []),
                description=item.get("description", ""),
            )
            payloads.append(payload)

        return YamlAttack(category, name, payloads)

    def load_builtin(self, category: str) -> Optional[BaseAttack]:
        """加载内置攻击用例"""
        yaml_path = self._builtin_dir / f"{category}.yaml"
        if yaml_path.exists():
            return self.load_from_yaml(yaml_path)
        return None

    def load_custom(self, category: str) -> Optional[BaseAttack]:
        """加载自定义攻击用例"""
        if self._custom_dir is None:
            return None
        yaml_path = self._custom_dir / f"{category}.yaml"
        if yaml_path.exists():
            return self.load_from_yaml(yaml_path)
        return None

    def load_all(self, categories: Optional[list[str]] = None) -> list[BaseAttack]:
        """加载所有攻击用例"""
        attacks = []

        # 确定要加载的类别
        if categories is None:
            categories = self._get_available_categories()

        for category in categories:
            # 优先加载自定义用例
            attack = self.load_custom(category)
            if attack is None:
                attack = self.load_builtin(category)
            if attack is not None:
                attacks.append(attack)

        return attacks

    def _get_available_categories(self) -> list[str]:
        """获取所有可用的攻击类别"""
        categories = set()

        # 扫描内置用例
        if self._builtin_dir.exists():
            for f in self._builtin_dir.glob("*.yaml"):
                categories.add(f.stem)

        # 扫描自定义用例
        if self._custom_dir and self._custom_dir.exists():
            for f in self._custom_dir.glob("*.yaml"):
                categories.add(f.stem)

        return sorted(categories)

    def list_categories(self) -> list[dict]:
        """列出所有可用的攻击类别"""
        result = []
        for category in self._get_available_categories():
            attack = self.load_builtin(category) or self.load_custom(category)
            if attack:
                result.append({
                    "category": category,
                    "name": attack.get_name(),
                    "payload_count": len(attack.get_payloads()),
                })
        return result
