import os
import uuid
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.store.base import BaseStore

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# --- Console ---
console = Console()

# Define the system prompt here instead of importing
SYSTEM_PROMPT = """You are BlitzCoder, an AI-powered development assistant. You help with:

1. **Code Generation**: Create new code, functions, classes, and complete applications
2. **Code Refactoring**: Improve existing code structure, performance, and readability
3. **Project Management**: Help with project structure, architecture, and scaffolding
4. **Debugging**: Identify and fix code issues and errors
5. **Documentation**: Generate code documentation and explanations
6. **Best Practices**: Suggest improvements and follow coding standards

You have access to various tools for:
- File and directory operations
- Code execution and testing
- Project structure generation
- Web development (React, Vue, Angular, etc.)
- Backend development (Django, Flask, FastAPI, etc.)
- Database operations
- Shell commands and system operations

Always provide clear, well-structured responses and use the appropriate tools when needed."""

class AgentState(MessagesState):
    documents: list[str]

# Define tools here instead of importing from graphapi
# For now, we'll create a minimal set of essential tools
tools = []

def validate_google_api_key(api_key: str) -> bool:
    try:
        model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=api_key)
        response = model.invoke(["Hello"])  # Simple call
        return True
    except Exception as e:
        print(f"[bold red]API key validation failed:[/bold red] {e}")
        return False

def print_agent_response(text: str, title: str = "BlitzCoder"):
    """Display agent output inside a Rich panel box with orange color"""
    console.print(Panel.fit(Markdown(text), title=f"[bold orange1]{title}[/bold orange1]", border_style="orange1"))

def print_welcome_banner():
    """Print the welcome banner"""
    banner =  """
      ██████╗ ██╗     ██╗████████╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗██████╗ 
      ██╔══██╗██║     ██║╚══██╔══╝╚══███╔╝██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
      ██████╔╝██║     ██║   ██║     ███╔╝ ██║     ██║   ██║██║  ██║█████╗  ██████╔╝
      ██╔══██╗██║     ██║   ██║    ███╔╝  ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗
      ██████╔╝███████╗██║   ██║   ███████╗╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║
      ╚═════╝ ╚══════╝╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝

    """
    console.print(Panel(banner, title="[bold blue]Welcome to BlitzCoder![/bold blue]", border_style="blue"))

def show_info(msg: str):
    """Show info message"""
    console.print(f"[blue]ℹ️  {msg}[/blue]")

def create_semantic_memory_store(api_key: str):
    """Create semantic memory store with the provided API key"""
    return InMemoryStore(
        index={
            "embed":  HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': False}
),
            "dims": 768,  # Google embedding dimension
            "fields": ["memory", "$"],  # Fields to embed
        }
    )

def update_memory(state: AgentState, config: RunnableConfig, *, store: BaseStore):
    user_id = config["configurable"].get("user_id", "default")
    namespace = (user_id, "memories")
    messages = state["messages"]

    if len(messages) >= 2:
        user_msg = messages[-2] if isinstance(messages[-2], HumanMessage) else None
        ai_msg = messages[-1] if isinstance(messages[-1], AIMessage) else None

        if user_msg and ai_msg:
            memory_id = str(uuid.uuid4())
            memory_content = {
                "memory": f"User asked: {user_msg.content} | Assistant responded: {ai_msg.content[:200]}...",
                "context": "conversation",
                "user_query": user_msg.content,
                "ai_response": ai_msg.content,
                "timestamp": str(uuid.uuid4()),  # Replace with actual timestamp if needed
            }

            store.put(
                namespace,
                memory_id,
                memory_content,
                index=["memory", "context", "user_query"],
            )

    return state

def retrieve_and_enhance_context(state: AgentState, config: RunnableConfig, *, store: BaseStore):
    user_id = config["configurable"].get("user_id", "default")
    namespace = (user_id, "memories")
    latest_message = state["messages"][-1]

    if isinstance(latest_message, HumanMessage):
        query = latest_message.content
        memories = store.search(namespace, query=query, limit=5)
        
        if memories:
            memory_context = [
                f"Previous context: {memory.value.get('memory', '')}" for memory in memories
            ]
            context_info = "\n".join(memory_context)
            enhanced_query = f"""Based on our previous conversations:
{context_info}

Current question: {query}

Please respond considering our conversation history and any relevant context from previous interactions."""

            enhanced_messages = state["messages"][:-1] + [HumanMessage(content=enhanced_query)]
            return {"messages": enhanced_messages}

    return state

