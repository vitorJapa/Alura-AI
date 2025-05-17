# CV Generator

Este projeto é uma ferramenta para gerar Currículos Vitae (CVs) personalizados em formato PDF a partir de descrições de vagas de emprego. Ele utiliza a biblioteca `fpdf` para criar os PDFs e a API do Gemini do Google para adaptar o conteúdo do CV base à vaga desejada.

## Sumário

* [Propósito](#proposito)
* [Objetivo](#objetivo)
* [Funcionalidades](#funcionalidades)
* [Instalação](#instalacao)
* [Execução](#execucao)
* [Dependências](#dependencias)
* [Uso](#uso)
* [Estrutura do Código](#estrutura-do-codigo)
* [Contribuição](#contribuicao)
* [Licença](#licenca)

## Propósito

O propósito deste projeto é automatizar e otimizar o processo de criação de CVs. Ao invés de criar um CV do zero ou adaptar manualmente um modelo existente para cada aplicação de emprego, esta ferramenta gera um CV personalizado que destaca as habilidades e experiências mais relevantes para a vaga.

## Objetivo

O objetivo principal é aumentar a eficiência na busca de emprego, fornecendo aos usuários uma maneira rápida e fácil de produzir CVs direcionados, aumentando assim as chances de passar por sistemas de triagem automatizados (ATS) e chamar a atenção de recrutadores.

## Funcionalidades

* **Geração de CV Personalizado:** Adapta o conteúdo de um CV base (arquivos `CV_Base`) para corresponder aos requisitos de uma descrição de vaga.
* **Utilização da API do Gemini:** Usa a inteligência artificial do Gemini para reescrever e ajustar o texto do CV.
* **Formatação em PDF:** Cria CVs formatados profissionalmente usando a biblioteca `fpdf`.
* **Modularidade do Código:** O código é organizado em funções e classes para facilitar a manutenção e extensibilidade.
* **Configuração via `.env`:** As chaves de API e outras configurações sensíveis são gerenciadas através de arquivos `.env` para segurança.

## Instalação

1.  **Clone o repositório:**

    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd <NOME_DO_REPOSITORIO>
    ```

2.  **Crie um ambiente virtual (recomendado):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No Linux/macOS
    venv\Scripts\activate  # No Windows
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**

    * Crie um arquivo `.env` na raiz do projeto.
    * Adicione sua chave da API do Google Gemini:

        ```
        GOOGLE_API_KEY=SUA_CHAVE_AQUI
        ```

5.  **Configuraçao dos arquivos .txt**
    ```
    * No arquivo CV_Base, coloque as informaçoes do seu curriculo em formato txt.
    ```
    
6.  **Alterar a Vaga**
    ```
    * No arquivo main.py, na variavel job_description coloque a descriçao da vaga inteira ou o link da vaga no linkedin.
    ```
    
## Execução

Para executar o script, forneça a descrição da vaga como uma string e execute o script `main.py`:

```bash
python main.py