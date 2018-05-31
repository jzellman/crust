from context import assert_equals, assert_true

from crust import links


def test_build_link():
    link = links.build_link('Test', '/test')
    assert_equals(u'<a href="/test">Test</a>', link)

    link = links.build_link('Test', '/test', css_class='css-test')
    assert_true(link in [u'<a href="/test" class="css-test">Test</a>',
                         u'<a class="css-test" href="/test">Test</a>'])

    link = links.build_link('1 < 2', '/test')
    assert_equals(u'<a href="/test">1 &lt; 2</a>', link)


def test_build_path():
    paths = links.build_path('/clients/1', '')
    assert_equals(paths, [('root_path', '/clients/1')])

    paths = links.build_path('/clients/1', '', root_name='base')
    assert_equals(paths, [('base_path', '/clients/1')])

    paths = links.build_path('/clients/1', '', 'forms', 'notes', 'documents')
    assert_equals(paths, [('root_path', '/clients/1'),
                          ('forms_path', '/clients/1/forms'),
                          ('notes_path', '/clients/1/notes'),
                          ('documents_path', '/clients/1/documents')])

    paths = links.build_path('/clients/1', 'forms_profile')
    assert_equals(paths, [('forms_profile_path', '/clients/1/forms/profile')])
