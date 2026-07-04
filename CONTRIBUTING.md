# Contributing

Thanks for considering a contribution to the Real Estate Price Prediction System.

## Getting Started

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate data and train a baseline model:
   ```bash
   python ml-pipeline/data/generate_data.py
   python ml-pipeline/training/train_models.py
   ```
4. Run the test suite before making changes, to confirm a clean baseline:
   ```bash
   pytest tests/ -v --cov=backend
   ```

## Development Workflow

- Create a feature branch: `git checkout -b feature/your-feature-name`
- Keep changes focused — one logical change per pull request
- Add or update tests for any behavioral change
- Ensure `pytest tests/ --cov=backend --cov-fail-under=80` passes locally
- Update `CHANGELOG.md` under an "Unreleased" heading
- Open a pull request against `develop`, describing what changed and why

## Code Style

- Follow PEP 8 for Python code
- Keep functions small and single-purpose; business logic belongs in
  `backend/services/`, not in route handlers
- Prefer explicit type hints on public functions
- Document non-obvious decisions with a short comment, not a wall of text

## Model Changes

Any change that affects `ml-pipeline/training/train_models.py` must pass the
model quality gate (`tests/test_model_performance.py`), which enforces a
minimum R² of 0.85 and a maximum MAPE of 15% on the validation split. If your
change legitimately needs to adjust these thresholds, explain why in the PR.

## Reporting Issues

Please include: steps to reproduce, expected vs. actual behavior, and
relevant logs (`docker compose logs backend`, or the pytest output).
