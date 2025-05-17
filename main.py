from fpdf import FPDF
from fpdf.enums import XPos, YPos
from google import genai
import os
from dotenv import load_dotenv, find_dotenv
import json

# Constantes
CV_BASE_FILENAME = "CV_Base"
DICIONARIO_BASE_FILENAME = "Dicionario"
OUTPUT_CV_FILENAME = "Vitor_Kihara_CV.pdf"
MODEL_NAME = 'gemini-2.0-flash'
LEFT_COLUMN_WIDTH = 60
RIGHT_COLUMN_WIDTH = 120  # Aumentei a largura da coluna da direita
ICON_SIZE = 3
TEXT_OFFSET = 1
CONTACT_ITEM_WIDTH = 40
SKILL_COLUMN_WIDTH = LEFT_COLUMN_WIDTH / 2
SKILL_ROW_HEIGHT = 5
LANGUAGE_ROW_HEIGHT = 6
SECTION_TITLE_FONT = ('Montserrat', 'B', 12)
NORMAL_TEXT_FONT = ('OpenSans', '', 8)
BOLD_TEXT_FONT = ('OpenSans', 'B', 7)
COMPANY_INFO_FONT = ('Montserrat', '', 9)
JOB_TITLE_FONT = ('Montserrat', 'B', 9)
JOB_DETAIL_FONT = ('Montserrat', '', 8)

# Carregar variáveis de ambiente
load_dotenv(find_dotenv())
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

def ler_arquivo(nome):
    """Lê o conteúdo de um arquivo de texto."""
    try:
        with open(nome, 'r', encoding='utf-8') as arquivo:
            return arquivo.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome}' não encontrado.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
        return None

def sanitize_text(text):
    """Substitui caracteres Unicode específicos por seus equivalentes ASCII."""
    replacements = {
        '\u2019': "'",
        '\u2013': "-",
        '\u2026': "..."
    }
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    return text

def limpar_string_json(texto, indentacao=2):
    """Tenta extrair e formatar uma string JSON de um texto."""
    try:
        inicio = texto.find('{')
        if inicio == -1:
            return None
        fim = texto.rfind('}')
        if fim == -1 or fim < inicio:
            return None
        json_string = texto[inicio:fim + 1]
        data = json.loads(json_string)
        return json.dumps(data, indent=indentacao, ensure_ascii=False)
    except json.JSONDecodeError:
        return None

