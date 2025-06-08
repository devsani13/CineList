import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from login import Ui_MainWindow as LoginUi
from cadastrar import Ui_MainWindow as CadastrarUi
from telaprincipal import Ui_MainWindow as PrincipalUi
from adicionar import Ui_MainWindow as AdicionarUi

class CineListApp:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.janela = QtWidgets.QMainWindow()

        self.mostrar_tela_login()

    def mostrar_tela_login(self):
        self.tela_login = LoginUi()
        self.tela_login.setupUi(self.janela)
        self.tela_login.MainWindow = self.janela
        self.tela_login.btnEntrar.clicked.connect(self.fazer_login)
        self.tela_login.btnCadastrar.clicked.connect(self.mostrar_tela_cadastro)

        self.janela.show()

    def mostrar_tela_cadastro(self):
        self.tela_cadastro = CadastrarUi()
        self.tela_cadastro.setupUi(self.janela)
        self.tela_cadastro.MainWindow = self.janela
        self.tela_cadastro.btnCadastrar.clicked.connect(self.salvar_usuario)
        self.tela_cadastro.btnVoltar.clicked.connect(self.mostrar_tela_login)

    def mostrar_tela_principal(self):
        self.tela_principal = PrincipalUi()
        self.tela_principal.setupUi(self.janela)
        self.tela_principal.MainWindow = self.janela

        self.tela_principal.btnAdicionar.clicked.connect(self.abrir_tela_adicionar)

        self.tela_principal.tabWidget.currentChanged.connect(self.verificar_aba_atual)
        self.verificar_aba_atual()

    def abrir_tela_adicionar(self):
        aba_atual = self.tela_principal.tabWidget.currentIndex()
        tipo = "filme" if aba_atual == 0 else "serie"

        self.janela_adicionar = QtWidgets.QMainWindow()
        self.ui_adicionar = AdicionarUi()
        self.ui_adicionar.setupUi(self.janela_adicionar)
        self.ui_adicionar.MainWindow = self.janela_adicionar
        self.ui_adicionar.usuario = self.usuario_logado
        self.ui_adicionar.btnAdicionar.clicked.connect(self.salvar)

        self.ui_adicionar.tipo = tipo

        self.janela_adicionar.show()

    def salvar(self):
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

    def verificar_aba_atual(self):
        aba = self.tela_principal.tabWidget.currentIndex()
        if aba == 2:
            self.tela_principal.btnAdicionar.hide()
        else:
            self.tela_principal.btnAdicionar.show()
            self.preencher_midia()

    def fazer_login(self):
        usuario = self.tela_login.btnUsuario.text()
        senha = self.tela_login.btnSenha.text()
        from utils import verificar_login
        if verificar_login(usuario, senha):
            self.usuario_logado = usuario.lower()
            self.mostrar_tela_principal()
        else:
            QtWidgets.QMessageBox.warning(self.janela, "Erro", "Usuário ou senha inválidos!")

    def salvar_usuario(self):
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

    def executar(self):
        sys.exit(self.app.exec_())

    def preencher_midia(self):
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
                linhaInfo.addWidget(lbl, 1)  # '1' define o stretch igual
            layoutVertical.addLayout(linhaInfo)

            # Data e assistido
            linhaFinal = QtWidgets.QHBoxLayout()
            dataTexto = f"Assistido em: {midia['data']}" if midia["assistido"] else ""
            lblData = QtWidgets.QLabel(dataTexto)
            lblData.setStyleSheet("color: rgb(226, 226, 226);")
            linhaFinal.addWidget(lblData)

            spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
            linhaFinal.addItem(spacer)

            check = QtWidgets.QCheckBox()
            check.setChecked(midia["assistido"])
            check.setEnabled(False)
            linhaFinal.addWidget(check)

            layoutVertical.addLayout(linhaFinal)

            layout.addWidget(item)

            item.show()

if __name__ == "__main__":
    app = CineListApp()
    app.executar()