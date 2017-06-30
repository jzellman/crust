import web


def static_urls(paths, static_class='static'):
    urls = []
    for path in paths:
        urls += ['/%s' % path, static_class]
    return urls


def build_link(name, path, **attrs):
    if 'css_class' in attrs:
        attrs['class'] = attrs.pop('css_class')
    attrs['href'] = path
    link_attrs = ' '.join(['{}="{}"'.format(f, v) for f, v in attrs.items()])
    return u'<a {}>{}</a>'.format(link_attrs, web.websafe(name))


def build_path(prefix, *fragments, **kwargs):
    root_name = kwargs.get('root_name', 'root')

    paths = []
    for frag in fragments:
        if frag == '':
            name = root_name
            path = prefix
        else:
            name = frag
            path = '{}/{}'.format(prefix, frag.replace("_", "/"))
        paths.append(('{}_path'.format(name), path))
    return paths
