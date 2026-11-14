import load_previous

from ast_nodes import (
    BinaryExpr,
    BinaryOperator,
    BoolLiteral,
    IdentifierExpr,
    IntLiteral,
    UnaryExpr,
    UnaryOperator,
)
from patterns import COND, IMM12, POW2, REG, Need, Pattern, Rule, imm12, neg_imm12, pow2


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

    literal_imm12 = Rule( #verifica se é um imm12
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

    soma_imediato_esquerda = Rule( #5 + x    -- addi v2, v0, 5
        name="soma_imediato_esquerda",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.ADD,
            children=(Need(IMM12), Need(REG)),
        ),
        cost=1,
        action="emitir_soma_imediato_esquerda",
    )

    subtracao_imediato_direita = Rule(  #x - 20   - -addi v2, v0, -20
        name="subtracao_imediato_direita",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.SUBTRACT,
            children=(Need(REG), Pattern(predicate=neg_imm12)),
        ),
        cost=1,
        action="emitir_subtracao_imediato_direita",
    )

    literal_pow2 = Rule(  #fornece o expoente  -----x * 8  ,  devolve 3
        name="literal_pow2",
        result=POW2,  #registra que o nó pode atender a uma regra que pede uma potência de dois.
        pattern=Pattern(predicate=pow2),
        cost=0,  #essa regra so disponibiliza o expoente
        action="emitir_literal_pow2",
    )

    multiplicacao_pow2_direita = Rule(  #usa o expoente calculado pelo POW2 pra multiplicar x
        name="multiplicacao_pow2_direita",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.MULTIPLY,
            children=(Need(REG), Need(POW2)),  #Need(POW2) fornece 3  # slli v2, v0, 3     
        ),
        cost=1,
        action="emitir_multiplicacao_pow2_direita",
    )

    multiplicacao_pow2_esquerda = Rule(
        name="multiplicacao_pow2_esquerda",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.MULTIPLY,
            children=(Need(POW2), Need(REG)),  #slli v2, v0, 3
        ),
        cost=1,
        action="emitir_multiplicacao_pow2_esquerda",
    )

    subtracao_reg_reg = Rule(  #x - y     --sub v2, v0, v1
        name="subtracao_reg_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.SUBTRACT,
            children=(Need(REG), Need(REG)),
        ),
        cost=1,
        action="emitir_subtracao_reg_reg",
    )

    multiplicacao_reg_reg = Rule(  #x * y     ---mul v2, v0, v1
        name="multiplicacao_reg_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.MULTIPLY,
            children=(Need(REG), Need(REG)),
        ),
        cost=1,
        action="emitir_multiplicacao_reg_reg",
    )

    divisao_reg_reg = Rule( #x / y     -div v2, v0, v1
        name="divisao_reg_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.DIVIDE,
            children=(Need(REG), Need(REG)),
        ),
        cost=1,
        action="emitir_divisao_reg_reg",
    )

    resto_reg_reg = Rule( #x % y         -rem v2, v0, v1
        name="resto_reg_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.REMAINDER,
            children=(Need(REG), Need(REG)),
        ),
        cost=1,
        action="emitir_resto_reg_reg",
    )

    literal_inteiro_negativo = Rule(  #li v1, -5
        name="literal_inteiro_negativo",
        result=REG,
        pattern=Pattern(
            kind=UnaryExpr,
            operator=UnaryOperator.NEGATE,
            children=(Pattern(kind=IntLiteral),),
        ),
        cost=1,
        action="emitir_literal_inteiro_negativo",
    )

    negacao_aritmetica = Rule(       #neg v1, v0
        name="negacao_aritmetica",
        result=REG,
        pattern=Pattern(
            kind=UnaryExpr,
            operator=UnaryOperator.NEGATE,
            children=(Need(REG),),
        ),
        cost=1,
        action="emitir_negacao_aritmetica",
    )

    literal_booleano = Rule(       
        name="literal_booleano",
        result=REG,
        pattern=Pattern(kind=BoolLiteral),
        cost=1,
        action="emitir_literal_booleano",
    )

    menor_reg_reg = Rule(    #x < y #	Slt ve se x é menor que y
        name="menor_reg_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.LESS,
            children=(Need(REG), Need(REG)),
        ),
        cost=1,
        action="emitir_menor_reg_reg",
    )

    maior_reg_reg = Rule(   #x > y #	Slt ve se y é menor que x
        name="maior_reg_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.GREATER,
            children=(Need(REG), Need(REG)),
        ),
        cost=1,
        action="emitir_maior_reg_reg",
    )
############################
#logica do menor e maior igual
    #A única situação em que x <= y é falso é quando y < x, ent o fazemos o Seqz inverter o resultado 
#mesma coisa para x >= y
    menor_igual_reg_reg = Rule(     # x <= y ,,,, Slt verifica y < x e depois o Seqz inverte o resultado
        name="menor_igual_reg_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.LESS_EQUAL,
            children=(Need(REG), Need(REG)),
        ),
        cost=2,  #por isso custo 2, verifica e dps inverte
        action="emitir_menor_igual_reg_reg",
    )

    maior_igual_reg_reg = Rule(    # x >= y ,,,, Slt verifica x < y e depois o Seqz inverte o resultado
        name="maior_igual_reg_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.GREATER_EQUAL,
            children=(Need(REG), Need(REG)),
        ),
        cost=2,
        action="emitir_maior_igual_reg_reg",
    )

    igual_reg_reg = Rule(  #x == y     - Xor = zero quando os valores são iguais, depois Seqz ve c se deu zero
        name="igual_reg_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.EQUAL,
            children=(Need(REG), Need(REG)),
        ),
        cost=2,
        action="emitir_igual_reg_reg",
    )

    diferente_reg_reg = Rule(  #x != y   -Xor = valor diferente de zero quando os valores são diferentes, dps Snez verifica isso
        name="diferente_reg_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.NOT_EQUAL,
            children=(Need(REG), Need(REG)),
        ),
        cost=2,
        action="emitir_diferente_reg_reg",
    )
    return (identificador,literal_inteiro,soma_reg_reg,literal_imm12,soma_imediato_direita,soma_imediato_esquerda,subtracao_imediato_direita,literal_pow2,multiplicacao_pow2_direita,multiplicacao_pow2_esquerda, subtracao_reg_reg,multiplicacao_reg_reg,divisao_reg_reg,resto_reg_reg,literal_inteiro_negativo,negacao_aritmetica,literal_booleano,)