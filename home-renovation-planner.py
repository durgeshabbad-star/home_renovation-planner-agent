# =============================================================================
# Home Renovation Planner -- A LangGraph Learning Project
# =============================================================================
#
# This project teaches you how LangGraph works by building a home renovation
# planning assistant that suggests personalized renovation ideas.

# WHAT THIS DOES:
# A user provides a space, budget, and goals. The system runs 3 planning
# steps in sequence to suggest layout ideas, materials/style choices, and
# budget/timeline estimates. Then a decision node chooses whether the best
# recommendation is a REFRESH or a REMODEL plan.
#
# LANGGRAPH CONCEPTS COVERED:
# 1. State Management (Pydantic) -- client brief and planning outputs flow
#    through the graph
# 2. Nodes -- each function does one job (layout, materials, budget, decision)
# 3. Sequential Execution -- planning steps happen in order
# 4. Conditional Edges -- routing to refresh vs remodel based on the decision
# 5. Graph Compilation -- turning the graph definition into a runnable app
#
# GRAPH STRUCTURE:
#
#   START
#     |
# [Client Brief]
#       |
#       |
#       +--> plan_layout_changes ----+
#       +--> plan_materials_and_style --+--> pick_best_plan
#       +--> estimate_budget_and_timeline -----+          |
#                                                   conditional
#                                                    /        \
#                                               refresh       remodel
#                                                    |           |
#                                                   END         END
#
# HOW TO RUN:
#   python home-renovation-planner.py
#
# DEPENDENCIES (same as requirements.txt):
#   langgraph, langchain-openai, python-dotenv, pydantic
#
# =============================================================================

import sys
import operator
import json
from typing import Annotated

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()


class PlannerState(BaseModel):
    client_brief: str = ""
    plan_layout_changes: str = ""
    plan_materials_and_style: str = ""
    estimate_budget_and_timeline: str = ""
    best_plan: str = ""
    plan_reason: str = ""
    final_suggestion: str = ""
    messages: Annotated[list, operator.add] = []


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.9)

def plan_layout_changes(state: PlannerState) -> dict:
    response = llm.invoke(
        f"You are a home renovation planning expert. "
        f"The user provided a space, budget, and goals: '{state.client_brief}'. "
        f"Suggest ONE specific layout or structural idea for renovation that would improve the space. "
        f"Include the idea, why it helps, and a simple implementation note. "
        f"Keep it under 3 sentences."
    )
    return {
        "plan_layout_changes": response.content,
        "messages": [f"[plan_layout_changes] {response.content}"]
    }


def plan_materials_and_style(state: PlannerState) -> dict:
    response = llm.invoke(
        f"You are a home renovation planning expert. "
        f"The user provided a space, budget, and goals: '{state.client_brief}'. "
        f"Suggest ONE specific materials or style choice for the renovation. "
        f"Include the choice, why it fits the user's needs, and a simple implementation note. "
        f"Keep it under 3 sentences."
    )
    return {
        "plan_materials_and_style": response.content,
        "messages": [f"[plan_materials_and_style] {response.content}"]
    }


def estimate_budget_and_timeline(state: PlannerState) -> dict:
    response = llm.invoke(
        f"You are a home renovation planning expert. "
        f"The user provided a space, budget, and goals: '{state.client_brief}'. "
        f"Estimate the budget and timeline for the renovation in the same currency the user provided. "
        f"Include a breakdown of costs and a realistic timeline. "
        f"Keep it under 3 sentences."
    )
    return {
        "estimate_budget_and_timeline": response.content,
        "messages": [f"[estimate_budget_and_timeline] {response.content}"]
    }


def pick_best_plan(state: PlannerState) -> dict:
    response = llm.invoke(
        f"You are a renovation planning advisor.\n\n"
        f"Based on these renovation recommendations:\n\n"
        f"LAYOUT / STRUCTURE: {state.plan_layout_changes}\n\n"
        f"MATERIALS / STYLE: {state.plan_materials_and_style}\n\n"
        f"BUDGET / TIMELINE: {state.estimate_budget_and_timeline}\n\n"
        f"Decide whether the best approach is 'Refresh' for lighter cosmetic updates or 'Remodel' for larger structural changes.\n\n"
        f"Reply STRICTLY in this JSON format (no other text):\n"
        f'{{"best_plan": "Refresh" or "Remodel", "reason": "one sentence explanation"}}'
    )
    try:
        result = json.loads(response.content)
        best_plan = result["best_plan"]
        reason = result["reason"]
    except (json.JSONDecodeError, KeyError):
        best_plan = "Refresh"
        reason = "Could not parse decision, defaulting to Refresh."

    return {
        "best_plan": best_plan,
        "plan_reason": reason,
        "messages": [f"[pick_best_plan] best_plan={best_plan}, reason={reason}"]
    }


