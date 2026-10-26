from app.models.user_model import GerenciadorDB

class Progressao:
    def __init__(self, user_id, item_id, area="", descricao="", concluido_jovem=False, aprovado_chefia=False):
        self.user_id = user_id
        self.item_id = item_id
        self.area = area
        self.descricao = descricao
        self.concluido_jovem = concluido_jovem
        self.aprovado_chefia = aprovado_chefia

    def salvar(self):
        with GerenciadorDB() as cursor:
            cursor.execute("SELECT 1 FROM jovem_progressao WHERE user_id = ? AND item_id = ?", (self.user_id, self.item_id))
            existe = cursor.fetchone()
            
            if existe:
                cursor.execute('''
                    UPDATE jovem_progressao 
                    SET concluido_jovem = ?, aprovado_chefia = ? 
                    WHERE user_id = ? AND item_id = ?
                ''', (int(self.concluido_jovem), int(self.aprovado_chefia), self.user_id, self.item_id))
            else:
                cursor.execute('''
                    INSERT INTO jovem_progressao (user_id, item_id, concluido_jovem, aprovado_chefia) 
                    VALUES (?, ?, ?, ?)
                ''', (self.user_id, self.item_id, int(self.concluido_jovem), int(self.aprovado_chefia)))

    @classmethod
    def listar_para_usuario(cls, user_id):
        with GerenciadorDB() as cursor:
            query = '''
                SELECT 
                    i.id as item_id, 
                    i.area, 
                    i.descricao, 
                    IFNULL(jp.concluido_jovem, 0) as concluido_jovem,
                    IFNULL(jp.aprovado_chefia, 0) as aprovado_chefia
                FROM itens_progressao i
                LEFT JOIN jovem_progressao jp ON i.id = jp.item_id AND jp.user_id = ?
                ORDER BY i.id
            '''
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            
            return [cls(
                user_id=user_id,
                item_id=row['item_id'], 
                area=row['area'], 
                descricao=row['descricao'], 
                concluido_jovem=bool(row['concluido_jovem']), 
                aprovado_chefia=bool(row['aprovado_chefia'])
            ) for row in rows]

    @classmethod
    def criar_tabelas_e_popular(cls):
        with GerenciadorDB() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS itens_progressao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    area TEXT NOT NULL,
                    descricao TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jovem_progressao (
                    user_id INTEGER,
                    item_id INTEGER,
                    concluido_jovem INTEGER DEFAULT 0,
                    aprovado_chefia INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, item_id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (item_id) REFERENCES itens_progressao(id)
                )
            ''')
            
            cursor.execute("SELECT COUNT(*) as qtd FROM itens_progressao")
            if cursor.fetchone()['qtd'] == 0:
                itens_iniciais = [
                    # Período Introdutório
                    ("Período Introdutório", "1. Conhecer a estrutura da Tropa Sênior;"),
                    ("Período Introdutório", "2. Conhecer os membros da sua Patrulha e os seus encargos;"),
                    ("Período Introdutório", "3. Entender e usar o lema do Escoteiro, o sinal, a saudação e o aperto de mão;"),
                    ("Período Introdutório", "4. Reconhecer os sinais manuais e apitos de comandos;"),
                    ("Período Introdutório", "5. Saber o grito da sua patrulha e conhecer o seu significado;"),
                    ("Período Introdutório", "6. Conhecer o uniforme/traje escoteiro e o significado dos seus distintivos;"),
                    ("Período Introdutório", "7. Conhecer o sistema de progressão do Ramo Sênior;"),
                    ("Período Introdutório", "8. Saber como hastear e arriar a Bandeira Nacional;"),
                    ("Período Introdutório", "9. Conhecer os aspectos mais importantes da história do Escotismo e do seu Fundador;"),
                    ("Período Introdutório", "10. Conhecer a Lei e Promessa Escoteira."),

                    # Desenvolvimento Físico (1 a 32)
                    ("Físico", "1. Conhecer os limites normais de pressão arterial, pulso e temperatura e saber como podem mudar devido a doença ou lesão. Conhecer 3 pontos de verificação de pulsação e saber quando utilizar cada um."),
                    ("Físico", "2. Saber identificar a existência de fraturas (internas e externas), entorses e luxações, conhecendo seus tratamentos e socorro de urgência."),
                    ("Físico", "3. Conhecer os sintomas e tratamento de urgência de: estado de choque, traumatismo craniano e hemorragia (interna e externa)."),
                    ("Físico", "4. Conhecer os principais sintomas e tratamento de urgência para: picadas de animais venenosos, envenenamentos e queimaduras de todos os graus."),
                    ("Físico", "5. Explicar como agir e como evitar casos de insolação, hipotermia e queimaduras e as medidas de primeiros socorros para cada situação."),
                    ("Físico", "6. Compreender a importância de se manter imóvel uma pessoa suspeita de fratura na coluna vertebral, bacia e costelas. Saber aplicar controle cervical e imobilização alternativa e conhecer meios de transporte improvisados e de urgência para acidentados em trilhas."),
                    ("Físico", "7. Compreender a importância de reconhecer e tratar rapidamente uma parada cardiorespiratória sabendo aplicar corretamente as técnicas de reanimação cardiopulmonar (RCP)."),
                    ("Físico", "8. Pesquisar e apresentar o resultado do trabalho à Seção, sobre um dos temas a seguir: a) Anorexia Nervosa, b) Perigos do uso de anabolizantes, c) Álcool e direção."),
                    ("Físico", "9. Identificar as doenças sexualmente transmissíveis (DST) comuns e respectivas formas de prevenção. Ser capaz de identificar comportamentos de risco e de tomar as devidas ações preventivas."),
                    ("Físico", "10. Identificar 3 drogas (dentre as quais uma estimulante, uma depressora e uma psicotrópica) e explicar seus efeitos no organismo e os riscos associados."),
                    ("Físico", "11. Organizar o material de primeiros socorros da patrulha para cada tipo de atividade por pelo menos 1 mês."),
                    ("Físico", "12. Conhecer o material individual necessário para diferentes tipos de excursões, de acordo com o programa de atividade (acampamento, acantonamento, volante, fixa, etc) sabendo arrumá-lo na mochila."),
                    ("Físico", "13. Selecionar corretamente o material de campo para um acampamento de patrulha ou Seção."),
                    ("Físico", "14. Demonstrar conhecer as regras de segurança no manuseio de facões e machadinhas, tomando cuidados para a manutenção e conservação das ferramentas da patrulha."),
                    ("Físico", "15. Construir com demais membros da Seção uma fogueira para o Fogo de Conselho, respeitando as regras de segurança na montagem e desmontagem da fogueira, bem como às normas do local."),
                    ("Físico", "16. Manter em conjunto com a patrulha o canto de patrulha limpo e organizado, colaborando também com a limpeza e organização da sede."),
                    ("Físico", "17. Elaborar e executar um cardápio para a patrulha em um acampamento de 3 dias."),
                    ("Físico", "18. Elaborar a lista de compras e um cardápio individual, corretamente equilibrado em quantidade, variedade e valores nutricionais para um bivaque ou um acampamento volante de 2 dias devidamente balanceado e adequado ao clima e à conservação dos gêneros."),
                    ("Físico", "19. Cozinhar à lenha ao ar livre, sem o uso de utensílios (cozinha mateira) pelo menos 3 pratos e 1 sobremesa."),
                    ("Físico", "20. Planejar um calendário mensal pessoal, distribuindo o tempo entre os estudos, obrigações familiares e sociais, escotismo e lazer."),
                    ("Físico", "21. Incorporar ao cotidiano a prática de um esporte ou atividades físicas regulares."),
                    ("Físico", "22. Fazer e saber utilizar as seguintes amarras: quadrada, paralela, diagonal e tripé na construção de pioneirias e engenhocas."),
                    ("Físico", "23. Fazer e saber utilizar os seguintes nós: volta redonda, pescador, oito, correr, balso pelo seio, catau, volta do salteador, nó de andaime, boca de lobo e volta do enfardador."),
                    ("Físico", "24. Confeccionar sozinho uma das seguintes pioneirias: a) lixeira com tampa e pedal; b) pórtico; c) canto de lenhador; ou d) intendência suspensa."),
                    ("Físico", "25. Planejar na cidade com sua patrulha e executar no acampamento a montagem do campo de patrulha, com as seguintes pioneiras básicas: toldo, mesa com bancos, dispensa e canto do lenhador com porta ferramentas; observando a correta disposição de barracas e pioneiras, considerando fatores como tipo e a inclinação do terreno, vento, rios, árvores e demais fatores do local."),
                    ("Físico", "26. Planejar e executar a construção de uma das seguintes pioneiras: a) barraca suspensa ou b) torre de observação com capacidade para 4 pessoas."),
                    ("Físico", "27. Mostrar conhecimento sobre os processos de ancoragem e estiramento de cabos."),
                    ("Físico", "28. Participar de um acampamento volante (ou travessia) que tenha pelo menos 12 km."),
                    ("Físico", "29. Percorrer uma trilha previamente delimitada de pelo menos 2 km, calculando as distâncias e azimutes entre os pontos demarcados."),
                    ("Físico", "30. Conseguir se orientar utilizando uma carta e uma bússola ao mesmo tempo, sabendo escolher a melhor rota na carta topográfica, calculando distâncias, reconhecendo a direção do curso de um rio, cumes e depressões do terreno e as principais convenções topográficas."),
                    ("Físico", "31. Saber utilizar recursos/métodos naturais para sua orientação no campo."),
                    ("Físico", "32. Participar (com outro membro de sua Seção) de uma jornada de pelo menos 15 km a pé ou de embarcação, ou ainda 30 km de bicicleta, acampando e preparando suas refeições durante o trajeto e fazendo o Percurso de Gilwell de no mínimo 5 km. Cumprir pelo menos 4 tarefas dentre as relacionadas, apresentando relatório: a) Estudo da fauna/flora; b) Recursos minerais; c) Transportes; d) Educação; e) População; f) Turismo; g) Recreação; h) Saúde; i) Comércio; j) Agronomia; k) Indústria; l) Impactos Ambientais."),

                    # Desenvolvimento Intelectual
                    ("Intelectual", "33. Manter (sozinho ou com sua patrulha) um informativo escoteiro durante 3 meses, com atualizações semanais, expondo também as principais notícias da semana colhidas em diversos meios de comunicação, junto com uma visão crítica de cada uma delas."),
                    ("Intelectual", "34. Participar ativamente do planejamento e organização de uma atividade de patrulha ou Seção, sendo posteriormente bem avaliado pelos companheiros e pela chefia."),
                    ("Intelectual", "35. Escolher uma das seguintes opções: a) Conquistar 3 especialidades de nível 2, em 3 dos ramos: Cultura, Desportos, Serviços e Ciência/Tecnologia; OU b) Comparar pelo menos 4 opções profissionais, indicando vantagens e desvantagens."),
                    ("Intelectual", "36. Escolher um tema de seu interesse e criar uma obra a partir dele, tal como uma escultura, pintura, esquete, canção, poesia, ou criar uma campanha de divulgação para a seção."),
                    ("Intelectual", "37. Participar ativamente de uma mesa redonda, debate ou estudo de caso com membros da sua Seção sobre um tema escolhido dentre vários apresentados pela chefia."),
                    ("Intelectual", "38. Escolher uma descoberta científica e explicar como esta contribui (ou pode vir a contribuir) para melhorar o mundo."),

                    # Desenvolvimento do Caráter
                    ("Caráter", "39. Exemplificar o significado que atribui à Lei e Promessa Escoteiras e os valores nelas contidos, identificando decisões e comportamentos e como tenta aplicá-los no dia a dia."),
                    ("Caráter", "40. Redigir o seu próprio Compromisso Sênior, discutindo-o com um dos escotistas da Seção. Este compromisso deverá ser validado pela Corte de Honra."),
                    ("Caráter", "41. Fazer uma auto-avaliação, indicando os seus progressos desde o Compromisso Sênior realizado e os pontos que possui mais dificuldades."),
                    ("Caráter", "42. Definir as metas de sua progressão na Tropa Sênior/Guia, estabelecendo prazos para concluir as etapas e as especialidades que pretende conquistar."),
                    ("Caráter", "43. Participar, com empenho e sem distinção, dos vários tipos de atividade da Seção por pelo menos 6 meses, procurando sempre justificar previamente suas ausências."),
                    ("Caráter", "44. Criar um filme, uma peça de teatro, uma poesia, um texto literário ou uma charge que expressem sua visão otimista de encarar o mundo."),
                    ("Caráter", "45. Descrever a importância do correto funcionamento dos Conselhos de Patrulha, Tropa e Corte de Honra."),
                    ("Caráter", "46. Assumir e desempenhar plenamente seus encargos na patrulha durante os últimos 3 meses, sendo bem avaliado pelos seus companheiros."),

                    # Desenvolvimento Afetivo
                    ("Afetivo", "47. Conhecer os procedimentos básicos para minorar a situação em caso de acidentes, mantendo a calma e o controle da situação."),
                    ("Afetivo", "48. Participar de jogos escoteiros ou competições esportivas, respeitando as regras e aceitando resultados negativos."),
                    ("Afetivo", "49. Participar de atividades aventureiras, respeitando as regras de segurança, buscando superar seus medos."),
                    ("Afetivo", "50. Participar ativamente dos debates e processos decisórios realizados na Seção, expondo as suas opinões e respeitando as opiniões alheias."),
                    ("Afetivo", "51. Identificar as principais organizações sociais e de serviço comunitário de sua cidade com as quais possa colaborar."),
                    ("Afetivo", "52. Participar ativamente das campanhas de serviço e de desenvolvimento comunitário organizadas pelo seu Grupo Escoteiro, pelo Distrito ou pela Região."),
                    ("Afetivo", "53. Participar ativamente de pelo menos 1 atividade de cunho comunitário desenvolvida pela sua patrulha."),
                    ("Afetivo", "54. Organizar sozinho ou em conjunto com a patrulha, uma reunião social, com jovens de ambos os sexos."),
                    ("Afetivo", "55. Assumir responsabilidades em casa, contribuindo assim com o aumento da confiança por parte de seus pais."),
                    ("Afetivo", "56. Organizar um debate com sua patrulha ou seção sobre um dos seguintes itens: infidelidade, ciúmes, ficar ou namorar, relacionamentos emocionalmente desequilibrados."),

                    # Desenvolvimento Social
                    ("Social", "57. Escolha uma: a) Identificar e discutir sobre o Bullying na escola, bairro, família e Escotismo. OU b) Assistir e debater um filme ou peça teatral a respeito dos direitos individuais e coletivos."),
                    ("Social", "58. Acolher as decisões de seus pais/responsáveis, manifestando respeitosamente seus pontos de vista em contrário."),
                    ("Social", "59. Participar ativamente e de forma respeitosa das discussões e decisões dos Conselhos de Patrulha, de Tropa e das eleição de monitores."),
                    ("Social", "60. Participar de forma respeitosa e contributiva de pelo menos 1 atividade: debates, estudos de caso ou júri simulado."),
                    ("Social", "61. Planejar e executar o seu Projeto para Escoteiro da Pátria."),
                    ("Social", "62. Escolher uma: a) Pesquisar sobre a cultura indígena predominante na sua Região e apresentar uma dramatização. OU b) Pesquisar e aplicar na Seção 2 jogos indígenas."),
                    ("Social", "63. Escolher uma: a) Produzir com a patrulha um troféu ou lembrança utilizando técnica de artesanato brasileiro. OU b) Preparar uma apresentação no Fogo de Conselho sobre a antiga cultura popular brasileira."),
                    ("Social", "64. Conhecer a Organização Mundial do Movimento Escoteiro(WOSM), localização do Escritório Mundial, suas Regiões e respectivos escritórios."),
                    ("Social", "65. Escolher uma: a) Manter contato com um sênior ou guia estrangeiro durante pelo menos 3 meses. OU b) Participar ativamente da organização de um Jantar Internacional da Seção."),
                    ("Social", "66. Tomar parte em pelo menos 1 atividade em cooperação com outras organizações ligadas à preservação do meio ambiente."),
                    ("Social", "67. Apresentar um estudo ilustrado de um problema ambiental de sua cidade. OU Escolher e executar uma das atividades principais da IMMA destinadas ao Ramo Sênior."),

                    # Desenvolvimento Espiritual
                    ("Espiritual", "68. Conhecer a teoria e realizar pelo menos uma vez uma «Cirurgia Vegetal» junto com sua patrulha. OU Escolher e executar uma das atividades complementares da IMMA."),
                    ("Espiritual", "69. Aplicar em conjunto com a patrulha normas de campismo de baixo impacto."),
                    ("Espiritual", "70. Escolher uma: a) Realizar uma pesquisa sobre as origens de sua crença religiosa e apresentar; OU b) Correlacionar os artigos da Lei Escoteira com os seus princípios religiosos e discuti-los com a chefia."),
                    ("Espiritual", "71. Participar, frequentemente, dos momentos de reflexão realizados no início e término das atividades escoteiras, buscando fazer orações sinceras e reflexivas."),
                    ("Espiritual", "72. Buscar reservar momentos de reflexão e aproximação com Deus, por meio da oração."),
                    ("Espiritual", "73. Participar de uma das seguintes atividades de reflexão (fichas REME): “Carta a mim mesmo” ou “Salmo 151”."),
                    ("Espiritual", "74. Realizar (sozinho ou com sua patrulha) uma pesquisa sobre ao menos 4 religiões, apontando suas similaridades e apresentando o resultado à Seção."),
                    ("Espiritual", "75. Pesquisar e promover um debate com a sua patrulha ou Seção sobre a relação entre a intolerância religiosa e conflitos atuais no Brasil e no mundo.")
                ]
                for area, desc in itens_iniciais:
                    cursor.execute("INSERT INTO itens_progressao (area, descricao) VALUES (?, ?)", (area, desc))