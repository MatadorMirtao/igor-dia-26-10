from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from app.middleware.auth_middleware import login_required
from app.models.progression_model import Progressao

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
@login_required
def welcome():
    user_id = session.get('user_id')
    lista_itens = Progressao.listar_para_usuario(user_id)
    
    ordem_areas = [
        "Período Introdutório", "Físico", "Intelectual", 
        "Caráter", "Afetivo", "Social", "Espiritual"
    ]
    progresso_por_area = {area: [] for area in ordem_areas}

    # Contadores para os Distintivos
    intro_concluidos = 0
    prog_concluidos = 0

    for item in lista_itens:
        # Agrupa para a lista do HTML
        if item.area in progresso_por_area:
            progresso_por_area[item.area].append(item)

        # Se o jovem marcou ou a chefia aprovou, conta como feito
        if item.concluido_jovem or item.aprovado_chefia:
            if item.area == "Período Introdutório":
                intro_concluidos += 1
            else:
                prog_concluidos += 1 # Conta itens das outras 6 áreas

    progresso_por_area = {area: itens for area, itens in progresso_por_area.items() if itens}

    # Lógica de Metas e Porcentagens solicitada por você
    stats = {
        'intro': {
            'nome': 'Período Introdutório',
            'atual': intro_concluidos, 'meta': 10,
            'perc': min((intro_concluidos / 10) * 100, 100)
        },
        'escalada': {
            'nome': 'Escalada',
            # Escalada exige concluir o introdutório (10 itens)
            'atual': intro_concluidos, 'meta': 10,
            'perc': min((intro_concluidos / 10) * 100, 100)
        },
        'conquista': {
            'nome': 'Conquista',
            # Conquista exige 25 itens da progressão
            'atual': prog_concluidos, 'meta': 25,
            'perc': min((prog_concluidos / 25) * 100, 100)
        },
        'azimute': {
            'nome': 'Azimute',
            # Azimute exige 50 itens da progressão
            'atual': prog_concluidos, 'meta': 50,
            'perc': min((prog_concluidos / 50) * 100, 100)
        }
    }

    return render_template('home/welcome.html', 
                           username=session.get('username'), 
                           progresso_por_area=progresso_por_area,
                           stats=stats)

@home_bp.route('/salvar_progressao', methods=['POST'])
@login_required
def salvar_progressao():
    user_id = session.get('user_id')
    marcados = request.form.getlist('itens_concluidos')
    
    lista_itens = Progressao.listar_para_usuario(user_id)
    
    for item in lista_itens:
        item.concluido_jovem = str(item.item_id) in marcados
        item.salvar()
        
    flash("Sua progressão foi salva! Aguarde a avaliação da Chefia.", "success")
    return redirect(url_for('home.welcome'))