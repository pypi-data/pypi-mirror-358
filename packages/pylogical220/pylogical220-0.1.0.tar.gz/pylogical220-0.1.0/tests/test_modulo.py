import unittest
from passwordrd.modulo import SetPassRD

class TestSetPassRD(unittest.TestCase):
    def setUp(self):
        self.obj = SetPassRD("minha_senha")

    def test_execucao_com_senha_correta(self):
        resultado = self.obj.eval("1 + 2", linha=1, caractere=1, senha="minha_senha")
        self.assertEqual(resultado, 3)

    def test_senha_incorreta(self):
        with self.assertRaises(PermissionError):
            self.obj.eval("1 + 2", linha=1, caractere=1, senha="senha_errada")

    def test_erro_no_codigo(self):
        with self.assertRaises(RuntimeError) as context:
            self.obj.eval("1 / 0", linha=10, caractere=5, senha="minha_senha")
        self.assertIn("linha 10, caractere 5", str(context.exception))

if __name__ == "__main__":
    unittest.main()
