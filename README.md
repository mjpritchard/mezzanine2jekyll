# mezzanine2jekyll

This is a Django management command to add support for exporting Mezzanine's
blog posts to Jekyll post files.

## Usage

1. Install the [package](https://pypi.python.org/pypi/mezzanine2jekyll) in your virtualenv:

```
$ pip install mezzanine2jekyll
```

2. Add `mezzanine2jekyll` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    ...
    "mezzanine2jekyll",
)
```

3. Use the new management command to export:

```
$ python manage.py mezzanine2jekyll -h
Usage: manage.py mezzanine2jekyll [options] 

Export Mezzanine blog posts as Jekyll files
```