def refresh_plan(state: PlannerState) -> dict:
    response = llm.invoke(
        f"You are a home renovation consultant.\n\n"
        f"Create a concise refresh plan based on these inputs:\n"
        f"LAYOUT: {state.plan_layout_changes}\n"
        f"MATERIALS: {state.plan_materials_and_style}\n"
        f"BUDGET/TIMELINE: {state.estimate_budget_and_timeline}\n\n"
        f"Focus on cosmetic updates, low-disruption improvements, and practical next steps."
    )
    return {
        "final_suggestion": f"REFRESH PLAN\n{'='*45}\n{response.content}",
        "messages": [f"[refresh_plan] Generated refresh plan"]
    }


def remodel_plan(state: PlannerState) -> dict:
    response = llm.invoke(
        f"You are a home renovation consultant.\n\n"
        f"Create a concise remodel plan based on these inputs:\n"
        f"LAYOUT: {state.plan_layout_changes}\n"
        f"MATERIALS: {state.plan_materials_and_style}\n"
        f"BUDGET/TIMELINE: {state.estimate_budget_and_timeline}\n\n"
        f"Focus on structural changes, phased work, and realistic implementation details."
    )
    return {
        "final_suggestion": f"REMODEL PLAN\n{'='*45}\n{response.content}",
        "messages": [f"[remodel_plan] Generated remodel plan"]
    }


def route_after_decision(state: PlannerState) -> str:
    if state.best_plan == "Remodel":
        return "remodel"
    else:
        return "refresh"


graph = StateGraph(PlannerState)

graph.add_node("plan_layout_changes", plan_layout_changes)
graph.add_node("plan_materials_and_style", plan_materials_and_style)
graph.add_node("estimate_budget_and_timeline", estimate_budget_and_timeline)
graph.add_node("pick_best_plan", pick_best_plan)
graph.add_node("refresh_plan", refresh_plan)
graph.add_node("remodel_plan", remodel_plan)

graph.add_edge(START, "plan_layout_changes")
graph.add_edge(START, "plan_materials_and_style")
graph.add_edge(START, "estimate_budget_and_timeline")
graph.add_edge("plan_layout_changes", "pick_best_plan")
graph.add_edge("plan_materials_and_style", "pick_best_plan")
graph.add_edge("estimate_budget_and_timeline", "pick_best_plan")

graph.add_conditional_edges(
    "pick_best_plan",
    route_after_decision,
    {
        "refresh": "refresh_plan",
        "remodel": "remodel_plan",
    }
)

graph.add_edge("refresh_plan", END)
graph.add_edge("remodel_plan", END)

app = graph.compile()


def run_renovation_plan(client_brief: str):
    print("=" * 55)
    print("  HOME RENOVATION PLAN SUGGESTER")
    print(f"  Client brief: \"{client_brief}\"")
    print("=" * 55)

    result = app.invoke({
        "client_brief": client_brief,
        "messages": [],
    })

    print("\n" + "=" * 55)
    print("  YOUR RECOMMENDED PLAN")
    print("=" * 55)
    print(f"\n{result['final_suggestion']}")

    print("\n" + "-" * 55)
    print("  MESSAGE LOG")
    print("-" * 55)
    for msg in result["messages"]:
        print(f"  {msg}")

    return result


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  HOME RENOVATION PLAN SUGGESTER")
    print("=" * 55)
    print("\n  Tell me about your space, budget, and goals")
    print("  and I'll suggest the best renovation approach.")
    print("  Type 'quit' to exit.\n")

    while True:
        client_brief = input("  Describe your renovation goals > ").strip()

        if client_brief.lower() in ("quit", "exit", "q"):
            print("\n  Take care and happy renovating!\n")
            break

        if not client_brief:
            continue

        run_renovation_plan(client_brief)
        print("\n")
