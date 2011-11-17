# CHANGES

## 0.3

* The core logic isn't in the project skeleton anymore. This allow you to 
update Clay whitout having to recreate your projects.
* Bugfix: Non-utf8 content now is handled correctly.
* Bugfix: Fix pyton package


## 0.4

* Added a per-project settings file.


## 0.5

* Added a list of all generated views (by default in `_index.html`, but it can
be changed im the settings.


## 0.6

* First static file processors! So far:
    - cleverCSS (*.ccss). Requires clevercss python library.