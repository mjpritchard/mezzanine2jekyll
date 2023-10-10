from django.core.management.base import BaseCommand
from mezzanine.blog.models import BlogPost
import os
import re
import markdownify

class Command(BaseCommand):
    help = 'Export Mezzanine blog posts as Hugo markdown files'

    def add_arguments(self, parser):
        parser.add_argument('output_dir', help='Where to put the outputted Hugo markdown files')
        parser.add_argument('limit', help='how many blog posts to export (in reverse date order)')
        parser.add_argument('base_url', help='base url for blog posts e.g. /blog (no http(s):// or trailing slash)')
        #parser.add_argument('end_date', help='end date for export (publish_date of post)')

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        limit = int(options['limit'])
        base_url = str(options['base_url'])
        #start_date = options['start_date']
        #end_date = options['end_date']

        STATUS_PUBLISHED = 2

        for post in BlogPost.objects.filter(status=STATUS_PUBLISHED)[:limit]: #, publish_date = start_date):
        
            tags = ['news',]
            for kw in post.keywords.all():
                tags.append(str(kw))

            url = '/'.join([base_url, post.slug])
            aliases = []
            aliases.append(url)

            print(aliases)

            #print(post.publish_date, post.title, len(tags), tags)

            header = {
                'title': post.title.replace(':', '').replace('"','').replace('\r\n',' '),
                'date': post.publish_date,
                'tags': tags,
                'aliases': aliases
            }

            filename = '{d.year:02}-{d.month:02}-{d.day:02}-{slug}.md'.format(
                    d=post.publish_date, slug=post.slug)

            try:
            
                md_content = markdownify.markdownify(post.content)

                # Write out the file
                with open(os.path.join(output_dir, filename), 'w') as fp:
                    fp.write('---' + os.linesep)
                    for k, v in header.items():
                        fp.write('%s: %s%s' % (k, v, os.linesep))
                    fp.write('---' + os.linesep)
                    fp.write(md_content)

            except TypeError:

                print("content for post",post.slug, " not valid")