class PDF(FPDF):
    """Classe PDF personalizada com cabeçalho e rodapé."""

    def __init__(self, personal_info=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.personal_info = personal_info if personal_info else {}
        self._carregar_fontes()

    def _carregar_fontes(self):
        """Carrega todas as fontes necessárias para o PDF."""
        self.add_font('Montserrat', '', 'Montserrat-Regular.ttf')
        self.add_font('Montserrat', 'B', 'Montserrat-Bold.ttf')
        self.add_font('Montserrat', 'I', 'Montserrat-Italic.ttf')
        self.add_font('Montserrat-Thin', '', 'Montserrat-Thin.ttf')
        self.add_font('OpenSans', '', 'OpenSans-Regular.ttf')
        self.add_font('OpenSans', 'B', 'OpenSans-Bold.ttf')

    def header(self):
        """Adiciona o cabeçalho com nome, título e informações de contato."""
        # Nome no topo
        self.set_font('Montserrat-Thin', '', 20)
        name_parts = self.personal_info.get("name", "").split(" ")
        first_name = name_parts[0].upper() if name_parts else ""
        last_name = " ".join(name_parts[1:]).upper() if len(name_parts) > 1 else ""
        self.cell(80, 5, first_name, align='R', new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.set_font('Montserrat', 'B', 20)
        self.cell(0, 5, last_name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Montserrat', '', 8)
        self.cell(0, 5, self.personal_info.get("title", "").upper(), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.line(35, 20, 175, 20)

        # Informações de contato
        self.set_font('OpenSans', '', 7)
        contact_info = [
            {"icon": "phone_icon.png", "text": self.personal_info.get("phone", "")},
            {"icon": "email_icon.png", "text": self.personal_info.get("email", "")},
            {"icon": "linkedin_icon.png", "text": self.personal_info.get("linkedin", "")},
            {"icon": "location_icon.png", "text": self.personal_info.get("location", "")}
        ]

        total_width = len(contact_info) * CONTACT_ITEM_WIDTH + 10
        start_x = (self.w - total_width) / 2
        y_offset = 25

        for i, item in enumerate(contact_info):
            self.set_xy(start_x, y_offset)
            self.image(item["icon"], x=start_x, y=y_offset, w=ICON_SIZE, h=ICON_SIZE)
            self.set_xy(start_x + ICON_SIZE + TEXT_OFFSET, y_offset)
            self.cell(CONTACT_ITEM_WIDTH - ICON_SIZE - TEXT_OFFSET, 3, item["text"], align='L')
            start_x += CONTACT_ITEM_WIDTH if i < 2 else CONTACT_ITEM_WIDTH + 5

    def _adicionar_secao(self, title, y_position):
        """Adiciona uma seção com título e linha divisória."""
        self.set_xy(10, y_position)
        self.set_font(*SECTION_TITLE_FONT)
        self.cell(LEFT_COLUMN_WIDTH, 10, title, border='B', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font(*NORMAL_TEXT_FONT)
        return self.get_y() + 2

    def _adicionar_item_lista(self, text):
        """Adiciona um item simples a uma lista."""
        self.set_x(10)
        self.multi_cell(LEFT_COLUMN_WIDTH, 6, sanitize_text(text))
        return self.get_y() + 2

    def _adicionar_experiencia(self, exp, start_x, start_y, right_column_width):
        """Adiciona a seção de experiência profissional formatada."""
        company = exp.get("company", "")
        location = exp.get("location", "")
        title = exp.get("title", "")
        duration = exp.get("duration", "")
        description = exp.get("description", "")
        details = description.split('\n') if isinstance(description, str) else [description]

        self.set_xy(start_x, start_y)
        self.set_font(*COMPANY_INFO_FONT)
        self.multi_cell(right_column_width, 6, sanitize_text(f"{company} - {location}"))
        current_y = self.get_y()
        self.set_xy(start_x, current_y)
        self.set_font(*JOB_TITLE_FONT)
        self.multi_cell(right_column_width, 6, sanitize_text(f"{title}, {duration}"))
        self.set_font(*JOB_DETAIL_FONT)
        current_y = self.get_y()
        for detail in details:
            self.set_xy(start_x, current_y)
            self.multi_cell(right_column_width, 6, sanitize_text(f"- {detail.strip()}"))
            current_y = self.get_y()
        return self.get_y() + 5

def generate_cv(job_description, output_path=OUTPUT_CV_FILENAME):
    """Gera o CV em PDF com base na descrição da vaga."""
    cvbase_content = ler_arquivo(CV_BASE_FILENAME)
    dicionario_base_content = ler_arquivo(DICIONARIO_BASE_FILENAME)

    if cvbase_content is None or dicionario_base_content is None:
        return None

    prompt = f"""
    Utilizando como base o meu curriculo, {cvbase_content}.
    e na vaga:
    {job_description}

    adapte as informacoes do curriculo para a vaga altere o conteudo do Sumario e da descricao de funcoes dos empregos mas nao invente informacao. Atencao, na parte de skills, as habilidades nao podem conter mais do que 21 letras por frase. De a resposta apenas em um formato JSON. Reescreva como achar melhor para que tenha mais chancer de passar na AI que analisa curriculos. Faca o CV em INGLES mas lembre-se que ingles nao eh a minha lingua materna :

    {dicionario_base_content}
    """

    cv_content_str = None
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        chat = client.chats.create(model=MODEL_NAME)
        response = chat.send_message(prompt)
        cv_content_str = limpar_string_json(response.text)

        if cv_content_str is None:
            print("Erro: Resposta do Gemini não continha um JSON válido.")
            return None

        try:
            cv_content = json.loads(cv_content_str)
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            print("Conteúdo da resposta do Gemini (para depuração):")
            print(cv_content_str)
            return None

        personal_information = cv_content.get("personal_information", {})
        pdf = PDF(format='A4', personal_info=personal_information)
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.add_page()

        current_y = 40

        # Profile Section
        current_y = pdf._adicionar_secao('PROFILE', current_y)
        profile_text = sanitize_text(cv_content.get("profile", ""))
        pdf.multi_cell(LEFT_COLUMN_WIDTH, 6, profile_text)
        current_y = pdf.get_y() + 5

        # Education Section
        current_y = pdf._adicionar_secao('EDUCATION', current_y)
        pdf.set_font(*BOLD_TEXT_FONT)
        education_data = cv_content.get("education", [])
        for edu_item in education_data:
            degree = edu_item.get("degree", "")
            institution = edu_item.get("institution", "")
            years = edu_item.get("years", "")
            pdf.set_x(10)
            pdf.cell(LEFT_COLUMN_WIDTH, 6, sanitize_text(degree), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font(*NORMAL_TEXT_FONT)
            pdf.set_x(10)
            pdf.multi_cell(LEFT_COLUMN_WIDTH, 6, sanitize_text(f"{institution} {years}"))
            current_y = pdf.get_y() + 2
        current_y += 3

        # Skills Section
        current_y = pdf._adicionar_secao('SKILLS', current_y)
        pdf.set_font(*NORMAL_TEXT_FONT)
        skills_dict = cv_content.get("skills", {})
        skills_list = list(skills_dict)
        for i in range(0, len(skills_list), 2):
            pdf.set_x(10)
            pdf.cell(SKILL_COLUMN_WIDTH, SKILL_ROW_HEIGHT, sanitize_text(skills_list[i]), border=0, align='L')
            if i + 1 < len(skills_list):
                pdf.cell(SKILL_COLUMN_WIDTH, SKILL_ROW_HEIGHT, sanitize_text(skills_list[i + 1]), border=0, align='L')
            pdf.ln(SKILL_ROW_HEIGHT)
        current_y = pdf.get_y() + 5

        # Languages Section
        current_y = pdf._adicionar_secao('LANGUAGES', current_y)
        languages_list = cv_content.get("languages", [])
        pdf.set_font(*NORMAL_TEXT_FONT)
        for lang_item in languages_list:
            language = lang_item.get("language", "")
            proficiency = lang_item.get("proficiency", "")
            pdf.set_x(10)
            pdf.cell(LEFT_COLUMN_WIDTH / 2, LANGUAGE_ROW_HEIGHT, language, border=0, align='L')
            pdf.cell(LEFT_COLUMN_WIDTH / 2, LANGUAGE_ROW_HEIGHT, f"({proficiency})", border=0, align='L')
            pdf.ln(LANGUAGE_ROW_HEIGHT)
        languages_end_y = pdf.get_y()  # Salva a posição Y do final da seção de idiomas
        current_y += 2

        # Certifications Section
        current_y = pdf._adicionar_secao('CERTIFICATIONS', languages_end_y + 5)  # Usa a posição Y correta
        certifications_list = cv_content.get("certifications", [])
        for cert in certifications_list:
            name = cert.get("name", "")
            date = cert.get("date", "")
            pdf._adicionar_item_lista(f"{name} - {date}")

        # Professional Experience Section
        pdf.set_xy(80, 40)
        pdf.set_font(*SECTION_TITLE_FONT)
        pdf.cell(RIGHT_COLUMN_WIDTH, 10, 'PROFESSIONAL EXPERIENCE', border='B', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

        start_x = 80
        start_y = pdf.get_y()
        experiences = cv_content.get("professional_experience", [])
        for exp in experiences:
            start_y = pdf._adicionar_experiencia(exp, start_x, start_y, RIGHT_COLUMN_WIDTH)

        # Save PDF
        pdf.output(output_path)
        print(f"CV gerado com sucesso e salvo em: {output_path}")

    except Exception as e:
        print(f"Erro ao gerar o CV: {e}")
        print(cv_content_str if cv_content_str else "Nenhuma resposta do Gemini recebida.")
        return None

if __name__ == '__main__':
    #adicione aqui a job descripton ou o link da pagina da vaga
    job_description = """
    Job Description

Are you passionate about designing effective prompts that drive accurate and culturally relevant data labeling and translation? Join our team as a Prompt Engineer, where you’ll play a key role in developing and optimizing prompts to enhance data annotation and localization across various languages and regions.
Key Responsibilities:

Design, develop, and refine prompts for data labeling and localization within software applications.
Analyze software components, use cases, and challenges to iterate on prompt solutions using a strong understanding of data structures, formats, and modeling.
Collaborate with data scientists, linguists, and localization experts to ensure prompt effectiveness and cultural adaptability.
Conduct user testing and analyze feedback to enhance prompt accuracy and linguistic consistency.
Develop guidelines and training materials for prompt implementation in data labeling and localization projects.
Stay updated on industry trends and tools to continuously improve prompt engineering techniques.
Requirements:

Bachelor’s degree in Computer Science, Linguistics, Localization, or a related field.
Proven experience in prompt engineering for data labeling and localization.
Proficiency in programming languages such as JSON, Python, JavaScript, or XML.
Strong understanding of localization best practices and cultural nuances across languages and regions.
Excellent communication and cross-functional collaboration skills.
Detail-oriented with a problem-solving mindset.
Knowledge of additional languages (e.g., German, French, Portuguese-Brazilian) is a plus.
Please note it is a Part-time role and required to work 10 hours/ week!
    """
    generate_cv(job_description)