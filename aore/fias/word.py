# -*- coding: utf-8 -*-
import re


class WordEntry:
    # Варианты распеределния для слов с первыми двумя символами, где:
    # 0 - не найдено, 1 - найдено одно, x - найдено много (>1)
    # 1st - кол-во слов по LIKE 'word%'
    # 2nd - кол-во слов по точному совпадению
    #
    # 00 - не найдено ничего вообще. Опечатка или дряное слово. Ищем с подсказками (много)
    # 01 - найдено одно точное совпадение, но нет лайков. Оставляем как есть.
    # -0x - найдено много точных совпадений и... быть не может, там уник.
    # 10 - найден один по лайку и ни одного точного. Недопечатка. * и немного подсказок.
    # 11 - одно по лайку и одно точное. Нашли. Оставляем слово как есть.
    # -1x - одно по лайку и много точных. Быть не может.
    # x0 - много по лайку и нет точных. Недопечатка. Немного подсказок и *.
    # x1 - много по лайку и один точный. Чет нашли. Как есть и *.
    # xx - много по лайку и много точных. Оставляем как есть и *
    #
    # Теперь по сокращениям. Они работюат отдельно (ПОКА ЧТО)
    # 3rd - кол-во слов по точному совпдению по полному сокращению.
    # 4th - кол-во слов по точному совпадению по малому сокращению.
    #
    # 00 - ни найдено нигде. Значит, не сокращение (или с опечаткой). Не обрабатываем.
    # 01 - найдено одно малое сокращение. Оставляем как есть (малые и так в словаре)
    # 0x - найдено много малых. Не обрабатываем.
    # 10 - найдено одно полное и 0 малых. Добавляем малое.
    # 11 - найдено одно полное и одно малое. Бывает (допустим, 'сад'). Добавляем как есть.
    # -1x - найдено одно полное и куча малых. Ну бред.
    # x0 - найдено куча полных и ни одного малого. Добавляем малое.
    # x1 - Куча полных и 1 малое. TODO Хз, бывает ли. Не обрабатываем.
    # xx - Куча полных и куча малых. Не обрабатываем.
    match_types = dict(
        MT_MANY_SUGG=['0000'],
        MT_SOME_SUGG=['10..', 'x0..'],
        MT_LAST_STAR=['10..', 'x...'],
        MT_AS_IS=['.1..', '...1', '...x'],
        MT_ADD_SOCR=['..10', '..x0']
    )

    def __init__(self, db, word):
        self.db = db
        self.word = word
        self.ranks = self.__get_word_entity()

        for x, y in self.match_types.iteritems():
            self.__dict__[x] = False
            for z in y:
                self.__dict__[x] = self.__dict__[x] or re.search(z, self.ranks) is not None

    def __get_word_entity(self):
        word_len = len(self.word)
        sql_qry = "SELECT COUNT(*) FROM \"AOTRIG\" WHERE word LIKE '{}%' AND LENGTH(word) > {} " \
                  "UNION ALL SELECT COUNT(*) FROM \"AOTRIG\" WHERE word='{}' " \
                  "UNION ALL SELECT COUNT(*) FROM \"SOCRBASE\" WHERE socrname ILIKE '{}'" \
                  "UNION ALL SELECT COUNT(*) FROM \"SOCRBASE\" WHERE scname ILIKE '{}'".format(
            self.word, word_len, self.word, self.word, self.word)

        result = self.db.get_rows(sql_qry)
        outmask = ""
        for ra in result:
            if ra[0] > 1:
                outmask += 'x'
            else:
                outmask += str(ra[0])
        return outmask

    def get_type(self):
        return ", ".join([x for x in self.match_types if self.__dict__[x]])

    def __str__(self):
        return str(self.word)
