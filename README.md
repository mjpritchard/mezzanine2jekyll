# mezzanine2jekyll

This is a Django management command to add support for exporting Mezzanine's
blog posts to Jekyll post files.

Adapted from <https://github.com/sjkingo/mezzanine2jekyll> to export blog items
with Hugo-flavoured frontmatter and using [hinode](https://gethinode.com) shortcodes.

- Fetches post.featured_image and adds thumbmail entry to frontmatter to represent this.
- Searches for each image link within content body, making a hinode-style shortcode to represent this image and downloading the image to specified directory
- Markdown files for blog posts are named `YYYY-MM-DD-slug.md` and stored in `YYYY` directories
- Media files are downloaded to corresponding directories `YYYY/YYYY-MM-DD-slug/` beneath specified media directory

## Usage

1. Install the [package](https://pypi.python.org/pypi/mezzanine2jekyll) in your virtualenv:

    ```
    pip install mezzanine2jekyll
    ```

2. Add `mezzanine2jekyll` to your `INSTALLED_APPS`:

    ```python
    INSTALLED_APPS = (
        ...
        "mezzanine2jekyll",
    )
    ```

3. Use the new management command to export:

For jekyll (original functionality unchanged):

```
$ python manage.py mezzanine2jekyll -h
Usage: manage.py mezzanine2jekyll [options] 

Export Mezzanine blog posts as Jekyll files
```

For Hugo:

```
python manage.py mezzanine2hugo output_dir limit base_url media_predix media_dir
```

where:

- `output_dir` = Where to put the output Hugo markdown files (relative path to local dir)
- `limit` = How many blog posts to export (in reverse date order)
- `base_url` = Base url for blog posts e.g. `/blog` (no `http(s)://` or trailing slash)
- `media_prefix` = Prefix url from which to fetch media, no trailing slash e.g. `https://example.com`
- `media_dir` = Where to put the downloaded media files relative path to local dir
