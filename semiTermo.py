import tkinter as tk
from tkinter import messagebox
import random
import string
import time
import mysql.connector

# ========================= CONFIGURAÇÕES =========================

DB_CADASTROS = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "cadastros"
}

DB_PALAVRAS = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "termo_palavras"
}

TABELAS = [f"palavras_{i}" for i in range(1, 7)]
COLUNA = "palavra"

NORMALIZAR = True
TAMANHO = 5
TENTATIVAS = 6

# ===== Cores =====
COR_FUNDO = "#242F50"
COR_VAZIO = "#101011"
COR_TEXTO = "#ffffff"
COR_CINZA = "#787c7e"
COR_AMARELO = "#d3ad69"
COR_AZUL = "#3aa394"  # acerto no lugar certo
COR_BOTAO = "#CC5656"
COR_SEGUNDA = "#29292C"

# ========================= FUNÇÕES DE BANCO =========================

def conectar_cadastros():
    return mysql.connector.connect(**DB_CADASTROS)

def conectar_palavras():
    return mysql.connector.connect(**DB_PALAVRAS)

def criar_tabelas_cadastros():
    try:
        conn = conectar_cadastros()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jogadores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                telefone VARCHAR(20) NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jogadas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                telefone VARCHAR(20) NOT NULL,
                tempo_segundos INT NOT NULL,
                tentativas_usadas INT NOT NULL,
                data_jogada TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Erro de Banco", f"Erro ao criar tabelas em 'cadastros':\n{e}")

def cadastrar_jogador(nome, telefone):
    try:
        conn = conectar_cadastros()
        cur = conn.cursor()
        cur.execute("INSERT INTO jogadores (nome, telefone) VALUES (%s, %s)", (nome, telefone))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao cadastrar jogador:\n{e}")
        return False

def verificar_login(nome, telefone):
    try:
        conn = conectar_cadastros()
        cur = conn.cursor()
        cur.execute("SELECT * FROM jogadores WHERE nome = %s AND telefone = %s", (nome, telefone))
        existe = cur.fetchone()
        cur.close()
        conn.close()
        return existe is not None
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao verificar login:\n{e}")
        return False

def salvar_jogada(nome, telefone, tempo_segundos, tentativas_usadas):
    try:
        conn = conectar_cadastros()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO jogadas (nome, telefone, tempo_segundos, tentativas_usadas) VALUES (%s, %s, %s, %s)",
            (nome, telefone, tempo_segundos, tentativas_usadas)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar jogada:\n{e}")
        return False

def carregar_palavras_do_banco():
    todas = []
    try:
        conn = conectar_palavras()
        cur = conn.cursor()
        for tabela in TABELAS:
            try:
                cur.execute(f"SELECT {COLUNA} FROM {tabela}")
            except Exception:
                continue
            rows = cur.fetchall()
            for (w,) in rows:
                if not isinstance(w, str):
                    continue
                w2 = w.strip()
                if NORMALIZAR:
                    w2 = ''.join(ch for ch in w2.upper() if ch in string.ascii_uppercase)
                if len(w2) == TAMANHO:
                    todas.append(w2)
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Erro de Banco", f"Erro ao carregar palavras:\n{e}")
        return []
    return list(dict.fromkeys(todas))

# ========================= FUNÇÕES DO JOGO =========================

def escolher_palavra(palavras, ultima=None):
    if not palavras:
        return None
    if len(palavras) == 1:
        return palavras[0]
    escolha = ultima
    while escolha == ultima:
        escolha = random.choice(palavras)
    return escolha

def avaliar_palpite(palpite, alvo):
    resultado = ['B'] * TAMANHO
    alvo_restante = list(alvo)
    for i in range(TAMANHO):
        if palpite[i] == alvo[i]:
            resultado[i] = 'G'
            alvo_restante[i] = None
    for i in range(TAMANHO):
        if resultado[i] == 'G':
            continue
        letra = palpite[i]
        if letra in alvo_restante:
            alvo_restante[alvo_restante.index(letra)] = None
            resultado[i] = 'Y'
    return resultado

