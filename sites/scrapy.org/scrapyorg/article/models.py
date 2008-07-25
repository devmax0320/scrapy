from datetime import datetime

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


REST_HELP_TEXT = _("""ReST markup language allowed
                      <a href='http://en.wikipedia.org/wiki/ReStructuredText'>
                      Read more</a>""")

MAIN_HELP_TEXT = _("Useful to filter articles, like those public on homepage")


class Article(models.Model):
    title = models.CharField(_("title"), max_length=256, core=True,
                             blank=False)
    slug = models.SlugField(_("slug"), prepopulate_from=("title",),
                            editable=False)
    text = models.TextField(_("text"), core=True, help_text=REST_HELP_TEXT)
    main = models.BooleanField(_("main"), core=True, blank=False,
                               default=False, help_text=MAIN_HELP_TEXT)
    position = models.IntegerField(_("position"), core=True, blank=False,
                                   default=0)
    publish = models.BooleanField(_("publish"), core=True, default=False)

    # automatic dates
    created = models.DateTimeField(core=True, editable=False)
    updated = models.DateTimeField(core=True, editable=False)

    def toggle_publish(self):
        self.publish = not self.publish
        self.save()

    def position_up(self):
        self.position += 1
        self.save()

    def position_down(self):
        self.position -= 1
        self.save()

    def save(self):
        if not self.id:
            self.created = datetime.now()
        self.updated = datetime.now()
        self.slug = slugify(self.title)
        super(Article, self).save()

    def __unicode__(self):
        return self.title

    # ugly, but django-admin isn't very versatile right now
    def position_link(self):
        return _("%(position)s (<a href='/admin/article/article/%(id)s/position/up/'>Up</a>" \
                 " | <a href='/admin/article/article/%(id)s/position/down/'>Down</a>)") % \
               { "position": self.position, "id": self.id }
    position_link.short_description = u"position"
    position_link.allow_tags = True

    def publish_link(self):
        img_url = "/media/img/admin/icon-%s.gif" % \
                  (self.publish and "yes" or "no")
        html = _('<img alt="%s" src="' + img_url + '"/> ' \
                 '(<a href="%s/publish/toggle/">Toggle</a>)')
        return html % (_(str(self.publish)), self.id)
    publish_link.short_description = u"publish"
    publish_link.allow_tags = True

    class Admin:
        list_display = ("title", "main", "position_link", "publish_link",
                        "updated")
        list_filter = ("main", "created", "publish")

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")
        ordering = [ "-position", ]
