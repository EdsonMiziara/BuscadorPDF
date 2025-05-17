# BuscadorPDF Inteligente com Gemini AI

![Python version](https://img.shields.io/badge/Python-3.x-blue.svg)

## 📚 Sobre o Projeto

O **BuscadorPDF Inteligente** é uma ferramenta em Python projetada para facilitar a busca e análise de documentos PDF em uma pasta local. Ele vai além da busca simples por nome de arquivo, permitindo encontrar documentos com base no **conteúdo** interno, utilizando o poder da inteligência artificial **Google Gemini** para filtrar e analisar a relevância dos resultados.

A **inspiração direta para este projeto veio da dificuldade enfrentada pela minha namorada em sua pesquisa de Iniciação Científica em História**. Ela passava muito tempo buscando manualmente por informações específicas em uma vasta coleção de PDFs, perdendo tempo que poderia ser dedicado à análise e escrita. Este projeto foi criado com o objetivo de **resolver esse problema**, automatizando e aprimorando a busca em documentos para que ela (e outros pesquisadores) possam encontrar a informação certa de forma mais rápida e eficiente.

## ✨ Funcionalidades

* **Busca em Diretórios:** Analisa todos os arquivos PDF dentro de uma pasta especificada.
* **Busca Flexível:** Encontra PDFs pela palavra-chave no **nome do arquivo** ou no **conteúdo** interno.
* **Extração Robusta de Texto:** Utiliza a biblioteca PyMuPDF para extrair texto de diversos tipos de PDFs.
* **OCR Opcional:** Pode processar PDFs escaneados (baseados em imagem) utilizando o Tesseract OCR (requer instalação separada do Tesseract).
* **Filtragem Inteligente com Gemini AI:** Envia trechos do texto extraído para o modelo Google Gemini para avaliar a relevância para sua busca.
* **Análise de Conteúdo com Gemini AI:** Para os PDFs considerados relevantes, o Gemini fornece uma breve análise sobre a relação do conteúdo com a palavra-chave buscada.
* **Interface por Terminal:** Ferramenta simples e direta para usar via linha de comando.

## 🚀 Como Funciona (Resumo)

O script solicita o caminho da pasta contendo os PDFs e a palavra-chave de busca. Ele itera sobre cada arquivo `.pdf` na pasta, tenta extrair seu texto. Se a funcionalidade Gemini estiver ativada, ele envia um trecho desse texto para o modelo Gemini com um prompt específico para determinar se o documento é relevante para a busca. Para os documentos identificados como relevantes pelo Gemini, uma nova chamada à API é feita para obter uma análise curta. Os resultados são exibidos no terminal.

## ⚙️ Requisitos

* **Python 3.7+**
* **Bibliotecas Python:** `PyMuPDF`, `google-generativeai`, `Pillow`.
* **Google Gemini API Key:** Necessária para utilizar as funcionalidades de IA. Você pode obter uma em [Google AI Studio](https://makersuite.google.com/keys).
* **Tesseract OCR Engine (Opcional):** Necessário SOMENTE se você precisa processar PDFs que são **documentos escaneados** (baseados em imagem). Veja instruções de instalação para Windows [aqui](https://github.com/UB-Mannheim/tesseract/wiki).

## 🔧 Instalação

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/SeuUsuario/NomeDoSeuRepositorio.git](https://github.com/EdsonMiziara/BuscadorPDF)
    cd NomeDoSeuRepositorio
    ```

2.  **Instale as Dependências Python:**
    É recomendado usar um ambiente virtual (`venv`).
    ```bash
    # Crie o ambiente virtual (se ainda não tiver um)
    python -m venv venv
    
    # Ative o ambiente virtual
    # No Windows:
    .\venv\Scripts\activate
    # No macOS/Linux:
    source venv/bin/activate
    
    # Instale as bibliotecas
    pip install -r requirements.txt

3.  **Instale o Tesseract OCR (Opcional - Para PDFs Escaneados):**
    Baixe e execute o instalador para o seu sistema operacional na [página de releases do Tesseract no GitHub](https://github.com/UB-Mannheim/tesseract/wiki). Certifique-se de **adicionar o Tesseract ao PATH do sistema** durante a instalação (recomendado). Se não adicionar ao PATH, você precisará configurar o caminho no script Python.

## 🔑 Configuração

1.  **Obtenha sua Chave de API do Gemini:** Se você ainda não tem uma, acesse o [Google AI Studio](https://makersuite.google.com/keys) e crie sua chave.
2.  **Configure a Chave no Script:** Abra o arquivo principal do script (`seu_script.py`, ou o nome que você deu a ele) e substitua `'SUA_CHAVE_DE_API'` pela sua chave real na seção de configuração do Gemini no início do arquivo:

    ```python
    # --- Configuração do Gemini ---
    API_KEY = 'SUA_CHAVE_DE_API' # <-- COLOQUE SUA CHAVE AQUI
    # ... resto da configuração ...
    ```
3.  **Configure o Caminho do Tesseract (Opcional - Se NÃO adicionou ao PATH):** Se você instalou o Tesseract mas **não** o adicionou ao PATH do sistema, você precisará descomentar a linha no script principal e fornecer o caminho completo para o executável `tesseract.exe`.

    ```python
    # --- Configuração do Tesseract (Opcional se adicionou ao PATH) ---
    # Se o Tesseract NÃO foi adicionado ao PATH, descomente e ajuste:
    # import pytesseract
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Caminho\Para\Tesseract-OCR\tesseract.exe'
    # -----------------------------------------------------------------
    ```

## 🚀 Como Usar

1.  **Ative seu ambiente virtual** (se estiver usando um):
    ```bash
    # No Windows:
    .\venv\Scripts\activate
    # No macOS/Linux:
    source venv/bin/activate
    ```
2.  **Execute o script principal** no terminal:
    ```bash
    python BuscadorPdf.py
    ```

3.  Siga as instruções no terminal:
    * Digite o **caminho completo da pasta** onde estão seus arquivos PDF e pressione Enter.
    * Digite a **palavra, frase ou nome** que você quer buscar e que o Gemini deve analisar a relevância e pressione Enter.

O script irá processar os arquivos e exibir os resultados encontrados com base na sua busca e na análise do Gemini.

## ⚠️ Notas Importantes e Limitações

* **Uso da API do Gemini:** O uso da API pode ter custos associados dependendo do seu plano e volume de requisições. Consulte a documentação do Google Gemini para detalhes de precificação.
* **Limite de Tokens:** Modelos de linguagem têm limites na quantidade de texto que podem processar por chamada. PDFs muito longos terão seu texto truncado (as primeiras X páginas/caracteres serão usados), o que significa que o Gemini não verá o conteúdo completo.
* **Precisão do OCR:** Para PDFs escaneados, a precisão da extração de texto depende da qualidade da imagem no PDF e do desempenho do Tesseract OCR.
* **Dependência da Extração:** A qualidade da análise do Gemini depende diretamente da qualidade do texto que foi extraído do PDF.
* **Velocidade:** Processar muitos arquivos ou arquivos longos, especialmente com OCR, pode levar tempo.

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues para relatar bugs, sugerir melhorias ou enviar Pull Requests.

## Autor

* EdsonMiziara


