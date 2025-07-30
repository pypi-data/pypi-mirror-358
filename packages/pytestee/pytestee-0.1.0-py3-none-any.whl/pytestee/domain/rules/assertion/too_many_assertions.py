"""PTAS002: Too Many Assertions."""

from typing import TYPE_CHECKING, Optional, Union

from pytestee.domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from pytestee.domain.rules.base_rule import BaseRule

if TYPE_CHECKING:
    from pytestee.domain.analyzers.assertion_analyzer import AssertionAnalyzer


class PTAS002(BaseRule):
    """Rule for detecting too many assertions."""

    def __init__(self, assertion_analyzer: "AssertionAnalyzer") -> None:
        super().__init__(
            rule_id="PTAS002",
            name="too_many_assertions",
            description="Test function has more assertions than maximum recommended",
        )
        self._analyzer = assertion_analyzer

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check if test function has too many assertions."""
        max_asserts = self._get_config_value(config, "max_asserts", 3)
        assert_count = self._analyzer.count_assertions(test_function)

        if assert_count > max_asserts:
            return self._create_failure_result(
                f"Too many assertions: {assert_count} (maximum recommended: {max_asserts})",
                test_file,
                test_function,
            )
        return self._create_success_result(
            f"Assertion count OK: {assert_count} assertions (maximum: {max_asserts})",
            test_file,
            test_function,
        )

    def _get_config_value(
        self, config: Optional[CheckerConfig], key: str, default: Union[int, float]
    ) -> Union[int, float]:
        """Get configuration value with fallback to default."""
        if config and config.config:
            return config.config.get(key, default)
        return default

    def get_conflicting_rules(self) -> set[str]:
        """PTAS002 conflicts with no assertions rule."""
        return {"PTAS004"}  # Conflicts with no assertions
