from app import create_app
from app.models.user_model import User
from app.models.progression_model import Progressao

# Garante que as tabelas de Usuário e de Progressão existam
User.criar_tabela()
Progressao.criar_tabelas_e_popular()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)