from context import assert_equals

from crust import url


def test_build_link():
    link = url.build_link('Test', '/test')
    assert_equals(u'<a href="/test">Test</a>', link)

    link = url.build_link('Test', '/test', css_class='css-test')
    assert_equals(u'<a href="/test" class="css-test">Test</a>', link)

    link = url.build_link('1 < 2', '/test')
    assert_equals(u'<a href="/test">1 &lt; 2</a>', link)


def test_build_path():
    paths = url.build_path('/clients/1', '')
    assert_equals(paths, [('root_path', '/clients/1')])

    paths = url.build_path('/clients/1', '', root_name='base')
    assert_equals(paths, [('base_path', '/clients/1')])

    paths = url.build_path('/clients/1', '', 'forms', 'notes', 'documents')
    assert_equals(paths, [('root_path', '/clients/1'),
                          ('forms_path', '/clients/1/forms'),
                          ('notes_path', '/clients/1/notes'),
                          ('documents_path', '/clients/1/documents')])

    paths = url.build_path('/clients/1', 'forms_profile')
    assert_equals(paths, [('forms_profile_path', '/clients/1/forms/profile')])
