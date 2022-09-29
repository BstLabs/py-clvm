
#!/bin/sh -e
set -x

pytype --config=pytype.cfg src/*/*.py
