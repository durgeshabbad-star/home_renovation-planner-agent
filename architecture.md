# Home Renovation Planner -- Architecture

## How It Works

```
User provides a renovation brief
        |
        v
  [plan_layout_changes] -- suggests one layout or structural idea
        |
        v
  [plan_materials_and_style] -- suggests one material/style choice
        |
        v
  [estimate_budget_and_timeline] -- estimates budget and timeline
        |
        v
  [pick_best_plan] -- decides whether the plan should be Refresh or Remodel
        |
        +-- "Refresh" --> [refresh_plan] --> lighter cosmetic plan
        |
        +-- "Remodel" --> [remodel_plan] --> larger structural plan
        |
        v
  Final output printed to user
```

## Interactive Mode

```
$ python home-renovation-planner.py

  =======================================================
    HOME RENOVATION PLAN SUGGESTER
  =======================================================

    Tell me about your space, budget, and goals
    and I'll suggest the best renovation approach.
    Type 'quit' to exit.

    Describe your renovation goals > I want a modern kitchen update under $15,000
    ...graph runs...
    YOUR RECOMMENDED PLAN
    ...

    Describe your renovation goals > quit
    Take care and happy renovating!
```

## Graph Structure (Detailed)

```
                    +-------+
                    | START |
                    +---+---+
                        |
                        v
            +-----------+-----------+
            |   plan_layout_changes   |
            |                         |
            | Suggests one layout     |
            | or structural idea       |
            +-----------+-----------+
                        |
                        v
            +-----------+-----------+
            | plan_materials_and_style|
            |                         |
            | Suggests one material   |
            | or style choice         |
            +-----------+-----------+
                        |
                        v
            +-----------+-----------+
            | estimate_budget_and_    |
            | timeline                |
            |                         |
            | Estimates budget/time   |
            +-----------+-----------+
                        |
                        v
            +-----------+-----------+
            |     pick_best_plan      |
            |                         |
            | Reads all planning info |
            | Returns JSON:           |
            | {best_plan, reason}     |
            +-----------+-----------+
                        |
               CONDITIONAL EDGE
              route_after_decision()
                    /           \
          "Refresh"           "Remodel"
                v                   v
      +-------------+        +--------------+
      | refresh_plan |        | remodel_plan  |
      |             |        |               |
      | Cosmetic    |        | Structural    |
      | updates     |        | updates       |
      +-------------+        +--------------+
                \               /
                 \             /
                  v           v
                  +----+----+
                  |   END   |
                  +---------+
```

## State Fields

```
PlannerState
|
|-- client_brief              <-- set by user input
|-- plan_layout_changes       <-- written by plan_layout_changes
|-- plan_materials_and_style  <-- written by plan_materials_and_style
|-- estimate_budget_and_timeline <-- written by estimate_budget_and_timeline
|-- best_plan                 <-- written by pick_best_plan
|-- plan_reason               <-- written by pick_best_plan
|-- final_suggestion          <-- written by refresh_plan OR remodel_plan
|-- messages                  <-- appended by ALL nodes (operator.add)
```

## LangGraph Concepts Used

| Concept | Where in Code | What It Does |
|---------|--------------|--------------|
| State (Pydantic) | `PlannerState` class | Typed data that flows through every node |
| Nodes | `plan_layout_changes`, `plan_materials_and_style`, `estimate_budget_and_timeline`, `pick_best_plan`, `refresh_plan`, `remodel_plan` | Functions that read state, do one job, return updates |
| Sequential Execution | Three planning nodes before decision | Each step builds on the brief and prior outputs |
| Conditional Edge | `route_after_decision()` | Routes to `refresh_plan` or `remodel_plan` |
| Graph Compilation | `graph.compile()` | Turns graph definition into runnable `app` |
| Invocation | `app.invoke({...})` | Runs the graph with initial state |
| Message Accumulation | `Annotated[list, operator.add]` | Nodes append messages without overwriting |

## Tech Stack

| Component | Purpose |
|-----------|---------|
| LangGraph | Graph orchestration -- nodes, edges, conditional routing |
| LangChain | OpenAI LLM wrapper (ChatOpenAI) |
| OpenAI | gpt-4o-mini -- fast and suitable for project demos |
| Pydantic | State validation and type safety |
| python-dotenv | Load API keys from `.env` |

## File Structure

```
home-renovation-planner/
|-- home-renovation-planner.py  Main code (graph + interactive loop)
|-- architecture.md             This file
|-- architecture.drawio         Visual diagram (open with draw.io extension)
|-- requirements.txt            Python dependencies
|-- .env                        OPENAI_API_KEY (not committed)
|-- .env.example                Template for .env
|-- .gitignore                  Ignores .env, venv, __pycache__
```
