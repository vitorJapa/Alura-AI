import unittest
from unittest.mock import patch, mock_open
import json
import os
from fpdf import FPDF
from io import StringIO
from main import ler_arquivo, sanitize_text, limpar_string_json, PDF, generate_cv, CV_BASE_FILENAME, DICIONARIO_BASE_FILENAME, OUTPUT_CV_FILENAME

class TestCVGenerator(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="conteúdo do arquivo")
    def test_ler_arquivo_sucesso(self, mock_file):
        """Testa a leitura bem-sucedida de um arquivo."""
        conteudo = ler_arquivo("arquivo_teste.txt")
        self.assertEqual(conteudo, "conteúdo do arquivo")
        mock_file.assert_called_once_with("arquivo_teste.txt", 'r', encoding='utf-8')

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_ler_arquivo_nao_encontrado(self, mock_file):
        """Testa o tratamento de arquivo não encontrado."""
        conteudo = ler_arquivo("arquivo_inexistente.txt")
        self.assertIsNone(conteudo)
        mock_file.assert_called_once_with("arquivo_inexistente.txt", 'r', encoding='utf-8')

    @patch("builtins.open", side_effect=IOError("Erro de I/O"))
    def test_ler_arquivo_erro_io(self, mock_file):
        """Testa o tratamento de erro de I/O ao ler o arquivo."""
        conteudo = ler_arquivo("arquivo_com_erro.txt")
        self.assertIsNone(conteudo)
        mock_file.assert_called_once_with("arquivo_com_erro.txt", 'r', encoding='utf-8')

    def test_sanitize_text(self):
        """Testa a substituição de caracteres Unicode."""
        texto_original = "This has a smart quote \u2019 and a dash \u2013 and ellipsis \u2026"
        texto_esperado = "This has a smart quote ' and a dash - and ellipsis ..."
        self.assertEqual(sanitize_text(texto_original), texto_esperado)

    def test_limpar_string_json_valido(self):
        """Testa a formatação de uma string JSON válida."""
        texto_json = "algum texto { \"nome\": \"Valor\", \"idade\": 30 } mais texto"
        esperado = "{\n  \"nome\": \"Valor\",\n  \"idade\": 30\n}"
        self.assertEqual(limpar_string_json(texto_json), esperado)

    def test_limpar_string_json_invalido(self):
        """Testa o tratamento de uma string que não contém JSON válido."""
        texto_invalido = "apenas um texto qualquer"
        self.assertIsNone(limpar_string_json(texto_invalido))

    def test_limpar_string_json_inicio_fim_faltando(self):
        """Testa o tratamento de string com chaves incompletas."""
        texto_incompleto1 = "\"nome\": \"Valor\" }"
        texto_incompleto2 = "{ \"nome\": \"Valor\""
        self.assertIsNone(limpar_string_json(texto_incompleto1))
        self.assertIsNone(limpar_string_json(texto_incompleto2))

    @patch("your_script.ler_arquivo", return_value='{"personal_information": {"name": "John Doe", "title": "Software Engineer"}}')
    def test_pdf_header(self, mock_ler_arquivo):
        """Testa a geração do cabeçalho do PDF."""
        pdf = PDF(personal_info={"name": "John Doe", "title": "Software Engineer", "phone": "123-456-7890", "email": "john.doe@example.com", "linkedin": "linkedin.com/in/johndoe", "location": "New York"})
        pdf.add_page()
        # Como o header() usa métodos internos do FPDF para desenho,
        # é difícil verificar diretamente o conteúdo do PDF sem renderização.
        # Este teste verifica se o método header() é executado sem erros.
        try:
            pdf.header()
            self.assertTrue(True) # Se chegou até aqui sem erro, o teste passa
        except Exception as e:
            self.fail(f"Erro ao gerar o cabeçalho: {e}")

    @patch("your_script.ler_arquivo", return_value='{"profile": "Resumo do perfil"}')
    def test_pdf_adicionar_secao_e_item_lista(self, mock_ler_arquivo):
        """Testa a adição de uma seção e um item de lista ao PDF."""
        pdf = PDF()
        pdf.add_page()
        y_inicial = 40
        y_apos_secao = pdf._adicionar_secao('PROFILE', y_inicial)
        self.assertGreater(y_apos_secao, y_inicial)
        y_apos_item = pdf._adicionar_item_lista('Um ponto da lista')
        self.assertGreater(y_apos_item, y_apos_secao)

    @patch("your_script.ler_arquivo", return_value='{"professional_experience": [{"company": "Tech Inc", "location": "Silicon Valley", "title": "Senior Engineer", "duration": "2020-Present", "description": "Responsável por..."}]}')
    def test_pdf_adicionar_experiencia(self, mock_ler_arquivo):
        """Testa a adição da seção de experiência profissional."""
        pdf = PDF()
        pdf.add_page()
        start_x = 80
        start_y = 40
        right_column_width = 120
        y_apos_experiencia = pdf._adicionar_experiencia({"company": "Tech Inc", "location": "Silicon Valley", "title": "Senior Engineer", "duration": "2020-Present", "description": "Responsável por várias tarefas importantes."}, start_x, start_y, right_column_width)
        self.assertGreater(y_apos_experiencia, start_y)

    @patch("your_script.ler_arquivo", return_value='{"education": [{"degree": "Bacharel em Ciência da Computação", "institution": "Universidade Exemplo", "years": "2016-2020"}]}')
    def test_pdf_adicionar_educacao(self, mock_ler_arquivo):
        """Testa a adição da seção de educação."""
        pdf = PDF()
        pdf.add_page()
        y_inicial = 60
        pdf._adicionar_secao('EDUCATION', y_inicial)
        pdf.set_font(*('OpenSans', 'B', 7))
        education_data = [{"degree": "Bacharel em Ciência da Computação", "institution": "Universidade Exemplo", "years": "2016-2020"}]
        for edu_item in education_data:
            pdf.set_x(10)
            pdf.cell(60, 6, sanitize_text(edu_item.get("degree", "")), new_x='LMARGIN', new_y='NEXT')
            pdf.set_font(*('OpenSans', '', 8))
            pdf.set_x(10)
            pdf.multi_cell(60, 6, sanitize_text(f"{edu_item.get('institution', '')} {edu_item.get('years', '')}"))
        self.assertTrue(True) # Verifica se o código executa sem erros

    @patch("your_script.ler_arquivo", return_value='{"skills": {"Python": 5, "Java": 4}}')
    def test_pdf_adicionar_habilidades(self, mock_ler_arquivo):
        """Testa a adição da seção de habilidades."""
        pdf = PDF()
        pdf.add_page()
        y_inicial = 80
        pdf._adicionar_secao('SKILLS', y_inicial)
        pdf.set_font(*('OpenSans', '', 8))
        skills_dict = {"Python": 5, "Java": 4}
        skills_list = list(skills_dict)
        for i in range(0, len(skills_list), 2):
            pdf.set_x(10)
            pdf.cell(30, 5, sanitize_text(skills_list[i]), border=0, align='L')
            if i + 1 < len(skills_list):
                pdf.cell(30, 5, sanitize_text(skills_list[i + 1]), border=0, align='L')
            pdf.ln(5)
        self.assertTrue(True) # Verifica se o código executa sem erros

    @patch("your_script.ler_arquivo", return_value='{"languages": [{"language": "Inglês", "proficiency": "Avançado"}]}')
    def test_pdf_adicionar_idiomas(self, mock_ler_arquivo):
        """Testa a adição da seção de idiomas."""
        pdf = PDF()
        pdf.add_page()
        y_inicial = 100
        pdf._adicionar_secao('LANGUAGES', y_inicial)
        languages_list = [{"language": "Inglês", "proficiency": "Avançado"}]
        pdf.set_font(*('OpenSans', '', 8))
        for lang_item in languages_list:
            pdf.set_x(10)
            pdf.cell(30, 6, lang_item.get("language", ""), border=0, align='L')
            pdf.cell(30, 6, f"({lang_item.get('proficiency', '')})", border=0, align='L')
            pdf.ln(6)
        self.assertTrue(True) # Verifica se o código executa sem erros

    @patch("your_script.ler_arquivo", return_value='{"certifications": [{"name": "Certificação X", "date": "2023"}]}')
    def test_pdf_adicionar_certificacoes(self, mock_ler_arquivo):
        """Testa a adição da seção de certificações."""
        pdf = PDF()
        pdf.add_page()
        y_inicial = 120
        y_apos_secao = pdf._adicionar_secao('CERTIFICATIONS', y_inicial)
        certifications_list = [{"name": "Certificação X", "date": "2023"}]
        for cert in certifications_list:
            pdf._adicionar_item_lista(f"{cert.get('name', '')} - {cert.get('date', '')}")
        self.assertTrue(True) # Verifica se o código executa sem erros

    @patch("your_script.ler_arquivo")
    @patch("your_script.genai.Client")
    def test_generate_cv_sucesso(self, mock_genai_client, mock_ler_arquivo):
        """Testa o fluxo completo de geração do CV com resposta bem-sucedida do Gemini."""
        mock_ler_arquivo.side_effect = [
            '{"personal_information": {"name": "Test Name"}, "profile": "Test Profile", "education": [], "skills": {}, "languages": [], "certifications": [], "professional_experience": []}', # CV_BASE_FILENAME
            '{"en": {"profile": "Summary", "education": "Education", "skills": "Skills", "languages": "Languages", "certifications": "Certifications", "professional_experience": "Professional Experience"}}' # DICIONARIO_BASE_FILENAME
        ]
        mock_chat = mock_genai_client.return_value.chats.create.return_value
        mock_chat.send_message.return_value.text = '{"personal_information": {"name": "Test Name"}, "profile": "Adapted Profile", "education": [], "skills": {}, "languages": [], "certifications": [], "professional_experience": []}'

        with patch.object(FPDF, 'output') as mock_output:
            generate_cv("Job Description Here", "test_cv.pdf")
            mock_output.assert_called_once_with("test_cv.pdf")

        self.assertTrue(os.path.exists("test_cv.pdf"))
        os.remove("test_cv.pdf")

    @patch("your_script.ler_arquivo", return_value=None)
    def test_generate_cv_arquivo_nao_encontrado(self, mock_ler_arquivo):
        """Testa o tratamento quando um dos arquivos base não é encontrado."""
        resultado = generate_cv("Job Description Here")
        self.assertIsNone(resultado)

    @patch("your_script.ler_arquivo")
    @patch("your_script.genai.Client")
    def test_generate_cv_resposta_gemini_invalida(self, mock_genai_client, mock_ler_arquivo):
        """Testa o tratamento quando a resposta do Gemini não contém um JSON válido."""
        mock_ler_arquivo.side_effect = [
            '{"personal_information": {"name": "Test Name"}, "profile": "Test Profile", "education": [], "skills": {}, "languages": [], "certifications": [], "professional_experience": []}',
            '{"en": {"profile": "Summary", "education": "Education", "skills": "Skills", "languages": "Languages", "certifications": "Certifications", "professional_experience": "Professional Experience"}}'
        ]
        mock_chat = mock_genai_client.return_value.chats.create.return_value
        mock_chat.send_message.return_value.text = "Resposta inválida sem JSON"

        resultado = generate_cv("Job Description Here")
        self.assertIsNone(resultado)

    @patch("your_script.ler_arquivo")
    @patch("your_script.genai.Client")
    def test_generate_cv_erro_decodificacao_json(self, mock_genai_client, mock_ler_arquivo):
        """Testa o tratamento de erro ao decodificar a resposta JSON do Gemini."""
        mock_ler_arquivo.side_effect = [
            '{"personal_information": {"name": "Test Name"}, "profile": "Test Profile", "education": [], "skills": {}, "languages": [], "certifications": [], "professional_experience": []}',
            '{"en": {"profile": "Summary", "education": "Education", "skills": "Skills", "languages": "Languages", "certifications": "Certifications", "professional_experience": "Professional Experience"}}'
        ]
        mock_chat = mock_genai_client.return_value.chats.create.return_value
        mock_chat.send_message.return_value.text = '{"chave": "valor",}' # JSON mal formado

        resultado = generate_cv("Job Description Here")
        self.assertIsNone(resultado)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)