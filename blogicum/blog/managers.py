from django.db.models import Manager
from django.utils.timezone import now


class PublishedPostManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            pub_date__lt=now(),
            category__is_published=True
        ).select_related(
            'author',
            'category',
            'location',
        )
