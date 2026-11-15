"""Reconhecimento de padrões e seleção de regras por menor custo."""

from patterns import Args, Choice, Need, SelectionTable, children
from ast_nodes import CallExpr



class Selector:
    def __init__(self, rules):
        self.rules = tuple(rules)

    def analyze(self, expr):
        table = SelectionTable()
        self._visit(expr, table)
        return table

    def _visit(self, node, table):
        for child in children(node):
            self._visit(child, table)

        for rule in self.rules:
            subproblems = self._match(node, rule.pattern)
            if subproblems is None:
                continue

            total_cost = self._cost(rule, subproblems, table)
            if total_cost is None:
                continue

            best = table.lookup(node, rule.result)
            if best is None or total_cost < best.cost:
                choice = Choice(total_cost, rule, tuple(subproblems))
                table.put(node, rule.result, choice)

    def _cost(self, rule, subproblems, table):
        total = rule.cost

        for child, result in subproblems:
            choice = table.lookup(child, result)
            if choice is None:
                return None
            total += choice.cost

        return total

    def _match(self, node, pattern):
        if isinstance(pattern, Need):
            return [(node, pattern.result)]

        if pattern.kind is not None and not isinstance(node, pattern.kind):
            return None

        if pattern.operator is not None:
            if getattr(node, "operator", None) != pattern.operator:
                return None

        if pattern.predicate is not None:
            if not pattern.predicate(node):
                return None
            if not pattern.children:
                return []

        node_children = children(node)

        if len(pattern.children) == 1 and isinstance(pattern.children[0], Args):
            if not isinstance(node, CallExpr):
                return None
            result = pattern.children[0].result
            return [(argument, result) for argument in node_children]

        if len(node_children) != len(pattern.children):
            return None

        subproblems = []
        for child, child_pattern in zip(node_children, pattern.children):
            child_subproblems = self._match(child, child_pattern)
            if child_subproblems is None:
                return None
            subproblems.extend(child_subproblems)

        return subproblems