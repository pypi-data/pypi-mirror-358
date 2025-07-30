python3.12 -m pytest --cov-config .coveragerc --cov sbe2 --cov-report=html:calc_cov
firefox calc_cov/index.html
# coverage run -m pytest
# coverage report -m
# coverage html