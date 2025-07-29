"""Tool management for the Arklex framework.

This module provides functionality for managing tools, including
initialization, execution, and slot filling integration.
"""

import os
import uuid
import inspect
import traceback
import json
from typing import Any, Callable, Dict, List, Optional

from arklex.utils.graph_state import MessageState, StatusEnum
from arklex.utils.slot import Slot
from arklex.orchestrator.NLU.core.slot import SlotFiller
from arklex.utils.utils import format_chat_history
from arklex.utils.exceptions import ToolExecutionError, AuthenticationError
from arklex.utils.logging_utils import LogContext
from arklex.orchestrator.NLU.services.model_service import ModelService
from arklex.orchestrator.NLU.services.api_service import APIClientService
log_context = LogContext(__name__)

PYTHON_TO_JSON_SCHEMA = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
}


def register_tool(
    desc: str,
    slots: List[Dict[str, Any]] = [],
    outputs: List[str] = [],
    isResponse: bool = False,
) -> Callable:
    """Register a tool with the Arklex framework.

    This decorator registers a function as a tool with the specified description, slots,
    outputs, and response flag. It handles path normalization and tool initialization.

    Args:
        desc (str): Description of the tool's functionality.
        slots (List[Dict[str, Any]], optional): List of slot definitions. Defaults to [].
        outputs (List[str], optional): List of output field names. Defaults to [].
        isResponse (bool, optional): Whether the tool is a response tool. Defaults to False.

    Returns:
        Callable: A function that creates and returns a Tool instance.
    """
    current_file_dir: str = os.path.dirname(__file__)

    def inner(func: Callable) -> Callable:
        file_path: str = inspect.getfile(func)
        relative_path: str = os.path.relpath(file_path, current_file_dir)
        # reformat the relative path to replace / and \\ with -, and remove .py, because the function calling in openai only allow the function name match the patter the pattern '^[a-zA-Z0-9_-]+$'
        # different file paths format in Windows and linux systems
        relative_path = (
            relative_path.replace("/", "-").replace("\\", "-").replace(".py", "")
        )
        key: str = f"{relative_path}-{func.__name__}"

        def tool() -> "Tool":
            return Tool(func, key, desc, slots, outputs, isResponse)

        return tool

    return inner


