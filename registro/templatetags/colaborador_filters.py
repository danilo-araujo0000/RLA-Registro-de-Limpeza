from django import template
import json

register = template.Library()

@register.filter(name='parse_colaboradores')
def parse_colaboradores(colaborador_str):
    if not colaborador_str:
        return ""

    try:
        colaboradores_dict = json.loads(colaborador_str)
        items = []
        for key in sorted(colaboradores_dict.keys(), key=lambda x: int(x)):
            items.append(f"{key}. {colaboradores_dict[key]}")
        return "\n".join(items)
    except (json.JSONDecodeError, ValueError, AttributeError, TypeError):
        return colaborador_str