# Home Renovation Planner - Learn LangGraph Step by Step

A beginner-friendly LangGraph project that helps turn a client brief into a
clear renovation recommendation using layout ideas, material/style choices,
and budget/timeline estimates.

The project demonstrates a clear LangGraph pattern:

```text
[Client Brief]
      |
      |
      +--> plan_layout_changes ----+
      +--> plan_materials_and_style --+--> pick_best_plan
      +--> estimate_budget_and_timeline -----+          |
                                         conditional
                                      /              \
                                 refresh           remodel
                                      |              |
                                     END            END
```

---

## What This Project Does

A user enters a renovation brief such as:

- `I want to modernize my small kitchen on a budget`
- `I need a better layout for my open-plan living room`
- `I want to improve my bathroom without major structural changes`

The graph then:

1. Uses the client brief to suggest one layout or structural idea.
2. Suggests one material or style choice that fits the space.
3. Estimates the budget and timeline for the project.
4. Uses a decision node to choose between:
   - a `Refresh` plan for lighter cosmetic updates, or
   - a `Remodel` plan for more structural work
5. Prints the final recommendation and message log.

---

## LangGraph Concepts Covered

| Concept | Where It Appears |
|---|---|
| State | `PlannerState` Pydantic model |
| Nodes | `plan_layout_changes`, `plan_materials_and_style`, `estimate_budget_and_timeline`, `pick_best_plan`, `refresh_plan`, `remodel_plan` |
| Sequential execution | The three planning functions run in order before the decision node |
| Conditional edges | `route_after_decision` sends the graph to `refresh_plan` or `remodel_plan` |
| Final output | `refresh_plan` or `remodel_plan` |
| Message accumulation | `messages: Annotated[list, operator.add]` |

---

## Project Files

```text
home-renovation-planner.py    Main LangGraph project
architecture.md               Architecture explanation
architecture.drawio           Diagram source file
requirements.txt              Python dependencies
.env.example                  Example environment file
.gitignore                    Ignored local files
```

---

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure your OpenAI API key

```powershell
copy .env.example .env
```

Edit `.env` and add your API key:

```text
OPENAI_API_KEY=sk-...
```

Never commit your real `.env` file.

### 4. Run the project

```powershell
python home-renovation-planner.py
```

---

## Expected Flow

Example input:

```text
I want to update my small kitchen with a modern look and keep the cost under $15,000.
```

The graph will:

1. Suggest one layout or structural improvement.
2. Suggest one material or style choice.
3. Estimate the budget and timeline.
4. Decide whether the plan should be a `Refresh` or `Remodel`.
5. Print the final recommendation.
6. Print the message log showing which nodes executed.

---

## Code Walkthrough

| Step | What Happens | File |
|---|---|---|
| 1 | Define `PlannerState` | `home-renovation-planner.py` |
| 2 | Initialize `ChatOpenAI` | `home-renovation-planner.py` |
| 3 | Define graph node functions | `home-renovation-planner.py` |
| 4 | Define `route_after_decision` | `home-renovation-planner.py` |
| 5 | Add nodes and edges to `StateGraph` | `home-renovation-planner.py` |
| 6 | Compile graph as `app` | `home-renovation-planner.py` |
| 7 | Run with `run_renovation_plan()` | `home-renovation-planner.py` |

---

## Important Note

This is a learning project for understanding LangGraph. The output is meant to
support planning ideas and should not replace professional advice from an
architect, contractor, or financial planner.

---

## Key Takeaways

1. State holds the data that travels through the graph.
2. Nodes are normal Python functions that read state and return updates.
3. Sequential execution happens when one node leads to the next planning step.
4. Conditional edges let the graph choose the next path at runtime.
5. A simple decision node can route the workflow to different final outputs.
