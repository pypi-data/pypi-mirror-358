"""PTLG001: AAA Pattern Detected Through Code Flow Analysis."""
from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from pytestee.domain.rules.base_rule import BaseRule

if TYPE_CHECKING:
    from pytestee.domain.models import (
        CheckerConfig,
        CheckResult,
        TestFile,
        TestFunction,
    )


class PTLG001(BaseRule):
    """Rule for detecting AAA pattern through code flow analysis."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTLG001",
            name="aaa_pattern_logical",
            description="AAA pattern detected through AST analysis of code structure",
        )

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: CheckerConfig | None = None,
    ) -> CheckResult:
        """Check for logical AAA pattern in code flow."""
        # Analyze the AST to detect typical patterns
        body_statements = test_function.body

        sections = self._categorize_statements(body_statements)

        if self._has_logical_aaa_flow(sections):
            # Pattern found - return success (INFO)
            return self._create_success_result(
                "AAA pattern detected through code flow analysis",
                test_file,
                test_function,
            )
        # Pattern not found - return failure (ERROR/WARNING based on config)
        return self._create_failure_result(
            "AAA pattern not detected through code flow analysis. Consider organizing code with clear Arrange, Act, Assert sections.",
            test_file,
            test_function,
        )

    def _categorize_statements(
        self, statements: list[ast.stmt]
    ) -> dict[str, list[ast.stmt]]:
        """Categorize statements into arrange, act, assert groups."""
        sections: dict[str, list[ast.stmt]] = {"arrange": [], "act": [], "assert": []}

        current_section = "arrange"

        for stmt in statements:
            if isinstance(stmt, ast.Assert):
                current_section = "assert"
                sections["assert"].append(stmt)
            elif isinstance(stmt, ast.Assign):
                if current_section == "arrange":
                    sections["arrange"].append(stmt)
                else:
                    sections["act"].append(stmt)
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                # Function calls are typically "act"
                if current_section in ["arrange", "act"]:
                    current_section = "act"
                sections["act"].append(stmt)
            else:
                sections[current_section].append(stmt)

        return sections

    def _has_logical_aaa_flow(self, sections: dict[str, list[ast.stmt]]) -> bool:
        """Check if sections represent a good AAA flow."""
        has_arrange = len(sections["arrange"]) > 0
        has_act = len(sections["act"]) > 0
        has_assert = len(sections["assert"]) > 0

        # Should have all three sections for clear AAA pattern
        return has_arrange and has_act and has_assert
