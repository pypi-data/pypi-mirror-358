"""Data fetcher agent using LangGraph for orchestration."""

import json
from typing import Any, Dict, List, Optional, TypedDict

from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import SecretStr

from khora.tools import APITool, GoogleDocsTool, WebScraperTool
from khora.utils.data_models import DataRequest, DataResponse, DataSourceType


class AgentState(TypedDict):
    """State for the data fetcher agent."""

    messages: List[BaseMessage]
    request: DataRequest
    response: Optional[DataResponse]
    tool_calls: List[Dict[str, Any]]
    final_answer: Optional[str]


class DataFetcherAgent:
    """Agent for fetching data based on AI prompts using LangGraph."""

    def __init__(self, openai_api_key: str, model: str = "gpt-4-turbo-preview"):
        """Initialize the data fetcher agent."""
        self.llm = ChatOpenAI(
            api_key=SecretStr(openai_api_key), model=model, temperature=0
        )

        # Initialize tools
        self.tools = {
            DataSourceType.API: APITool(),
            DataSourceType.WEB_SCRAPER: WebScraperTool(),
            DataSourceType.GOOGLE_DOCS: GoogleDocsTool(),
            DataSourceType.SPREADSHEET: GoogleDocsTool(),
        }

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self):  # type: ignore
        """Build the LangGraph state graph."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("analyze_request", self._analyze_request)
        workflow.add_node("execute_tool", self._execute_tool)
        workflow.add_node("process_response", self._process_response)

        # Add edges
        workflow.set_entry_point("analyze_request")
        workflow.add_edge("analyze_request", "execute_tool")
        workflow.add_edge("execute_tool", "process_response")
        workflow.add_edge("process_response", END)

        return workflow.compile()

    def _analyze_request(self, state: AgentState) -> AgentState:
        """Analyze the data request and prepare tool invocation."""
        request = state["request"]

        system_prompt = f"""
        You are a data fetching assistant. Analyze the user's request and determine
        how to fetch the data using the {request.source_type} tool.

        Based on the prompt: "{request.prompt}"
        And the source configuration: {json.dumps(request.source_config)}

        Determine the exact parameters needed for the tool invocation.
        Respond with a JSON object containing the tool parameters.
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.prompt),
        ]

        response = self.llm.invoke(messages)

        # Parse the response to get tool parameters
        try:
            content = (
                response.content
                if isinstance(response.content, str)
                else str(response.content)
            )
            tool_params = json.loads(content)
        except json.JSONDecodeError:
            # Fallback to basic parameters
            tool_params = request.source_config

        state["tool_calls"] = [{"tool": request.source_type, "parameters": tool_params}]
        state["messages"] = messages + [response]

        return state

    def _execute_tool(self, state: AgentState) -> AgentState:
        """Execute the selected tool with parameters."""
        tool_call = state["tool_calls"][0]
        tool = self.tools[DataSourceType(tool_call["tool"])]

        # Execute tool directly
        result = tool._run(**tool_call["parameters"])  # type: ignore

        # Store result in state
        state["final_answer"] = json.dumps(result)

        return state

    def _process_response(self, state: AgentState) -> AgentState:
        """Process the tool response and create final DataResponse."""
        request = state["request"]
        final_answer = state["final_answer"] or "{}"
        tool_result = json.loads(final_answer)

        # Create response
        response = DataResponse(
            request_id=f"{request.source_type}_{id(request)}",
            status=tool_result.get("status", "error"),
            data=tool_result.get("data"),
            error_message=tool_result.get("error"),
            source_type=request.source_type,
            metadata={
                "tool_parameters": state["tool_calls"][0]["parameters"],
                "request_metadata": request.metadata,
            },
        )

        state["response"] = response

        return state

    async def fetch_data(self, request: DataRequest) -> DataResponse:
        """
        Fetch data based on the request.

        Args:
            request: Data request with prompt and configuration

        Returns:
            DataResponse with fetched data or error
        """
        initial_state: AgentState = {
            "messages": [],
            "request": request,
            "response": None,
            "tool_calls": [],
            "final_answer": None,
        }

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)

        return final_state["response"]
