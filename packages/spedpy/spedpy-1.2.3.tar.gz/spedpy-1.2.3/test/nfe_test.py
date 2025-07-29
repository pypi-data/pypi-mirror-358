# -*- coding: utf-8 -*-
from decimal import Decimal
import unittest
import os
import sys

# Necessário para que o arquivo de testes encontre
test_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(test_root)
sys.path.insert(0, os.path.dirname(test_root))
sys.path.insert(0, test_root)

from sped.nfe.arquivos import ArquivoDigital

class TestNFe(unittest.TestCase):

    def test_read_registro(self):
        
        txt = """|0000|TESTE LTDA|23004906000180|
|N001|1|
|N100|23004906000180|TESTE LTDA|135418|1|02052024|SAIDA|35240523004906000180550010001354181002078142|23.004.906/0001-80||DANIELA EVANGELISTA DA SILVA|BA|80,00|05_2024|27092024|AUTORIZADA||TESTE|
|N170|1|AERCX02RD|CAIXA DE SOM BLUETOOTH COR VERMELHO CARMIM AERBOX 2|85182100||2949|80,00|1,0000|UN|80,00|0,00|0,00|0,00|0,00|80,00|||80,00|4,00|3,20|0,00|0,00|0,00|0,00|03|0,00|0,00|0,00|99|0,00|0,00|0,00|01|80,00|3,00|2,40|
|N990|2|
|Z001|0|
|Z990|0|
|9999|2|
"""
        with open('nfe.txt', 'w') as f:
            f.write(txt)
            
        nfe = ArquivoDigital()
        nfe.readfile('nfe.txt')
        nfe.prepare()
        self.assertEqual("TESTE LTDA", nfe.abertura.NOME_EMPRESA)
        
        for r in nfe.blocoN.registros:
            if r.REG == "N100":
                self.assertEqual("AUTORIZADA", r.STATUS_NFE)
                self.assertEqual("TESTE", r.X_USER2)
            elif r.REG == "N170":
                self.assertEqual("AERCX02RD", r.COD_PROD)
                self.assertEqual(Decimal('0.0'), r.VLR_PIS)
                self.assertEqual("01", r.CST_COFINS)
                self.assertEqual(Decimal('2.40'), r.VLR_COFINS)
        
        print(nfe)

if __name__ == '__main__':
    unittest.main()
