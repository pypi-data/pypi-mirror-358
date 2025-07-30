#!/bin/zsh

# Simple helper script with uv commands for linting and formatting

function usage() {
  echo "Usage: ./scripts/dev.sh [command]"
  echo ""
  echo "Available commands:"
  echo "  lint      - Run ruff linter"
  echo "  format    - Run ruff formatter"
  echo "  typecheck - Run mypy type checker"
  echo "  fix       - Fix linting issues automatically"
  echo "  check-all - Run all checks"
  echo "  tests     - Run tests"
  echo "  hooks     - Run all pre-commit hooks on all files"
  echo "  clean     - Clean up build artifacts (dist/, build/, *.egg-info/)"
  echo ""
  exit 1
}

if [ $# -eq 0 ]; then
  usage
fi

case "$1" in
  lint)
    echo "🔍 Running ruff linter..."
    uv run ruff check src/
    ;;
  format)
    echo "📝 Running ruff formatter..."
    uv run ruff format src/
    ;;
  typecheck)
    echo "🔍 Running mypy type checker..."
    uv run mypy src/
    ;;
  fix)
    echo "🔧 Fixing code style issues with ruff..."
    uv run ruff check src/ --fix --unsafe-fixes
    echo "📝 Formatting code with ruff..."
    uv run ruff format src/
    echo "✅ Fixes completed!"
    ;;
  check-all)
    echo "🔍 Running all checks..."
    uv run ruff check src/ && \
    uv run ruff format src/ --check && \
    uv run mypy src/ && \
    echo "✅ All checks completed!"
    ;;
  tests)
    echo "🧪 Running tests..."
    uv run pytest tests/
    ;;
  hooks)
    echo "🪝 Running all pre-commit hooks on all files..."
    uv run pre-commit run --all-files
    ;;
  clean)
    echo "🧹 Cleaning up build artifacts..."
    rm -rf dist/ build/
    echo "✅ Cleanup completed!"
    ;;
  *)
    usage
    ;;
esac
