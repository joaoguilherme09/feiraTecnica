# 🎮 Termo — Jogo de Adivinhação de Palavras (Python + MySQL)

Bem-vindo ao **Termo**, um jogo onde o objetivo é adivinhar uma palavra secreta escolhida aleatoriamente do banco de dados.  
Este projeto foi criado com foco em **lógica de programação**, **tratamento de strings**, e **integração com MySQL** usando Python.

---

## 🧠 Objetivo do Jogo

- O programa seleciona uma palavra secreta do banco de dados.
- O jogador deve tentar descobri-la em um número limitado de tentativas.
- O tempo gasto, número de tentativas e nome do jogador são registrados.
- No final, é gerado um ranking com os jogadores que tiveram o melhor desempenho.

É uma forma divertida de aprender programação, banco de dados e boas práticas de desenvolvimento. 🚀

---

## 🛠 Tecnologias Utilizadas

| Tecnologia | Função |
|-----------|--------|
| 🐍 **Python** | Lógica do jogo |
| 🗄 **MySQL** (via XAMPP) | Armazenamento das palavras e registros |
| 🔌 **PyMySQL** | Comunicação Python ↔ MySQL |
| 📂 **Visual Studio Code** | Ambiente de desenvolvimento |

---

## 📦 Instalação de Bibliotecas

Antes de rodar o projeto, execute os comandos necessários:
pip install pymysql
pip install unicodedata



⚠️ Caso o código apresente erro de importação, basta instalar escrevendo:
Copiar código:
pip install nome_da_biblioteca


---

🚦 Passo a Passo Para Rodar o Projeto
✔️ 1️⃣ Ativar o MySQL
Abra o XAMPP e ligue:
✔️ MySQL

---
 

✔️ 2️⃣ Criar os bancos de dados no MySQL Workbench


Copiar código:
CREATE SCHEMA termo_palavras;


Copiar código:
CREATE DATABASE IF NOT EXISTS cadastros;
USE cadastros;

CREATE TABLE IF NOT EXISTS jogadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    tempo_segundos INT NOT NULL,
    tentativas_usadas INT NOT NULL,
    data_jogada TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


---

✔️ 3️⃣ Abrir o projeto no VS Code
Abra o Visual Studio Code

Clique em Open Folder

Selecione a pasta chamada TERMŌ


---

✔️ 4️⃣ Instalar dependências (caso falte alguma)
No terminal do VS Code, execute:
 
pip install pymysql
pip install unicodedata

---


✔️ 5️⃣ Rodar o script banco.py
Esse script irá ler todas as palavras e criar as tabelas no banco automaticamente.

A saída esperada é parecida com:

🔍 Lendo arquivo...
📄 Palavras lidas do arquivo: 6033
✅ Palavras únicas após limpeza: 5433
📌 Criando tabela palavras_1...
📌 Criando tabela palavras_2...
📌 Criando tabela palavras_3...
📌 Criando tabela palavras_4...
📌 Criando tabela palavras_5...
📌 Criando tabela palavras_6...
✅ Inseridas 5433 palavras em 6 tabelas!
🏁 Concluído!


---

✔️ 6️⃣ Executar o jogo
Agora rode:
python semiTermo.py
