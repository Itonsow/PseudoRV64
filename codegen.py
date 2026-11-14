"""Pontos de implementação da geração de comandos e expressões."""

import load_previous
from ir import (
    Context,
    ProgramIR,
    FunctionIR,
    Move,
    Param,
    Return,
)
from ast_nodes import (
    TypeName,
    Block,
    VarDecl,
    Assignment,
    ReturnStmt,
)
from patterns import REG


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
        """Selecione e reconstrua uma expressão, preservando curto-circuito."""
        raise NotImplementedError("implemente seleção e emissão")

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

        #caso 7 return; ou return x;
        elif isinstance(node, ReturnStmt):
            if node.value is None: #return sem valor, funcao void
                self.contexto.emit(Return(None, origin=node.span))
            else:
                valor = self.expression(node.value, REG)
                self.contexto.emit(Return(valor, origin=node.span))

        else: #se n for nenhum dos acima, da erro
            raise ValueError(f"comando desconhecido em {node.span}")
