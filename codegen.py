"""Pontos de implementação da geração de comandos e expressões."""

import load_previous
from ir import (
    Context,
    ProgramIR,
    FunctionIR,
    Param,
    Return,
)
from ast_nodes import (
    TypeName,
    Block,
)


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

        else: #se n for nenhum dos acima, da erro
            raise ValueError(f"comando desconhecido em {node.span}")
