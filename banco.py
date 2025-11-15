import pymysql 
import unicodedata

# Função para remover acentos
def remover_acentos(txt):
    return ''.join(
        c for c in unicodedata.normalize('NFD', txt)
        if unicodedata.category(c) != 'Mn'
    )

# Conectar ao MySQL (ajuste usuário e senha)
conexao = pymysql.connect(
    host="127.0.0.1",
    user="root",       # seu usuário
    password="",       # sua senha se precisar  ve qual a senha do seu pc na escola não tem senha dai dixa só as ""
    database="termo_palavras",
    charset="utf8mb4"   
)
cursor = conexao.cursor()

# Ler arquivo
print("🔍 Lendo arquivo...")
with open("resultado2.txt", "r", encoding="utf-8") as f:
    conteudo = f.read()

# Separar palavras
palavras = conteudo.split()
print(f"📄 Palavras lidas do arquivo: {len(palavras)}")

# Limpar e normalizar
palavras_limpa = []
for p in palavras:
    p_limpa = remover_acentos(p.strip().lower())
    if p_limpa:
        palavras_limpa.append(p_limpa)

# Remover duplicatas mantendo ordem
palavras_unicas = list(dict.fromkeys(palavras_limpa))
total = len(palavras_unicas)
print(f"✅ Palavras únicas após limpeza: {total}")

# Função para criar tabela
def criar_tabela(nome_tabela):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `{nome_tabela}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            palavra VARCHAR(50) UNIQUE
        )
    """)

# Se não houver palavras, cria tabela vazia para teste
if total == 0:
    print("⚠ Nenhuma palavra encontrada! Criando tabela vazia para teste...")
    criar_tabela("palavras_1")
else:
    batch_size = 1000
    num_tabelas = (total + batch_size - 1) // batch_size  # ceil

    for i in range(num_tabelas):
        tabela_nome = f"palavras_{i + 1}"
        print(f"📌 Criando tabela {tabela_nome}...")
        criar_tabela(tabela_nome)
        inicio = i * batch_size
        fim = inicio + batch_size
        lote = palavras_unicas[inicio:fim]

        for palavra in lote:
            try:
                cursor.execute(f"INSERT IGNORE INTO `{tabela_nome}` (palavra) VALUES (%s)", (palavra,))
            except Exception as e:
                print(f"Erro ao inserir '{palavra}' na tabela {tabela_nome}: {e}")

    conexao.commit()
    print(f"✅ Inseridas {total} palavras em {num_tabelas} tabelas!")

cursor.close()
conexao.close()
print("🏁 Concluído!")