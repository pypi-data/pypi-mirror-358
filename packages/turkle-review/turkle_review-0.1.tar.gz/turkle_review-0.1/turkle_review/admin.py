from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html

from turkle.models import Batch
from turkle.admin import BatchAdmin as OriginalBatchAdmin

from .views import review_batch_view


class ReviewBatchAdmin(OriginalBatchAdmin):
    def get_urls(self):
        # adds the review url to those registered for BatchAdmin
        original_urls = super().get_urls()
        custom_urls = [
            path(
                '<int:batch_id>/review/',
                self.admin_site.admin_view(review_batch_view),
                name='batch-review'
            ),
        ]
        return custom_urls + original_urls

    def review(self, obj):
        # adds the review button to the BatchAdmin changelist page
        url = reverse('admin:batch-review', args=[obj.id])
        return format_html('<a href="{}" class="button">Review</a>'.format(url))
    review.short_description = 'Review'
    list_display = OriginalBatchAdmin.list_display + ('review',)

# Swap out the BatchAdmin for one with a review option
admin.site.unregister(Batch)
admin.site.register(Batch, ReviewBatchAdmin)
