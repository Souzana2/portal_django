"""
Comando de seed para dados de demonstraÃ§Ã£o genÃ©ricos.

Uso:
    python manage.py seed_demo             # Popula (seguro se jÃ¡ existirem dados)
    python manage.py seed_demo --flush     # Limpa tudo e repopula

Popula:
    - 12 Empresas
    - 6 Formadores
    - 8 Cursos
    - 15 AÃ§Ãµes / Turmas
    - 60 Formandos
    - ~120 InscriÃ§Ãµes
    - ML_Previsao_Churn por inscriÃ§Ã£o
    - ML_Recomendacao_Curso por formando
"""
import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from entidades.models import Empresa, Formador, Formando, Curso, Acao, Inscricao
from modelos_previsao.models import ML_Previsao_Churn, ML_Recomendacao_Curso


# â”€â”€â”€ Gerador de NIF PT vÃ¡lido â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _calc_digito_controlo(primeiros8: str) -> int:
    pesos = [9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(int(d) * p for d, p in zip(primeiros8, pesos))
    resto = total % 11
    return 0 if resto in (0, 1) else 11 - resto


def gerar_nif(prefixo: int, sequencia: int) -> str:
    """Gera NIF vÃ¡lido PT: prefixo (1 dÃ­gito) + 7 dÃ­gitos de sequÃªncia + check digit."""
    base = f"{prefixo}{sequencia:07d}"
    check = _calc_digito_controlo(base)
    return base + str(check)


# â”€â”€â”€ Dados fictÃ­cios PT â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

EMPRESAS = [
    ("Construtora Alves & Filhos Lda",      "4470-001", "Maia"),
    ("Agro Silva Unipessoal Lda",           "4900-001", "Viana do Castelo"),
    ("Transportes Ferreira SA",             "3800-001", "Aveiro"),
    ("ServiÃ§os TecnolÃ³gicos Braga Lda",     "4700-001", "Braga"),
    ("MetalÃºrgica Coimbra SA",              "3000-001", "Coimbra"),
    ("Hotel Parque Verde SA",               "8000-001", "Faro"),
    ("Cooperativa AgrÃ­cola do Minho CRL",   "4990-001", "Paredes de Coura"),
    ("FarmÃ¡cia Central Norte Lda",          "4000-001", "Porto"),
    ("IndÃºstria TÃªxtil GuimarÃ£es SA",       "4800-001", "GuimarÃ£es"),
    ("ClÃ­nica SaÃºde Moderna Lda",           "1000-001", "Lisboa"),
    ("RestauraÃ§Ã£o e Eventos Porto Lda",     "4050-001", "Porto"),
    ("Escola de ConduÃ§Ã£o Segura Lda",       "2700-001", "Amadora"),
]

FORMADORES = [
    ("Ana Cristina Silva",     "ana.silva@formadores.pt",     "T001"),
    ("Carlos Manuel Pereira",  "carlos.pereira@formadores.pt","T002"),
    ("Marta Sofia GonÃ§alves",  "marta.goncalves@formadores.pt","T003"),
    ("JoÃ£o Pedro Rodrigues",   "joao.rodrigues@formadores.pt","T004"),
    ("Filipa Alexandra Costa", "filipa.costa@formadores.pt",  "T005"),
    ("Rui AntÃ³nio Fernandes",  "rui.fernandes@formadores.pt", "T006"),
]

CURSOS = [
    ("SEG001", "SeguranÃ§a e Higiene no Trabalho",       "811", "ProteÃ§Ã£o do Ambiente e SeguranÃ§a"),
    ("INF002", "Excel para Profissionais",               "481", "CiÃªncias InformÃ¡ticas"),
    ("GES003", "GestÃ£o e LideranÃ§a de Equipas",         "345", "GestÃ£o e AdministraÃ§Ã£o"),
    ("AMB004", "Ambiente e Sustentabilidade",            "850", "ProteÃ§Ã£o do Ambiente"),
    ("COM005", "ComunicaÃ§Ã£o Empresarial",                "341", "ComÃ©rcio"),
    ("FIN006", "GestÃ£o Financeira para PME",             "344", "Contabilidade e Fiscalidade"),
    ("TIC007", "InformÃ¡tica para NÃ£o Especialistas",    "482", "InformÃ¡tica na Ã“tica do Utilizador"),
    ("RH008",  "Recursos Humanos e LegislaÃ§Ã£o Laboral", "346", "Secretariado e Trabalho Administrativo"),
]

LOCAIS = [
    "Porto", "Lisboa", "Braga", "Coimbra", "Aveiro",
    "GuimarÃ£es", "Viseu", "Leiria", "SetÃºbal", "Faro",
]

# Nomes PT fictÃ­cios para formandos
PRIMEIROS_NOMES = [
    "Ana", "JoÃ£o", "Maria", "Carlos", "Sofia", "Pedro", "InÃªs", "Rui",
    "Marta", "Miguel", "Catarina", "AndrÃ©", "Beatriz", "Tiago", "Filipa",
    "LuÃ­s", "Sara", "Paulo", "Helena", "Ricardo", "ClÃ¡udia", "Nuno",
    "Daniela", "Bruno", "Margarida", "SÃ©rgio", "PatrÃ­cia", "Hugo", "Vera",
    "Diogo", "Susana", "GonÃ§alo", "Cristina", "Marco", "Teresa",
]

APELIDOS = [
    "Silva", "Santos", "Ferreira", "Pereira", "Oliveira", "Costa",
    "Rodrigues", "Martins", "Jesus", "Sousa", "Fernandes", "GonÃ§alves",
    "Gomes", "Lopes", "Marques", "Alves", "Almeida", "Ribeiro",
    "Pinto", "Carvalho", "Teixeira", "Moreira", "Nunes", "Correia",
    "Mendes", "Freitas", "Machado", "Castro", "Monteiro", "Cardoso",
]

ESTADOS_PROF = ["Certificado", "Pendente", "Desistente"]
ESTADOS_PAG  = ["Pago", "Pendente"]

COMERCIAIS_DEMO = [
    "Comercial A", "Comercial B", "Comercial C", "Comercial D",
]


def _data_aleatoria(inicio: date, fim: date) -> str:
    delta = (fim - inicio).days
    return (inicio + timedelta(days=random.randint(0, delta))).isoformat()


# â”€â”€â”€ Comando â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class Command(BaseCommand):
    help = "Popula a base de dados com dados de demonstraÃ§Ã£o genÃ©ricos (sem dados reais)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Apaga todos os dados existentes antes de popular",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=120,
            help="NÃºmero aproximado de inscriÃ§Ãµes a criar (default: 120)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("  A limpar dados existentes...")
            ML_Previsao_Churn.objects.all().delete()
            ML_Recomendacao_Curso.objects.all().delete()
            Inscricao.all_objects.all().delete()
            Acao.all_objects.all().delete()
            Formando.all_objects.all().delete()
            Curso.all_objects.all().delete()
            Formador.all_objects.all().delete()
            Empresa.all_objects.all().delete()
            self.stdout.write(self.style.SUCCESS("  âœ“ Dados limpos"))

        rng = random.Random(42)  # seed fixo para resultados reproduzÃ­veis

        # â”€â”€ 1. Empresas â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.stdout.write("\n  A criar Empresas...")
        empresas = []
        for i, (nome, cp, local) in enumerate(EMPRESAS):
            nif = gerar_nif(5, i + 100)
            emp, created = Empresa.objects.get_or_create(
                nif=nif,
                defaults={
                    "nome": nome,
                    "morada": f"Rua Exemplo, {i+1}",
                    "codigo_postal": cp,
                    "localidade": local,
                }
            )
            empresas.append(emp)
        self.stdout.write(self.style.SUCCESS(f"  âœ“ {len(empresas)} empresas"))

        # â”€â”€ 2. Formadores â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.stdout.write("  A criar Formadores...")
        formadores = []
        for i, (nome, email, cod) in enumerate(FORMADORES):
            fmt, created = Formador.objects.get_or_create(
                nome=nome,
                defaults={
                    "email1": email,
                    "codigo": cod,
                    "id_etl": f"FMT-{i+1:03d}",
                    "morada": f"Av. da FormaÃ§Ã£o, {i+10}",
                    "codigo_postal": "4000-001",
                    "descricao_postal": "Porto",
                }
            )
            formadores.append(fmt)
        self.stdout.write(self.style.SUCCESS(f"  âœ“ {len(formadores)} formadores"))

        # â”€â”€ 3. Cursos â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.stdout.write("  A criar Cursos...")
        cursos = []
        for cod, nome, area_cod, area_nome in CURSOS:
            cur, created = Curso.objects.get_or_create(
                codigo=cod,
                defaults={
                    "nome": nome,
                    "area_codigo": area_cod,
                    "area_nome": area_nome,
                    "id_etl": f"CUR-{cod}",
                }
            )
            cursos.append(cur)
        self.stdout.write(self.style.SUCCESS(f"  âœ“ {len(cursos)} cursos"))

        # â”€â”€ 4. AÃ§Ãµes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.stdout.write("  A criar AÃ§Ãµes...")
        acoes = []
        hoje = date.today()
        for i in range(15):
            # Datas: Ãºltimos 18 meses
            meses_atras = rng.randint(1, 18)
            d_inicio = hoje - timedelta(days=meses_atras * 30)
            d_fim = d_inicio + timedelta(days=rng.randint(1, 5))
            ano = str(d_inicio.year)
            curso = rng.choice(cursos)
            formador = rng.choice(formadores)
            local = rng.choice(LOCAIS)
            ref = f"ACO-{ano}-{i+1:03d}"
            acao, created = Acao.objects.get_or_create(
                referencia=ref,
                defaults={
                    "curso": curso,
                    "formador": formador,
                    "local": local,
                    "data_inicio": d_inicio.isoformat(),
                    "data_fim": d_fim.isoformat(),
                    "ano": ano,
                    "id_etl": f"AET-{i+1:04d}",
                }
            )
            acoes.append(acao)
        self.stdout.write(self.style.SUCCESS(f"  âœ“ {len(acoes)} aÃ§Ãµes"))

        # â”€â”€ 5. Formandos â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.stdout.write("  A criar Formandos...")
        formandos = []
        nomes_usados = set()
        for i in range(60):
            # Gerar nome Ãºnico
            for _ in range(50):
                nome = f"{rng.choice(PRIMEIROS_NOMES)} {rng.choice(APELIDOS)} {rng.choice(APELIDOS)}"
                if nome not in nomes_usados:
                    nomes_usados.add(nome)
                    break
            nif = gerar_nif(rng.choice([1, 2, 3]), i + 1000)
            empresa = rng.choice(empresas) if rng.random() > 0.2 else None
            ano_nasc = rng.randint(1965, 2000)
            fnd, created = Formando.objects.get_or_create(
                nif=nif,
                defaults={
                    "nome": nome,
                    "tipo_identificacao": "CartÃ£o de CidadÃ£o",
                    "numero_identificacao": f"CC{i+100000:06d}",
                    "data_nascimento": f"{ano_nasc}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
                    "morada": f"Rua das Flores, {rng.randint(1, 300)}",
                    "codigo_postal": f"{rng.randint(1000,9999):04d}-{rng.randint(100,999):03d}",
                    "localidade": rng.choice(LOCAIS),
                    "email": f"formando{i+1:03d}@demo.pt",
                    "empresa": empresa,
                    "id_etl": f"FND-{i+1:04d}",
                }
            )
            formandos.append(fnd)
        self.stdout.write(self.style.SUCCESS(f"  âœ“ {len(formandos)} formandos"))

        # â”€â”€ 6. InscriÃ§Ãµes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.stdout.write("  A criar InscriÃ§Ãµes...")
        n_target = options["count"]
        inscricoes = []
        pares_usados = set()

        # DistribuiÃ§Ã£o: 60% Certificado, 25% Pendente, 15% Desistente
        _estados = (
            ["Certificado"] * 60 +
            ["Pendente"]    * 25 +
            ["Desistente"]  * 15
        )

        tentativas = 0
        while len(inscricoes) < n_target and tentativas < n_target * 10:
            tentativas += 1
            formando = rng.choice(formandos)
            acao = rng.choice(acoes)
            par = (formando.pk, acao.pk)
            if par in pares_usados:
                continue
            pares_usados.add(par)

            estado_prof = rng.choice(_estados)
            estado_pag  = "Pago" if estado_prof == "Certificado" else rng.choice(ESTADOS_PAG)
            num_cert    = f"CERT-{len(inscricoes)+1:05d}" if estado_prof == "Certificado" else ""
            data_insc   = _data_aleatoria(
                date.fromisoformat(acao.data_inicio),
                date.fromisoformat(acao.data_inicio) + timedelta(days=5)
            ) if acao.data_inicio else date.today().isoformat()

            try:
                insc = Inscricao.objects.create(
                    formando=formando,
                    acao=acao,
                    empresa=formando.empresa,
                    data_inscricao=data_insc,
                    estado_profissional=estado_prof,
                    estado_pagamento=estado_pag,
                    numero_certificado=num_cert,
                    comercial=rng.choice(COMERCIAIS_DEMO),
                    id_etl=f"INS-{len(inscricoes)+1:05d}",
                )
                inscricoes.append(insc)
            except Exception:
                pass

        self.stdout.write(self.style.SUCCESS(f"  âœ“ {len(inscricoes)} inscriÃ§Ãµes"))

        # â”€â”€ 7. ML Churn â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.stdout.write("  A criar previsÃµes ML de desistÃªncia...")
        churn_count = 0
        fatores_cert  = ["HistÃ³rico positivo de conclusÃ£o", "Empresa financiadora estÃ¡vel", "Formador experiente na Ã¡rea"]
        fatores_pend  = ["Sem histÃ³rico de cursos anteriores", "Empresa nova sem historial", "PerÃ­odo de inscriÃ§Ã£o recente"]
        fatores_desist= ["MÃºltiplas desistÃªncias anteriores", "DistÃ¢ncia ao local de formaÃ§Ã£o", "Curso de longa duraÃ§Ã£o"]

        for insc in inscricoes:
            if ML_Previsao_Churn.objects.filter(inscricao=insc).exists():
                continue
            estado = insc.estado_profissional
            if estado == "Certificado":
                prob = rng.uniform(2.0, 18.0)
                fatores = rng.sample(fatores_cert, 2)
            elif estado == "Desistente":
                prob = rng.uniform(72.0, 96.0)
                fatores = rng.sample(fatores_desist, 2)
            else:
                prob = rng.uniform(28.0, 62.0)
                fatores = rng.sample(fatores_pend, 2)
            ML_Previsao_Churn.objects.create(
                inscricao=insc,
                probabilidade_desistencia=round(prob, 1),
                principais_fatores="; ".join(fatores),
            )
            churn_count += 1
        self.stdout.write(self.style.SUCCESS(f"  âœ“ {churn_count} previsÃµes de churn"))

        # â”€â”€ 8. ML RecomendaÃ§Ãµes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.stdout.write("  A criar recomendaÃ§Ãµes de cursos...")
        rec_count = 0
        for formando in rng.sample(formandos, min(30, len(formandos))):
            # Cursos jÃ¡ feitos por este formando
            cursos_feitos = set(
                i.acao.curso for i in
                Inscricao.objects.filter(formando=formando, estado_profissional="Certificado")
                if i.acao.curso
            )
            cursos_disponiveis = [c for c in cursos if c not in cursos_feitos]
            if not cursos_disponiveis:
                continue
            curso_sug = rng.choice(cursos_disponiveis)
            if ML_Recomendacao_Curso.objects.filter(formando=formando, curso_sugerido=curso_sug).exists():
                continue
            ML_Recomendacao_Curso.objects.create(
                formando=formando,
                curso_sugerido=curso_sug,
                score_confianca=round(rng.uniform(55.0, 94.0), 1),
            )
            rec_count += 1
        self.stdout.write(self.style.SUCCESS(f"  âœ“ {rec_count} recomendaÃ§Ãµes ML"))

        # â”€â”€ SumÃ¡rio â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("â•" * 50))
        self.stdout.write(self.style.SUCCESS("  SEED CONCLUÃDO â€” Base de dados demo pronta"))
        self.stdout.write(self.style.SUCCESS("â•" * 50))
        self.stdout.write(f"  Empresas:       {Empresa.objects.count():>5}")
        self.stdout.write(f"  Formadores:     {Formador.objects.count():>5}")
        self.stdout.write(f"  Cursos:         {Curso.objects.count():>5}")
        self.stdout.write(f"  AÃ§Ãµes:          {Acao.objects.count():>5}")
        self.stdout.write(f"  Formandos:      {Formando.objects.count():>5}")
        self.stdout.write(f"  InscriÃ§Ãµes:     {Inscricao.objects.count():>5}")
        self.stdout.write(f"  Churn ML:       {ML_Previsao_Churn.objects.count():>5}")
        self.stdout.write(f"  RecomendaÃ§Ãµes:  {ML_Recomendacao_Curso.objects.count():>5}")
        self.stdout.write(self.style.SUCCESS("â•" * 50))
        self.stdout.write("")
