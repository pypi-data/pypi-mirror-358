# jutlautil

Package for simple utilities that I find myself using in multiple projects.

## Installing
`pip install jutlautil` to install from PyPI. No dependencies.

## Utilities

### anchor.set_anchor()
Identifies the "anchor point" for a project and, by default, changes the working directory to that point. To identify the anchor point, it follows a simple heuristic: it looks in the current directory for a file called `anchor`, and if it doesn't find it, it goes to the parent directory and looks again. It keeps doing this until it either finds the file or reaches the filesystem root. This is analogous to (and inspired by) the behavior of R's `here` package.
