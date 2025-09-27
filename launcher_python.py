import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import subprocess
import os
import threading
import time
import webbrowser
from datetime import datetime
from PIL import Image, ImageTk
import random

class WelcomeScreen:
    def __init__(self, parent, new_features):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Bem-vindo ao Python Launcher")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configurar tema escuro
        self.apply_dark_theme()
        
        # Conteúdo
        tk.Label(self.dialog, text="Novidades no Python Launcher", font=("Arial", 18, "bold")).pack(pady=10)
        
        # Área de scroll para novidades
        frame = tk.Frame(self.dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=15)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Botões
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(button_frame, text="Continuar", command=self.continue_to_main, bg="#28A745", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Ver Documentação", command=self.view_docs, bg="#007ACC", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Preencher com novidades
        self.display_new_features(new_features)
    
    def apply_dark_theme(self):
        """Aplica tema escuro à janela de diálogo"""
        style = ttk.Style()
        style.theme_use('clam')
        
        bg_color = "#1E1E1E"
        fg_color = "#FFFFFF"
        accent_color = "#007ACC"
        secondary_bg = "#2D2D2D"
        
        self.dialog.configure(bg=bg_color)
        
        style.configure('.', 
                      background=bg_color,
                      foreground=fg_color,
                      fieldbackground=secondary_bg)
        
        style.configure('TButton',
                      background=accent_color,
                      foreground=fg_color,
                      borderwidth=0,
                      padding=5)
        
        style.map('TButton',
                 background=[('active', '#005A9E')])
        
        style.configure('TLabel',
                      background=bg_color,
                      foreground=fg_color)
        
        style.configure('TScrolledText',
                      background=secondary_bg,
                      foreground=fg_color)
    
    def display_new_features(self, features):
        """Exibe as novidades disponíveis"""
        self.text_area.insert(tk.END, "Olá! Confira as últimas novidades:\n\n")
        
        for feature in features:
            self.text_area.insert(tk.END, f"✨ {feature['title']}\n")
            self.text_area.insert(tk.END, f"   {feature['description']}\n")
            self.text_area.insert(tk.END, f"   Data: {feature['date']}\n\n")
        
        self.text_area.config(state=tk.DISABLED)
    
    def continue_to_main(self):
        """Fecha a tela e continua para o launcher principal"""
        self.dialog.destroy()
    
    def view_docs(self):
        """Abre a documentação no navegador"""
        webbrowser.open("https://seu-documentacao.com")

class PythonLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Python Launcher")
        self.root.geometry("800x500")
        
        # Configuração do tema escuro
        self.dark_theme = True
        self.apply_dark_theme()
        
        # Carregar apps existentes
        self.apps_file = "apps.json"
        self.apps = self.load_apps()
        
        # Variáveis para controle
        self.selected_category = "Todos"
        self.categories = ["Todos"] + list(set(app["category"] for app in self.apps if app["category"]))
        self.search_term = ""
        
        # Interface
        self.create_widgets()
        
        # Atalhos de teclado
        self.setup_shortcuts()
        
        # Iniciar verificação de atualizações
        self.check_for_updates()
        
        # Timer para verificação automática
        self.schedule_next_check()
        
        # Mostrar tela de boas-vindas se houver novidades
        self.show_welcome_screen()
    
    def apply_dark_theme(self):
        """Aplica tema escuro à interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores do tema escuro
        bg_color = "#1E1E1E"
        fg_color = "#FFFFFF"
        accent_color = "#007ACC"
        secondary_bg = "#2D2D2D"
        
        self.root.configure(bg=bg_color)
        
        style.configure('.', 
                      background=bg_color,
                      foreground=fg_color,
                      fieldbackground=secondary_bg)
        
        style.configure('TButton',
                      background=accent_color,
                      foreground=fg_color,
                      borderwidth=0,
                      padding=5)
        
        style.map('TButton',
                 background=[('active', '#005A9E')])
        
        style.configure('TLabel',
                      background=bg_color,
                      foreground=fg_color)
        
        style.configure('TEntry',
                      fieldbackground=secondary_bg,
                      foreground=fg_color)
        
        style.configure('TListbox',
                      background=secondary_bg,
                      foreground=fg_color,
                      selectbackground=accent_color,
                      selectforeground=fg_color)
        
        style.configure('TCombobox',
                      fieldbackground=secondary_bg,
                      foreground=fg_color)
        
        style.configure('TScrolledText',
                      background=secondary_bg,
                      foreground=fg_color)
    
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#1E1E1E")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame com título e filtro
        top_frame = tk.Frame(main_frame, bg="#1E1E1E")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title_label = tk.Label(top_frame, text="Python Launcher", font=("Arial", 18, "bold"), bg="#1E1E1E", fg="#FFFFFF")
        title_label.pack(side=tk.LEFT)
        
        # Barra de pesquisa
        search_frame = tk.Frame(top_frame, bg="#1E1E1E")
        search_frame.pack(side=tk.RIGHT, fill=tk.X, padx=(10, 0))
        
        tk.Label(search_frame, text="Pesquisar:", bg="#1E1E1E", fg="#FFFFFF").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=25, bg="#2D2D2D", fg="#FFFFFF")
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        # Frame central com duas colunas
        content_frame = tk.Frame(main_frame, bg="#1E1E1E")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Coluna esquerda - Lista de apps
        left_frame = tk.Frame(content_frame, bg="#1E1E1E")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Frame da lista
        list_frame = tk.LabelFrame(left_frame, text="Aplicativos", bg="#1E1E1E", fg="#FFFFFF")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar para a lista
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, bg="#2D2D2D", fg="#FFFFFF", selectbackground="#007ACC")
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.listbox.yview)
        
        # Botões de ação
        button_frame = tk.Frame(list_frame, bg="#1E1E1E")
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(button_frame, text="Executar", command=self.run_app, bg="#007ACC", fg="#FFFFFF").pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Remover", command=self.remove_app, bg="#FF4444", fg="#FFFFFF").pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Atualizar", command=self.update_selected_app, bg="#28A745", fg="#FFFFFF").pack(side=tk.LEFT, padx=2)
        
        # Coluna direita - Formulário de cadastro
        right_frame = tk.Frame(content_frame, bg="#1E1E1E")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        form_frame = tk.LabelFrame(right_frame, text="Adicionar Aplicativo", bg="#1E1E1E", fg="#FFFFFF")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Campos do formulário
        tk.Label(form_frame, text="Nome:", bg="#1E1E1E", fg="#FFFFFF").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = tk.Entry(form_frame, bg="#2D2D2D", fg="#FFFFFF")
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        tk.Label(form_frame, text="Caminho do arquivo .py:", bg="#1E1E1E", fg="#FFFFFF").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.path_entry = tk.Entry(form_frame, bg="#2D2D2D", fg="#FFFFFF")
        self.path_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Botão de busca
        browse_button = tk.Button(form_frame, text="Procurar...", command=self.browse_file, bg="#555555", fg="#FFFFFF")
        browse_button.grid(row=1, column=2, padx=5, pady=5)
        
        tk.Label(form_frame, text="Categoria:", bg="#1E1E1E", fg="#FFFFFF").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.category_entry = ttk.Combobox(form_frame, values=["Jogos", "Ferramentas", "Estudos", "Outros"], state="readonly")
        self.category_entry.set("Outros")
        self.category_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        tk.Label(form_frame, text="Ícone (opcional):", bg="#1E1E1E", fg="#FFFFFF").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.icon_entry = tk.Entry(form_frame, bg="#2D2D2D", fg="#FFFFFF")
        self.icon_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        icon_browse_button = tk.Button(form_frame, text="Selecionar Ícone", command=self.browse_icon, bg="#555555", fg="#FFFFFF")
        icon_browse_button.grid(row=3, column=2, padx=5, pady=5)
        
        # Botão de adição
        add_button = tk.Button(form_frame, text="Adicionar App", command=self.add_app, bg="#28A745", fg="#FFFFFF")
        add_button.grid(row=4, column=0, columnspan=3, pady=10, sticky=tk.EW)
        
        # Ajustar peso das colunas
        form_frame.columnconfigure(1, weight=1)
        
        # Atualizar lista inicial
        self.update_listbox()
    
    def setup_shortcuts(self):
        """Configura atalhos de teclado"""
        self.root.bind('<Control-n>', lambda e: self.name_entry.focus())
        self.root.bind('<Control-o>', lambda e: self.browse_file())
        self.root.bind('<Return>', lambda e: self.run_app() if self.listbox.size() > 0 else None)
        self.root.bind('<Delete>', lambda e: self.remove_app())
        self.root.bind('<Control-a>', lambda e: self.add_app())
        self.root.bind('<Control-u>', lambda e: self.check_for_updates())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<F2>', lambda e: self.show_statistics())
    
    def load_apps(self):
        """Carrega apps do arquivo JSON"""
        try:
            with open(self.apps_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
    
    def save_apps(self):
        """Salva apps no arquivo JSON"""
        with open(self.apps_file, 'w') as f:
            json.dump(self.apps, f, indent=4)
    
    def update_listbox(self):
        """Atualiza a lista de apps exibidos"""
        self.listbox.delete(0, tk.END)
        
        filtered_apps = [
            app for app in self.apps 
            if (self.selected_category == "Todos" or app["category"] == self.selected_category) and
               (not self.search_term or self.search_term.lower() in app["name"].lower())
        ]
        
        for app in filtered_apps:
            display_text = f"{app['name']} [{app['category']}]"
            self.listbox.insert(tk.END, display_text)
    
    def filter_by_category(self, event=None):
        """Filtra apps pela categoria selecionada"""
        self.selected_category = self.category_combo.get()
        self.update_listbox()
    
    def on_search_change(self, event=None):
        """Atualiza a pesquisa"""
        self.search_term = self.search_entry.get().strip()
        self.update_listbox()
    
    def browse_file(self):
        """Abre o gerenciador de arquivos para selecionar o arquivo Python"""
        filename = filedialog.askopenfilename(
            title="Selecione o arquivo Python",
            filetypes=[("Arquivos Python", "*.py")]
        )
        if filename:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filename)
    
    def browse_icon(self):
        """Permite selecionar um ícone personalizado"""
        filename = filedialog.askopenfilename(
            title="Selecione o ícone",
            filetypes=[("Arquivos de Imagem", "*.png *.jpg *.ico *.gif")]
        )
        if filename:
            self.icon_entry.delete(0, tk.END)
            self.icon_entry.insert(0, filename)
    
    def add_app(self):
        """Adiciona um novo app à lista"""
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        category = self.category_entry.get()
        icon = self.icon_entry.get().strip()
        
        if not name or not path:
            messagebox.showerror("Erro", "Preencha o nome e o caminho do arquivo!")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("Erro", "O arquivo não existe!")
            return
        
        # Verificar se já existe um app com o mesmo nome
        if any(app['name'] == name for app in self.apps):
            messagebox.showerror("Erro", "Já existe um aplicativo com este nome!")
            return
        
        # Adicionar o novo app
        new_app = {
            "name": name,
            "path": path,
            "category": category,
            "icon": icon,
            "version": "1.0.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "changelog": "Primeira versão"
        }
        
        self.apps.append(new_app)
        self.save_apps()
        
        # Atualizar categorias
        if category not in self.categories:
            self.categories.append(category)
            self.category_entry['values'] = self.categories
        
        self.update_listbox()
        
        # Limpar campos
        self.name_entry.delete(0, tk.END)
        self.path_entry.delete(0, tk.END)
        self.icon_entry.delete(0, tk.END)
        
        messagebox.showinfo("Sucesso", f"App '{name}' adicionado com sucesso!")
    
    def remove_app(self):
        """Remove o app selecionado da lista"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um aplicativo para remover!")
            return
        
        index = selection[0]
        app_info = self.apps[index]
        app_name = app_info['name']
        
        confirm = messagebox.askyesno("Confirmação", f"Tem certeza que deseja remover '{app_name}'?")
        
        if confirm:
            del self.apps[index]
            self.save_apps()
            
            # Atualizar categorias
            categories_in_use = set(app['category'] for app in self.apps)
            unused_categories = [cat for cat in self.categories if cat != "Todos" and cat not in categories_in_use]
            
            for cat in unused_categories:
                if cat in self.categories:
                    self.categories.remove(cat)
            
            self.category_entry['values'] = self.categories
            
            self.update_listbox()
            messagebox.showinfo("Sucesso", f"App '{app_name}' removido com sucesso!")
    
    def run_app(self):
        """Executa o app selecionado"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um aplicativo para executar!")
            return
        
        index = selection[0]
        app_path = self.apps[index]['path']
        
        try:
            # Executa o script Python
            subprocess.Popen(['python', app_path])
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao executar o aplicativo:\n{str(e)}")
    
    def update_selected_app(self):
        """Atualiza o app selecionado manualmente"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um aplicativo para atualizar!")
            return
        
        index = selection[0]
        app_name = self.apps[index]['name']
        
        # Simular verificação de atualização
        latest_version = self.get_latest_version(app_name)
        if latest_version and latest_version != self.apps[index]['version']:
            self.show_update_dialog([{
                "name": app_name,
                "current_version": self.apps[index]['version'],
                "latest_version": latest_version,
                "release_date": datetime.now().strftime("%Y-%m-%d"),
                "changelog": "Correções de bugs e melhorias de desempenho"
            }])
        else:
            messagebox.showinfo("Atualização", f"Nenhuma atualização disponível para '{app_name}'.")
    
    def check_for_updates(self):
        """Verifica atualizações automaticamente"""
        def check():
            # Simulação de verificação de atualizações
            time.sleep(60)  # Espera 1 minuto antes de verificar novamente
            
            # Verificar se há novas versões para alguns apps
            updates_available = []
            for app in self.apps:
                # Simulação: verifica se há nova versão
                current_version = app['version']
                latest_version = self.get_latest_version(app['name'])
                
                if latest_version and latest_version != current_version:
                    updates_available.append({
                        "name": app['name'],
                        "current_version": current_version,
                        "latest_version": latest_version,
                        "release_date": datetime.now().strftime("%Y-%m-%d"),
                        "changelog": "Correções de bugs e melhorias de desempenho"
                    })
            
            # Mostrar diálogo se houver atualizações
            if updates_available:
                self.root.after(0, lambda: self.show_update_dialog(updates_available))
            
            # Agendar próxima verificação
            self.root.after(0, self.check_for_updates)
        
        # Inicia a thread de verificação
        threading.Thread(target=check, daemon=True).start()
    
    def get_latest_version(self, app_name):
        """Simula obtenção da última versão (em um cenário real, seria uma chamada API)"""
        # Versões simuladas para demonstração
        versions = {
            "Meu Jogo": "1.2.3",
            "Calculadora Avançada": "2.1.0",
            "Editor de Texto": "3.0.5"
        }
        return versions.get(app_name, None)
    
    def show_update_dialog(self, updates):
        """Exibe o diálogo de atualizações"""
        dialog = UpdateDialog(self.root, updates)
    
    def schedule_next_check(self):
        """Agenda a próxima verificação de atualizações"""
        self.root.after(3600000, self.check_for_updates)  # Verifica a cada hora
    
    def show_welcome_screen(self):
        """Mostra a tela de boas-vindas com novidades"""
        # Definir novidades fictícias
        new_features = [
            {
                "title": "Nova Interface Moderna",
                "description": "Design atualizado com tema escuro e melhor navegação",
                "date": "2023-11-01"
            },
            {
                "title": "Busca Inteligente",
                "description": "Nova função de pesquisa com sugestões automáticas",
                "date": "2023-10-28"
            },
            {
                "title": "Atualizações Automáticas",
                "description": "Verificador de atualizações integrado com notificações",
                "date": "2023-10-25"
            },
            {
                "title": "Suporte a Ícones Personalizados",
                "description": "Agora você pode adicionar ícones personalizados para cada app",
                "date": "2023-10-22"
            }
        ]
        
        # Mostrar tela de boas-vindas se houver novidades
        welcome_screen = WelcomeScreen(self.root, new_features)
    
    def setup_shortcuts(self):
        """Configura atalhos de teclado"""
        self.root.bind('<Control-n>', lambda e: self.name_entry.focus())
        self.root.bind('<Control-o>', lambda e: self.browse_file())
        self.root.bind('<Return>', lambda e: self.run_app() if self.listbox.size() > 0 else None)
        self.root.bind('<Delete>', lambda e: self.remove_app())
        self.root.bind('<Control-a>', lambda e: self.add_app())
        self.root.bind('<Control-u>', lambda e: self.check_for_updates())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<F2>', lambda e: self.show_statistics())
    
    def show_help(self):
        """Mostra a ajuda do aplicativo"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Ajuda - Python Launcher")
        help_window.geometry("500x400")
        help_window.configure(bg="#1E1E1E")
        
        # Aplicar tema escuro
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background="#1E1E1E", foreground="#FFFFFF")
        
        # Conteúdo da ajuda
        help_frame = tk.Frame(help_window, bg="#1E1E1E")
        help_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(help_frame, text="Python Launcher - Ajuda", font=("Arial", 16, "bold"), bg="#1E1E1E", fg="#FFFFFF").pack(pady=10)
        
        help_text = """
        Bem-vindo ao Python Launcher!

        Este aplicativo permite organizar e executar facilmente seus scripts Python.

        Principais Funcionalidades:
        • Adicionar novos aplicativos com nome, caminho e categorias
        • Executar aplicativos Python com um clique
        • Gerenciar e remover aplicativos
        • Pesquisar aplicativos na lista
        • Filtrar por categorias
        • Verificar e instalar atualizações automaticamente

        Atalhos de Teclado:
        • Ctrl+N: Focar no campo Nome
        • Ctrl+O: Procurar arquivo
        • Enter: Executar app selecionado
        • Delete: Remover app selecionado
        • Ctrl+A: Adicionar novo app
        • Ctrl+U: Verificar atualizações
        • F1: Exibir esta ajuda
        • F2: Exibir estatísticas

        Para mais informações, visite nosso repositório no GitHub.
        """
        
        text_widget = tk.Text(help_frame, wrap=tk.WORD, bg="#2D2D2D", fg="#FFFFFF", insertbackground="#FFFFFF")
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Button(help_frame, text="GitHub", command=lambda: webbrowser.open("https://github.com/seu-repositorio"), bg="#007ACC", fg="white").pack(pady=10)
    
    def show_statistics(self):
        """Mostra estatísticas do launcher"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estatísticas do Python Launcher")
        stats_window.geometry("400x300")
        stats_window.configure(bg="#1E1E1E")
        
        # Aplicar tema escuro
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background="#1E1E1E", foreground="#FFFFFF")
        
        # Conteúdo das estatísticas
        stats_frame = tk.Frame(stats_window, bg="#1E1E1E")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(stats_frame, text="Estatísticas do Launcher", font=("Arial", 16, "bold"), bg="#1E1E1E", fg="#FFFFFF").pack(pady=10)
        
        # Calcular estatísticas
        total_apps = len(self.apps)
        categories_count = {}
        for app in self.apps:
            category = app['category']
            categories_count[category] = categories_count.get(category, 0) + 1
        
        # Exibir estatísticas
        stats_text = f"Total de Aplicativos: {total_apps}\n\n"
        stats_text += "Por Categoria:\n"
        
        for category, count in sorted(categories_count.items(), key=lambda x: x[1], reverse=True):
            stats_text += f"• {category}: {count}\n"
        
        text_widget = tk.Text(stats_frame, wrap=tk.WORD, bg="#2D2D2D", fg="#FFFFFF", insertbackground="#FFFFFF")
        text_widget.insert(tk.END, stats_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Button(stats_frame, text="Fechar", command=stats_window.destroy, bg="#757575", fg="white").pack(pady=10)
    
    def schedule_next_check(self):
        """Agenda a próxima verificação de atualizações"""
        self.root.after(3600000, self.check_for_updates)  # Verifica a cada hora

if __name__ == "__main__":
    launcher = PythonLauncher()
    launcher.root.mainloop()