def create_enhanced_tool_calling_llm(api_key: str):
    """Create enhanced tool calling LLM with the provided API key"""
    def enhanced_tool_calling_llm(state: AgentState, config: RunnableConfig, *, store: BaseStore):
        gemini_model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            api_key=api_key,
            max_tokens=100000
        )

        enhanced_state = retrieve_and_enhance_context(state, config, store=store)
        messages = [
            msg for msg in enhanced_state["messages"]
            if not (hasattr(msg, "role") and getattr(msg, "role", None) == "system")
        ]
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        llm_with_tool = gemini_model.bind_tools(tools)
        response = llm_with_tool.invoke(messages)
        return {"messages": [response]}
    
    return enhanced_tool_calling_llm

def create_semantic_graph(api_key: str):
    """Create semantic graph with the provided API key"""
    semantic_memory_store = create_semantic_memory_store(api_key)
    enhanced_tool_calling_llm = create_enhanced_tool_calling_llm(api_key)
    
    builder = StateGraph(AgentState)
    builder.add_node("enhanced_llm", enhanced_tool_calling_llm)
    builder.add_node("update_memory", update_memory)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "enhanced_llm")
    builder.add_conditional_edges("enhanced_llm", tools_condition, {"tools": "tools", "__end__": "update_memory"})
    builder.add_edge("tools", "enhanced_llm")
    builder.add_edge("update_memory", END)

    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer, store=semantic_memory_store)

def run_agent_with_memory(query: str, api_key: str, user_id: str = "default", thread_id: str = None):
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    config = {
        "configurable": {"thread_id": thread_id, "user_id": user_id},
        "recursion_limit": 100
    }

    output_buffer = ""
    semantic_graph = create_semantic_graph(api_key)

    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Initializing AI agent...", total=None)
        progress.update(task, description="[yellow]Retrieving relevant memories...")

        for chunk, metadata in semantic_graph.stream(
            {"messages": [HumanMessage(content=query)]},
            config=config,
            stream_mode="messages",
        ):
            if hasattr(chunk, "content") and chunk.content:
                if not output_buffer:
                    progress.update(task, description="[green]Receiving AI response...")
                output_buffer += chunk.content

        progress.stop()

    if output_buffer.strip():
        print_agent_response(output_buffer.strip())

def search_memories(user_id: str, query: str):
    """Search memories for a specific user"""
    show_info(f"Searching memories for user: {user_id}")
    show_info(f"Query: {query}")
    show_info("Memory search functionality will be implemented in future versions.")

@click.group()
def cli():
    """BlitzCoder CLI - AI-Powered Dev Assistant"""
    pass

@cli.command()
@click.option('--google-api-key', help='Google API key for Gemini model')
def chat(google_api_key):
    """Start interactive chat with BlitzCoder AI agent."""
    if google_api_key:
        if validate_google_api_key(google_api_key):
            pass  # API key is valid, will be used directly
        else:
            console.print("[bold red]❌ Invalid API key. Please try again.[/bold red]")
            exit(1)
    else:
        google_api_key = Prompt.ask("🔑 [bold green]Paste your API key[/bold green]", password=True)
        if validate_google_api_key(google_api_key):
            pass  # API key is valid, will be used directly
        else:
            console.print("[bold red]❌ Invalid API key. Please try again.[/bold red]")
            exit(1)

    print_welcome_banner()
    user_id = str(uuid.uuid4())
    thread_id = str(uuid.uuid4())

    while True:
        query = Prompt.ask("[bold orange1]Enter your query[/bold orange1]", console=console)
        if query.lower() in {"bye", "exit"}:
            show_info("Exiting interactive agent loop.")
            break
        if query.startswith("search:"):
            search_query = query[7:].strip()
            search_memories(user_id, search_query)
            continue
        run_agent_with_memory(query, google_api_key, user_id, thread_id)

@cli.command()
@click.option('--user-id', default=None, help='User ID for memory search')
@click.option('--query', prompt='Search query', help='Query to search in memories')
@click.option('--google-api-key', help='Google API key for Gemini model')
def search_memories_cli(user_id, query, google_api_key):
    """Search your agent memories."""
    if not google_api_key:
        console.print(Panel.fit(
            "[bold orange1]🔑 Google API Key Required[/bold orange1]\n\n"
            "Please paste your API key below (input is hidden):",
            border_style="red"
        ))
        google_api_key = Prompt.ask("🔑 [bold green]Paste your API key[/bold green]", password=True)
        if validate_google_api_key(google_api_key):
            pass  # API key is valid, will be used directly
        else:
            console.print("[bold red]❌ Invalid API key. Please try again.[/bold red]")
            exit(1)

    if not user_id:
        user_id = str(uuid.uuid4())
    search_memories(user_id, query)

if __name__ == "__main__":
    cli()
