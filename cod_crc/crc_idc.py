import fitz
import re
import unicodedata

def extrair_dados(pdf_path, tipo_pdf, nome_do_arquivo_e_nome_do_aluno, nome_do_arquivo):
    """
    Extrai dados de certificados do CRC Protótipo,
    com a opção de usar o nome do arquivo como o nome do aluno.
    """
    dados_extraidos = {
        "Nome": [],
        "Curso": [],
        "Carga Horária": [],
        "Data": []
    }

    try:
        doc = fitz.open(pdf_path)

        if "Vários" in tipo_pdf:
            if "frente e verso" in tipo_pdf:
                paginas_para_ler = range(0, doc.page_count, 2)
            else:
                paginas_para_ler = range(doc.page_count)
        else:
            paginas_para_ler = [0]

        for page_num in paginas_para_ler:
            page = doc.load_page(page_num)
            texto_bruto = page.get_text()
            
            # Normalizar o texto para lidar com possíveis quebras de linha e espaços
            texto_limpo = re.sub(r'\s+', ' ', texto_bruto).strip()

            # Lógica para extrair o nome do aluno
            if nome_do_arquivo_e_nome_do_aluno:
                # Remove a extensão do arquivo e trata possíveis caracteres extras
                nome_bruto = nome_do_arquivo.replace(".pdf", "")
                # Substitui underlines e hifens por espaços e capitaliza cada palavra
                nome = " ".join([word.capitalize() for word in nome_bruto.replace("_", " ").replace("-", " ").split()])
            else:
                # Lógica de extração baseada no texto, como antes
                nome_match = re.search(r"que (.+?) concluiu o curso", texto_limpo, re.IGNORECASE)
                nome = nome_match.group(1).strip() if nome_match else "Não Encontrado"

            # O restante da lógica de extração permanece a mesma, pois está fora do bloco "if"
            curso_match = re.search(r"o curso de (.+?) com carga horária total", texto_limpo, re.IGNORECASE)
            curso = curso_match.group(1).strip() if curso_match else "Não Encontrado"

            carga_horaria_match = re.search(r"carga horária total de (.+?)\. Uma iniciativa", texto_limpo, re.IGNORECASE)
            carga_horaria = carga_horaria_match.group(1).strip() if carga_horaria_match else "Não Encontrado"
            
            data_match = re.search(r"(\d{1,2} de \w+ de \d{4})", texto_limpo)
            data = data_match.group(1).strip() if data_match else "Não Encontrada"

            dados_extraidos["Nome"].append(nome)
            dados_extraidos["Curso"].append(curso)
            dados_extraidos["Carga Horária"].append(carga_horaria)
            dados_extraidos["Data"].append(data)
            
        doc.close()

    except Exception as e:
        print(f"Erro ao processar o arquivo {nome_do_arquivo}: {e}")
        dados_extraidos["Nome"].append("ERRO")
        dados_extraidos["Curso"].append("ERRO")
        dados_extraidos["Carga Horária"].append("ERRO")
        dados_extraidos["Data"].append("ERRO")

    return dados_extraidos
