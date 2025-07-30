ppip install build twine

# Install in editable mode (for development)
pip install -e .
# Build the package
python -m build
# Upload to PyPI or Artifactory
twine upload dist/*

pip freeze > requirements.txt

twine upload -u __token__ -p pypi-AgEI... dist/*

twine upload -u __token__ -p pypi-AgEIcHlwaS5vcmcCJDM3NTU4OTI1LTM5NzMtNDVmNC04MzRkLTZlNTVkMjRiMWVmYQACKlszLCI5YzFhZTUwZC0zZTc0LTQzMTctOTVhMS1jNDg3ODExMTQ0MjciXQAABiBZW2n1_gTvVKCeLel-koKOHhTZ0CWOq8CBaZRzvBbZ3A dist/*