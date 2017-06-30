from nose.tools import assert_equals, assert_is_not_none

import crust


def test_debug_mailer():
    mailer = crust.debugmail
    message = mailer('from@example.com', 'to@example.com', 'subject', 'body')
    assert_is_not_none(message)

    assert_equals('from@example.com', message['from'])
    assert_equals('from@example.com', message.from_address)
    assert_equals('to@example.com', message.to)
    assert_equals('to@example.com', message.to_address)
    assert_equals('subject', message.subject)
    assert_equals('body', message.message)

    assert_equals([message], mailer.messages)
