# WSQ Editor Makefile
# Author: Patrik Nemeth

# freeze and filter out "pkg-resources" from pip freeze output - bug in debian/ubuntu systems
freeze:
	pip freeze | grep -v "pkg-resources" > requirements.txt

doc:
	doxygen Doxyfile
