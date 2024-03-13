import tempfile
import time
from pathlib import Path

import django
from django.conf import settings
from django.template import Context
from django.template import Template as DjangoTemplate
from jinja2 import Template as JinjaTemplate

from htpy import table, tbody, td, th, thead, tr

settings.configure(TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates"}])
django.setup()

django_jinja_template = """
<table>
    <thead><tr><th>Row #</th></tr></thead>
    <tbody>
        {% for row in rows %}
        <tr><td>{{ row }}</td></tr>
        {% endfor %}
    </tbody>
</table>
"""


tests = [
    (
        "htpy",
        lambda rows: str(table[thead[tr[th["Row #"]]], tbody[(tr[td[str(row)]] for row in rows)]]),
    ),
    (
        "django",
        lambda rows: DjangoTemplate(django_jinja_template).render(Context({"rows": rows})),
    ),
    ("jinja2", lambda rows: JinjaTemplate(django_jinja_template).render(rows=rows)),
]
rows = list(range(50_000))

tmp = Path(tempfile.mkdtemp())
for name, func in tests:
    start = time.perf_counter()
    output = func(rows)
    result = time.perf_counter() - start
    out_path = tmp / f"{name}_table.html"
    out_path.write_text(output)
    print(f"{name}: {result} seconds - {out_path}")
