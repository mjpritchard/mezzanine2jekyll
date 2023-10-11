from django.core.management.base import BaseCommand
from mezzanine.blog.models import BlogPost
import os
import re
import markdownify
from urllib.request import urlretrieve
from urllib.error import HTTPError

class Command(BaseCommand):
    help = 'Export Mezzanine blog posts as Hugo markdown files'

    def add_arguments(self, parser):
        parser.add_argument('output_dir', help='Where to put the outputted Hugo markdown files (relative path to local dir)')
        parser.add_argument('limit', help='how many blog posts to export (in reverse date order)')
        parser.add_argument('base_url', help='base url for blog posts e.g. /blog (no http(s):// or trailing slash)')
        parser.add_argument('media_prefix', help="prefix url from which to fetch media, no trailing slash e.g. https://www.ceda.ac.uk")
        parser.add_argument('media_dir', help="where to put the downloaded media files (relative path to local dir)")
        #parser.add_argument('end_date', help='end date for export (publish_date of post)')

    def handle(self, *args, **options):
        limit = int(options['limit'])

        for post in BlogPost.objects.published()[:limit]: #, publish_date = start_date):

            tags = ['news',]
            for kw in post.keywords.all():
                tags.append(str(kw))

            url = '/'.join([options['base_url'], post.slug])
            aliases = []
            aliases.append(url)

            try:
                print(post.slug, "featured image: " + post.featured_image.url)

                # fetch the image to a local directory
                dest_path = os.path.join(options['media_dir'], post.slug)
                print("2. media_prefix = ", options['media_prefix'])
                source_url = options['media_prefix'] + post.featured_image.url

                print("SOURCE: ", source_url)
                
                # Save featured image locally & return its new location
                if os.path.exists(dest_path):
                    print("EXISTS")
                else:
                    print("MAKEDIRS")
                    os.makedirs(dest_path)

                source_filename = os.path.basename(post.featured_image.url)
                dest_file = os.path.join(dest_path, source_filename)

                try:
                    print("Trying download of ",source_url ,"to", dest_file)
                    urlretrieve(source_url, dest_file)
                except:
                    print("Download failed")

                print("DEST:", dest_file)
                thumbnail = dest_file

            except ValueError:
                thumbnail=""

            #TODO check image size options

            header = {
                'title': post.title.replace(':', '').replace('"','').replace('\r\n',' '),
                'date': post.publish_date,
                'tags': tags,
                'aliases': aliases,
                'thumbnail': thumbnail
            }

            filename = '{d.year:02}-{d.month:02}-{d.day:02}-{slug}.md'.format(
                    d=post.publish_date, slug=post.slug)

            try:
            
                md_content = markdownify.markdownify(post.content)

                # Write out the file
                with open(os.path.join(options['output_dir'], filename), 'w') as fp:
                    fp.write('---' + os.linesep)
                    for k, v in header.items():
                        fp.write('%s: %s%s' % (k, v, os.linesep))
                    fp.write('---' + os.linesep)

                    #TODO check for any other images in the text?

                    fp.write(md_content)

            except TypeError:

                print("content for post",post.slug, " not valid")
