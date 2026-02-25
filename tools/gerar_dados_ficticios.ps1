# Script para gerar arquivos JSON com dados fictícios para o projeto Planejador CETI.
# Autor: Gemini Code Assist
# Data: 23/02/2026

# --- CONFIGURAÇÕES ---
$pastaDados = "data"

# --- FUNÇÕES AUXILIARES ---

# Função para garantir que a pasta de dados exista
function Garantir-PastaDados {
    param($caminho)
    if (-not (Test-Path -Path $caminho)) {
        Write-Host "Criando pasta '$caminho'..."
        New-Item -ItemType Directory -Path $caminho | Out-Null
    }
}

# Função para criar um arquivo JSON a partir de um objeto PowerShell
function Criar-Json {
    param(
        [string]$nomeArquivo,
        [object]$conteudo
    )
    $caminhoCompleto = Join-Path $pastaDados $nomeArquivo
    $json = $conteudo | ConvertTo-Json -Depth 10
    Write-Host "Gerando arquivo '$caminhoCompleto'..."
    Set-Content -Path $caminhoCompleto -Value $json -Encoding UTF8
}

# --- INÍCIO DO SCRIPT ---

Write-Host "--- Iniciando Geração de Dados Fictícios ---" -ForegroundColor Yellow
Garantir-PastaDados -caminho $pastaDados
Garantir-PastaDados -caminho (Join-Path $pastaDados "perfis")
Garantir-PastaDados -caminho (Join-Path $pastaDados "escola")

# 1. escola_db.json (Banco de Dados Institucional)
$escolaDb = @{
    turmas = @{
        "1ª Série A - Ensino Médio" = @{
            componentes = @("Língua Portuguesa", "Matemática", "História", "Geografia", "Biologia", "Física", "Química")
        }
        "2º Ano B - T.I." = @{
            componentes = @("Língua Portuguesa", "Matemática", "PROGRAMAÇÃO ORIENTADA À OBJETOS - POO", "PROGRAMAÇÃO WEB FRONT-END", "MENTORIAS TEC II")
        }
        "3º Ano C - Administração" = @{
            componentes = @("Língua Portuguesa", "Matemática", "Gestão de Projetos", "Contabilidade Básica")
        }
    }
    professores = @("Helio Lima", "Maria Souza", "Carlos Andrade")
}
Criar-Json -nomeArquivo "escola/escola_db.json" -conteudo $escolaDb

# 2. alunos.json (Base de Alunos)
$alunos = @{
    "1ª Série A - Ensino Médio" = @(
        @{ n = 1; nome = "Ana Beatriz Costa" },
        @{ n = 2; nome = "Bruno Cesar Dias" },
        @{ n = 3; nome = "Carla Daniela Esteves" },
        @{ n = 4; nome = "Daniel Farias Gomes" },
        @{ n = 5; nome = "Eduarda Guedes Holanda" }
    )
    "2º Ano B - T.I." = @(
        @{ n = 1; nome = "Felipe Hélio Iglesias" },
        @{ n = 2; nome = "Gabriela Jasmim Klein" },
        @{ n = 3; nome = "Heitor Klein Lopes" },
        @{ n = 4; nome = "Igor Lopes Martins" },
        @{ n = 5; nome = "Julia Martins Nogueira" },
        @{ n = 6; nome = "Kevim Nogueira Oliveira" }
    )
    "3º Ano C - Administração" = @(
        @{ n = 1; nome = "Larissa Oliveira Pires" },
        @{ n = 2; nome = "Marcos Pires Queiroz" },
        @{ n = 3; nome = "Natália Queiroz Ribeiro" },
        @{ n = 4; nome = "Otávio Ribeiro Santos" }
    )
}
Criar-Json -nomeArquivo "escola/alunos.json" -conteudo $alunos

