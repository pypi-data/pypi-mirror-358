# jutlautil

Package for simple utilities that I find myself using in multiple projects.

## Installing
`pip install jutlautil` to install from PyPI. No dependencies.

## Utilities

### anchor.set_anchor()
Sets the working directory for a project by following a simple heuristic: it looks in the current directory for a file called `.anchor`, and if it doesn't find it, it goes to the parent directory and looks again. It keeps doing this until it either finds the file or runs out of directories to search. If it finds the file, it sets the working directory to that file's location. This is analogous to (and inspired by) R's `here` package.
