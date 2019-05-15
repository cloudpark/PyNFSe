# -*- coding: utf-8 -*-
from PyNFSe.base.certificate import get_certificate
from PyNFSe.base.nfse_signer import NFSeSigner
from PyNFSe.nfse.pr.curitiba import serializacao as s
from PyNFSe.nfse.pr.curitiba.comunicacao import Comunicacao
from lxml import etree, objectify


class Facade:

    def __init__(self, certificado_pfx, senha, producao=False):
        namespace = '{http://isscuritiba.curitiba.pr.gov.br/iss/nfse.xsd}'
        url_homologacao = 'https://pilotoisscuritiba.curitiba.pr.gov.br/nfse_ws/NfseWs.asmx?WSDL'
        url_producao = 'https://isscuritiba.curitiba.pr.gov.br/Iss.NfseWebService/nfsews.asmx?WSDL'

        self.cert, self.cert_file, self.key, self.key_file = get_certificate(certificado_pfx, senha)
        url_ambiente = url_producao if producao else url_homologacao
        cert_file_and_key_file = (self.cert_file.name, self.key_file.name)

        self._assinador = NFSeSigner(self.cert, self.key, namespace)
        self._servicos_wsdl = Comunicacao(url_ambiente, cert_file_and_key_file, producao)

    def consultar_nfse_por_numero(self, prestador, numero_nfse):
        xml = s.consulta_nfse_por_numero(prestador, numero_nfse)
        xml_retorno = self._servicos_wsdl.consultar_nfse(xml)

        return xml_retorno

    def consultar_nfse_por_data(self, prestador, data_inicial, data_final):
        xml = s.consulta_nfse_por_data(prestador, data_inicial, data_final)
        xml_retorno = self._servicos_wsdl.consultar_nfse(xml)

        return xml_retorno

    def consultar_nfse_por_rps(self, rps):
        xml = s.consulta_nfse_por_rps(rps)
        xml_retorno = self._servicos_wsdl.consultar_nfse_por_rps(xml)

        return xml_retorno

    def consultar_situacao_lote_rps(self, prestador, protocolo):
        xml = s.consulta_situacao_lote_rps(prestador, protocolo)
        xml_retorno = self._servicos_wsdl.consultar_situacao_lote_rps(xml)

        return xml_retorno

    def consultar_lote_rps(self, prestador, protocolo):
        xml = s.consulta_lote_rps(prestador, protocolo)
        xml_retorno = self._servicos_wsdl.consultar_lote_rps(xml)

        return xml_retorno

    def recepcionar_lote_rps(self, lote_rps):
        xml = s.envio_lote_rps(lote_rps).encode('utf-8')
        xml = self._assinador.sign_rps_batch(xml)
        response = self._servicos_wsdl.recepcionar_lote_rps(xml)
        response = self.sanitize_response(response)
        return response

    def cancelar_nfse(self, pedido_cancelamento_nfse):
        xml = s.cancela_nfse(pedido_cancelamento_nfse)
        xml = self._assinador.sign_cancellation_request(xml)
        xml_retorno = self._servicos_wsdl.cancelar_nfse(xml)

        return xml_retorno

    def validar_xml(self, xml):
        retorno = self._servicos_wsdl.validar_xml(xml)

        return retorno

    def sanitize_response(self, response):
        tree = etree.fromstring(response)
        for elem in tree.getiterator():
            if not hasattr(elem.tag, 'find'):
                continue
            i = elem.tag.find('}')
            if i >= 0:
                elem.tag = elem.tag[i + 1:]
        objectify.deannotate(tree, cleanup_namespaces=True)
        return objectify.fromstring(etree.tostring(tree))