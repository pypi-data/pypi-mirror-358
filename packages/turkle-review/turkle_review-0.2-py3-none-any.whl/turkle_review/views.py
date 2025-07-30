from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render

from turkle.models import Batch 

def process_batch_data(field_names, rows):
    # remove the MTurk-like metadata so we get input and answers
    keys = ['Turkle.Username']
    header = ['Username']
    for name in field_names:
        if name.startswith("Input."):
            keys.append(name)
            header.append(name[len("Input."):])
        elif name.startswith("Answer."):
            keys.append(name)
            header.append(name[len("Answer."):])
    rows = [[row[key] if key in row else "N/A" for key in keys] for row in rows]

    # we will guess that if the first row has json, every row has json
    if rows:
        # 0-based indexes of which columns look like json
        json_columns = [
            i for i, entry in enumerate(rows[0])
            if isinstance(entry, str) and entry.startswith("{") and entry.endswith("}")
        ]
    else:
        json_columns = []

    return header, rows, json_columns

@staff_member_required
def review_batch_view(request, batch_id):
    batch = get_object_or_404(Batch, pk=batch_id)

    fieldnames, rows = batch._results_data(batch.task_set.all())
    fieldnames, rows, json_columns = process_batch_data(fieldnames, rows)

    context = admin.site.each_context(request)
    context['title'] = f'Review for Batch: {batch.name}'
    context.update({
        'batch': batch,
        'field_names': fieldnames,
        'rows': rows,
        'json_columns': json_columns,
    })

    return render(request, 'turkle_review/review.html', context)
