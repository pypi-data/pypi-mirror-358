"""
Parser for BIDS Query Language (BIQL)

Converts tokenized BIQL queries into Abstract Syntax Trees (AST).
"""

from typing import List

from .ast_nodes import *
from .lexer import BIQLLexer, Token, TokenType


class BIQLParseError(Exception):
    """Exception raised for BIQL parsing errors"""

    pass


class BIQLParser:
    """Parses BIQL queries into AST"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

    @classmethod
    def from_string(cls, query: str) -> "BIQLParser":
        """Create parser from query string"""
        lexer = BIQLLexer(query)
        tokens = lexer.tokenize()
        return cls(tokens)

    def parse(self) -> Query:
        """Parse tokens into Query AST"""
        # Optional SELECT clause
        select_clause = None
        if self._current_token_type() == TokenType.SELECT:
            select_clause = self._parse_select()

        # WHERE clause (optional WHERE keyword)
        where_clause = None
        if self._current_token_type() == TokenType.WHERE:
            self._consume(TokenType.WHERE)

        if (
            self._current_token_type() != TokenType.EOF
            and not self._is_clause_keyword()
        ):
            condition = self._parse_expression()
            where_clause = WhereClause(condition)

        # GROUP BY
        group_by = None
        if self._current_token_type() == TokenType.GROUP:
            group_by = self._parse_group_by()

        # HAVING
        having = None
        if self._current_token_type() == TokenType.HAVING:
            self._consume(TokenType.HAVING)
            having = self._parse_expression()

        # ORDER BY
        order_by = None
        if self._current_token_type() == TokenType.ORDER:
            order_by = self._parse_order_by()

        # FORMAT
        format_type = None
        if self._current_token_type() == TokenType.FORMAT:
            self._consume(TokenType.FORMAT)
            format_type = self._consume(TokenType.IDENTIFIER).value

        return Query(
            select_clause, where_clause, group_by, having, order_by, format_type
        )

    def _current_token(self) -> Token:
        """Get current token"""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return self.tokens[-1]  # EOF

    def _current_token_type(self) -> TokenType:
        """Get current token type"""
        return self._current_token().type

    def _consume(self, expected: TokenType) -> Token:
        """Consume token of expected type or raise error"""
        token = self._current_token()
        if token.type != expected:
            raise BIQLParseError(
                f"Expected {expected}, got {token.type} at position {token.position}"
            )
        self.position += 1
        return token

    def _is_clause_keyword(self) -> bool:
        """Check if current token is a clause keyword"""
        return self._current_token_type() in [
            TokenType.GROUP,
            TokenType.HAVING,
            TokenType.ORDER,
            TokenType.FORMAT,
        ]

    def _parse_select(self) -> SelectClause:
        """Parse SELECT clause"""
        self._consume(TokenType.SELECT)

        # Check for DISTINCT
        distinct = False
        if self._current_token_type() == TokenType.DISTINCT:
            self._consume(TokenType.DISTINCT)
            distinct = True

        items = []

        if self._current_token_type() == TokenType.STAR:
            self._consume(TokenType.STAR)
            items.append(("*", None))
        else:
            while True:
                # Handle function calls or regular identifiers
                if self._current_token_type() in [
                    TokenType.COUNT,
                    TokenType.AVG,
                    TokenType.MAX,
                    TokenType.MIN,
                    TokenType.SUM,
                ]:
                    # This is a function call
                    func_name = self._consume(self._current_token_type()).value
                    self._consume(TokenType.LPAREN)

                    # Handle function arguments
                    if self._current_token_type() == TokenType.STAR:
                        self._consume(TokenType.STAR)
                        func_expr = f"{func_name}(*)"
                    else:
                        arg = self._parse_identifier_path()
                        func_expr = f"{func_name}({arg})"

                    self._consume(TokenType.RPAREN)
                    expr = func_expr
                else:
                    # Regular identifier path
                    expr = self._parse_identifier_path()

                alias = None
                if self._current_token_type() == TokenType.AS:
                    self._consume(TokenType.AS)
                    alias = self._consume(TokenType.IDENTIFIER).value

                items.append((expr, alias))

                if self._current_token_type() != TokenType.COMMA:
                    break
                self._consume(TokenType.COMMA)

        return SelectClause(items, distinct)

    def _parse_expression(self) -> Expression:
        """Parse expression with precedence"""
        return self._parse_or()

    def _parse_or(self) -> Expression:
        """Parse OR expressions (lowest precedence)"""
        left = self._parse_and()

        while self._current_token_type() == TokenType.OR:
            op = self._consume(TokenType.OR)
            right = self._parse_and()
            left = BinaryOp(left, op.type, right)

        return left

    def _parse_and(self) -> Expression:
        """Parse AND expressions"""
        left = self._parse_not()

        # Handle implicit AND (when expressions are adjacent)
        while self._current_token_type() == TokenType.AND or (
            self._current_token_type()
            in [TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.NOT]
            and not self._is_clause_keyword()
        ):

            if self._current_token_type() == TokenType.AND:
                self._consume(TokenType.AND)
            # Implicit AND
            right = self._parse_not()
            left = BinaryOp(left, TokenType.AND, right)

        return left

    def _parse_not(self) -> Expression:
        """Parse NOT expressions"""
        if self._current_token_type() == TokenType.NOT:
            op = self._consume(TokenType.NOT)
            operand = self._parse_not()
            return UnaryOp(op.type, operand)
        return self._parse_comparison()

    def _parse_comparison(self) -> Expression:
        """Parse comparison expressions"""
        left = self._parse_term()

        if self._current_token_type() in [
            TokenType.EQ,
            TokenType.NEQ,
            TokenType.GT,
            TokenType.LT,
            TokenType.GTE,
            TokenType.LTE,
            TokenType.MATCH,
            TokenType.IN,
            TokenType.LIKE,
        ]:
            op = self._consume(self._current_token_type())
            right = self._parse_term()
            return BinaryOp(left, op.type, right)

        return left

    def _parse_term(self) -> Expression:
        """Parse terminal expressions"""
        # Parentheses
        if self._current_token_type() == TokenType.LPAREN:
            self._consume(TokenType.LPAREN)
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN)
            return expr

        # Function calls
        if self._current_token_type() in [
            TokenType.COUNT,
            TokenType.AVG,
            TokenType.MAX,
            TokenType.MIN,
            TokenType.SUM,
        ]:
            return self._parse_function_call()

        # Range
        if self._current_token_type() == TokenType.LBRACKET:
            return self._parse_range_or_list()

        # Field access or literal
        if self._current_token_type() == TokenType.IDENTIFIER:
            return self._parse_field_or_literal()

        # Wildcard pattern (starts with *)
        if self._current_token_type() == TokenType.STAR:
            return self._parse_wildcard_pattern()

        # String literal
        if self._current_token_type() == TokenType.STRING:
            token = self._consume(TokenType.STRING)
            return Literal(token.value)

        # Number literal
        if self._current_token_type() == TokenType.NUMBER:
            token = self._consume(TokenType.NUMBER)
            return Literal(token.value)

        raise BIQLParseError(f"Unexpected token: {self._current_token()}")

    def _parse_field_or_literal(self) -> Expression:
        """Parse field access expression or wildcard pattern"""
        first_part = self._consume(TokenType.IDENTIFIER).value

        # Check if this might be part of a wildcard pattern
        if self._current_token_type() in [TokenType.STAR, TokenType.QUESTION]:
            # This is a wildcard pattern starting with identifier
            pattern = first_part
            while self._current_token_type() in [
                TokenType.STAR,
                TokenType.IDENTIFIER,
                TokenType.QUESTION,
            ]:
                token = self._consume(self._current_token_type())
                pattern += token.value
            return Literal(pattern)

        # Handle dots for metadata/participants access
        parts = [first_part]
        while self._current_token_type() == TokenType.DOT:
            self._consume(TokenType.DOT)
            parts.append(self._consume(TokenType.IDENTIFIER).value)

        # Return field access
        if len(parts) > 1:
            return FieldAccess(parts[0], parts[1:])
        return FieldAccess(parts[0])

    def _parse_range_or_list(self) -> Expression:
        """Parse range [start:end] or list [item1, item2, ...]"""
        self._consume(TokenType.LBRACKET)

        # First element
        first = self._parse_expression()

        # Check if it's a range (has colon)
        if self._current_token_type() == TokenType.COLON:
            self._consume(TokenType.COLON)
            end = self._parse_expression()
            self._consume(TokenType.RBRACKET)
            return Range(first, end)

        # It's a list
        items = [first]
        while self._current_token_type() == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            items.append(self._parse_expression())

        self._consume(TokenType.RBRACKET)
        return ListExpression(items)

    def _parse_function_call(self) -> Expression:
        """Parse function call expression"""
        name = self._consume(self._current_token_type()).value
        self._consume(TokenType.LPAREN)

        args = []
        if self._current_token_type() != TokenType.RPAREN:
            if self._current_token_type() == TokenType.STAR:
                self._consume(TokenType.STAR)
                args.append(Literal("*"))
            else:
                args.append(self._parse_expression())
                while self._current_token_type() == TokenType.COMMA:
                    self._consume(TokenType.COMMA)
                    args.append(self._parse_expression())

        self._consume(TokenType.RPAREN)
        return FunctionCall(name, args)

    def _parse_group_by(self) -> List[str]:
        """Parse GROUP BY clause"""
        self._consume(TokenType.GROUP)
        self._consume(TokenType.BY)

        fields = []
        fields.append(self._consume(TokenType.IDENTIFIER).value)

        while self._current_token_type() == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            fields.append(self._consume(TokenType.IDENTIFIER).value)

        return fields

    def _parse_order_by(self) -> List[Tuple[str, str]]:
        """Parse ORDER BY clause"""
        self._consume(TokenType.ORDER)
        self._consume(TokenType.BY)

        items = []
        field = self._consume(TokenType.IDENTIFIER).value
        direction = "ASC"

        if self._current_token_type() in [TokenType.ASC, TokenType.DESC]:
            direction = self._consume(self._current_token_type()).value

        items.append((field, direction))

        while self._current_token_type() == TokenType.COMMA:
            self._consume(TokenType.COMMA)
            field = self._consume(TokenType.IDENTIFIER).value
            direction = "ASC"

            if self._current_token_type() in [TokenType.ASC, TokenType.DESC]:
                direction = self._consume(self._current_token_type()).value

            items.append((field, direction))

        return items

    def _parse_wildcard_pattern(self) -> Expression:
        """Parse wildcard pattern like *bold* or *text"""
        pattern = ""

        # Consume tokens until we hit a non-pattern token
        while self._current_token_type() in [
            TokenType.STAR,
            TokenType.IDENTIFIER,
            TokenType.QUESTION,
        ]:
            token = self._consume(self._current_token_type())
            pattern += token.value

        return Literal(pattern)

    def _parse_identifier_path(self) -> str:
        """Parse dot-separated identifier path"""
        parts = [self._consume(TokenType.IDENTIFIER).value]

        while self._current_token_type() == TokenType.DOT:
            self._consume(TokenType.DOT)
            parts.append(self._consume(TokenType.IDENTIFIER).value)

        return ".".join(parts)
