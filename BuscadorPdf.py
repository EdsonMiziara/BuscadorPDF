import os
import fitz
import google.generativeai as genai
import textwrap
import pytesseract # Interface para Tesseract
from PIL import Image

# --- Configuração do Gemini ---
# IMPORTANTE: Substitua 'SUA_CHAVE_DE_API' pela sua chave real do Gemini
# Obtenha uma chave em https://www.google.com/url?sa=E&source=gmail&q=https://makersuite.google.com/keys
API_KEY = 'AIzaSyBAJFq6EVElUhP6xd1UY40-qNICCILI7lw' # <-- COLOQUE SUA CHAVE AQUI

gemini_model = None
try:
    if API_KEY == 'SUA_CHAVE_DE_API':
        print("ERRO: Por favor, substitua 'SUA_CHAVE_DE_API' no código pela sua chave de API do Gemini.")
        print("Este script requer a configuração da chave para funcionar.")
        genai_configured = False
    else:
        genai.configure(api_key = API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        genai_configured = True
        print("Gemini API configurado com sucesso.")
        # Teste básico para verificar a conexão e a chave
        try:
            gemini_model.generate_content("Test connection", request_options={"timeout": 10})
            print("Conexão com Gemini API verificada.")
        except Exception as e:
            print(f"AVISO: Gemini API configurado, mas o teste de conexão falhou: {e}")
            print("Pode haver problemas de rede ou com a chave.")


except Exception as e:
    print(f"ERRO fatal ao configurar o Gemini API: {e}")
    print("Não será possível usar o Gemini para análise/busca.")
    genai_configured = False
# -----------------------------

def extract_text_from_pdf(pdf_path):
    """Extrai texto de um arquivo PDF usando PyMuPDF, com mensagens de progresso e erro."""
    doc = None 
    text = ""
    # print(f"  [DEBUG] Tentando abrir arquivo: {os.path.basename(pdf_path)}") # Removido DEBUG
    
    try:
        doc = fitz.open(pdf_path)
        # print(f"  [DEBUG] Arquivo '{os.path.basename(pdf_path)}' aberto com sucesso.") # Removido DEBUG

        if doc.is_encrypted:
             print(f"  [INFO] PDF '{os.path.basename(pdf_path)}' está criptografado.") # Mantido INFO
             try:
                 doc.authenticate("") 
                 if doc.is_encrypted: 
                     print(f"  [INFO] PDF '{os.path.basename(pdf_path)}' requer senha. Pulando.") # Mantido INFO
                     return None 
                 else:
                      print(f"  [INFO] PDF '{os.path.basename(pdf_path)}' descriptografado com senha vazia.") # Mantido INFO
             except Exception as auth_error:
                  print(f"  [ERRO AUTH] Falha ao tentar descriptografar '{os.path.basename(pdf_path)}': {auth_error}. Pulando.") # Mantido ERRO
                  return None 

        MAX_PAGES_TO_PROCESS = 50
        # print(f"  [DEBUG] Total de páginas em '{os.path.basename(pdf_path)}': {doc.page_count}. Processando até {min(doc.page_count, MAX_PAGES_TO_PROCESS)} páginas.") # Removido DEBUG

        for page_num in range(min(doc.page_count, MAX_PAGES_TO_PROCESS)):
            page = doc.load_page(page_num)
            try:
                # >>> SUA VERSÃO DE EXTRAÇÃO (TEXTO OU OCR) AQUI <<<
                # VERSÃO APENAS TEXTO SELECIONÁVEL:
                page_text = page.get_text()

                # VERSÃO OCR (se você configurou Tesseract e precisa):
                # pix = page.get_pixmap(dpi=300)
                # img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                # page_text = pytesseract.image_to_string(img)
                # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                
                if page_text.strip():
                   text += page_text + "\n" # Use "\n---\n" se for OCR
                # else:
                   # print(f"    [DEBUG] Página {page_num+1} sem texto extraível.") # Removido DEBUG

            except pytesseract.TesseractNotFoundError: # Se estiver usando OCR
                 print("\n[ERRO FATAL TESSERACT] Tesseract OCR não encontrado durante o processamento de página.") # Mantido ERRO FATAL
                 # Não feche o doc aqui, o finally cuidará disso
                 raise 

            except Exception as page_extract_error:
                print(f"  [ERRO PÁGINA] Falha na extração/OCR da página {page_num+1} em '{os.path.basename(pdf_path)}': {page_extract_error}") # Mantido ERRO
                pass 

        # print(f"  [DEBUG] Fim do loop de processamento de páginas para '{os.path.basename(pdf_path)}'.") # Removido DEBUG
        # O texto foi acumulado na variável 'text'

    except FileNotFoundError:
        print(f"\n[ERRO FILE NOT FOUND] Arquivo não encontrado: {pdf_path}. Pulando.") # Mantido ERRO
        return None 
    except fitz.EmptyFileError:
         print(f"\n[ERRO EMPTY FILE] Arquivo PDF vazio ou corrompido detectado por PyMuPDF: {os.path.basename(pdf_path)}. Pulando.") # Mantido ERRO
         return None 
    except Exception as e: 
        # Captura qualquer outro erro inesperado que aconteça *antes* do bloco finally
        print(f"  [ERRO ABRIR/PROCESSAR] Ocorreu um erro inesperado ANTES de fechar o documento para '{os.path.basename(pdf_path)}': {e}") # Mantido ERRO
        # Não retorne None aqui ainda

    finally:
        if doc is not None:
            try:
                doc.close()
                # print(f"  [DEBUG] Arquivo '{os.path.basename(pdf_path)}' fechado em finally.") # Removido DEBUG
            except Exception as close_error:
                 print(f"  [ERRO CLOSE] Ocorreu um erro ao tentar fechar o documento '{os.path.basename(pdf_path)}': {close_error}") # Mantido ERRO


    # --- Decisão Final de Retorno ---
    if text.strip():
        # print(f"  [DEBUG] Extração concluída para '{os.path.basename(pdf_path)}'. Retornando texto extraído ({len(text.strip())} caracteres).") # Removido DEBUG
        return text 
    else:
        # print(f"  [DEBUG] Nenhum texto útil extraído de '{os.path.basename(pdf_path)}'. Retornando None.") # Removido DEBUG
        # Esta mensagem é redundante se o chamador verificar por 'None'
        # print(f"  [INFO] Nenhum texto útil extraído de '{os.path.basename(pdf_path)}'.") # Opcional INFO
        return None

def gemini_search_and_analyze_pdfs(directory_path, search_term):
    """Usa Gemini para buscar e analisar PDFs em um diretório."""

    if not genai_configured or gemini_model is None:
        print("\nERRO: Configuração do Gemini API falhou. Não é possível executar a busca com Gemini.")
        return

    if not os.path.isdir(directory_path):
        print(f"Erro: O caminho '{directory_path}' não é um diretório válido.")
        return

    print(f"Buscando e analisando PDFs em '{directory_path}' usando Gemini para a busca por '{search_term}'...\n")

    found_pdfs = []
    
    entries = os.listdir(directory_path)
    pdf_files = [entry for entry in entries if entry.lower().endswith('.pdf') and os.path.isfile(os.path.join(directory_path, entry))]
    
    if not pdf_files:
        print("Nenhum arquivo PDF encontrado na pasta especificada.")
        return

    total_pdfs = len(pdf_files)
    processed_count = 0

    for filename in pdf_files:
        file_path = os.path.join(directory_path, filename)
        processed_count += 1
        print(f"({processed_count}/{total_pdfs}) Analisando: {filename}...")
            
        pdf_text = extract_text_from_pdf(file_path)

        if not pdf_text:
            print(f"  [INFO] Pulando '{filename}' - não foi possível extrair texto ou texto vazio.")
            continue

        # --- Etapa 1: Usar Gemini para Decidir se o PDF é Relevante (Filtragem) ---
        # Limitamos o texto enviado para a filtragem também
        MAX_CHARS_FOR_FILTER = 8000 # Limite para a chamada de filtragem
        text_for_filter = pdf_text[:MAX_CHARS_FOR_FILTER]
        
        # Prompt direto para obter uma resposta Sim/Não sobre a relevância
        filter_prompt = f"""Tarefa: Analise o texto a seguir para determinar se ele contém informações relevantes sobre a palavra-chave/frase fornecida.
        Responda APENAS com "Sim" se o texto for relevante ou "Não" caso contrário. Não adicione mais nada na primeira linha.

        Palavra-chave/Frase: "{search_term}"

        Texto (pode ser parcial):
        ---
        {text_for_filter}
        ---

        Resposta:
        """
        
        is_relevant = False
        filter_analysis = "Não avaliado pelo Gemini."

        try:
            # print("  Consultando Gemini para filtragem...")
            filter_response = gemini_model.generate_content(filter_prompt)
            
            if filter_response and filter_response.text:
                # Tenta parsear a resposta para Sim/Não
                response_text_lower = filter_response.text.strip().lower()
                
                # Verifica se a resposta começa com "sim"
                if response_text_lower.startswith("sim"):
                    is_relevant = True
                    # Opcional: Capturar o restante da resposta como uma breve explicação
                    filter_analysis = filter_response.text.strip()
                    # Remove "Sim" ou "sim" do início se houver
                    if filter_analysis.lower().startswith("sim"):
                         filter_analysis = filter_analysis[3:].strip(" .:") # Remove "Sim", pontos ou dois pontos

                elif response_text_lower.startswith("não"):
                     is_relevant = False
                     filter_analysis = filter_response.text.strip()
                     if filter_analysis.lower().startswith("não"):
                          filter_analysis = filter_analysis[3:].strip(" .:") # Remove "Não", pontos ou dois pontos
                else:
                    # Resposta inesperada do Gemini para a filtragem
                    print(f"  [AVISO] Resposta de filtragem inesperada do Gemini para '{filename}': '{filter_response.text.strip()}'")
                    filter_analysis = f"Resposta de filtragem inesperada: {filter_response.text.strip()}"
                    # Continuamos com is_relevant = False
                    
            else:
                print(f"  [AVISO] Gemini não retornou texto para a filtragem de '{filename}' (possível bloqueio de conteúdo ou erro).")
                filter_analysis = "Gemini não retornou texto para filtragem."


        except Exception as e:
             print(f"  [ERRO] Falha na chamada de filtragem ao Gemini para '{filename}': {e}")
             filter_analysis = f"Erro na chamada de filtragem: {e}"
             # Continuamos com is_relevant = False

        # --- Etapa 2: Se o PDF é Relevante, Pedir uma Análise Mais Detalhada ---
        if is_relevant:
            print(f"  -> Gemini identificou como relevante.")
            
            # Usamos um limite de texto possivelmente maior para a análise,
            # mas ainda dentro dos limites do modelo.
            MAX_CHARS_FOR_ANALYSIS = 15000 # Limite maior para análise, se necessário
            text_for_analysis = pdf_text[:MAX_CHARS_FOR_ANALYSIS] # Usa o texto extraído, limitado
            
            # Prompt para a análise específica do conteúdo relevante
            analysis_prompt = f"""Tarefa: O texto a seguir foi identificado como relevante para a palavra-chave/frase "{search_term}".
            Forneça uma breve análise (máximo 2-3 frases) explicando como o texto se relaciona com a palavra-chave/frase, baseada *somente* nas informações fornecidas no texto.
            Não adicione informações externas. Se a relação não for clara no texto fornecido, diga isso.

            Texto (pode ser parcial):
            ---
            {text_for_analysis}
            ---

            Análise:
            """
            
            detailed_analysis = "Análise não disponível." # Análise padrão se a segunda chamada falhar

            try:
                # print("  Consultando Gemini para análise detalhada...")
                analysis_response = gemini_model.generate_content(analysis_prompt)
                
                if analysis_response and analysis_response.text:
                     detailed_analysis = analysis_response.text.strip()
                     # print("  Análise detalhada recebida.")
                else:
                     detailed_analysis = "Gemini não retornou análise detalhada (possível bloqueio ou erro)."
                     # print("  A consulta de análise detalhada não retornou texto.")

            except Exception as e:
                 detailed_analysis = f"Erro na chamada de análise detalhada: {e}"
                 print(f"  [ERRO] Falha na chamada de análise detalhada ao Gemini para '{filename}': {e}")


            found_pdfs.append({
                'filename': filename,
                'gemini_relevance_note': filter_analysis, # Nota original da filtragem (Sim/Não + breve expl)
                'detailed_analysis': detailed_analysis # Análise mais longa
            })
        # else:
             # print(f"  -> Gemini identificou como não relevante. ({filter_analysis})")


    print("\n--- Resultados da Busca e Análise do Gemini ---")
    if found_pdfs:
        print(f"O Gemini identificou {len(found_pdfs)} arquivos PDF como relevantes para a busca por '{search_term}':")
        for pdf_info in found_pdfs:
            print(f"\nArquivo: {pdf_info['filename']}")
            print(f"Relevância (Nota do Gemini): {pdf_info['gemini_relevance_note']}")
            print(f"Análise Detalhada:")
            # Usa textwrap para formatar a análise detalhada
            print(textwrap.fill(pdf_info['detailed_analysis'], width=80))
            print("-" * 20) # Separador
                 
    else:
        print("O Gemini não identificou nenhum arquivo PDF como relevante na pasta especificada.")

# --- Execução ---
if __name__ == "__main__":
    print("Bem-vindo ao Buscador e Analisador de PDFs via Gemini!")
    print("Este script usa o Gemini para *decidir* quais PDFs são relevantes.")

    if not genai_configured:
        print("\nPor favor, configure sua chave de API do Gemini no código antes de executar.")
    else:
        pdf_directory = input("\nPor favor, digite o caminho completo da pasta onde estão seus PDFs: ")
        search_term = input("Digite a palavra, frase ou nome que você quer que o Gemini busque e analise: ")

        gemini_search_and_analyze_pdfs(pdf_directory, search_term)

        print("\nProcesso concluído.")