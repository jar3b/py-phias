# -*- coding: utf-8 -*-


class FiasException(Exception):
    def __str__(self):
        return repr(self.args[0])
