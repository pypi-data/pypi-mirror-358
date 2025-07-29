def render_template(template_str, context):
    for key, value in context.items():
        placeholder = f"{{{{{key}}}}}"
        template_str = template_str.replace(placeholder, str(value))
    return template_str