# 3. curriculo_db.json (Cópia do currículo existente)
# Este arquivo é complexo e estático, então replicamos a estrutura principal.
$curriculoDb = @{
  "BASICO" = @{
    "MATEMÁTICA" = @{
      "competencia" = "Utilizar estratégias, conceitos e procedimentos matemáticos para interpretar situações."
      "habilidades" = @("EM13MAT101", "EM13MAT302", "EM13MAT401")
      "objetos" = @("Conjuntos Numéricos", "Intervalos Reais", "Funções Exponenciais", "Análise de Gráficos")
    }
    "LÍNGUA PORTUGUESA" = @{
      "competencia" = "Compreender o funcionamento das diferentes linguagens e práticas culturais."
      "habilidades" = @("EM13LGG101", "EM13LGG103", "EM13LGG701")
      "objetos" = @("Estratégias de Leitura", "Relação entre Textos", "Discursos Midiáticos", "Norma Culta")
    }
    # Adicionar outros componentes básicos se necessário...
  }
  "APROFUNDAMENTO" = @{
    "INTELIGÊNCIA ARTIFICIAL" = @{
      "competencia" = "Compreender e utilizar tecnologias digitais de forma crítica e ética."
      "habilidades" = @("EM13CO24", "EM13CO25", "EM13CO01")
      "objetos" = @("Ética na IA", "Algoritmos e Bolhas Digitais", "Segurança em Ambientes Virtuais")
    }
  }
  "EPT" = @{
    "PROGRAMAÇÃO ORIENTADA À OBJETOS - POO" = @{
      "competencia" = "Modelar sistemas computacionais utilizando o paradigma orientado a objetos."
      "habilidades" = @("Identificar o paradigma da orientação a objetos.", "Realizar encapsulamento e sobrecarga.")
      "objetos" = @("UML (Diagramas de Classe)", "Herança e Polimorfismo", "Encapsulamento e Interfaces")
    }
    "PROGRAMAÇÃO WEB FRONT-END" = @{
      "competencia" = "Desenvolver interfaces interativas e responsivas para web."
      "habilidades" = @("HPT-WEB-01", "HPT-WEB-02")
      "objetos" = @("HTML5/CSS3 Avançado", "JavaScript/React", "UI/UX Design")
    }
    "MENTORIAS TEC II" = @{
      "competencia" = "Planejar e gerenciar projetos integrados às áreas de conhecimento de forma colaborativa."
      "habilidades" = @("Planejar e gerenciar projetos.", "Identificar tecnologias digitais.")
      "objetos" = @("Gestão de Projetos Integrados", "Tecnologias Digitais no Trabalho")
    }
  }
}
Criar-Json -nomeArquivo "curriculo_db.json" -conteudo $curriculoDb

# 4. config_componentes.json (Motor de Planejamento)
$configComponentes = @{
    "MAPEAMENTO_POR_CHAVE" = @{
        "MODULAR_EPT" = @{
            "palavras_chave" = @("POO", "WEB", "IOT")
            "tipo_curso" = "Modular Mensal (80h)"
            "duracao_semanas" = 10
            "aulas_por_semana" = 4
        }
        "MENTORIA" = @{
            "palavras_chave" = @("MENTORIA")
            "tipo_curso" = "Técnico Anual"
            "duracao_semanas" = 40
            "aulas_por_semana" = 2
        }
    }
    "PADRAO_GERAL" = @{
        "tipo_curso" = "Anual / Regular"
        "duracao_semanas" = 40
        "aulas_por_semana" = 2
    }
    "PADRAO_TECNICO_MODULAR" = @{
        "tipo_curso" = "Modular Mensal (40h)"
        "duracao_semanas" = 5
        "aulas_por_semana" = 4
    }
}
Criar-Json -nomeArquivo "config_componentes.json" -conteudo $configComponentes

# 5. professor_config.json (Perfil Ativo Local)
$professorConfig = @{
    "professor" = "Helio Lima"
    "email" = "helio.lima@email.com"
    "municipio" = "Teresina"
    "api_key" = ""
    "vinculos" = @(
        @{
            "turma" = "2º Ano B - T.I."
            "componentes" = @("PROGRAMAÇÃO ORIENTADA À OBJETOS - POO", "MENTORIAS TEC II")
        }
        @{
            "turma" = "3º Ano C - Administração"
            "componentes" = @("Gestão de Projetos")
        }
    )
}
Criar-Json -nomeArquivo "professor_config.json" -conteudo $professorConfig

# 6. Perfil do Administrador (Helio Lima) com Senhas
$perfilHelio = @{
    "professor" = "Helio Lima"
    "email" = "helio.lima@email.com"
    "municipio" = "Teresina"
    "vinculos" = @(
        @{
            "turma" = "2º Ano B - T.I."
            "componentes" = @("PROGRAMAÇÃO ORIENTADA À OBJETOS - POO", "MENTORIAS TEC II")
        }
    )
    "senhas" = @{
        "admin" = "helio@raldir"
        "usuario" = "helio@raldir"
        "professor" = "helio@raldir"
    }
}
Criar-Json -nomeArquivo "perfis/perfil_helio_lima.json" -conteudo $perfilHelio


# 6. planejamentos.json (Arquivo de Rascunhos)
$planejamentos = @{} # Começa vazio
Criar-Json -nomeArquivo "planejamentos.json" -conteudo $planejamentos

