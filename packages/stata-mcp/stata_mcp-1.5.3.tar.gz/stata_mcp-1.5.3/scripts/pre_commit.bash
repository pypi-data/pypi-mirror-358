#!/usr/bin/env bash
set -euo pipefail

echo "🛠  Running pre-commit formatting & linting…"

# 1. 排序 imports
echo "  → isort"
isort src

# 2. autopep8 强力格式化
echo "  → autopep8"
autopep8 --in-place --aggressive --aggressive $(find src -type f -name '*.py')

# 3. autoflake 只移除未使用的 imports（不移除变量）
echo "  → autoflake (imports only)"
autoflake --in-place --remove-all-unused-imports $(find src -type f -name '*.py')

# 4. 最终检查：flake8
echo "  → flake8"
flake8 src --extend-ignore=E501

echo "✅  All checks passed!"
