# -*- coding: utf-8 -*-
from fastcodedog.generation.base.block import Block
from fastcodedog.generation.base.required_import import RequiredImport


class TableArgs(Block):
    def __init__(self, unique_constraints=[]):
        super().__init__('__table_args__', {})
        self.unique_constraints = unique_constraints

        self.add_possible_imports('from sqlalchemy import UniqueConstraint')

    def get_required_imports(self):
        required_import = RequiredImport()
        if self.unique_constraints:
            required_import.add(self.possible_imports['UniqueConstraint'])
        return required_import

    def serialize(self):
        """有点不一样的是，参数最后的逗号,"""
        if self.unique_constraints:
            content = '__table_args__ = ('
            for constraint in self.unique_constraints:
                content += f'UniqueConstraint({", ".join(constraint)}), '
            content = content.strip() + ')'
            return content
        return ''
