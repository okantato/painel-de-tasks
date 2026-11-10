from __future__ import annotations

import json
from typing import Any

import streamlit as st

from api_client import TaskAPI, TaskAPIError

st.set_page_config(page_title="Painel de tasks", page_icon="🗂️", layout="wide")
st.title("🗂️ Painel de tasks")
st.caption("Consulte e atualize tasks usando o número do chamado GLPI.")


def pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def parse_json_object(raw: str, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label}: JSON inválido na linha {exc.lineno}, coluna {exc.colno}.") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label}: informe um objeto JSON.")
    return value


def parse_json_array(raw: str, label: str) -> list[Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label}: JSON inválido na linha {exc.lineno}, coluna {exc.colno}.") from exc
    if not isinstance(value, list):
        raise ValueError(f"{label}: informe uma lista JSON.")
    return value


with st.sidebar:
    st.header("Buscar chamado")
    ticket_id = st.text_input("Número do chamado GLPI", placeholder="Ex.: 13155")
    lookup = st.button("Consultar task", type="primary", use_container_width=True)
    st.divider()
    st.caption("A conexão usa as variáveis locais do arquivo .env.")

if lookup:
    cleaned_id = ticket_id.strip()
    if not cleaned_id.isdigit():
        st.error("Informe um número de chamado válido.")
    else:
        try:
            api = TaskAPI()
            st.session_state.task_data = api.get_task(cleaned_id)
            st.session_state.ticket_id = cleaned_id
            st.session_state.api_error = None
        except TaskAPIError as exc:
            st.session_state.task_data = None
            st.session_state.api_error = (str(exc), exc.details)

if st.session_state.get("api_error"):
    message, details = st.session_state.api_error
    st.error(message)
    if details:
        st.json(details)

data = st.session_state.get("task_data")
if data:
    task = data.get("task", data)
    ticket = st.session_state.ticket_id
    st.subheader(f"Chamado GLPI {ticket}")

    overview, raw_data = st.tabs(["Visão geral", "Dados recebidos"])
    with overview:
        columns = st.columns(3)
        columns[0].metric("Status", str(task.get("status", "—")))
        columns[1].metric("Prioridade", str(task.get("priority", "—")))
        columns[2].metric("Responsável", str(task.get("assignee", task.get("assignee_id", "—"))))

        st.markdown("#### Descrição")
        st.write(task.get("description") or "Sem descrição")
        st.markdown("#### Pessoas, projeto e prazo")
        st.json(
            {
                key: task.get(key)
                for key in ("requester", "requester_id", "assignee", "assignee_id", "observers", "observer_ids", "project", "project_id", "due_date", "tags")
                if key in task
            }
        )
        st.markdown("#### Subtarefas")
        st.json(data.get("subtasks", task.get("subtasks", [])))
        st.markdown("#### Atividades recentes")
        st.json(data.get("activities", task.get("activities", [])))

        st.divider()
        st.markdown("#### Atualizar task")
        st.caption("Envie apenas os campos que deseja alterar. IDs devem ser do Cadê Task; tags são nomes.")
        task_patch_raw = st.text_area(
            "Campos da task (JSON)",
            value="{}",
            height=180,
            key=f"task_patch_{ticket}",
            help='Ex.: {"priority":"high","status":"em_andamento","due_date":"2026-11-10"}',
        )
        subtasks_raw = st.text_area(
            "Subtarefas para criar ou atualizar (JSON)",
            value="[]",
            height=140,
            key=f"subtasks_patch_{ticket}",
            help='Ex.: [{"title":"Revisar endpoint","due_date":"2026-11-10","responsible_user_id":18}]',
        )
        activities_raw = st.text_area(
            "Comentários a adicionar (JSON)",
            value="[]",
            height=100,
            key=f"activities_patch_{ticket}",
            help='Ex.: [{"description":"Alinhado com a equipe."}]',
        )
        if st.button("Salvar alterações", type="primary", key=f"save_{ticket}"):
            try:
                patch = parse_json_object(task_patch_raw, "Campos da task")
                subtasks = parse_json_array(subtasks_raw, "Subtarefas")
                activities = parse_json_array(activities_raw, "Comentários")
                payload: dict[str, Any] = {}
                if patch:
                    payload["task"] = patch
                if subtasks:
                    payload["subtasks"] = subtasks
                if activities:
                    payload["activities"] = activities
                if not payload:
                    st.warning("Nenhuma alteração foi informada.")
                else:
                    result = TaskAPI().update_task(ticket, payload)
                    st.success("Alterações enviadas à API.")
                    st.session_state.task_data = result if result else TaskAPI().get_task(ticket)
                    st.rerun()
            except ValueError as exc:
                st.error(str(exc))
            except TaskAPIError as exc:
                st.error(str(exc))
                if exc.details:
                    st.json(exc.details)

    with raw_data:
        st.json(data)
else:
    st.info("Consulte um chamado pela barra lateral para ver a task, subtarefas e atividades.")

with st.expander("Análise com IA / Educa"):
    st.write(
        "A API de tasks já permite consultar a solicitação pelo número GLPI. "
        "Para a IA analisar contexto do projeto, sugerir diagnóstico e preparar uma correção, "
        "falta conectar o Educa: precisamos do endereço, autenticação e formato de consulta "
        "dos conteúdos do projeto. A integração deve gerar uma análise em rascunho para revisão "
        "humana antes de qualquer atualização da task."
    )
