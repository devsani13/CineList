import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from login import Ui_MainWindow as LoginUi
from cadastrar import Ui_MainWindow as CadastrarUi
from telaprincipal import Ui_MainWindow as PrincipalUi
from adicionar import Ui_MainWindow as AdicionarUi

# Inicializa o app e gerencia as trocas de telas, login, cadastro e ações de mídia
class CineListApp:
    def __init__(self): # Inicialização
        self.app = QtWidgets.QApplication(sys.argv)
        self.janela = QtWidgets.QMainWindow()

        self.mostrar_tela_login()

    def mostrar_tela_login(self): # Tela inicial
        self.tela_login = LoginUi()
        self.tela_login.setupUi(self.janela)
        self.tela_login.MainWindow = self.janela
        self.tela_login.btnEntrar.clicked.connect(self.fazer_login)
        self.tela_login.btnCadastrar.clicked.connect(self.mostrar_tela_cadastro)

        self.janela.show()

    def mostrar_tela_cadastro(self): # Exibe tela de cadastro
        self.tela_cadastro = CadastrarUi()
        self.tela_cadastro.setupUi(self.janela)
        self.tela_cadastro.MainWindow = self.janela
        self.tela_cadastro.btnCadastrar.clicked.connect(self.salvar_usuario)
        self.tela_cadastro.btnVoltar.clicked.connect(self.mostrar_tela_login)

    def mostrar_tela_principal(self): # Tela principal com abas de filmes/séries
        self.tela_principal = PrincipalUi()
        self.tela_principal.setupUi(self.janela)
        self.tela_principal.MainWindow = self.janela

        self.tela_principal.btnAdicionar.clicked.connect(self.abrir_tela_adicionar)

        self.tela_principal.tabWidget.currentChanged.connect(self.verificar_aba_atual)
        self.verificar_aba_atual()

    def fazer_login(self): # Valida usuário e senha
        usuario = self.tela_login.btnUsuario.text()
        senha = self.tela_login.btnSenha.text()
        from utils import verificar_login
        if verificar_login(usuario, senha):
            self.usuario_logado = usuario.lower()
            self.mostrar_tela_principal()
        else:
            QtWidgets.QMessageBox.warning(self.janela, "Erro", "Usuário ou senha inválidos!")

    def salvar_usuario(self): # Registra novo usuário
        nome = self.tela_cadastro.txtNome.text()
        usuario = self.tela_cadastro.txtUsuario.text()
        senha = self.tela_cadastro.txtSenha.text()
        if nome and usuario and senha:
            from utils import salvar_usuario
            sucesso = salvar_usuario({"nome": nome, "usuario": usuario, "senha": senha})
            if sucesso:
                QtWidgets.QMessageBox.information(self.janela, "Sucesso", "Usuário cadastrado com sucesso!")
                self.mostrar_tela_login()
            else:
                QtWidgets.QMessageBox.warning(self.janela, "Erro", "Esse nome de usuário já existe!")
        else:
            QtWidgets.QMessageBox.warning(self.janela, "Erro", "Preencha todos os campos!")

    def abrir_tela_adicionar(self): # Abre janela para adicionar filme/série
        aba_atual = self.tela_principal.tabWidget.currentIndex()
        tipo = "filmes" if self.tela_principal.tabWidget.currentIndex() == 0 else "series"

        self.janela_adicionar = QtWidgets.QMainWindow()
        self.ui_adicionar = AdicionarUi()
        self.ui_adicionar.setupUi(self.janela_adicionar)
        self.ui_adicionar.MainWindow = self.janela_adicionar
        self.ui_adicionar.usuario = self.usuario_logado
        self.ui_adicionar.btnAdicionar.clicked.connect(self.salvar)
        self.ui_adicionar.radioAssistido.toggled.connect(self.ativar_desativar_nota)
        self.ativar_desativar_nota()

        self.ui_adicionar.tipo = tipo

        self.janela_adicionar.show()

    def salvar(self): # Salva uma nova mídia
        nome = self.ui_adicionar.inputNome.text()
        genero = self.ui_adicionar.inputGenero.text()
        ano = self.ui_adicionar.inputAnoLan.text()
        diretor = self.ui_adicionar.inputDiretor.text()
        nota = self.ui_adicionar.sliderNota.value() / 2
        assistido = self.ui_adicionar.radioAssistido.isChecked()

        if not nome or not genero or not ano or not diretor:
            QtWidgets.QMessageBox.warning(self.janela_adicionar, "Erro", "Preencha todos os campos!")
            return
        
        from utils import carregar_dados, adicionar_midia
        dados = carregar_dados()
        usuario = self.ui_adicionar.usuario
        tipo = self.ui_adicionar.tipo

        midias_usuario = dados.get(usuario, {}).get(tipo + "s", [])

        for m in midias_usuario:
            if m["nome"].strip().lower() == nome.lower():
                QtWidgets.QMessageBox.warning(self.janela_adicionar, "Erro", f"{tipo.capitalize()} já adicionado com esse nome!")
                return

        from datetime import datetime

        data = datetime.today().strftime("%d/%m/%Y") if assistido else ""

        midia = {
            "nome": nome,
            "genero": genero,
            "ano": ano,
            "diretor": diretor,
            "nota": nota,
            "assistido": assistido,
            "data": data
        }

        tipo = self.ui_adicionar.tipo
        usuario = self.ui_adicionar.usuario

        from utils import adicionar_midia
        adicionar_midia(usuario, tipo, midia)

        QtWidgets.QMessageBox.information(self.janela_adicionar, "Sucesso", f"{tipo.capitalize()} adicionado com sucesso!")
        self.janela_adicionar.close()
        self.preencher_midia()

    def verificar_aba_atual(self): # Determina a aba atual (filmes ou séries)
        aba = self.tela_principal.tabWidget.currentIndex()
        if aba in [0, 1]:  # Filmes ou Séries
            self.tela_principal.btnAdicionar.show()
            self.preencher_midia()
        else:
            self.tela_principal.btnAdicionar.hide()

    def preencher_midia(self): # Exibe todas as mídias do usuário
        from utils import carregar_dados
        dados = carregar_dados()
        usuario = self.usuario_logado

        if usuario not in dados:
            return

        tipo = "filmes" if self.tela_principal.tabWidget.currentIndex() == 0 else "series"
        lista = dados[usuario][tipo]

        # Escolhe a área certa para inserir os itens
        if tipo == "filmes":
            layout = self.tela_principal.layoutFilmes
        else:
            layout = self.tela_principal.layoutSeries

        # Limpa o layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for midia in lista:
            item = QtWidgets.QWidget()
            item.setStyleSheet("background-color:#B0060F; border-radius: 20px;")
            item.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            item.setFixedHeight(130)
            item.setFixedWidth(382)

            layoutVertical = QtWidgets.QVBoxLayout(item)
            layoutVertical.setContentsMargins(15, 10, 15, 10)

            item.midia_dados = midia.copy()
            item.tipo = tipo
            item.usuario = usuario

            item.mousePressEvent = lambda event, midia=midia: self.abrir_tela_edicao(midia, tipo)

            # Nome
            lblNome = QtWidgets.QLabel(midia["nome"])
            lblNome.setStyleSheet("color: white;")
            font = QtGui.QFont()
            font.setFamily("Malgun Gothic")
            font.setPointSize(12)
            font.setBold(True)
            lblNome.setFont(font)
            lblNome.setAlignment(QtCore.Qt.AlignCenter)
            layoutVertical.addWidget(lblNome)

            # Linha separadora
            linha = QtWidgets.QFrame()
            linha.setFixedHeight(3)
            linha.setStyleSheet("background-color: #B0B0B0; border-radius: 1px;")
            layoutVertical.addWidget(linha)

            # Ano, Gênero, Diretor
            linhaInfo = QtWidgets.QHBoxLayout()
            for texto in [midia["ano"], midia["genero"], midia["diretor"]]:
                lbl = QtWidgets.QLabel(texto)
                lbl.setStyleSheet("color: rgb(226, 226, 226);")
                lbl.setAlignment(QtCore.Qt.AlignCenter)
                linhaInfo.addWidget(lbl, 1)
            layoutVertical.addLayout(linhaInfo)

            linhaFinal = QtWidgets.QHBoxLayout()

            containerInferior = QtWidgets.QWidget()
            layoutInferior = QtWidgets.QHBoxLayout(containerInferior)
            layoutInferior.setContentsMargins(0, 0, 0, 0)

            # Texto da data
            dataTexto = f"Assistido em: {midia['data']}" if midia["assistido"] else "Não assistido"
            lblData = QtWidgets.QLabel(dataTexto)
            lblData.setStyleSheet("color: rgb(226, 226, 226);")
            linhaFinal.addWidget(lblData, alignment=QtCore.Qt.AlignLeft)

            # Estrelas
            nota = midia["nota"]
            containerEstrelas = QtWidgets.QWidget()
            layoutEstrelas = QtWidgets.QHBoxLayout(containerEstrelas)
            layoutEstrelas.setContentsMargins(0, 0, 0, 0)
            layoutEstrelas.setAlignment(QtCore.Qt.AlignCenter)

            cheias = int(nota)
            meia = 1 if (nota - cheias) >= 0.5 else 0
            vazias = 5 - cheias - meia

            for _ in range(cheias):
                estrela = QtWidgets.QLabel()
                estrela.setPixmap(QtGui.QPixmap("imagens/estrela_cheia.png").scaled(16, 16))
                layoutEstrelas.addWidget(estrela)

            if meia:
                estrela = QtWidgets.QLabel()
                estrela.setPixmap(QtGui.QPixmap("imagens/estrela_meia.png").scaled(16, 16))
                layoutEstrelas.addWidget(estrela)

            for _ in range(vazias):
                estrela = QtWidgets.QLabel()
                estrela.setPixmap(QtGui.QPixmap("imagens/estrela_vazia.png").scaled(16, 16))
                layoutEstrelas.addWidget(estrela)

            linhaFinal.addWidget(containerEstrelas, alignment=QtCore.Qt.AlignCenter)

            check = QtWidgets.QCheckBox()
            check.setChecked(midia["assistido"])
            check.setEnabled(False)
            linhaFinal.addWidget(check, alignment=QtCore.Qt.AlignRight)

            layoutVertical.addLayout(linhaFinal)

            layout.addWidget(item)

            item.show()

    def abrir_tela_edicao(self, midia, tipo): # Abre tela de edição/exclusão de uma mídia
        from atualizarexcluir import Ui_MainWindow as AtualizarUi
        self.janela_editar = QtWidgets.QMainWindow()
        self.ui_editar = AtualizarUi()
        self.ui_editar.setupUi(self.janela_editar)
        self.ui_editar.MainWindow = self.janela_editar
        self.ui_editar.radioAssistido.toggled.connect(self.ativar_desativar_nota_edicao)
        self.ativar_desativar_nota_edicao()

        self.ui_editar.inputNome.setText(midia["nome"])
        self.ui_editar.inputGenero.setText(midia["genero"])
        self.ui_editar.inputAnoLan.setText(midia["ano"])
        self.ui_editar.inputDiretor.setText(midia["diretor"])
        self.ui_editar.sliderNota.setValue(int(midia["nota"] * 2))
        self.ui_editar.radioAssistido.setChecked(midia["assistido"])
        self.ui_editar.radioAssistir.setChecked(not midia["assistido"])

        self.ui_editar.usuario = self.usuario_logado
        self.ui_editar.tipo = tipo
        self.ui_editar.nome_original = midia["nome"]

        self.ui_editar.btnAdicionar.clicked.connect(lambda: self.atualizar_midia(self.ui_editar))
        self.ui_editar.btnExcluir.clicked.connect(lambda: self.excluir_midia(self.ui_editar))

        self.janela_editar.show()

    def atualizar_midia(self, ui): # Atualiza dados da mídia
        nome = ui.inputNome.text()
        genero = ui.inputGenero.text()
        ano = ui.inputAnoLan.text()
        diretor = ui.inputDiretor.text()
        nota = ui.sliderNota.value() / 2
        assistido = ui.radioAssistido.isChecked()
        from datetime import datetime
        data = datetime.today().strftime("%d/%m/%Y") if assistido else ""

        midia = {
            "nome": nome,
            "genero": genero,
            "ano": ano,
            "diretor": diretor,
            "nota": nota,
            "assistido": assistido,
            "data": data
        }

        from utils import atualizar_midia
        sucesso = atualizar_midia(ui.usuario, ui.tipo, ui.nome_original, midia)

        if sucesso:
            QtWidgets.QMessageBox.information(ui.MainWindow, "Atualizado", "Mídia atualizada com sucesso!")
            ui.MainWindow.close()
            self.preencher_midia()
        else:
            QtWidgets.QMessageBox.warning(ui.MainWindow, "Erro", "Erro ao atualizar a mídia.")

    def excluir_midia(self, ui): # Remove mídia selecionada
        from utils import excluir_midia
        excluir_midia(ui.usuario, ui.tipo, ui.nome_original)
        QtWidgets.QMessageBox.information(ui.MainWindow, "Excluído", "Mídia excluída com sucesso!")
        ui.MainWindow.close()
        self.preencher_midia()

    def ativar_desativar_nota(self): # Habilita/desabilita nota ao marcar "Assistido"
        assistido = self.ui_adicionar.radioAssistido.isChecked()
        self.ui_adicionar.sliderNota.setEnabled(assistido)
        if not assistido:
            self.ui_adicionar.sliderNota.setValue(0)

    def ativar_desativar_nota_edicao(self): # O mesmo, mas para a tela de edição
        assistido = self.ui_editar.radioAssistido.isChecked()
        self.ui_editar.sliderNota.setEnabled(assistido)
        if not assistido:
            self.ui_editar.sliderNota.setValue(0)

    def executar(self): # Inicia o loop da aplicação
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = CineListApp()
    app.executar()