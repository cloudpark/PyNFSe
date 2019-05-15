# -*- coding: utf-8 -*-
from decimal import Decimal


class Prestador(object):

    cnpj = None
    inscricao_municipal = None

    def __post_init__(self, **kwargs):
        self.validate()


class Tomador(object):
    inscricao_municipal = None
    numero_documento = None
    razao_social = None
    tipo_documento = None

    bairro = None
    cep = None
    codigo_municipio = None
    endereco = None
    endereco_complemento = None
    endereco_numero = None
    uf = None

    email = None
    telefone = None


class Servico(object):
    aliquota = None
    codigo_cnae = None
    codigo_municipio = None
    codigo_tributacao_municipio = None
    discriminacao = None
    iss_retido = None
    item_lista = None
    valor_servico = None
    base_calculo = None
    valor_liquido = 0
    valor_iss = 0
    valor_iss_retido = 0

    desconto_condicionado = 0
    desconto_incondicionado = 0
    outras_retencoes = 0
    valor_cofins = 0
    valor_csll = 0
    valor_deducoes = 0
    valor_inss = 0
    valor_ir = 0
    valor_pis = 0

    def gerar_valores_faltantes(self):
        self.base_calculo = self._calcular_base_calculo()
        self.valor_iss = self._calcular_iss()
        self.valor_iss_retido = Decimal() if self.iss_retido == 2 else self.valor_iss
        self.valor_liquido = self._calcular_valor_liquido()

    def _calcular_base_calculo(self):
        return self.valor_servico - self.valor_deducoes - self.desconto_incondicionado

    def _calcular_valor_liquido(self):
        descontos = sum([
            self.desconto_condicionado,
            self.desconto_incondicionado,
            self.outras_retencoes,
            self.valor_cofins,
            self.valor_csll,
            self.valor_inss,
            self.valor_ir,
            self.valor_iss_retido,
            self.valor_pis,
        ])

        return Decimal(self.valor_servico - descontos)

    def _calcular_iss(self):
        return Decimal(self.base_calculo * self.aliquota).quantize(Decimal('0.01'))


class RPS(object):
    data_emissao = None
    identificador = None
    incentivo = None
    natureza_operacao = None
    numero = None
    prestador = None
    regime_especial = None
    serie = None
    servico = None
    simples = None
    tipo = None
    tomador = None
    status = None

    @classmethod
    def criar_a_partir_de_dados(cls, dados_rps):
        return cls(
            data_emissao=dados_rps['data_emissao'],
            identificador=dados_rps['identificador'],
            incentivo=dados_rps['incentivo'],
            natureza_operacao=dados_rps['natureza_operacao'],
            numero=dados_rps['numero'],
            prestador=Prestador(**dados_rps['prestador']),
            regime_especial=dados_rps.get('regime_especial'),
            serie=dados_rps['serie'],
            servico=Servico(**dados_rps['servico']),
            simples=dados_rps['simples'],
            tipo=dados_rps['tipo'],
            tomador=Tomador(**dados_rps['tomador']),
        )


class LoteRPS(object):
    cnpj = None
    identificador = None
    inscricao_municipal = None
    lista_rps = None
    numero_lote = None

    @classmethod
    def criar_a_partir_de_dados(cls, dados_lote_rps):
        return cls(
            cnpj=dados_lote_rps['cnpj'],
            identificador=dados_lote_rps['identificador'],
            inscricao_municipal=dados_lote_rps['inscricao_municipal'],
            lista_rps=[RPS.criar_a_partir_de_dados(dados_rps) for dados_rps in dados_lote_rps['lista_rps']],
            numero_lote=dados_lote_rps['numero_lote'],
        )
