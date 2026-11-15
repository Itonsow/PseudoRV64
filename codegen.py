"""Geração de comandos e expressões em pseudoRV64."""

import load_previous

from catalogue import catalogue
from ir import (
    Add, Addi, Beq, Bge, Blt, Bne, Bnez, Context, Div, FunctionIR,
    Jump, Li, Mul, Neg, ProgramIR, Rem, Seqz, Slli, Slt, Snez, Sub, Xor,
)
from patterns import signed_literal
from selector import Selector
from ir import (
    Context,
    ProgramIR,
    FunctionIR,
    Move,
    Param,
    Return,
    PrintInt,
    PrintBool,
    PrintString,
    LabelInstr,
    Jump,
    Bnez,
    Call,
    Seqz,
    Li,
)
from ast_nodes import (
    TypeName,
    Block,
    VarDecl,
    Assignment,
    ReturnStmt,
    PrintStmt,
    StringLiteral,
    IfStmt,
    WhileStmt,
    CallStmt,
)
from patterns import REG, COND, EFFECT


class CodeGenerator:
    """Coordene comandos ad hoc e seleção de expressões com DP."""

    def generate(self, program): #traduz o programa inteiro, uma FunctionIR p cada funcao
        """Traduza funções e comandos. Selecione expressões com DP."""
        #raise NotImplementedError("implemente CodeGenerator.generate")
        programa_ir = ProgramIR() #cria um novo a cada chamada, pra poder reutilizar o gerador

        for funcao in program.functions:
            simbolo = funcao.metadata["symbol"] #pega o simbolo da funcao q o resolvedor de nomes guardou
            funcao_ir = FunctionIR(simbolo) #cria a funcao da IR
            programa_ir.functions.append(funcao_ir)
            self.contexto = Context(funcao_ir, programa_ir) #cada funcao tem seus proprios vregs e labels

            # emite um param p cada parametro, no inicio e na ordem da assinatura
            for indice, parametro in enumerate(funcao.parameters):
                registrador = self.contexto.variable(parametro.metadata["symbol"]) #vreg do parametro
                funcao_ir.instructions.append(Param(registrador, indice, origin=parametro.span))

            self.statement(funcao.body) #traduz o corpo da funcao

            # funcao void tem q terminar com return, msm q o corpo n tenha return
            if simbolo.type is TypeName.VOID:
                funcao_ir.instructions.append(Return(None, origin=funcao.span))

        return programa_ir

    def expression(self, node, result_class, true_label=None, false_label=None):
        selector = Selector(catalogue())
        table = selector.analyze(node)
        return self._emit(node, result_class, table, true_label, false_label)

    def _emit(self, node, result_class, table, true_label=None, false_label=None):
        choice = table.lookup(node, result_class)
        if choice is None:
            raise ValueError(f"Sem regra para {result_class.name} em {node.span}")

        action = getattr(self, choice.rule.action)
        return action(node, table, choice.subproblems, true_label, false_label)

    def _emitir_dois_filhos(self, table, subproblems):
        (left_node, left_class), (right_node, right_class) = subproblems

        left = self._emit(left_node, left_class, table)
        right = self._emit(right_node, right_class, table)
        return left, right

    def _emitir_valor(self, node, instrucao, *operandos):
        dst = self.context.temp()
        self.context.emit(instrucao(dst, *operandos, origin=node.span))
        return dst

    def emitir_identificador(self, node, table, subproblems, true_label, false_label):
        symbol = node.metadata["symbol"]
        return self.context.variable(symbol)

    def emitir_literal_inteiro(self, node, table, subproblems, true_label, false_label):
        return self._emitir_valor(node, Li, node.value)

    def emitir_literal_inteiro_negativo(
        self, node, table, subproblems, true_label, false_label
    ):
        return self._emitir_valor(node, Li, signed_literal(node))

    def emitir_literal_booleano(self, node, table, subproblems, true_label, false_label):
        return self._emitir_valor(node, Li, int(node.value))

    def emitir_literal_imm12(self, node, table, subproblems, true_label, false_label):
        return signed_literal(node)

    def emitir_literal_pow2(self, node, table, subproblems, true_label, false_label):
        value = signed_literal(node)
        return value.bit_length() - 1

    def emitir_negacao_aritmetica(self, node, table, subproblems, true_label, false_label):
        (operand, operand_class), = subproblems
        src = self._emit(operand, operand_class, table)
        return self._emitir_valor(node, Neg, src)

    def emitir_soma_imediato_direita(
        self, node, table, subproblems, true_label, false_label
    ):
        src, imm = self._emitir_dois_filhos(table, subproblems)
        return self._emitir_valor(node, Addi, src, imm)

    def emitir_soma_imediato_esquerda(
        self, node, table, subproblems, true_label, false_label
    ):
        imm, src = self._emitir_dois_filhos(table, subproblems)
        return self._emitir_valor(node, Addi, src, imm)

    def emitir_subtracao_imediato_direita(
        self, node, table, subproblems, true_label, false_label
    ):
        (left_node, left_class), = subproblems
        src = self._emit(left_node, left_class, table)
        imm = -signed_literal(node.right)
        return self._emitir_valor(node, Addi, src, imm)

    def emitir_multiplicacao_pow2_direita(
        self, node, table, subproblems, true_label, false_label
    ):
        src, shift = self._emitir_dois_filhos(table, subproblems)
        return self._emitir_valor(node, Slli, src, shift)

    def emitir_multiplicacao_pow2_esquerda(
        self, node, table, subproblems, true_label, false_label
    ):
        shift, src = self._emitir_dois_filhos(table, subproblems)
        return self._emitir_valor(node, Slli, src, shift)

    def emitir_soma_reg_reg(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        return self._emitir_valor(node, Add, left, right)

    def emitir_subtracao_reg_reg(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        return self._emitir_valor(node, Sub, left, right)

    def emitir_multiplicacao_reg_reg(
        self, node, table, subproblems, true_label, false_label
    ):
        left, right = self._emitir_dois_filhos(table, subproblems)
        return self._emitir_valor(node, Mul, left, right)

    def emitir_divisao_reg_reg(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        return self._emitir_valor(node, Div, left, right)

    def emitir_resto_reg_reg(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        return self._emitir_valor(node, Rem, left, right)

    def emitir_menor_reg_reg(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        return self._emitir_valor(node, Slt, left, right)

    def emitir_maior_reg_reg(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        return self._emitir_valor(node, Slt, right, left)

    def emitir_menor_igual_reg_reg(
        self, node, table, subproblems, true_label, false_label
    ):
        left, right = self._emitir_dois_filhos(table, subproblems)
        comparacao = self._emitir_valor(node, Slt, right, left)
        return self._emitir_valor(node, Seqz, comparacao)

    def emitir_maior_igual_reg_reg(
        self, node, table, subproblems, true_label, false_label
    ):
        left, right = self._emitir_dois_filhos(table, subproblems)
        comparacao = self._emitir_valor(node, Slt, left, right)
        return self._emitir_valor(node, Seqz, comparacao)

    def emitir_igual_reg_reg(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        diferenca = self._emitir_valor(node, Xor, left, right)
        return self._emitir_valor(node, Seqz, diferenca)

    def emitir_diferente_reg_reg(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        diferenca = self._emitir_valor(node, Xor, left, right)
        return self._emitir_valor(node, Snez, diferenca)

    def _emitir_desvio(self, node, instrucao, true_label, false_label, *operandos):
        self.context.emit(instrucao(*operandos, true_label, origin=node.span))
        self.context.emit(Jump(false_label, origin=node.span))

    def emitir_menor_cond(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        self._emitir_desvio(node, Blt, true_label, false_label, left, right)

    def emitir_maior_cond(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        self._emitir_desvio(node, Blt, true_label, false_label, right, left)

    def emitir_menor_igual_cond(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        self._emitir_desvio(node, Bge, true_label, false_label, right, left)

    def emitir_maior_igual_cond(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        self._emitir_desvio(node, Bge, true_label, false_label, left, right)

    def emitir_igual_cond(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        self._emitir_desvio(node, Beq, true_label, false_label, left, right)

    def emitir_diferente_cond(self, node, table, subproblems, true_label, false_label):
        left, right = self._emitir_dois_filhos(table, subproblems)
        self._emitir_desvio(node, Bne, true_label, false_label, left, right)

    def emitir_literal_booleano_cond(
        self, node, table, subproblems, true_label, false_label
    ):
        destino = true_label if node.value else false_label
        self.context.emit(Jump(destino, origin=node.span))

    def emitir_identificador_booleano_cond(
        self, node, table, subproblems, true_label, false_label
    ):
        symbol = node.metadata["symbol"]
        src = self.context.variable(symbol)
        self._emitir_desvio(node, Bnez, true_label, false_label, src)

    def statement(self, node): #olha o tipo do comando e decide oq emitir
        """Traduza um comando ad hoc."""
        #raise NotImplementedError("implemente comandos")

        #caso 1 bloco: { ... }
        if isinstance(node, Block):
            for comando in node.statements: #percorre os comandos na ordem
                self.statement(comando)

        #caso 2 declaracao: int x = 10;
        elif isinstance(node, VarDecl):
            if node.initializer is not None: #sem inicializador n emite nada
                valor = self.expression(node.initializer, REG) #avalia primeiro
                variavel = self.contexto.variable(node.metadata["symbol"]) #vreg da variavel
                self.contexto.emit(Move(variavel, valor, origin=node.span)) #dps escreve na variavel

        #caso 3 atribuicao: x = x + 1;
        elif isinstance(node, Assignment):
            valor = self.expression(node.value, REG) #avalia o lado direito antes de escrever
            variavel = self.contexto.variable(node.target.metadata["symbol"]) #vreg do alvo
            self.contexto.emit(Move(variavel, valor, origin=node.span))

        #caso 4 chamada como comando: registrar(1, 2);
        elif isinstance(node, CallStmt):
            self.expression(node.call, EFFECT) #o resultado eh descartado

        #caso 5 if (cond) { ... } else { ... }
        elif isinstance(node, IfStmt):
            rotulo_then = self.contexto.label()
            rotulo_fim = self.contexto.label()
            if node.else_block is not None: #se tiver else, a condicao falsa vai p ele
                rotulo_else = self.contexto.label()
            else: #se n tiver else, a condicao falsa vai direto pro fim
                rotulo_else = rotulo_fim

            self.expression(node.condition, COND, rotulo_then, rotulo_else) #condicao como desvio

            self.contexto.emit(LabelInstr(rotulo_then))
            self.statement(node.then_block)

            if node.else_block is not None:
                self.contexto.emit(Jump(rotulo_fim, origin=node.span)) #dps do then pula o else
                self.contexto.emit(LabelInstr(rotulo_else))
                self.statement(node.else_block)

            self.contexto.emit(LabelInstr(rotulo_fim)) #continuacao do if

        #caso 6 while (cond) { ... }
        elif isinstance(node, WhileStmt):
            rotulo_teste = self.contexto.label()
            rotulo_corpo = self.contexto.label()
            rotulo_saida = self.contexto.label()

            self.contexto.emit(LabelInstr(rotulo_teste)) #volta aqui a cada repeticao
            self.expression(node.condition, COND, rotulo_corpo, rotulo_saida) #c for falso sai do laco

            self.contexto.emit(LabelInstr(rotulo_corpo))
            self.statement(node.body)
            self.contexto.emit(Jump(rotulo_teste, origin=node.span)) #salto de volta pro teste

            self.contexto.emit(LabelInstr(rotulo_saida))

        #caso 7 return; ou return x;
        elif isinstance(node, ReturnStmt):
            if node.value is None: #return sem valor, funcao void
                self.contexto.emit(Return(None, origin=node.span))
            else:
                valor = self.expression(node.value, REG)
                self.contexto.emit(Return(valor, origin=node.span))

        #caso 8 print("a", x, true);
        elif isinstance(node, PrintStmt):
            for item in node.items: #cada item eh impresso por completo antes do proximo
                if isinstance(item, StringLiteral): #string vai pro pool, n usa vreg
                    texto = self.contexto.string(item.value)
                    self.contexto.emit(PrintString(texto, origin=item.span))
                else: #expressao, escolhe o print pelo tipo anotado
                    valor = self.expression(item, REG)
                    if item.metadata["type"] is TypeName.BOOL:
                        self.contexto.emit(PrintBool(valor, origin=item.span))
                    else:
                        self.contexto.emit(PrintInt(valor, origin=item.span))

            quebra = self.contexto.string("\n") #reutiliza a msm entrada "\n" do pool
            self.contexto.emit(PrintString(quebra, origin=node.span)) #uma quebra no final de cada print

        else: #se n for nenhum dos acima, da erro
            raise ValueError(f"comando desconhecido em {node.span}")

    # acoes de chamadas
    # todas recebem o no, a escolha do seletor e os destinos (os destinos so sao usados em COND)

    def avaliar_argumentos(self, no): #avalia os argumentos da esquerda p direita
        argumentos = []
        for argumento in no.arguments: #ja vem na ordem em q aparecem na chamada
            argumentos.append(self.expression(argumento, REG)) #cada argumento vira um vreg
        return argumentos

    def emitir_chamada_reg(self, no, escolha, rotulo_verdadeiro=None, rotulo_falso=None): #chamada q devolve valor
        argumentos = self.avaliar_argumentos(no)
        destino = self.contexto.temp() #vreg q recebe o retorno
        self.contexto.emit(Call(destino, no.metadata["symbol"], argumentos, origin=no.span))
        return destino

    def emitir_chamada_effect(self, no, escolha, rotulo_verdadeiro=None, rotulo_falso=None): #chamada com resultado descartado
        argumentos = self.avaliar_argumentos(no)
        self.contexto.emit(Call(None, no.metadata["symbol"], argumentos, origin=no.span)) #dst None, n guarda nada

    def emitir_chamada_cond(self, no, escolha, rotulo_verdadeiro=None, rotulo_falso=None): #chamada bool usada como condicao
        argumentos = self.avaliar_argumentos(no)
        destino = self.contexto.temp()
        self.contexto.emit(Call(destino, no.metadata["symbol"], argumentos, origin=no.span))
        self.contexto.emit(Bnez(destino, rotulo_verdadeiro, origin=no.span)) #c deu true vai pro verdadeiro
        self.contexto.emit(Jump(rotulo_falso, origin=no.span)) #senao vai pro falso

    # acoes de ! && ||

    def emitir_negacao_logica_reg(self, no, escolha, rotulo_verdadeiro=None, rotulo_falso=None): #!x como valor 0/1
        valor = self.expression(no.operand, REG)
        destino = self.contexto.temp()
        self.contexto.emit(Seqz(destino, valor, origin=no.span)) #1 c era 0, 0 c era 1
        return destino

    def emitir_negacao_logica_cond(self, no, escolha, rotulo_verdadeiro=None, rotulo_falso=None): #!x como desvio
        self.expression(no.operand, COND, rotulo_falso, rotulo_verdadeiro) #so troca os destinos, n emite nada

    def emitir_e_logico_cond(self, no, escolha, rotulo_verdadeiro=None, rotulo_falso=None): #a && b como desvio
        rotulo_meio = self.contexto.label()
        self.expression(no.left, COND, rotulo_meio, rotulo_falso) #c a for falso n avalia b
        self.contexto.emit(LabelInstr(rotulo_meio)) #so chega aqui c a foi verdadeiro
        self.expression(no.right, COND, rotulo_verdadeiro, rotulo_falso)

    def emitir_ou_logico_cond(self, no, escolha, rotulo_verdadeiro=None, rotulo_falso=None): #a || b como desvio
        rotulo_meio = self.contexto.label()
        self.expression(no.left, COND, rotulo_verdadeiro, rotulo_meio) #c a for verdadeiro n avalia b
        self.contexto.emit(LabelInstr(rotulo_meio)) #so chega aqui c a foi falso
        self.expression(no.right, COND, rotulo_verdadeiro, rotulo_falso)

    def escrever_0_ou_1(self, no, rotulo_verdadeiro, rotulo_falso): #dps dos desvios, escreve 1 ou 0 num vreg
        destino = self.contexto.temp()
        rotulo_fim = self.contexto.label()

        self.contexto.emit(LabelInstr(rotulo_verdadeiro))
        self.contexto.emit(Li(destino, 1, origin=no.span)) #caminho verdadeiro escreve 1
        self.contexto.emit(Jump(rotulo_fim, origin=no.span)) #pula o caminho falso
        self.contexto.emit(LabelInstr(rotulo_falso))
        self.contexto.emit(Li(destino, 0, origin=no.span)) #caminho falso escreve 0
        self.contexto.emit(LabelInstr(rotulo_fim)) #os dois caminhos se juntam aqui
        return destino

    def emitir_e_logico_reg(self, no, escolha, rotulo_verdadeiro=None, rotulo_falso=None): #a && b como valor
        verdadeiro = self.contexto.label()
        falso = self.contexto.label()
        self.emitir_e_logico_cond(no, escolha, verdadeiro, falso) #monta os desvios do &&
        return self.escrever_0_ou_1(no, verdadeiro, falso)

    def emitir_ou_logico_reg(self, no, escolha, rotulo_verdadeiro=None, rotulo_falso=None): #a || b como valor
        verdadeiro = self.contexto.label()
        falso = self.contexto.label()
        self.emitir_ou_logico_cond(no, escolha, verdadeiro, falso) #monta os desvios do ||
        return self.escrever_0_ou_1(no, verdadeiro, falso)
