from langgraph.graph import StateGraph, END

# Import our modularized components!
from state import PipelineState
from agents.observer import observer_node
from agents.engineer import engineer_node
from agents.sandbox import sandbox_node

MAX_RETRIES = 3

# ==========================================
# ROUTING LOGIC (The "Loop")
# ==========================================
def routing_logic(state: PipelineState) -> str:
    """Decides where the pipeline goes after the Sandbox runs."""
    if state["sandbox_status"] == "SUCCESS":
        print("\n🎉 [Router]: Sandbox Approved! Code is safe. Ending Pipeline.")
        return "end"
    elif state["retry_count"] >= MAX_RETRIES:
        print("\n💀 [Router]: Max retries reached. AI failed to fix the code.")
        return "end"
    else:
        print(f"\n🔄 [Router]: Sandbox Rejected! Sending new error logs back to Engineer...")
        return "continue"

# ==========================================
# BUILD THE GRAPH (The Orchestrator)
# ==========================================
workflow = StateGraph(PipelineState)

# We map our imported node functions to the Graph
workflow.add_node("observer", observer_node)
workflow.add_node("engineer", engineer_node)
workflow.add_node("sandbox", sandbox_node)

workflow.set_entry_point("observer")
workflow.add_edge("observer", "engineer")
workflow.add_edge("engineer", "sandbox")

# This is where the magic loop happens!
workflow.add_conditional_edges(
    "sandbox", 
    routing_logic, 
    {
        "continue": "engineer", # Loop back!
        "end": END              # Finish!
    }
)

app = workflow.compile()

if __name__ == "__main__":
    print("🚀 Starting Modularized Tectonic Pipeline...")
    
    initial_state = {
        "error_logs": "",
        "target_file": "",
        "proposed_code": None,
        "sandbox_status": None,
        "retry_count": 0
    }
    
    result = app.invoke(initial_state)
    
    if result["sandbox_status"] == "SUCCESS":
        print("\n✅ Self-Healing Complete! Here is the validated code:\n")
        print(result["proposed_code"])
