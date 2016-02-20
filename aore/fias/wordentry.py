# -*- coding: utf-8 -*-
import re

from aore.config import sphinx_conf
from aore.fias.wordvariation import WordVariation, VariationType


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
    # xx - много по лайку и много точных. Оставляем как есть и * TODO В данном случае лайк лучше убрать
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
    # x1 - Куча полных и 1 малое. Хз, бывает ли. Не обрабатываем.
    # xx - Куча полных и куча малых. Не обрабатываем.
    match_types = dict(
        MT_MANY_SUGG=['0000'],
        MT_SOME_SUGG=['10..', 'x0..'],
        MT_LAST_STAR=['10..', 'x...'],
        MT_AS_IS=['.1..', '...1', '...x'],
        MT_ADD_SOCR=['..10', '..x0']
    )

    rating_limit_soft = 0.41
    rating_limit_soft_count = 6

    rating_limit_hard = 0.82
    rating_limit_hard_count = 3

    def __init__(self, db, word):
        self.db = db
        self.word = str(word)
        self.word_len = len(unicode(self.word))
        self.parameters = dict(IS_FREQ=False, SOCR_WORD=None)
        self.ranks = self.__init_ranks()

        # Заполняем параметры слова
        for mt_name, mt_values in self.match_types.iteritems():
            self.__dict__[mt_name] = False
            for mt_value in mt_values:
                self.__dict__[mt_name] = self.__dict__[mt_name] or re.search(mt_value, self.ranks) is not None

        # Если ищем по лайку, то точное совпадение не ищем (оно и так будет включено)
        if self.MT_LAST_STAR:
            self.MT_AS_IS = False

        # Строка слишком котроткая, то по лайку не ищем, сфинкс такого не прожует
        # Если найдено сокращение, то по лайку тоже не ищем TODO добавить это в правила
        if self.MT_LAST_STAR and (self.word_len < sphinx_conf.min_length_to_star or self.MT_ADD_SOCR):
            self.MT_LAST_STAR = False
            self.MT_AS_IS = True

    def variations_gen(self, strong, suggestion_func):
        default_var_type = VariationType.normal
        # Если слово встречается часто, ставим у всех вариантов тип VariationType.freq
        if self.parameters['IS_FREQ']:
            default_var_type = VariationType.freq

        # Добавляем подсказки (много штук)
        if self.MT_MANY_SUGG and not strong:
            suggs = suggestion_func(self.word, self.rating_limit_soft, self.rating_limit_soft_count)
            for suggestion in suggs:
                yield WordVariation(self, suggestion[0], default_var_type)

        # Добавляем подсказки (немного)
        if self.MT_SOME_SUGG and not strong:
            suggs = suggestion_func(self.word, self.rating_limit_hard, self.rating_limit_hard_count)
            for suggestion in suggs:
                yield WordVariation(self, suggestion[0], default_var_type)

        # Добавляем звездочку на конце
        if self.MT_LAST_STAR:
            yield WordVariation(self, self.word + '*', default_var_type)

        # Добавляем слово "как есть"
        if self.MT_AS_IS:
            yield WordVariation(self, self.word, default_var_type)

        # -- Дополнительные функции --
        # Добавляем сокращение
        if self.MT_ADD_SOCR:
            if self.parameters['SOCR_WORD']:
                yield WordVariation(self, self.parameters['SOCR_WORD'], VariationType.freq)

    def __init_ranks(self):
        sql_qry = "SELECT COUNT(*), NULL FROM \"AOTRIG\" WHERE word LIKE '{}%' AND LENGTH(word) > {} " \
                  "UNION ALL SELECT COUNT(*), NULL FROM \"AOTRIG\" WHERE word='{}' " \
                  "UNION ALL SELECT COUNT(*), MAX(scname) FROM \"SOCRBASE\" WHERE socrname ILIKE '{}'" \
                  "UNION ALL SELECT COUNT(*), NULL FROM \"SOCRBASE\" WHERE scname ILIKE '{}'" \
                  "UNION ALL SELECT frequency, NULL FROM \"AOTRIG\" WHERE word='{}';".format(
            self.word, self.word_len, self.word, self.word, self.word, self.word)

        result = self.db.get_rows(sql_qry)

        # Проставляем "сокращенное" сокращение, если нашли полное
        if not self.parameters['SOCR_WORD']:
            self.parameters['SOCR_WORD'] = result[2][1]

        # Проверяем, если слово встречается слишком много раз
        if len(result) == 5 and result[4][0] > 30000:
            self.parameters['IS_FREQ'] = True

        # Формируем список найденных величин совпадений:
        # result[x]
        # x = 0, поиск по неполному совпадению (лайк*), и по длине строки больше исходной
        # x = 1, поиск по точному совпадению
        # x = 2, поиск по базе сокращений (по полному)
        # x = 3, то же, но по краткому
        out_mask_list = []
        for i in range(0, 4):
            if result[i][0] > 1:
                out_mask_list.append('x')
            else:
                out_mask_list.append(str(result[i][0]))

        return ''.join(out_mask_list)

    def get_type(self):
        return ", ".join([x for x in self.match_types if self.__dict__[x]])

    def __unicode__(self):
        return self.word

    def __str__(self):
        return str(self.word)