class Tool:
    """Base class for tools in the Arklex framework.

    This class provides the core functionality for tool execution, slot management,
    and state handling. It supports slot filling, parameter validation, and error
    handling during tool execution.

    Attributes:
        func (Callable): The function implementing the tool's functionality.
        name (str): The name of the tool.
        description (str): Description of the tool's functionality.
        output (List[str]): List of output field names.
        slotfillapi (Optional[SlotFiller]): Slot filling API instance.
        info (Dict[str, Any]): Tool information including parameters and requirements.
        slots (List[Slot]): List of slot instances.
        isResponse (bool): Whether the tool is a response tool.
        properties (Dict[str, Dict[str, Any]]): Tool properties.
        llm_config (Dict[str, Any]): Language model configuration.
    """

    def __init__(
        self,
        func: Callable,
        name: str,
        description: str,
        slots: List[Dict[str, Any]],
        outputs: List[str],
        isResponse: bool,
    ) -> None:
        """Initialize a new Tool instance.

        Args:
            func (Callable): The function implementing the tool's functionality.
            name (str): The name of the tool.
            description (str): Description of the tool's functionality.
            slots (List[Dict[str, Any]]): List of slot definitions.
            outputs (List[str]): List of output field names.
            isResponse (bool): Whether the tool is a response tool.
        """
        self.func: Callable = func
        self.name: str = name
        self.description: str = description
        self.output: List[str] = outputs
        self.slotfiller: Optional[SlotFiller] = None
        self.info: Dict[str, Any] = self.get_info(slots)
        self.slots: List[Slot] = [Slot.model_validate(slot) for slot in slots]
        self.isResponse: bool = isResponse
        self.properties: Dict[str, Dict[str, Any]] = {}
        self.llm_config: Dict[str, Any] = {}
        self.fixed_args = {}
        self.auth = {}

    def get_info(self, slots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get tool information including parameters and requirements.

        This method processes the slot definitions to create a structured
        representation of the tool's parameters and requirements.

        Args:
            slots (List[Dict[str, Any]]): List of slot definitions.

        Returns:
            Dict[str, Any]: Tool information including parameters and requirements.
        """
        self.properties = {}
        for slot in slots:
            self.properties[slot["name"]] = {
                k: v
                for k, v in slot.items()
                if k in ["type", "description", "prompt", "items"]
            }
        required: List[str] = [
            slot["name"] for slot in slots if slot.get("required", False)
        ]
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.properties,
                    "required": required,
                },
            },
        }

    def init_slotfiller(self, slotfiller_api: SlotFiller) -> None:
        """Initialize the slot filler for this tool.

        Args:
            slotfiller_api: API endpoint for slot filling
        """
        self.slotfiller = slotfiller_api

    def init_default_slots(self, default_slots: List[Slot]) -> None:
        """Initializes the default slots as provided and returns a dictionary of slots which have been populated."""
        populated_slots: Dict[str:Any] = {}
        for default_slot in default_slots:
            populated_slots[default_slot.name] = default_slot.value
            for slot in self.slots:
                if slot.name == default_slot.name:
                    slot.value = default_slot.value
                    slot.verified = True
        return populated_slots

    def _init_slots(self, state: MessageState) -> None:
        """Initialize slots with default values from the message state.

        This method processes default slots from the message state and updates
        the tool's slots with their values.

        Args:
            state (MessageState): The current message state.
        """
        default_slots: List[Slot] = state.slots.get("default_slots", [])
        log_context.info(f"Default slots are: {default_slots}")
        if not default_slots:
            return
        response: Dict[str, Any] = self.init_default_slots(default_slots)
        state.function_calling_trajectory.append(
            {
                "role": "tool",
                "tool_call_id": str(uuid.uuid4()),
                "name": "default_slots",
                "content": json.dumps(response),
            }
        )

        log_context.info(f"Slots after initialization are: {self.slots}")

    def _execute(self, state: MessageState, **fixed_args: Any) -> MessageState:
        """Execute the tool with the current state and fixed arguments.

        This method handles slot filling, parameter validation, and tool execution.
        It manages the execution flow, error handling, and state updates.

        Args:
            state (MessageState): The current message state.
            **fixed_args (Any): Additional fixed arguments for the tool.

        Returns:
            MessageState: The updated message state after tool execution.
        """
        slot_verification: bool = False
        reason: str = ""
        response: str = ""  # Initialize response variable
        # if this tool has been called before, then load the previous slots status
        if state.slots.get(self.name):
            self.slots = state.slots[self.name]
        else:
            state.slots[self.name] = self.slots
        # init slot values saved in default slots
        self._init_slots(state)
        # do slotfilling
        chat_history_str: str = format_chat_history(state.function_calling_trajectory)
        slots: List[Slot] = self.slotfiller.fill_slots(
            self.slots, chat_history_str, self.llm_config
        )
        log_context.info(f"{slots=}")

        # Check if any required slots are missing or unverified
        missing_required = any(
            not (slot.value and slot.verified) for slot in slots if slot.required
        )
        if missing_required:
            for slot in slots:
                # if there is extracted slots values but haven't been verified
                if slot.value and not slot.verified:
                    # check whether it verified or not
                    verification_needed: bool
                    thought: str
                    verification_needed, thought = self.slotfiller.verify_slot(
                        slot.model_dump(), chat_history_str, self.llm_config
                    )
                    if verification_needed:
                        response: str = slot.prompt + "The reason is: " + thought
                        slot_verification = True
                        reason = thought
                        break
                    else:
                        slot.verified = True
                # if there is no extracted slots values, then should prompt the user to fill the slot
                if not slot.value and slot.required:
                    response = slot.prompt
                    break

            state.status = StatusEnum.INCOMPLETE

        # Re-check if any required slots are still missing after verification
        missing_required = any(
            not (slot.value and slot.verified) for slot in slots if slot.required
        )

        # if all required slots are filled and verified, then execute the function
        tool_success: bool = False
        if not missing_required:
            log_context.info("all required slots filled")
            # Get all slot values, including optional ones that have values
            kwargs: Dict[str, Any] = {}
            for slot in slots:
                # Always include the slot value, even if None
                kwargs[slot.name] = slot.value if slot.value is not None else ""

            combined_kwargs: Dict[str, Any] = {
                **kwargs,
                **fixed_args,
                **self.llm_config,
            }
            try:
                # Get the function signature to check required arguments
                sig = inspect.signature(self.func)
                required_args = [
                    name
                    for name, param in sig.parameters.items()
                    if param.default == inspect.Parameter.empty
                ]

                # Ensure all required arguments are present
                for arg in required_args:
                    if arg not in kwargs:
                        kwargs[arg] = ""

                response = self.func(**combined_kwargs)
                tool_success = True
            except ToolExecutionError as tee:
                log_context.error(traceback.format_exc())
                response = tee.extra_message
            except AuthenticationError as ae:
                log_context.error(traceback.format_exc())
                response = str(ae)
            except Exception as e:
                log_context.error(traceback.format_exc())
                response = str(e)
            log_context.info(f"Tool {self.name} response: {response}")
            call_id: str = str(uuid.uuid4())
            state.function_calling_trajectory.append(
                {
                    "content": None,
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "function": {
                                "arguments": json.dumps(kwargs),
                                "name": self.name,
                            },
                            "id": call_id,
                            "type": "function",
                        }
                    ],
                    "function_call": None,
                }
            )
            state.function_calling_trajectory.append(
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": self.name,
                    "content": response,
                }
            )
            state.status = (
                StatusEnum.COMPLETE if tool_success else StatusEnum.INCOMPLETE
            )

        state.trajectory[-1][-1].input = slots
        state.trajectory[-1][-1].output = response

        if tool_success:
            # Tool execution success
            if self.isResponse:
                log_context.info(
                    "Tool exeuction COMPLETE, and the output is stored in response"
                )
                state.response = response
            else:
                log_context.info(
                    "Tool execution COMPLETE, and the output is stored in message flow"
                )
                state.message_flow = (
                    state.message_flow
                    + f"Context from {self.name} tool execution: {response}\n"
                )
        else:
            # Tool execution failed
            if slot_verification:
                log_context.info("Tool execution INCOMPLETE due to slot verification")
                state.message_flow = f"Context from {self.name} tool execution: {response}\n Focus on the '{reason}' to generate the verification request in response please and make sure the request appear in the response."
            else:
                log_context.info(
                    "Tool execution INCOMPLETE due to tool execution failure"
                )
                state.message_flow = (
                    state.message_flow
                    + f"Context from {self.name} tool execution: {response}\n"
                )
        state.slots[self.name] = slots
        return state

    def execute(self, state: MessageState, **fixed_args: Any) -> MessageState:
        """Execute the tool with the current state and fixed arguments.

        This method is a wrapper around _execute that handles the execution flow
        and state management.

        Args:
            state (MessageState): The current message state.
            **fixed_args (Any): Additional fixed arguments for the tool.

        Returns:
            MessageState: The updated message state after tool execution.
        """
        self.llm_config = state.bot_config.llm_config.model_dump()
        state = self._execute(state, **fixed_args)
        return state

    def to_openai_tool_def(self) -> dict:
        """Convert the tool to an OpenAI tool definition.

        Returns:
            dict: The OpenAI tool definition.
        """
        parameters = {
            "type": "object",
            "properties": {},
            "required": [
                slot.name
                for slot in self.slots
                if slot.required and not (slot.verified and slot.value)
            ],
        }
        for slot in self.slots:
            # If the default slots have been populated and verified, then don't show the slot in the tool definition
            if slot.verified and slot.value:
                continue
            if slot.items:
                parameters["properties"][slot.name] = {
                    "type": "array",
                    "items": slot.items,
                }
            else:
                parameters["properties"][slot.name] = {
                    "type": PYTHON_TO_JSON_SCHEMA[slot.type],
                    "description": slot.description,
                }
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": parameters,
        }

    def __str__(self) -> str:
        """Get a string representation of the tool.

        Returns:
            str: A string representation of the tool.
        """
        return f"{self.__class__.__name__}"

    def __repr__(self) -> str:
        """Get a detailed string representation of the tool.

        Returns:
            str: A detailed string representation of the tool.
        """
        return f"{self.__class__.__name__}"
