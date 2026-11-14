import load_previous

from ast_nodes import BinaryExpr, BinaryOperator, IdentifierExpr, IntLiteral
from patterns import IMM12, REG, Need, Pattern, Rule, imm12


def catalogue():
    identificador = Rule(
        name="identificador",
        result=REG,
        pattern=Pattern(kind=IdentifierExpr),
        cost=0,
        action="emitir_identificador",
    )

    literal_inteiro = Rule(  #li v2, 5
        name="literal_inteiro",
        result=REG,
        pattern=Pattern(kind=IntLiteral),
        cost=1,
        action="emitir_literal_inteiro",
    )

    soma_reg_reg = Rule(  #add v2, v0, v1
        name="soma_reg_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.ADD,
            children=(Need(REG), Need(REG)),
        ),
        cost=1,
        action="emitir_soma_reg_reg",
    )

    literal_imm12 = Rule(
        name="literal_imm12",
        result=IMM12,
        pattern=Pattern(predicate=imm12),
        cost=0,
        action="emitir_literal_imm12",
    )

    soma_imediato_direita = Rule( #  addi v2, v0, 5
        name="soma_imediato_direita",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.ADD,
            children=(Need(REG), Need(IMM12)), #inteiro no lado direito
        ),
        cost=1,
        action="emitir_soma_imediato_direita",
    )


    return (identificador, literal_inteiro, soma_reg_reg)