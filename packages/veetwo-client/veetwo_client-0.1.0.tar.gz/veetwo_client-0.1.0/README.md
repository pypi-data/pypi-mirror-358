uv venv create --python=python3.13
uv pip install grpcio-tools


🔐 CI Setup (e.g., GitHub Actions)
In your workflow:

yaml
Copy
Edit
env:
  TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
  TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}

steps:
  - run: make publish-prod