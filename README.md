# SGC (Sistema de Gestão de Componentes)

## Descrição
SGC é uma aplicação Django desenvolvida para gerenciar componentes, categorias, subcategorias, fornecedores, e outras entidades relacionadas a um sistema de inventário. A aplicação suporta funcionalidades de listagem, filtragem, ordenação e CRUD (Create, Read, Update, Delete) para diversos modelos, oferecendo uma interface responsiva para desktop e dispositivos móveis.

## Funcionalidades
- **Gestão de Componentes**: Criação, visualização, edição e exclusão de componentes.
- **Categorias e Subcategorias**: Organização de componentes por categorias e subcategorias.
- **Fornecedores**: Cadastro e gestão de fornecedores.
- **Filtros Avançados**: Filtragem e ordenação dos dados listados.
- **Interface Responsiva**: Adaptação automática para diferentes tamanhos de tela.
- **Controle de Permissões**: Gerenciamento de acesso baseado em permissões de usuário para cada funcionalidade.

## Requisitos do Sistema
- Python 3.12 ou superior
- Django 4.2 ou superior
- SQLite (padrão) ou outro banco de dados suportado pelo Django

## Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/DiegoGarzaro/sgc.git
cd sgc
```

### 2. Crie e ative um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados
Realize as migrações iniciais do banco de dados:
```bash
python manage.py migrate
```

### 5. Execute o servidor de desenvolvimento
Inicie o servidor local:
```bash
python manage.py runserver
```
Acesse a aplicação em [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Estrutura do Projeto

```
sgc/
├── brands/           # App para gerenciar fabricantes
├── components/       # App para gerenciar componentes
├── categories/       # App para categorias
├── packages/         # App para encapsulamentos
├── sub_categories/   # App para sub-categorias
├── suppliers/        # App para fornecedores
├── static/           # Arquivos estáticos (CSS, JS, imagens)
├── app/              # Arquivos de configuração e Templates HTML
├── manage.py         # Script de gerenciamento do Django
└── requirements.txt  # Dependências do projeto
```

## Configuração Avançada

### Variáveis de Ambiente
Configure variáveis de ambiente no arquivo `.env` para gerenciar configurações sensíveis:
```plaintext
DEBUG=True
SECRET_KEY=sua_chave_secreta
DATABASE_URL=sqlite:///db.sqlite3
```

### Banco de Dados
Para usar outro banco de dados, atualize as configurações no arquivo `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sgc_db',
        'USER': 'seu_usuario',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Testes
Execute os testes automatizados para garantir que o sistema funcione corretamente:
```bash
python manage.py test
```

## Contribuição
1. Faça um fork do repositório.
2. Crie um branch para sua feature (`git checkout -b feature/nova-feature`).
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`).
4. Envie o branch (`git push origin feature/nova-feature`).
5. Abra um Pull Request.

## Licença
Este projeto está licenciado sob a [MIT License](LICENSE).

Autor: Diego R. Garzaro
