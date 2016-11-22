# -*- coding: utf-8 -*-
"""
    StepPy
    :copyright: (c) 2016 by Yann Gravrand.
    :license: BSD, see LICENSE for more details.
"""

class Rule(object):

    def __init__(self, **criteria):
        self.criteria = criteria
        self.matched_message = None
        # print('Rule registered: %s' % self.criteria)

    def matches(self, msg):
        matched = 0
        for name, expected_value in self.criteria.items():
            val = getattr(msg, name.replace('type_', 'type'), None)
            # print('%s -- %s -- %s' % (name, val, expected_value))
            if val is not None:
                if expected_value in ('*', val) or \
                   (isinstance(expected_value, str) and \
                    expected_value.startswith('!') and \
                    expected_value[1:] != str(val)):
                    matched += 1
            else:
                pass  # print('msg.%s does not exist' % name)
        return matched == len(self.criteria)

    def run(self, msg):
        match = self.matches(msg)
        self.matched_message = msg if match else None
        return match

    @property
    def matched(self):
        return self.matched_message is not None

    def __repr__(self):
        return '{Rule matched_msg=%s crit=%s}' % (self.matched_message, self.criteria)


class RulesChain(object):

    def __init__(self, *rules):
        self.rules = list(rules)
        self.matched_rule_index = -1

    def add_rule(self, rule):
        self.rules.append(rule)

    def run(self, func, msg):
        if self.full_match:
            # Last run was a full match: reset
            self.reset()

        for i, rule in enumerate(self.rules):
            if i <= self.matched_rule_index:
                # Rule already matched
                continue
            matches = rule.run(msg)
            if matches:
                self.matched_rule_index = i
                if i == len(self.rules) - 1:
                    # All rules have been matched
                    func([rule.matched_message for rule in self.rules], self.rules)
                    return True, False, ('*' * i) + '!'
                return True, True, '*' * (i+1)
            else:
                # No more match
                break
        self.reset()
        return False, False, ''

    def reset(self):
        self.matched_rule_index = -1

    @property
    def has_matched_rule(self):
        return self.matched_rule_index > -1

    @property
    def partial_match(self):
        return self.has_matched_rule and self.matched_rule_index < len(self.rules) - 1

    @property
    def full_match(self):
        return self.has_matched_rule and self.matched_rule_index == len(self.rules) - 1

    @property
    def matched_messages(self):
        return [rule.matched_message for rule in self.rules if rule.matched]
