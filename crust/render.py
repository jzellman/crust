class RenderPartial:
    """
        Looks for templates starting with an underscore.
        For example render('foo') will look for _foo.html in
        template directory.
        Also supports nested directories. For example
        render('person/status/foo') will find _foo.html in
        template directory _+ /person/status.
    """
    def __init__(self, renderer):
        self.renderer = renderer

    def __call__(self, template_name, *args, **kwargs):
        renderer = self.renderer
        parts = template_name.split('/')
        template_name = parts.pop()

        for directory in parts:
            renderer = getattr(renderer, directory)

        template_name = '_' + template_name
        return getattr(renderer, template_name)(*args, **kwargs)
