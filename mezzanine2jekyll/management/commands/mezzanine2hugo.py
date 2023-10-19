from django.core.management.base import BaseCommand
from mezzanine.blog.models import BlogPost
import os
import re
import markdownify
from urllib.request import urlretrieve
from urllib.error import HTTPError
from urllib.parse import quote

class Command(BaseCommand):
    help = 'Export Mezzanine blog posts as Hugo markdown files'

    def add_arguments(self, parser):
        parser.add_argument('output_dir', help='Where to put the outputted Hugo markdown files (relative path to local dir)')
        parser.add_argument('limit', help='how many blog posts to export (in reverse date order)')
        parser.add_argument('base_url', help='base url for blog posts e.g. /blog (no http(s):// or trailing slash)')
        parser.add_argument('media_prefix', help="prefix url from which to fetch media, no trailing slash e.g. https://www.ceda.ac.uk")
        parser.add_argument('media_dir', help="where to put the downloaded media files (relative path to local dir)")
        #parser.add_argument('end_date', help='end date for export (publish_date of post)'
    
    def save_and_replace_image_link(self, m):
        g = list(m.groups())
        print("SUB: SELF.FILENAME_BASE: ", self.filename_base, self.year)
        caption = g[0] # pass thro unchanged
        url = g[1].replace('/static', '')
        url = self.media_prefix + url # where to fetch from
        filename = os.path.basename(url) # just the filename part
        save_path = "/img/news/" + self.year + "/" + self.filename_base # make the path inc the date+slug dir string
        save_filename = os.path.join(save_path, filename)
        print("MEDIA_DIR = ", self.media_dir)
        print("SAVE_FILENAME:", save_filename)
        real_save_path = self.media_dir + save_path
        print("SUB: REAL_SAVE_PATH = ", real_save_path)
        real_save_filename = self.media_dir + save_filename
        if not os.path.exists(real_save_path):
            print("Making path :", real_save_path )
            os.makedirs(real_save_path)
        try:
            print("SUB: RETRIEVE: ", url, real_save_filename)
            url = quote(url, safe="%/:=&?~#+!$,;'@()*[]")
            urlretrieve(url, real_save_filename)
        except:
            print("Error downloading image ", url, " for ", real_save_path, "\n")

        shortcode = '{{< image src="{}"  caption="{}" class="rounded" >}}'.format(
            save_filename,
            caption
        )
        shortcode = "{" + shortcode + "}"
        return shortcode #"".join(g)

    def handle(self, *args, **options):
        limit = int(options['limit'])
        self.media_prefix = options['media_prefix']
        self.media_dir = options['media_dir']


        for post in BlogPost.objects.published()[:limit]: #, publish_date = start_date):
            self.filename_base = '{d.year:02}-{d.month:02}-{d.day:02}-{slug}'.format(
                d=post.publish_date, slug=post.slug)
            self.year = post.publish_date.strftime("%Y")
            tags = ['news',]
            for kw in post.keywords.all():
                tags.append(str(kw))

            url = '/'.join([options['base_url'], post.slug])
            aliases = []
            aliases.append(url)

            try:
                print(post.slug, "featured image: " + post.featured_image.url)
                print("YEAR: ", self.year)
                # fetch the image to a local directory
                self.dest_path = os.path.join("img/news", self.year, self.filename_base)
                self.real_dest_path = os.path.join(options['media_dir'], self.dest_path)
                source_url = options['media_prefix'] + post.featured_image.url
                
                # Save featured image locally & return its new location
                if not os.path.exists(self.real_dest_path):
                    print("Making path :", self.real_dest_path )
                    os.makedirs(self.real_dest_path)

                source_filename = os.path.basename(post.featured_image.url)
                dest_file = os.path.join(self.dest_path, source_filename)
                real_dest_file = os.path.join(self.real_dest_path, source_filename)

                try:
                    print("Trying download of ",source_url ,"to", real_dest_file)
                    url = quote(url, safe="%/:=&?~#+!$,;'@()*[]")
                    urlretrieve(source_url, real_dest_file)
                except:
                    print("Download failed")

                print("DEST:", dest_file)
                thumbnail = "/" + dest_file
                icon = ""

            except ValueError:
                # if no thumbnail, set to blank & set an icon instead
                thumbnail=""
                icon = "fas circle-info"

            #TODO check image size options

            header = {
                'title': post.title.replace(':', '').replace('"','').replace('\r\n',' '),
                'date': post.publish_date,
                'tags': tags,
                'aliases': aliases,
                'thumbnail': thumbnail,
                'icon': icon
            }

            filename = self.filename_base + ".md"

            try:
            
                md_content = markdownify.markdownify(post.content)

                # Write out the file
                output_dir = os.path.join(options['output_dir'], self.year)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                with open(os.path.join(output_dir, filename), 'w') as fp:
                    fp.write('---' + os.linesep)
                    for k, v in header.items():
                        fp.write('%s: %s%s' % (k, v, os.linesep))
                    fp.write('---' + os.linesep)

                    #replace all image links in the text with a shortcode
                    # saving the image locally along the way
                    #regex for an image link
                    pattern = re.compile(r"(?:[!]\[(?P<caption>.*?)\])\((?P<image>.*?)(?P<description>\".*?\")?\)")
                    new_content = pattern.sub(self.save_and_replace_image_link, md_content)

                    fp.write(new_content)

            except TypeError as e:

                print("ERROR: content for post",post.slug, " not valid.\n", e)

