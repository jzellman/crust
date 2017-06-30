import bcrypt


class SimpleCryptor:
    def crypt(self, word):
        return word

    def is_crypted(self, word, crypted_word):
        return word == crypted_word


class Bcryptor(SimpleCryptor):
    def crypt(self, word):
        return bcrypt.hashpw(word.encode('utf-8'), bcrypt.gensalt())

    def is_crypted(self, word, crypted):
        crypted = crypted.encode('utf-8')
        return bcrypt.hashpw(word.encode('utf-8'), crypted) == crypted
