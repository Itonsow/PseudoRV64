import load_previous

from ast_nodes import (
    BinaryExpr,
    BinaryOperator,
    BoolLiteral,
    IdentifierExpr,
    IntLiteral,
    UnaryExpr,
    UnaryOperator,
    CallExpr,
    TypeName
)
from patterns import COND, IMM12, POW2, REG, Need, Pattern, Rule, imm12, neg_imm12, pow2,Args, EFFECT


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


###################COND   Dois caminhos
    menor_cond = Rule(    #if (x < y)   -	blt v0, v1, L_true caso seja true, pula para L_ture c n, tem um false logo depois para ir para o otruo caminho
        name="menor_cond",
        result=COND,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.LESS,
            children=(Need(REG), Need(REG)),
        ),
        cost=2,
        action="emitir_menor_cond",
    )

    maior_cond = Rule(
        name="maior_cond",
        result=COND,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.GREATER,
            children=(Need(REG), Need(REG)),
        ),
        cost=2,
        action="emitir_maior_cond",
    )

    menor_igual_cond = Rule( # bge v1, v0, L_true
        name="menor_igual_cond",
        result=COND,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.LESS_EQUAL,
            children=(Need(REG), Need(REG)),
        ),
        cost=2,
        action="emitir_menor_igual_cond",
    )

    maior_igual_cond = Rule(
        name="maior_igual_cond",
        result=COND,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.GREATER_EQUAL,
            children=(Need(REG), Need(REG)),
        ),
        cost=2,
        action="emitir_maior_igual_cond",
    )

    igual_cond = Rule(#	beq v0, v1, L_true
        name="igual_cond",
        result=COND,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.EQUAL,
            children=(Need(REG), Need(REG)),
        ),
        cost=2,
        action="emitir_igual_cond",
    )

    diferente_cond = Rule(               #	bne v0, v1, L_true
        name="diferente_cond",
        result=COND,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.NOT_EQUAL,
            children=(Need(REG), Need(REG)),
        ),
        cost=2,
        action="emitir_diferente_cond",
    )

    literal_booleano_cond = Rule(   #if (bool)
        name="literal_booleano_cond",
        result=COND,
        pattern=Pattern(kind=BoolLiteral),
        cost=1,
        action="emitir_literal_booleano_cond",
    )

    identificador_booleano_cond = Rule(  #if(variavel)
        name="identificador_booleano_cond",
        result=COND,
        pattern=Pattern(
            kind=IdentifierExpr,
            predicate=lambda node: node.metadata.get("type") is TypeName.BOOL,
        ),
        cost=2,
        action="emitir_identificador_booleano_cond",
    )


    negacao_logica_reg = Rule( #seqz v1, v0  # v1 recebe 1 se v0 == 0, senão recebe 0
        name="negacao_logica_reg",
        result=REG,
        pattern=Pattern(
            kind=UnaryExpr,
            operator=UnaryOperator.NOT,
            children=(Need(REG),),
        ),
        cost=1,
        action="emitir_negacao_logica_reg",
    )

    negacao_logica_cond = Rule(
        name="negacao_logica_cond",
        result=COND,
        pattern=Pattern(
            kind=UnaryExpr,
            operator=UnaryOperator.NOT,
            children=(Need(COND),),
        ),
        cost=0,
        action="emitir_negacao_logica_cond",
    )

    e_logico_cond = Rule(  #if (a && b) - print("entrou")
        name="e_logico_cond",
        result=COND,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.LOGICAL_AND,
            children=(Need(COND), Need(COND)),
        ),
        cost=0,
        action="emitir_e_logico_cond",
    )

    e_logico_reg = Rule(  #bool ok = a && b;    - guardar o reultado em um registrador
        name="e_logico_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.LOGICAL_AND,
            children=(Need(COND), Need(COND)),
        ),
        cost=3,
        action="emitir_e_logico_reg",
    )

    ou_logico_cond = Rule(  #if (x || y) print("Pode acessar")
        name="ou_logico_cond",
        result=COND,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.LOGICAL_OR,
            children=(Need(COND), Need(COND)),
        ),
        cost=0,
        action="emitir_ou_logico_cond",
    )

    ou_logico_reg = Rule( #bool acesso = x || y  - print("acesso")
        name="ou_logico_reg",
        result=REG,
        pattern=Pattern(
            kind=BinaryExpr,
            operator=BinaryOperator.LOGICAL_OR,
            children=(Need(COND), Need(COND)),
        ),
        cost=3,
        action="emitir_ou_logico_reg",
    )



######chamada
    chamada_reg = Rule(  #guardar o retorno em um registrador
        name="chamada_reg",
        result=REG,
        pattern=Pattern(
            kind=CallExpr,
            children=(Args(REG),),
            predicate=lambda node: node.metadata.get("type") in (
                TypeName.INT,
                TypeName.BOOL,
            ),
        ),
        cost=1,
        action="emitir_chamada_reg",
    )

    chamada_cond = Rule(  #usar o retorno para decidir para onde pular, usa como um condicao
        name="chamada_cond",
        result=COND,
        pattern=Pattern(
            kind=CallExpr,
            children=(Args(REG),),
            predicate=lambda node: node.metadata.get("type") is TypeName.BOOL,
        ),
        cost=3,
        action="emitir_chamada_cond",
    )

    chamada_effect = Rule(  #executar a função e não retorna nada
        name="chamada_effect",
        result=EFFECT,
        pattern=Pattern(
            kind=CallExpr,
            children=(Args(REG),),
        ),
        cost=1,
        action="emitir_chamada_effect",
    )
    return (identificador,literal_inteiro,soma_reg_reg,literal_imm12,soma_imediato_direita,soma_imediato_esquerda,subtracao_imediato_direita,literal_pow2,multiplicacao_pow2_direita,multiplicacao_pow2_esquerda, subtracao_reg_reg,multiplicacao_reg_reg,divisao_reg_reg,resto_reg_reg,literal_inteiro_negativo,negacao_aritmetica,literal_booleano,        menor_reg_reg,
        maior_reg_reg,
        menor_igual_reg_reg,
        maior_igual_reg_reg,
        igual_reg_reg,
        diferente_reg_reg,
        menor_cond,
        maior_cond,
        menor_igual_cond,
        maior_igual_cond,
        igual_cond,
        diferente_cond,
        e_logico_cond,
        e_logico_reg,
        ou_logico_cond,
        ou_logico_reg,
        literal_booleano_cond,
        identificador_booleano_cond,
        negacao_logica_reg,
        negacao_logica_cond,
        chamada_reg,
        chamada_cond,
        chamada_effect,)