from sped.registros import Registro
from sped.campos import Campo, CampoFixo, CampoData, CampoNumerico

class Registro0000(Registro):
    """
    ABERTURA DO ARQUIVO DIGITAL 
    """
    campos = [
        CampoFixo(1, 'REG', '0000'),
        Campo(2, 'NOME_EMPRESA'),
        Campo(3, 'CNPJ'),
    ]

class RegistroN001(Registro):
    """
    ABERTURA DO BLOCO N
    """
    campos = [
        CampoFixo(1, 'REG', 'N001'),
        Campo(2, 'IND_DAD'),
    ]

class RegistroN100(Registro):
    """
    CABEÇALHO DA NFE (NIVEL 1) (1:N)
    """    
    campos = [
        CampoFixo(1, 'REG', 'N100'),
        Campo(2, 'CNPJ_EMIT'),
        Campo(3, 'NOME_EMIT'),
        Campo(4, 'NUM_NFE'),
        Campo(5, 'SERIE'),
        CampoData(6, 'DT_EMISSAO'),
        Campo(7, 'TIPO_NFE'),
        Campo(8, 'CHAVE_NFE'),    
        Campo(9, 'CNPJ_DEST'),
        Campo(10, 'CPF_DEST'),
        Campo(11, 'NOME_DEST'),
        Campo(12, 'UF'),
        CampoNumerico(13, 'VALOR_NFE', precisao=2),
        Campo(14, 'MES_ANO'),
        CampoData(15, 'DATA_IMPORTACAO'),
        Campo(16, 'STATUS_NFE'),
        Campo(17, 'X_USER1'),
        Campo(18, 'X_USER2'),
    ]

class RegistroN140(Registro):
    """
    FATURAS DA NFE (NIVEL 2) (1:N)
    """
    campos = [
        CampoFixo(1, 'REG', 'N140'),
        Campo(2, 'NUM_FAT'),
        CampoNumerico(3, 'VLR_ORIG', precisao=2),        
        CampoNumerico(4, 'VLR_DESC', precisao=2), 
        CampoNumerico(5, 'VLR_LIQ', precisao=2), 
    ]

class RegistroN141(Registro):
    """
    DUPLICATAS DA FATURA (NIVEL 3) (1:N)
    """
    campos = [
        CampoFixo(1, 'REG', 'N141'),
        Campo(2, 'NUM_DUP'),
        CampoData(3, 'DT_VENC'),
        CampoNumerico(4, 'VLR_DUP', precisao=2),        
    ]
    
class RegistroN170(Registro):
    """
    ITENS DA NFE (NIVEL 2) (1:N)
    """
    campos = [
        CampoFixo(1, 'REG', 'N170'),
        CampoNumerico(2, 'NUM_ITEM'),
        Campo(3, 'COD_PROD'),
        Campo(4, 'DESC_PROD'),
        Campo(5, 'NCM'),
        Campo(6, 'CEST'),
        Campo(7, 'CFOP'),
        CampoNumerico(8, 'VLR_UNIT', precisao=2),
        CampoNumerico(9, 'QTDE', precisao=4),
        Campo(10, 'UNID'),
        CampoNumerico(11, 'VLR_PROD', precisao=2),
        CampoNumerico(12, 'VLR_FRETE', precisao=2),
        CampoNumerico(13, 'VLR_SEGURO', precisao=2),
        CampoNumerico(14, 'VLR_DESC', precisao=2),
        CampoNumerico(15, 'VLR_OUTROS', precisao=2),
        CampoNumerico(16, 'VLR_ITEM', precisao=2),
        Campo(17, 'ORIGEM'),
        Campo(18, 'CST_ICMS'),
        CampoNumerico(19, 'BC_ICMS', precisao=2),
        CampoNumerico(20, 'ALQ_ICMS', precisao=2),
        CampoNumerico(21, 'VLR_ICMS', precisao=2),
        CampoNumerico(22, 'MVA', precisao=2),
        CampoNumerico(23, 'BC_ICMSST', precisao=2),
        CampoNumerico(24, 'ALQ_ICMSST', precisao=2),
        CampoNumerico(25, 'ICMSST', precisao=2),
        Campo(26, 'CST_IPI'),
        CampoNumerico(27, 'BC_IPI', precisao=2),
        CampoNumerico(28, 'ALQ_IPI', precisao=2),
        CampoNumerico(29, 'VLR_IPI', precisao=2),
        Campo(30, 'CST_PIS'),
        CampoNumerico(31, 'BC_PIS', precisao=2),
        CampoNumerico(32, 'ALQ_PIS', precisao=2),
        CampoNumerico(33, 'VLR_PIS', precisao=2),
        Campo(34, 'CST_COFINS'),
        CampoNumerico(35, 'BC_COFINS', precisao=2),
        CampoNumerico(36, 'ALQ_COFINS', precisao=2),
        CampoNumerico(37, 'VLR_COFINS', precisao=2),        
    ]

class RegistroN990(Registro):
    """
    ENCERRAMENTO DO BLOCO N
    """
    campos = [
        CampoFixo(1, 'REG', 'N990'),
        CampoNumerico(2, 'QTD_LIN_N'),        
    ]

class RegistroZ001(Registro):
    """
    ABERTURA DO BLOCO Z
    """
    campos = [
        CampoFixo(1, 'REG', 'Z001'),
        Campo(2, 'IND_DAD'),
    ]

class RegistroZ100(Registro):
    """
    EVENTOS DA NFE
    """
    campos = [
        CampoFixo(1, 'REG', 'Z100'),
        Campo(2, 'CNPJ'),
        Campo(3, 'CPF'),
        Campo(4, 'CHAVE_NFE'),
        CampoData(5, 'DATA_EVENTO'),  
        Campo(6, 'TIPO_EVENTO'),    
        Campo(7, 'DESC_EVENTO'),  
        Campo(8, 'MOTIVO'),  
        Campo(9, 'PROTOCOLO'), 
    ]

class RegistroZ990(Registro):
    """
    ENCERRAMENTO DO BLOCO Z
    """
    campos = [
        CampoFixo(1, 'REG', 'Z990'),
        CampoNumerico(2, 'QTD_LIN_Z'),        
    ]

class Registro9999(Registro):
    """
    ENCERRAMENTO DO ARQUIVO DIGITAL
    """
    campos = [
        CampoFixo(1, 'REG', '9999'),
        CampoNumerico(2, 'QTD_LIN'),
    ]