# 7. horario_professor.json (Grade Horária)
$horario = @(
    @{ "Horário" = "07:20 - 08:20"; "Período" = "1ª Aula"; "Segunda" = "2ºB-T.I./POO"; "Terça" = ""; "Quarta" = ""; "Quinta" = ""; "Sexta" = "" },
    @{ "Horário" = "08:20 - 09:20"; "Período" = "2ª Aula"; "Segunda" = "2ºB-T.I./POO"; "Terça" = ""; "Quarta" = ""; "Quinta" = ""; "Sexta" = "" },
    @{ "Horário" = "09:20 - 09:40"; "Período" = "☕ Lanche"; "Segunda" = "---"; "Terça" = "---"; "Quarta" = "---"; "Quinta" = "---"; "Sexta" = "---" },
    @{ "Horário" = "09:40 - 10:40"; "Período" = "3ª Aula"; "Segunda" = ""; "Terça" = "3ºC-ADM/Gestão"; "Quarta" = ""; "Quinta" = ""; "Sexta" = "" },
    @{ "Horário" = "10:40 - 11:40"; "Período" = "4ª Aula"; "Segunda" = ""; "Terça" = "3ºC-ADM/Gestão"; "Quarta" = ""; "Quinta" = ""; "Sexta" = "" },
    @{ "Horário" = "11:40 - 12:40"; "Período" = "🍽️ Almoço"; "Segunda" = "---"; "Terça" = "---"; "Quarta" = "---"; "Quinta" = "---"; "Sexta" = "---" },
    @{ "Horário" = "12:40 - 13:40"; "Período" = "5ª Aula"; "Segunda" = ""; "Terça" = ""; "Quarta" = "2ºB-T.I./Mentorias"; "Quinta" = ""; "Sexta" = "" },
    @{ "Horário" = "13:40 - 14:40"; "Período" = "6ª Aula"; "Segunda" = ""; "Terça" = ""; "Quarta" = "2ºB-T.I./Mentorias"; "Quinta" = ""; "Sexta" = "" },
    @{ "Horário" = "14:40 - 14:50"; "Período" = "☕ Lanche"; "Segunda" = "---"; "Terça" = "---"; "Quarta" = "---"; "Quinta" = "---"; "Sexta" = "---" },
    @{ "Horário" = "14:50 - 15:50"; "Período" = "7ª Aula"; "Segunda" = ""; "Terça" = ""; "Quarta" = ""; "Quinta" = ""; "Sexta" = "" },
    @{ "Horário" = "15:50 - 16:50"; "Período" = "8ª Aula"; "Segunda" = ""; "Terça" = ""; "Quarta" = ""; "Quinta" = ""; "Sexta" = "" }
)
Criar-Json -nomeArquivo "horario_professor.json" -conteudo $horario

# 8. calendario_letivo_2026.json (Bússola do Tempo)
$calendario = @{
    "trimestres" = @{
        "1º" = @{
            "inicio" = "2026-02-19"
            "fim" = "2026-05-22"
            "semana_inicio" = 0
            "semana_fim" = 13
        }
        "2º" = @{
            "inicio" = "2026-05-25"
            "fim" = "2026-08-28"
            "semana_inicio" = 13
            "semana_fim" = 26
        }
        "3º" = @{
            "inicio" = "2026-08-31"
            "fim" = "2026-12-18"
            "semana_inicio" = 26
            "semana_fim" = 40
        }
    }
}
Criar-Json -nomeArquivo "calendario_letivo_2026.json" -conteudo $calendario


Write-Host ""
Write-Host "✅ Processo concluído! Todos os arquivos de dados fictícios foram gerados na pasta '$pastaDados'." -ForegroundColor Green
Write-Host "Lembre-se de adicionar a pasta 'data/' ao seu .gitignore se ainda não o fez."

```

### Como usar:

# 1.  Salve o código acima em um arquivo chamado `gerar_dados_ficticios.ps1` na raiz do seu projeto (na mesma pasta que `app.py`).
# 2.  Abra um terminal PowerShell.
# 3.  Navegue até a pasta do seu projeto.
# 4.  Execute o script com o comando:
#    ```powershell
#    .\gerar_dados_ficticios.ps1
#    ```
# 5.  O script criará a pasta `data` (se ela não existir) e a preencherá com todos os arquivos JSON necessários para executar e testar a aplicação.

# Este script automatiza a criação do ambiente de teste, economizando tempo e garantindo que todos os desenvolvedores trabalhem com a mesma base de dados fictícia.

# <!--
# [PROMPT_SUGGESTION]Como posso adicionar um novo tipo de componente modular no `config_componentes.json`?[/PROMPT_SUGGESTION]
# [PROMPT_SUGGESTION]Explique como o arquivo `professor_config.json` interage com o `escola_db.json` no sistema.[/PROMPT_SUGGESTION]