# ========================= CLASSE DO JOGO =========================

class TermoApp:
    def __init__(self, root, jogador_nome, jogador_telefone):
        self.root = root
        self.jogador_nome = jogador_nome
        self.jogador_telefone = jogador_telefone

        self.root.title("DECIFRA - Tkinter + MySQL")
        self.root.configure(bg=COR_FUNDO)

        self.palavras = carregar_palavras_do_banco()
        self.alvo = None
        self.ultima_alvo = None
        self.tentativa_atual = 0
        self.jogo_ativo = True
        self.grade_entries = []
        self.teclado_botoes = {}

        self.start_time = None
        self.tempo_var = tk.StringVar()
        self.tempo_var.set("Tempo: 0s")

        # ===== TOPO =====
        top = tk.Frame(root, bg=COR_FUNDO)
        top.pack(pady=10)

        self.lbl_player = tk.Label(top, text=f"Jogador: {self.jogador_nome}", fg=COR_TEXTO, bg=COR_FUNDO, font=("Segoe UI", 18, "bold"))
        self.lbl_player.pack(side=tk.LEFT, padx=10)

        tk.Label(top, textvariable=self.tempo_var, fg=COR_TEXTO, bg=COR_FUNDO, font=("Segoe UI", 16)).pack(side=tk.LEFT, padx=10)

        tk.Button(top, text="Novo jogo", command=self.novo_jogo, bg=COR_BOTAO, fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Cadastrar Outro", command=self.voltar_para_cadastro, bg=COR_BOTAO, fg="white").pack(side=tk.LEFT, padx=5)

        # ===== GRADE =====
        grid = tk.Frame(root, bg=COR_FUNDO)
        grid.pack(pady=8)
        for r in range(TENTATIVAS):
            linha = []
            for c in range(TAMANHO):
                ent = tk.Entry(
                    grid, width=2, font=("Segoe UI", 36, "bold"),
                    bg=COR_VAZIO, fg=COR_TEXTO, bd=2, relief="solid",
                    justify="center"
                )
                ent.grid(row=r, column=c, padx=4, pady=4)
                # permitir clicar e focar cada célula:
                ent.bind("<Button-1>", lambda e, row=r, col=c: self.on_entry_click(e, row, col))
                linha.append(ent)
            self.grade_entries.append(linha)

        self.lbl_status = tk.Label(root, text="", fg=COR_TEXTO, bg=COR_FUNDO, font=("Segoe UI", 14))
        self.lbl_status.pack(pady=4)

        self.criar_teclado_virtual()
        self.novo_jogo()

        # Bind global: vamos interceptar teclas e impedir propagação padrão (retornando "break")
        self.root.bind_all("<Key>", self.keypress_event)

    # ================= FUNÇÕES DO JOGO =================

    def atualizar_tempo(self):
        if self.jogo_ativo and self.start_time:
            tempo_decorrido = int(time.time() - self.start_time)
            self.tempo_var.set(f"Tempo: {tempo_decorrido}s")
            self.root.after(1000, self.atualizar_tempo)

    def novo_jogo(self):
        if not self.palavras:
            self.palavras = carregar_palavras_do_banco()
        self.alvo = escolher_palavra(self.palavras, self.ultima_alvo)
        self.ultima_alvo = self.alvo
        self.tentativa_atual = 0
        self.jogo_ativo = True
        self.start_time = time.time()

        for r in range(TENTATIVAS):
            for c in range(TAMANHO):
                self.grade_entries[r][c].delete(0, tk.END)
                self.grade_entries[r][c].config(bg=COR_VAZIO)

        for botao in self.teclado_botoes.values():
            botao.config(bg=COR_VAZIO)

        self.lbl_status.config(text="Digite a palavra (o cursor anda sozinho; você pode clicar em qualquer casa).")
        self.grade_entries[0][0].focus_set()
        self.atualizar_tempo()

    def voltar_para_cadastro(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tela_cadastro_inicial(self.root)

    def enviar(self):
        if not self.jogo_ativo:
            return

        palpite = "".join(self.grade_entries[self.tentativa_atual][c].get().strip().upper() for c in range(TAMANHO))
        if len(palpite) != TAMANHO or not all(ch in string.ascii_uppercase for ch in palpite):
            self.lbl_status.config(text=f"A palavra deve ter {TAMANHO} letras válidas.")
            return
        if palpite not in self.palavras:
            self.lbl_status.config(text="Palavra não encontrada no banco.")
            return

        padroes = avaliar_palpite(palpite, self.alvo)

        for i, ch in enumerate(palpite):
            if padroes[i] == 'B':
                cor = COR_CINZA
            elif padroes[i] == 'Y':
                cor = COR_AMARELO
            else:
                cor = COR_AZUL

            self.grade_entries[self.tentativa_atual][i].config(bg=cor)
            self.atualizar_teclado(ch, cor)

        if palpite == self.alvo:
            tempo_total = int(time.time() - self.start_time)
            tentativas_usadas = self.tentativa_atual + 1
            salvar_jogada(self.jogador_nome, self.jogador_telefone, tempo_total, tentativas_usadas)
            self.lbl_status.config(text=f"Parabéns! Acertou em {tentativas_usadas} tentativas e {tempo_total}s.")
            self.jogo_ativo = False
            return

        self.tentativa_atual += 1
        if self.tentativa_atual >= TENTATIVAS:
            self.lbl_status.config(text=f"Fim de jogo! A palavra era {self.alvo}.")
            self.jogo_ativo = False
        else:
            self.lbl_status.config(text=f"Tentativa {self.tentativa_atual+1}/{TENTATIVAS}")
            self.grade_entries[self.tentativa_atual][0].focus_set()

    # ===== TECLADO VIRTUAL =====
    def criar_teclado_virtual(self):
        teclado_frame = tk.Frame(self.root, bg=COR_FUNDO)
        teclado_frame.pack(pady=12)

        linhas = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]

        for i, linha in enumerate(linhas):
            f = tk.Frame(teclado_frame, bg=COR_FUNDO)
            f.pack(pady=2)
            for letra in linha:
                b = tk.Button(
                    f, text=letra, width=4, height=2,
                    bg=COR_VAZIO, fg=COR_TEXTO,
                    font=("Segoe UI", 12, "bold"),
                    command=lambda l=letra: self.inserir_letra_virtual(l)
                )
                b.pack(side=tk.LEFT, padx=2)
                self.teclado_botoes[letra] = b

            if i == 2:
                tk.Button(f, text="Enter", width=6, height=2, bg=COR_SEGUNDA, fg="white",
                          font=("Segoe UI", 12, "bold"), command=self.enviar).pack(side=tk.LEFT, padx=2)
                tk.Button(f, text="⌫", width=6, height=2, bg=COR_SEGUNDA, fg="white",
                          font=("Segoe UI", 12, "bold"), command=self.backspace_virtual).pack(side=tk.LEFT, padx=2)

    def atualizar_teclado(self, letra, cor):
        letra = letra.upper()
        if letra not in self.teclado_botoes:
            return

        prioridade = {COR_AZUL: 3, COR_AMARELO: 2, COR_CINZA: 1, COR_VAZIO: 0}
        atual = self.teclado_botoes[letra].cget("bg")

        if prioridade[cor] > prioridade.get(atual, 0):
            self.teclado_botoes[letra].config(bg=cor)

    # ===== BACKSPACE E INSERÇÃO (com comportamento correto) =====
    def backspace_virtual(self):
        """Apaga na célula que está com foco; se já vazia, apaga a anterior e move foco."""
        if not self.jogo_ativo:
            return
        row = self.tentativa_atual
        focado = self.root.focus_get()
        # se foco não está em Entry da linha atual, força foco na última preenchida
        if focado not in self.grade_entries[row]:
            # procura da direita pra esquerda a primeira com conteúdo
            for c in reversed(range(TAMANHO)):
                if self.grade_entries[row][c].get() != "":
                    self.grade_entries[row][c].delete(0, tk.END)
                    self.grade_entries[row][c].focus_set()
                    return
            # nada para apagar: coloca foco na primeira casa
            self.grade_entries[row][0].focus_set()
            return

        for c in range(TAMANHO):
            if self.grade_entries[row][c] == focado:
                if self.grade_entries[row][c].get() != "":
                    # apaga a própria célula (não pula)
                    self.grade_entries[row][c].delete(0, tk.END)
                    self.grade_entries[row][c].focus_set()
                else:
                    # se já vazia, volta e apaga anterior
                    if c > 0:
                        self.grade_entries[row][c-1].delete(0, tk.END)
                        self.grade_entries[row][c-1].focus_set()
                break

    def inserir_letra_virtual(self, letra):
        """Chamado pelo botão virtual: insere na célula com foco (ou primeira vazia) e avança."""
        if not self.jogo_ativo:
            return
        row = self.tentativa_atual
        focado = self.root.focus_get()
        # se foco está em uma Entry da linha atual, insere lá
        if focado in self.grade_entries[row]:
            for c in range(TAMANHO):
                if self.grade_entries[row][c] == focado:
                    self.grade_entries[row][c].delete(0, tk.END)
                    self.grade_entries[row][c].insert(0, letra.upper())
                    # avança se não for última
                    if c < TAMANHO - 1:
                        self.grade_entries[row][c+1].focus_set()
                    return
        else:
            # coloca na primeira vazia (comportamento padrão)
            for c in range(TAMANHO):
                if self.grade_entries[row][c].get() == "":
                    self.grade_entries[row][c].insert(0, letra.upper())
                    if c < TAMANHO - 1:
                        self.grade_entries[row][c+1].focus_set()
                    else:
                        self.grade_entries[row][c].focus_set()
                    return

    def inserir_letra(self, letra):
        """Chamado por keypress_event (teclado físico). Reaproveita a lógica do virtual."""
        # reaproveita inserir_letra_virtual (mantém comportamento igual)
        return self.inserir_letra_virtual(letra)

    # ===== CLICK NAS CÉLULAS =====
    def on_entry_click(self, event, row, col):
        """Ao clicar numa célula, garante foco nessa célula."""
        # Apenas permite editar a linha ativa; se clicar em linha diferente ignora
        if row != self.tentativa_atual or not self.jogo_ativo:
            return "break"
        event.widget.focus_set()
        # posição do cursor interno do Entry não é necessária, pois tratamos o Entry como caixa única
        return

    # ===== TECLADO FÍSICO (intercepta e impede propagação padrão) =====
    def keypress_event(self, event):
        # sempre intercepta quando jogo ativo e evento relevante
        if not self.jogo_ativo:
            return  # deixa propagar normalmente (não interferir)
        # Teclas que queremos controlar:
        if event.keysym == "Return":
            self.enviar()
            return "break"   # impede ação padrão
        if event.keysym == "BackSpace":
            # chama nossa lógica de backspace e impede ação padrão do Entry
            self.backspace_virtual()
            return "break"
        # letras: impedir inserção padrão e tratar manualmente (assim autotransição de foco funciona)
        ch = event.char
        if ch and ch.upper() in string.ascii_uppercase:
            self.inserir_letra(ch.upper())
            return "break"
        # para qualquer outra tecla (setas, etc.), não interferir (deixa propagar)
        return

# ========================= RANKING =========================

def carregar_ranking():
    try:
        conn = conectar_cadastros()
        cur = conn.cursor()
        cur.execute("""
            SELECT nome, telefone, tentativas_usadas, tempo_segundos, data_jogada
            FROM jogadas
            ORDER BY tentativas_usadas ASC, tempo_segundos ASC
            LIMIT 10
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        messagebox.showerror("Erro de Banco", f"Erro ao carregar ranking:\n{e}")
        return []

def mostrar_ranking():
    ranking = carregar_ranking()
    if not ranking:
        messagebox.showinfo("Ranking", "Nenhuma jogada registrada ainda!")
        return

    win = tk.Toplevel()
    win.title("Ranking DECIFRA")
    win.configure(bg=COR_FUNDO)
    tk.Label(win, text="🏆 Ranking DECIFRA 🏆", fg=COR_TEXTO, bg=COR_FUNDO,
             font=("Segoe UI", 18, "bold")).pack(pady=10)

    cabecalho = tk.Label(win, text=f"{'Pos':<4} {'Nome':<20} {'Telefone':<15} {'Tent':<5} {'Tempo(s)':<8}", 
                         fg=COR_TEXTO, bg=COR_FUNDO, font=("Segoe UI", 12, "bold"))
    cabecalho.pack(pady=5)

    for i, (nome, telefone, tentativas, tempo, data) in enumerate(ranking, 1):
        linha = tk.Label(win, text=f"{i:<4} {nome:<20} {telefone:<15} {tentativas:<5} {tempo:<8}", 
                         fg=COR_TEXTO, bg=COR_FUNDO, font=("Segoe UI", 12))
        linha.pack()

# ========================= TELA DE CADASTRO / LOGIN =========================

def tela_cadastro_inicial(root):
    root.title("Cadastro / Login")
    root.configure(bg=COR_FUNDO)

    frame = tk.Frame(root, bg=COR_FUNDO, width=400, height=300)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="Bem-vindo ao DECIFRA", fg=COR_TEXTO, bg=COR_FUNDO,
             font=("Segoe UI", 18, "bold")).pack(pady=10)

    tk.Label(frame, text="Nome:", fg=COR_TEXTO, bg=COR_FUNDO,
             font=("Segoe UI", 14)).pack(anchor="w", padx=12)
    nome_entry = tk.Entry(frame, font=("Segoe UI", 14))
    nome_entry.pack(fill="x", padx=12, pady=4)

    tk.Label(frame, text="Telefone:", fg=COR_TEXTO, bg=COR_FUNDO,
             font=("Segoe UI", 14)).pack(anchor="w", padx=12)
    telefone_entry = tk.Entry(frame, font=("Segoe UI", 14))
    telefone_entry.pack(fill="x", padx=12, pady=4)

    tk.Button(root, text="Ranking", command=mostrar_ranking,
          bg=COR_BOTAO, fg="white", font=("Segoe UI", 14)).pack(pady=10)

    def confirmar_cadastro():
        nome = nome_entry.get().strip()
        telefone = telefone_entry.get().strip()
        if not nome or not telefone:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        if cadastrar_jogador(nome, telefone):
            iniciar_jogo(root, nome, telefone)

    def confirmar_login():
        nome = nome_entry.get().strip()
        telefone = telefone_entry.get().strip()
        if not nome or not telefone:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        if verificar_login(nome, telefone):
            iniciar_jogo(root, nome, telefone)
        else:
            messagebox.showerror("Erro", "Jogador não encontrado!")

    btn_frame = tk.Frame(frame, bg=COR_FUNDO)
    btn_frame.pack(pady=12)

    tk.Button(btn_frame, text="Cadastrar", command=confirmar_cadastro,
              bg=COR_BOTAO, fg="white", font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=6)
    tk.Button(btn_frame, text="Login", command=confirmar_login,
              bg=COR_BOTAO, fg="white", font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=6)

# ========================= INICIAR JOGO =========================

def iniciar_jogo(root, nome, telefone):
    for widget in root.winfo_children():
        widget.destroy()
    TermoApp(root, nome, telefone)

# ========================= MAIN =========================

if __name__ == "__main__":
    criar_tabelas_cadastros()
    root = tk.Tk()
    root.geometry("1920x1080")
    tela_cadastro_inicial(root)
    root.mainloop()
