"""配置管理测试"""

import yaml

from llm_audit.config import AuditConfig, load_config, migrate_old_config


class TestAuditConfig:
    """配置模型测试"""

    def test_default_config(self):
        config = AuditConfig()
        assert config.model.provider == "openai"
        assert config.model.timeout == 60
        assert "prompt_injection" in config.test.categories
        assert config.evaluator.method == "heuristic"
        assert "markdown" in config.report.formats

    def test_custom_config(self):
        config = AuditConfig(
            model={"model_name": "test-model", "timeout": 30},
            test={"categories": ["prompt_injection"], "concurrency": 5},
        )
        assert config.model.model_name == "test-model"
        assert config.model.timeout == 30
        assert config.test.concurrency == 5


class TestLoadConfig:
    """配置加载测试"""

    def test_load_nonexistent(self):
        config = load_config("nonexistent.yaml")
        assert config.model.provider == "openai"

    def test_load_valid_yaml(self, tmp_path):
        config_file = tmp_path / "test_config.yaml"
        config_data = {
            "model": {"model_name": "test-model"},
            "test": {"categories": ["jailbreak"]},
        }
        config_file.write_text(yaml.dump(config_data))

        config = load_config(str(config_file))
        assert config.model.model_name == "test-model"
        assert config.test.categories == ["jailbreak"]


class TestMigrateOldConfig:
    """旧配置迁移测试"""

    def test_migration(self):
        old_config = {
            "model": {
                "api_url": "http://localhost:8000/v1/chat/completions",
                "model_name": "deepseek-r1:1.5b",
                "api_key": "test-key",
                "request_timeout": 45,
            },
            "security_tests": {
                "enable_prompt_injection": True,
                "enable_jailbreak": True,
                "enable_information_leakage": False,
            },
            "report": {"output_dir": "./test_reports"},
        }

        new_config = migrate_old_config(old_config)

        assert new_config.model.endpoint == "http://localhost:8000/v1/chat/completions"
        assert new_config.model.model_name == "deepseek-r1:1.5b"
        assert new_config.model.timeout == 45
        assert "prompt_injection" in new_config.test.categories
        assert "jailbreak" in new_config.test.categories
        assert "info_leakage" not in new_config.test.categories
        assert new_config.report.output_dir == "./test_reports"
