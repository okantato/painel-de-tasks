# Painel de tasks

Painel local em Python/Streamlit para consultar e atualizar uma task pelo número do chamado GLPI, usando a API descrita em `task_management.md`.

## Iniciar

1. Instale Python 3.10 ou mais recente.
2. Crie e ative um ambiente virtual: `python -m venv .venv`.
3. Instale as dependências: `pip install -r requirements.txt`.
4. Copie `.env.example` para `.env` e configure `TASK_API_BASE_URL` e `API_TASK_MANAGEMENT_TOKEN`. O `API_TASK_MANAGEMENT_USER_ID` citado na documentação é configuração do servidor da API; o painel não o envia.
5. Execute: `streamlit run app.py`.

As credenciais ficam no `.env`, que é ignorado pelo Git. Não coloque tokens no código, no navegador ou em mensagens.

## O que já funciona

- Consulta de uma task pelo chamado GLPI.
- Exibição de dados principais, subtarefas e até as atividades que a API devolver.
- Atualização de campos da task, criação/atualização de subtarefas e inclusão de comentários, seguindo o formato documentado.
- Exibição dos detalhes de erro retornados pela API, incluindo validações HTTP 422.

## Próxima integração: Educa e IA

O contrato fornecido não inclui uma forma de listar todas as tasks nem uma API do Educa. Por isso, a primeira versão consulta uma task por vez. Para montar uma fila do projeto e fazer análise de IA com base no conteúdo do Educa, precisamos do URL e da documentação/autorização dessa integração. O desenho recomendado é: buscar task pelo chamado GLPI, coletar contexto permitido do projeto no Educa, produzir resumo/diagnóstico/plano sugerido e deixar a pessoa revisar antes de enviar alterações à API.
