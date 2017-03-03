"""PytSite Routing Rules Map
"""
import re as _re
from typing import Dict as _Dict
from . import _rule, _error

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

_rule_arg_re = _re.compile('<((\w+:)?[\w\-]+)>')
_rule_arg_param_re = _re.compile('\w+:')


class RulesMap:
    """Rules Map
    """

    def __init__(self):
        """Init.
        """
        self._rules = {}  # type: _Dict[str, _rule.Rule]

    def add(self, rule: _rule.Rule):
        """Add a rule.
        """
        # Check if the rule with the same name is already exist
        if rule.name in self._rules:
            raise _error.RuleExists("Rule with name '{}' is already added".format(rule.name))

        # Add a rule
        self._rules[rule.name] = rule

    def get(self, name: str):
        """Get rule by name
        """
        try:
            return self._rules[name]
        except KeyError:
            raise _error.RuleNotFound("Rule with name '{}' is not found".format(name))

    def match(self, path: str, method: str = 'GET') -> _rule.Rule:
        """Match rule against a path.
        """
        method = method.upper()

        for rule in self._rules.values():
            m = rule.regex.match(path)
            if not m or method not in rule.methods:
                continue

            # Fill rule's arguments
            for group_n, group_i in rule.regex.groupindex.items():
                rule.args[group_n] = m.group(group_n)

            return rule

        raise _error.RuleNotFound("No rules match the path '{}' against method '{}'".format(path, method))

    def path(self, name: str, args: dict = None) -> str:
        """Build path for a rule.
        """

        def repl(match):
            nonlocal rule

            arg_k = _rule_arg_param_re.sub('', match.group(1))

            if arg_k in args:
                return str(args.pop(arg_k))
            elif arg_k in rule.defaults:
                return str(rule.defaults[arg_k])
            else:
                raise _error.RulePathBuildError("Argument '{}' for rule '{}' is not provided".format(arg_k, name))

        if args is None:
            args = {}

        rule = self.get(name)
        path = _rule_arg_re.sub(repl, rule.path)

        # Add remaining args as query string
        if args:
            path += '?' + '&'.join(['{}={}'.format(k, v) for k, v in args.items()])

        return path
