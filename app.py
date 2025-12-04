# app.py (VERSÃO FINAL MAXIMIZADA E REFINADA, COM CORREÇÃO DE GRID/PACK)
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk 

# Importações completas do database
from database import (
    adicionar_empregado, listar_empregados, atualizar_empregado, deletar_empregado, 
    buscar_empregado_por_id, adicionar_tarefa, listar_tarefas, atualizar_tarefa, 
    deletar_tarefa, buscar_tarefa_por_id, listar_proximas_tarefas 
)

# --- Estrutura de Telas (Views) ---

class FlowSchedulerApp(ttk.Window):
    """Classe principal da aplicação Desktop Flow Scheduler."""
    def __init__(self):
        super().__init__(themename="cosmo") 
        self.title("Flow Scheduler - Gestão de Carga de Trabalho")
        
        # MAXIMIZAÇÃO (Tela expandida)
        self.state('zoomed') 
        
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True) # O container principal AINDA usa pack
        self.frames = {}
        for F in (DashboardView, EmpregadosView, TarefasView):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[page_name] = frame
        
        self.show_frame("DashboardView")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "DashboardView":
             frame.atualizar_preview() 
        frame.tkraise()

    def go_to_home(self):
        self.show_frame("DashboardView")

class BaseView(ttk.Frame):
    """Classe base para todas as Views (Telas)."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # CORREÇÃO CRÍTICA: O botão agora usa GRID (Tiramos o pack)
        home_button = ttk.Button(self, text="<< Dashboard Principal", command=controller.go_to_home, bootstyle="secondary")
        home_button.grid(row=0, column=0, pady=10, padx=10, sticky="nw")
        
        # Configuração do Grid para suportar o botão Home e o conteúdo abaixo
        self.grid_rowconfigure(0, weight=0) # Linha do botão Home (não expande)
        self.grid_rowconfigure(1, weight=1) # Linha do conteúdo principal (expande)
        self.grid_columnconfigure(0, weight=1) # Coluna de conteúdo expande

class DashboardView(BaseView):
    """Tela principal com opções de navegação e visualização de status."""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Usamos um Frame interno para o conteúdo principal (abaixo do botão Home)
        main_content_frame = ttk.Frame(self)
        main_content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20) 

        # Configuração do Grid interno para a Divisão (Navegação Col 0, Preview Col 1)
        main_content_frame.grid_rowconfigure(0, weight=1)
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_columnconfigure(1, weight=1)

        # --- Painel de Navegação (Coluna 0) ---
        nav_frame = ttk.Frame(main_content_frame)
        nav_frame.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")
        
        # Centralizando os elementos dentro do nav_frame 
        nav_frame.grid_rowconfigure(0, weight=1) 
        nav_frame.grid_rowconfigure(4, weight=1) 
        nav_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(nav_frame, text="DASHBOARD PRINCIPAL", font=("Arial", 24)).grid(row=1, column=0, pady=20)
        
        ttk.Button(nav_frame, text="Gerenciar Empregados", bootstyle="primary",
                   command=lambda: controller.show_frame("EmpregadosView")).grid(row=2, column=0, pady=10, sticky="ew")
        
        ttk.Button(nav_frame, text="Gerenciar Tarefas e Atribuições", bootstyle="primary",
                   command=lambda: controller.show_frame("TarefasView")).grid(row=3, column=0, pady=10, sticky="ew")

        # --- Painel de Preview de Tarefas (Coluna 1) ---
        self.preview_frame = ttk.Frame(main_content_frame, bootstyle="info", width=350)
        self.preview_frame.grid(row=0, column=1, padx=50, pady=50, sticky="nsew")
        self.preview_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(self.preview_frame, text="🚨 PRÓXIMAS TAREFAS PENDENTES 🚨", font=("Arial", 14), bootstyle="inverse-info").grid(row=0, column=0, sticky="ew", pady=(10, 5), padx=5)
        
        self.lista_urgente = ttk.Frame(self.preview_frame)
        self.lista_urgente.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def atualizar_preview(self):
        """Busca as tarefas urgentes e as exibe no painel lateral."""
        
        for widget in self.lista_urgente.winfo_children():
            widget.destroy()
            
        tarefas = listar_proximas_tarefas()
        
        if not tarefas:
            ttk.Label(self.lista_urgente, text="🎉 Nenhuma tarefa urgente encontrada!").pack(pady=20)
            return

        # Cabeçalhos
        ttk.Label(self.lista_urgente, text="Prazo", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        ttk.Label(self.lista_urgente, text="Tarefa", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, sticky="w")
        ttk.Label(self.lista_urgente, text="Responsável", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, sticky="w")

        # Exibe as tarefas
        for i, t in enumerate(tarefas, start=1):
            cor = "danger" if i == 1 else "warning" if i == 2 else "light"
            
            ttk.Label(self.lista_urgente, text=t.prazo, font=("Arial", 9), bootstyle=cor).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            ttk.Label(self.lista_urgente, text=t.titulo, font=("Arial", 9)).grid(row=i, column=1, padx=5, pady=2, sticky="w")
            ttk.Label(self.lista_urgente, text=t.empregado_nome or "N/A", font=("Arial", 9)).grid(row=i, column=2, padx=5, pady=2, sticky="w")

# --- EmpregadosView ---
class EmpregadosView(BaseView):
    """Tela para CRUD de Empregados."""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        # Usamos um Frame interno (content_frame) para usar .pack() sem conflito com o Grid da BaseView
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew") 
        
        ttk.Label(content_frame, text="GERENCIAMENTO DE EMPREGADOS", font=("Arial", 18)).pack(pady=10)

        colunas = ('id', 'nome', 'cargo', 'email')
        self.tree = ttk.Treeview(content_frame, columns=colunas, show='headings', bootstyle="info") 
        self.tree.heading('id', text='ID', anchor=tk.W)
        self.tree.heading('nome', text='Nome')
        self.tree.heading('cargo', text='Cargo')
        self.tree.heading('email', text='Email')
        self.tree.column('id', width=40, anchor=tk.CENTER)
        self.tree.column('nome', width=200)
        self.tree.column('cargo', width=150)
        self.tree.column('email', width=200)
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)

        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Adicionar Novo", bootstyle="success",
                   command=self.abrir_formulario_adicionar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar Selecionado", bootstyle="warning",
                   command=self.abrir_formulario_edicao).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Excluir Selecionado", bootstyle="danger",
                   command=self.deletar_empregado).pack(side=tk.LEFT, padx=5)
        
        self.atualizar_lista()

    # ... (Restante dos métodos da EmpregadosView) ...
    def atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        empregados = listar_empregados()
        
        if not empregados:
            self.tree.insert('', tk.END, values=('Nenhum empregado cadastrado.', '', '', ''), tags=('empty',))
        else:
            for e in empregados:
                self.tree.insert('', tk.END, values=(e.id, e.nome, e.cargo, e.email))
    
    def abrir_formulario_adicionar(self):
        janela_form = tk.Toplevel(self)
        janela_form.title("Adicionar Empregado")
        janela_form.transient(self.controller)
        
        ttk.Label(janela_form, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        nome_entry = ttk.Entry(janela_form)
        nome_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(janela_form, text="Cargo:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        cargo_entry = ttk.Entry(janela_form)
        cargo_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(janela_form, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        email_entry = ttk.Entry(janela_form)
        email_entry.grid(row=2, column=1, padx=5, pady=5)

        def submit():
            nome = nome_entry.get()
            cargo = cargo_entry.get()
            email = email_entry.get()
            
            if nome and cargo:
                if adicionar_empregado(nome, cargo, email):
                    messagebox.showinfo("Sucesso", "Empregado adicionado com sucesso!", parent=janela_form)
                    self.atualizar_lista()
                    janela_form.destroy()
                else:
                    messagebox.showerror("Erro", "Falha ao adicionar empregado no DB.", parent=janela_form)
            else:
                messagebox.showwarning("Atenção", "Preencha Nome e Cargo.", parent=janela_form)

        ttk.Button(janela_form, text="Salvar", command=submit, bootstyle="success").grid(row=3, column=0, columnspan=2, pady=15)
    
    def abrir_formulario_edicao(self):
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione um empregado para editar.")
            return

        item_selecionado = self.tree.item(selecao[0], 'values')
        empregado_id = item_selecionado[0]
        empregado = buscar_empregado_por_id(empregado_id)

        if not empregado:
            messagebox.showerror("Erro", "Empregado não encontrado.")
            return

        janela_form = tk.Toplevel(self)
        janela_form.title(f"Editar Empregado: {empregado.nome}")
        janela_form.transient(self.controller)
        
        ttk.Label(janela_form, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        nome_entry = ttk.Entry(janela_form)
        nome_entry.insert(0, empregado.nome)
        nome_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(janela_form, text="Cargo:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        cargo_entry = ttk.Entry(janela_form)
        cargo_entry.insert(0, empregado.cargo)
        cargo_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(janela_form, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        email_entry = ttk.Entry(janela_form)
        email_entry.insert(0, empregado.email)
        email_entry.grid(row=2, column=1, padx=5, pady=5)

        def submit_edicao():
            novo_nome = nome_entry.get()
            novo_cargo = cargo_entry.get()
            novo_email = email_entry.get()
            
            if novo_nome and novo_cargo:
                if atualizar_empregado(empregado_id, novo_nome, novo_cargo, novo_email):
                    messagebox.showinfo("Sucesso", "Empregado atualizado com sucesso!", parent=janela_form)
                    self.atualizar_lista()
                    janela_form.destroy()
                else:
                    messagebox.showerror("Erro", "Falha ao atualizar empregado no DB.", parent=janela_form)
            else:
                messagebox.showwarning("Atenção", "Preencha Nome e Cargo.", parent=janela_form)

        ttk.Button(janela_form, text="Salvar Alterações", command=submit_edicao, bootstyle="warning").grid(row=3, column=0, columnspan=2, pady=15)
        
    def deletar_empregado(self):
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione um empregado para deletar.")
            return

        item_selecionado = self.tree.item(selecao[0], 'values')
        empregado_id = item_selecionado[0]
        nome_empregado = item_selecionado[1]

        confirmar = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja DELETAR o empregado: {nome_empregado} (ID: {empregado_id})?\nEsta ação é irreversível.",
            icon='warning'
        )
        
        if confirmar:
            if deletar_empregado(empregado_id):
                messagebox.showinfo("Sucesso", f"Empregado {nome_empregado} deletado com sucesso!")
                self.atualizar_lista()
            else:
                messagebox.showerror("Erro", "Falha ao deletar empregado no DB.")

# --- TarefasView ---
class TarefasView(BaseView):
    """Tela para CRUD de Tarefas."""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        # Usamos um Frame interno (content_frame) para usar .pack() sem conflito com o Grid da BaseView
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew") # Colocamos o conteúdo abaixo do botão Home
        
        ttk.Label(content_frame, text="GERENCIAMENTO DE TAREFAS", font=("Arial", 18)).pack(pady=10)

        colunas = ('id', 'titulo', 'prazo', 'empregado', 'concluida')
        self.tree = ttk.Treeview(content_frame, columns=colunas, show='headings', bootstyle="info")
        self.tree.heading('id', text='ID', anchor=tk.W)
        self.tree.heading('titulo', text='Título')
        self.tree.heading('prazo', text='Prazo')
        self.tree.heading('empregado', text='Atribuído a')
        self.tree.heading('concluida', text='Concluída')
        self.tree.column('id', width=40, anchor=tk.CENTER)
        self.tree.column('titulo', width=250)
        self.tree.column('prazo', width=100, anchor=tk.CENTER)
        self.tree.column('empregado', width=150)
        self.tree.column('concluida', width=80, anchor=tk.CENTER)
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree.tag_configure('concluida', background='#e0ffe0')
        self.tree.tag_configure('pendente', background='#ffdbdb')

        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Nova Tarefa", bootstyle="success",
                   command=self.abrir_formulario_adicionar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar Tarefa", bootstyle="warning",
                   command=self.abrir_formulario_edicao).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Deletar Tarefa", bootstyle="danger",
                   command=self.deletar_tarefa).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Marcar/Desmarcar Concluída", bootstyle="info",
                   command=self.toggle_concluida).pack(side=tk.LEFT, padx=5)
        
        self.atualizar_lista()

    def atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        tarefas = listar_tarefas()
        
        if not tarefas:
            self.tree.insert('', tk.END, values=('Nenhuma tarefa cadastrada.', '', '', '', ''), tags=('empty',))
        else:
            for t in tarefas:
                empregado_nome = t.empregado_nome if t.empregado_nome else "Não Atribuído"
                status = "✅ SIM" if t.concluida else "❌ NÃO"
                
                self.tree.insert('', tk.END, 
                                 values=(t.id, t.titulo, t.prazo, empregado_nome, status),
                                 tags=('concluida' if t.concluida else 'pendente',)
                                )

    def _carregar_empregados_para_combo(self):
        empregados = listar_empregados()
        self.empregados_dict = {f"{e.nome} ({e.cargo})": e.id for e in empregados}
        empregado_nomes = ["Não Atribuído"] + list(self.empregados_dict.keys())
        return empregado_nomes

    def _criar_formulario_tarefa(self, janela_pai, tarefa_item=None):
        janela_form = tk.Toplevel(janela_pai)
        janela_form.title("Editar Tarefa" if tarefa_item else "Adicionar Tarefa")
        janela_form.transient(self.controller)
        
        opcoes_empregados = self._carregar_empregados_para_combo()

        ttk.Label(janela_form, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        titulo_entry = ttk.Entry(janela_form, width=40)
        titulo_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(janela_form, text="Descrição:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        descricao_entry = tk.Text(janela_form, height=4, width=30)
        descricao_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(janela_form, text="Prazo (AAAA-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        prazo_entry = ttk.Entry(janela_form)
        prazo_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(janela_form, text="Atribuir a:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        empregado_var = tk.StringVar(janela_form)
        empregado_combo = ttk.Combobox(janela_form, textvariable=empregado_var, values=opcoes_empregados, state="readonly")
        empregado_combo.grid(row=3, column=1, padx=5, pady=5)
        empregado_combo.set("Não Atribuído")

        concluida_var = tk.BooleanVar(janela_form)
        if tarefa_item:
            tarefa_id = tarefa_item[0]
            tarefa_completa = buscar_tarefa_por_id(tarefa_id) 

            ttk.Label(janela_form, text="Concluída:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
            concluida_check = ttk.Checkbutton(janela_form, variable=concluida_var, bootstyle="round-toggle")
            concluida_check.grid(row=4, column=1, padx=5, pady=5, sticky="w")

            titulo_entry.insert(0, tarefa_completa.titulo)
            descricao_entry.insert('1.0', tarefa_completa.descricao)
            prazo_entry.insert(0, tarefa_completa.prazo)
            concluida_var.set(tarefa_completa.concluida)
            
            if tarefa_completa.empregado_id:
                nome_completo = next((nome for nome, id_val in self.empregados_dict.items() if id_val == tarefa_completa.empregado_id), "Não Atribuído")
                empregado_combo.set(nome_completo)
            
        return janela_form, titulo_entry, descricao_entry, prazo_entry, empregado_var, concluida_var
    
    def abrir_formulario_adicionar(self):
        janela_form, titulo_entry, descricao_entry, prazo_entry, empregado_var, _ = self._criar_formulario_tarefa(self)
        
        def submit():
            titulo = titulo_entry.get()
            descricao = descricao_entry.get('1.0', tk.END).strip()
            prazo = prazo_entry.get()
            nome_selecionado = empregado_var.get()
            empregado_id = self.empregados_dict.get(nome_selecionado, None) 
            
            if titulo and prazo:
                if adicionar_tarefa(titulo, descricao, prazo, empregado_id):
                    messagebox.showinfo("Sucesso", "Tarefa adicionada com sucesso!", parent=janela_form)
                    self.atualizar_lista()
                    janela_form.destroy()
                else:
                    messagebox.showerror("Erro", "Falha ao adicionar tarefa no DB.", parent=janela_form)
            else:
                messagebox.showwarning("Atenção", "Preencha Título e Prazo.", parent=janela_form)

            ttk.Button(janela_form, text="Salvar Tarefa", command=submit, bootstyle="success").grid(row=5, column=0, columnspan=2, pady=15)

    def abrir_formulario_edicao(self):
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione uma tarefa para editar.")
            return

        item_selecionado = self.tree.item(selecao[0], 'values')
        tarefa_id = item_selecionado[0]
        
        janela_form, titulo_entry, descricao_entry, prazo_entry, empregado_var, concluida_var = self._criar_formulario_tarefa(self, tarefa_item=item_selecionado)
        
        def submit_edicao():
            titulo = titulo_entry.get()
            descricao = descricao_entry.get('1.0', tk.END).strip()
            prazo = prazo_entry.get()
            nome_selecionado = empregado_var.get()
            empregado_id = self.empregados_dict.get(nome_selecionado, None) 
            concluida = concluida_var.get()

            if titulo and prazo:
                if atualizar_tarefa(tarefa_id, titulo, descricao, prazo, empregado_id, concluida):
                    messagebox.showinfo("Sucesso", "Tarefa atualizada com sucesso!", parent=janela_form)
                    self.atualizar_lista()
                    janela_form.destroy()
                else:
                    messagebox.showerror("Erro", "Falha ao atualizar tarefa no DB.", parent=janela_form)
            else:
                messagebox.showwarning("Atenção", "Preencha Título e Prazo.", parent=janela_form)

            ttk.Button(janela_form, text="Salvar Alterações", command=submit_edicao, bootstyle="warning").grid(row=5, column=0, columnspan=2, pady=15)

    def deletar_tarefa(self):
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione uma tarefa para deletar.")
            return

        item_selecionado = self.tree.item(selecao[0], 'values')
        tarefa_id = item_selecionado[0]
        titulo_tarefa = item_selecionado[1]

        confirmar = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja DELETAR a tarefa: {titulo_tarefa} (ID: {tarefa_id})?",
            icon='warning'
        )
        
        if confirmar:
            if deletar_tarefa(tarefa_id):
                messagebox.showinfo("Sucesso", f"Tarefa {titulo_tarefa} deletada com sucesso!")
                self.atualizar_lista()
            else:
                messagebox.showerror("Erro", "Falha ao deletar tarefa no DB.")
                
    def toggle_concluida(self):
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione uma tarefa para alterar o status.")
            return

        item_selecionado = self.tree.item(selecao[0], 'values')
        tarefa_id = item_selecionado[0]
        status_atual_texto = item_selecionado[4] 
        novo_status = True if status_atual_texto == "❌ NÃO" else False

        tarefa_completa = buscar_tarefa_por_id(tarefa_id)

        if tarefa_completa:
            if atualizar_tarefa(
                tarefa_id, 
                tarefa_completa.titulo, 
                tarefa_completa.descricao, 
                tarefa_completa.prazo, 
                tarefa_completa.empregado_id, 
                novo_status
            ):
                messagebox.showinfo("Sucesso", f"Status de '{tarefa_completa.titulo}' alterado para {'CONCLUÍDA' if novo_status else 'PENDENTE'}.")
                self.atualizar_lista()
            else:
                messagebox.showerror("Erro", "Falha ao alterar status da tarefa.")
        else:
            messagebox.showerror("Erro", "Tarefa não encontrada no banco de dados.")

# --- Execução da Aplicação ---
if __name__ == "__main__":
    app = FlowSchedulerApp()
    app.mainloop()
