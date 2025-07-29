import logging
import time
import types
from typing import Annotated, Literal, Optional, Type, overload

from dotenv import load_dotenv
from pydantic import ConfigDict, Field, validate_call

from askui.container import telemetry
from askui.locators.locators import Locator
from askui.models.shared.computer_agent_cb_param import OnMessageCb
from askui.models.shared.computer_agent_message_param import MessageParam
from askui.models.shared.tools import ToolCollection
from askui.tools.computer import Computer20241022Tool, Computer20250124Tool
from askui.tools.exception_tool import ExceptionTool
from askui.utils.image_utils import ImageSource, Img

from .logger import configure_logging, logger
from .models import ModelComposition
from .models.exceptions import ElementNotFoundError
from .models.model_router import ModelRouter, initialize_default_model_registry
from .models.models import (
    ModelChoice,
    ModelName,
    ModelRegistry,
    Point,
    TotalModelChoice,
)
from .models.types.response_schemas import ResponseSchema
from .reporting import CompositeReporter, Reporter
from .retry import ConfigurableRetry, Retry
from .tools import AgentToolbox, ModifierKey, PcKey
from .tools.askui import AskUiControllerClient


class VisionAgent:
    """
    A vision-based agent that can interact with user interfaces through computer vision and AI.

    This agent can perform various UI interactions like clicking, typing, scrolling, and more.
    It uses computer vision models to locate UI elements and execute actions on them.

    Args:
        log_level (int | str, optional): The logging level to use. Defaults to `logging.INFO`.
        display (int, optional): The display number to use for screen interactions. Defaults to `1`.
        reporters (list[Reporter] | None, optional): List of reporter instances for logging and reporting. If `None`, an empty list is used.
        tools (AgentToolbox | None, optional): Custom toolbox instance. If `None`, a default one will be created with `AskUiControllerClient`.
        model (ModelChoice | ModelComposition | str | None, optional): The default choice or name of the model(s) to be used for vision tasks. Can be overridden by the `model` parameter in the `click()`, `get()`, `act()` etc. methods.
        retry (Retry, optional): The retry instance to use for retrying failed actions. Defaults to `ConfigurableRetry` with exponential backoff. Currently only supported for `locate()` method.
        models (ModelRegistry | None, optional): A registry of models to make available to the `VisionAgent` so that they can be selected using the `model` parameter of `VisionAgent` or the `model` parameter of its `click()`, `get()`, `act()` etc. methods. Entries in the registry override entries in the default model registry.

    Example:
        ```python
        from askui import VisionAgent

        with VisionAgent() as agent:
            agent.click("Submit button")
            agent.type("Hello World")
            agent.act("Open settings menu")
        ```
    """

    @telemetry.record_call(exclude={"model_router", "reporters", "tools"})
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(
        self,
        log_level: int | str = logging.INFO,
        display: Annotated[int, Field(ge=1)] = 1,
        reporters: list[Reporter] | None = None,
        tools: AgentToolbox | None = None,
        model: ModelChoice | ModelComposition | str | None = None,
        retry: Retry | None = None,
        models: ModelRegistry | None = None,
    ) -> None:
        load_dotenv()
        configure_logging(level=log_level)
        self._reporter = CompositeReporter(reporters=reporters)
        self.tools = tools or AgentToolbox(
            agent_os=AskUiControllerClient(
                display=display,
                reporter=self._reporter,
            ),
        )
        self._tool_collection = ToolCollection(
            tools=[
                ExceptionTool(),
            ]
        )
        _models = initialize_default_model_registry(
            tool_collection=self._tool_collection,
            reporter=self._reporter,
        )
        _models.update(models or {})
        self._model_router = ModelRouter(
            reporter=self._reporter,
            models=_models,
        )
        self.model = model
        self._retry = retry or ConfigurableRetry(
            strategy="Exponential",
            base_delay=1000,
            retry_count=3,
            on_exception_types=(ElementNotFoundError,),
        )
        self._model_choice = self._initialize_model_choice(model)

    def _initialize_model_choice(
        self, model_choice: ModelComposition | ModelChoice | str | None
    ) -> TotalModelChoice:
        """Initialize the model choice based on the provided model parameter.

        Args:
            model (ModelComposition | ModelChoice | str | None): The model to initialize from. Can be a ModelComposition, ModelChoice dict, string, or None.

        Returns:
            TotalModelChoice: A dict with keys "act", "get", and "locate" mapping to model names (or a ModelComposition for "locate").
        """
        if isinstance(model_choice, ModelComposition):
            return {
                "act": ModelName.ASKUI,
                "get": ModelName.ASKUI,
                "locate": model_choice,
            }
        if isinstance(model_choice, str) or model_choice is None:
            return {
                "act": model_choice or ModelName.ASKUI,
                "get": model_choice or ModelName.ASKUI,
                "locate": model_choice or ModelName.ASKUI,
            }
        return {
            "act": model_choice.get("act", ModelName.ASKUI),
            "get": model_choice.get("get", ModelName.ASKUI),
            "locate": model_choice.get("locate", ModelName.ASKUI),
        }

    @telemetry.record_call(exclude={"locator"})
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def click(
        self,
        locator: Optional[str | Locator] = None,
        button: Literal["left", "middle", "right"] = "left",
        repeat: Annotated[int, Field(gt=0)] = 1,
        model: ModelComposition | str | None = None,
    ) -> None:
        """
        Simulates a mouse click on the user interface element identified by the provided locator.

        Args:
            locator (str | Locator | None, optional): The identifier or description of the element to click. If `None`, clicks at current position.
            button ('left' | 'middle' | 'right', optional): Specifies which mouse button to click. Defaults to `'left'`.
            repeat (int, optional): The number of times to click. Must be greater than `0`. Defaults to `1`.
            model (ModelComposition | str | None, optional): The composition or name of the model(s) to be used for locating the element to click on using the `locator`.

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                agent.click()              # Left click on current position
                agent.click("Edit")        # Left click on text "Edit"
                agent.click("Edit", button="right")  # Right click on text "Edit"
                agent.click(repeat=2)      # Double left click on current position
                agent.click("Edit", button="middle", repeat=4)   # 4x middle click on text "Edit"
            ```
        """
        msg = "click"
        if button != "left":
            msg = f"{button} " + msg
        if repeat > 1:
            msg += f" {repeat}x times"
        if locator is not None:
            msg += f" on {locator}"
        logger.debug("VisionAgent received instruction to %s", msg)
        self._reporter.add_message("User", msg)
        self._click(locator, button, repeat, model)

    def _click(
        self,
        locator: Optional[str | Locator],
        button: Literal["left", "middle", "right"],
        repeat: int,
        model: ModelComposition | str | None,
    ) -> None:
        if locator is not None:
            self._mouse_move(locator, model)
        self.tools.os.click(button, repeat)

    def _locate(
        self,
        locator: str | Locator,
        screenshot: Optional[Img] = None,
        model: ModelComposition | str | None = None,
    ) -> Point:
        def locate_with_screenshot() -> Point:
            _screenshot = ImageSource(
                self.tools.os.screenshot() if screenshot is None else screenshot
            )
            return self._model_router.locate(
                screenshot=_screenshot,
                locator=locator,
                model_choice=model or self._model_choice["locate"],
            )

        point = self._retry.attempt(locate_with_screenshot)
        self._reporter.add_message("ModelRouter", f"locate: ({point[0]}, {point[1]})")
        logger.debug("ModelRouter locate: (%d, %d)", point[0], point[1])
        return point

    @telemetry.record_call(exclude={"locator", "screenshot"})
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def locate(
        self,
        locator: str | Locator,
        screenshot: Optional[Img] = None,
        model: ModelComposition | str | None = None,
    ) -> Point:
        """
        Locates the UI element identified by the provided locator.

        Args:
            locator (str | Locator): The identifier or description of the element to locate.
            screenshot (Img | None, optional): The screenshot to use for locating the element. Can be a path to an image file, a PIL Image object or a data URL. If `None`, takes a screenshot of the currently selected display.
            model (ModelComposition | str | None, optional): The composition or name of the model(s) to be used for locating the element using the `locator`.

        Returns:
            Point: The coordinates of the element as a tuple (x, y).

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                point = agent.locate("Submit button")
                print(f"Element found at coordinates: {point}")
            ```
        """
        self._reporter.add_message("User", f"locate {locator}")
        logger.debug("VisionAgent received instruction to locate %s", locator)
        return self._locate(locator, screenshot, model)

    def _mouse_move(
        self, locator: str | Locator, model: ModelComposition | str | None = None
    ) -> None:
        point = self._locate(locator=locator, model=model)
        self.tools.os.mouse_move(point[0], point[1])

    @telemetry.record_call(exclude={"locator"})
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def mouse_move(
        self,
        locator: str | Locator,
        model: ModelComposition | str | None = None,
    ) -> None:
        """
        Moves the mouse cursor to the UI element identified by the provided locator.

        Args:
            locator (str | Locator): The identifier or description of the element to move to.
            model (ModelComposition | str | None, optional): The composition or name of the model(s) to be used for locating the element to move the mouse to using the `locator`.

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                agent.mouse_move("Submit button")  # Moves cursor to submit button
                agent.mouse_move("Close")  # Moves cursor to close element
                agent.mouse_move("Profile picture", model="custom_model")  # Uses specific model
            ```
        """
        self._reporter.add_message("User", f"mouse_move: {locator}")
        logger.debug("VisionAgent received instruction to mouse_move to %s", locator)
        self._mouse_move(locator, model)

    @telemetry.record_call()
    @validate_call
    def mouse_scroll(
        self,
        x: int,
        y: int,
    ) -> None:
        """
        Simulates scrolling the mouse wheel by the specified horizontal and vertical amounts.

        Args:
            x (int): The horizontal scroll amount. Positive values typically scroll right, negative values scroll left.
            y (int): The vertical scroll amount. Positive values typically scroll down, negative values scroll up.

        Note:
            The actual scroll direction depends on the operating system's configuration.
            Some systems may have "natural scrolling" enabled, which reverses the traditional direction.

            The meaning of scroll units varies across operating systems and applications.
            A scroll value of `10` might result in different distances depending on the application and system settings.

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                agent.mouse_scroll(0, 10)  # Usually scrolls down 10 units
                agent.mouse_scroll(0, -5)  # Usually scrolls up 5 units
                agent.mouse_scroll(3, 0)   # Usually scrolls right 3 units
            ```
        """
        self._reporter.add_message("User", f'mouse_scroll: "{x}", "{y}"')
        self.tools.os.mouse_scroll(x, y)

    @telemetry.record_call(exclude={"text", "locator"})
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def type(
        self,
        text: Annotated[str, Field(min_length=1)],
        locator: str | Locator | None = None,
        model: ModelComposition | str | None = None,
        clear: bool = True,
    ) -> None:
        """
        Types the specified text as if it were entered on a keyboard.

        If `locator` is provided, it will first click on the element to give it focus before typing.
        If `clear` is `True` (default), it will triple click on the element to select the current text (in multi-line inputs like textareas the current line or paragraph) before typing.

        **IMPORTANT:** `clear` only works if a `locator` is provided.

        Args:
            text (str): The text to be typed. Must be at least `1` character long.
            locator (str | Locator | None, optional): The identifier or description of the element (e.g., input field) to type into. If `None`, types at the current focus.
            model (ModelComposition | str | None, optional): The composition or name of the model(s) to be used for locating the element, i.e., input field, to type into using the `locator`.
            clear (bool, optional): Whether to triple click on the element to give it focus and select the current text before typing. Defaults to `True`.

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                agent.type("Hello, world!")  # Types "Hello, world!" at current focus
                agent.type("user@example.com", locator="Email")  # Clicks on "Email" input, then types
                agent.type("password123", locator="Password field", model="custom_model")  # Uses specific model
                agent.type("Hello, world!", locator="Textarea", clear=False)  # Types "Hello, world!" into textarea without clearing
            ```
        """
        msg = f'type "{text}"'
        if locator is not None:
            msg += f" into {locator}"
            if clear:
                repeat = 3
                msg += " clearing the current content (line/paragraph) of input field"
            else:
                repeat = 1
            self._click(locator=locator, button="left", repeat=repeat, model=model)
        logger.debug("VisionAgent received instruction to %s", msg)
        self._reporter.add_message("User", msg)
        self.tools.os.type(text)

    @overload
    def get(
        self,
        query: Annotated[str, Field(min_length=1)],
        response_schema: None = None,
        model: str | None = None,
        image: Optional[Img] = None,
    ) -> str: ...
    @overload
    def get(
        self,
        query: Annotated[str, Field(min_length=1)],
        response_schema: Type[ResponseSchema],
        model: str | None = None,
        image: Optional[Img] = None,
    ) -> ResponseSchema: ...

    @telemetry.record_call(exclude={"query", "image", "response_schema"})
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def get(
        self,
        query: Annotated[str, Field(min_length=1)],
        response_schema: Type[ResponseSchema] | None = None,
        model: str | None = None,
        image: Optional[Img] = None,
    ) -> ResponseSchema | str:
        """
        Retrieves information from an image (defaults to a screenshot of the current screen) based on the provided query.

        Args:
            query (str): The query describing what information to retrieve.
            image (Img | None, optional): The image to extract information from. Defaults to a screenshot of the current screen. Can be a path to an image file, a PIL Image object or a data URL.
            response_schema (Type[ResponseSchema] | None, optional): A Pydantic model class that defines the response schema. If not provided, returns a string.
            model (str | None, optional): The composition or name of the model(s) to be used for retrieving information from the screen or image using the `query`. Note: `response_schema` is not supported by all models.

        Returns:
            ResponseSchema | str: The extracted information, `str` if no `response_schema` is provided.

        Example:
            ```python
            from askui import ResponseSchemaBase, VisionAgent
            from PIL import Image
            import json

            class UrlResponse(ResponseSchemaBase):
                url: str

            class NestedResponse(ResponseSchemaBase):
                nested: UrlResponse

            class LinkedListNode(ResponseSchemaBase):
                value: str
                next: "LinkedListNode | None"

            with VisionAgent() as agent:
                # Get URL as string
                url = agent.get("What is the current url shown in the url bar?")

                # Get URL as Pydantic model from image at (relative) path
                response = agent.get(
                    "What is the current url shown in the url bar?",
                    response_schema=UrlResponse,
                    image="screenshot.png",
                )
                # Dump whole model
                print(response.model_dump_json(indent=2))
                # or
                response_json_dict = response.model_dump(mode="json")
                print(json.dumps(response_json_dict, indent=2))
                # or for regular dict
                response_dict = response.model_dump()
                print(response_dict["url"])

                # Get boolean response from PIL Image
                is_login_page = agent.get(
                    "Is this a login page?",
                    response_schema=bool,
                    image=Image.open("screenshot.png"),
                )
                print(is_login_page)

                # Get integer response
                input_count = agent.get(
                    "How many input fields are visible on this page?",
                    response_schema=int,
                )
                print(input_count)

                # Get float response
                design_rating = agent.get(
                    "Rate the page design quality from 0 to 1",
                    response_schema=float,
                )
                print(design_rating)

                # Get nested response
                nested = agent.get(
                    "Extract the URL and its metadata from the page",
                    response_schema=NestedResponse,
                )
                print(nested.nested.url)

                # Get recursive response
                linked_list = agent.get(
                    "Extract the breadcrumb navigation as a linked list",
                    response_schema=LinkedListNode,
                )
                current = linked_list
                while current:
                    print(current.value)
                    current = current.next
            ```
        """
        logger.debug("VisionAgent received instruction to get '%s'", query)
        _image = ImageSource(self.tools.os.screenshot() if image is None else image)
        self._reporter.add_message("User", f'get: "{query}"', image=_image.root)
        response = self._model_router.get(
            image=_image,
            query=query,
            response_schema=response_schema,
            model_choice=model or self._model_choice["get"],
        )
        message_content = (
            str(response)
            if isinstance(response, (str, bool, int, float))
            else response.model_dump()
        )
        self._reporter.add_message("Agent", message_content)
        return response

    @telemetry.record_call()
    @validate_call
    def wait(
        self,
        sec: Annotated[float, Field(gt=0.0)],
    ) -> None:
        """
        Pauses the execution of the program for the specified number of seconds.

        Args:
            sec (float): The number of seconds to wait. Must be greater than `0.0`.

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                agent.wait(5)  # Pauses execution for 5 seconds
                agent.wait(0.5)  # Pauses execution for 500 milliseconds
            ```
        """
        time.sleep(sec)

    @telemetry.record_call()
    @validate_call
    def key_up(
        self,
        key: PcKey | ModifierKey,
    ) -> None:
        """
        Simulates the release of a key.

        Args:
            key (PcKey | ModifierKey): The key to be released.

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                agent.key_up('a')  # Release the 'a' key
                agent.key_up('shift')  # Release the 'Shift' key
            ```
        """
        self._reporter.add_message("User", f'key_up "{key}"')
        logger.debug("VisionAgent received in key_up '%s'", key)
        self.tools.os.keyboard_release(key)

    @telemetry.record_call()
    @validate_call
    def key_down(
        self,
        key: PcKey | ModifierKey,
    ) -> None:
        """
        Simulates the pressing of a key.

        Args:
            key (PcKey | ModifierKey): The key to be pressed.

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                agent.key_down('a')  # Press the 'a' key
                agent.key_down('shift')  # Press the 'Shift' key
            ```
        """
        self._reporter.add_message("User", f'key_down "{key}"')
        logger.debug("VisionAgent received in key_down '%s'", key)
        self.tools.os.keyboard_pressed(key)

    @telemetry.record_call()
    @validate_call
    def mouse_up(
        self,
        button: Literal["left", "middle", "right"] = "left",
    ) -> None:
        """
        Simulates the release of a mouse button.

        Args:
            button ('left' | 'middle' | 'right', optional): The mouse button to be released. Defaults to `'left'`.

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                agent.mouse_up()  # Release the left mouse button
                agent.mouse_up('right')  # Release the right mouse button
                agent.mouse_up('middle')  # Release the middle mouse button
            ```
        """
        self._reporter.add_message("User", f'mouse_up "{button}"')
        logger.debug("VisionAgent received instruction to mouse_up '%s'", button)
        self.tools.os.mouse_up(button)

    @telemetry.record_call()
    @validate_call
    def mouse_down(
        self,
        button: Literal["left", "middle", "right"] = "left",
    ) -> None:
        """
        Simulates the pressing of a mouse button.

        Args:
            button ('left' | 'middle' | 'right', optional): The mouse button to be pressed. Defaults to `'left'`.

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                agent.mouse_down()  # Press the left mouse button
                agent.mouse_down('right')  # Press the right mouse button
                agent.mouse_down('middle')  # Press the middle mouse button
            ```
        """
        self._reporter.add_message("User", f'mouse_down "{button}"')
        logger.debug("VisionAgent received instruction to mouse_down '%s'", button)
        self.tools.os.mouse_down(button)

    @telemetry.record_call(exclude={"goal", "on_message"})
    @validate_call
    def act(
        self,
        goal: Annotated[str | list[MessageParam], Field(min_length=1)],
        model: str | None = None,
        on_message: OnMessageCb | None = None,
    ) -> None:
        """
        Instructs the agent to achieve a specified goal through autonomous actions.

        The agent will analyze the screen, determine necessary steps, and perform actions
        to accomplish the goal. This may include clicking, typing, scrolling, and other
        interface interactions.

        Args:
            goal (str | list[MessageParam]): A description of what the agent should achieve.
            model (str | None, optional): The composition or name of the model(s) to be used for achieving the `goal`.
            on_message (OnMessageCb | None, optional): Callback for new messages. If it returns `None`, stops and does not add the message.

        Returns:
            None

        Raises:
            MaxTokensExceededError: If the model reaches the maximum token limit
                defined in the agent settings.
            ModelRefusalError: If the model refuses to process the request.

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                agent.act("Open the settings menu")
                agent.act("Search for 'printer' in the search box")
                agent.act("Log in with username 'admin' and password '1234'")
            ```
        """
        goal_str = (
            goal
            if isinstance(goal, str)
            else "\n".join(msg.model_dump_json() for msg in goal)
        )
        self._reporter.add_message("User", f'act: "{goal_str}"')
        logger.debug(
            "VisionAgent received instruction to act towards the goal '%s'", goal_str
        )
        messages: list[MessageParam] = (
            [MessageParam(role="user", content=goal)] if isinstance(goal, str) else goal
        )
        _model = model or self._model_choice["act"]
        self._update_tool_collection(_model)
        self._model_router.act(messages, _model, on_message)

    def _update_tool_collection(self, model: str) -> None:
        if model == ModelName.ANTHROPIC__CLAUDE__3_5__SONNET__20241022:
            self._tool_collection.append_tool(
                Computer20241022Tool(agent_os=self.tools.os)
            )
        if model == ModelName.CLAUDE__SONNET__4__20250514 or model == ModelName.ASKUI:
            self._tool_collection.append_tool(
                Computer20250124Tool(agent_os=self.tools.os)
            )

    @telemetry.record_call()
    @validate_call
    def keyboard(
        self,
        key: PcKey | ModifierKey,
        modifier_keys: Optional[list[ModifierKey]] = None,
        repeat: Annotated[int, Field(gt=0)] = 1,
    ) -> None:
        """
        Simulates pressing (and releasing) a key or key combination on the keyboard.

        Args:
            key (PcKey | ModifierKey): The main key to press. This can be a letter, number, special character, or function key.
            modifier_keys (list[ModifierKey] | None, optional): List of modifier keys to press along with the main key. Common modifier keys include `'ctrl'`, `'alt'`, `'shift'`.
            repeat (int, optional): The number of times to press (and release) the key. Must be greater than `0`. Defaults to `1`.

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                agent.keyboard('a')  # Press 'a' key
                agent.keyboard('enter')  # Press 'Enter' key
                agent.keyboard('v', ['control'])  # Press Ctrl+V (paste)
                agent.keyboard('s', ['control', 'shift'])  # Press Ctrl+Shift+S
                agent.keyboard('a', repeat=2)  # Press 'a' key twice
            ```
        """
        msg = f"press and release key '{key}'"
        if modifier_keys is not None:
            modifier_keys_str = " + ".join(f"'{key}'" for key in modifier_keys)
            msg += f" with modifiers key{'s' if len(modifier_keys) > 1 else ''} {modifier_keys_str}"
        if repeat > 1:
            msg += f" {repeat}x times"
        self._reporter.add_message("User", msg)
        logger.debug("VisionAgent received instruction to press '%s'", key)
        self.tools.os.keyboard_tap(key, modifier_keys, count=repeat)

    @telemetry.record_call(exclude={"command"})
    @validate_call
    def cli(
        self,
        command: Annotated[str, Field(min_length=1)],
    ) -> None:
        """
        Executes a command on the command line interface.

        This method allows running shell commands directly from the agent. The command
        is split on spaces and executed as a subprocess.

        Args:
            command (str): The command to execute on the command line.

        Example:
            ```python
            from askui import VisionAgent

            with VisionAgent() as agent:
                # Use for Windows
                agent.cli(fr'start "" "C:\Program Files\VideoLAN\VLC\vlc.exe"') # Start in VLC non-blocking
                agent.cli(fr'"C:\Program Files\VideoLAN\VLC\vlc.exe"') # Start in VLC blocking

                # Mac
                agent.cli("open -a chrome")  # Open Chrome non-blocking for mac
                agent.cli("chrome")  # Open Chrome blocking for linux
                agent.cli("echo Hello World")  # Prints "Hello World"
                agent.cli("python --version")  # Displays Python version

                # Linux
                agent.cli("nohub chrome")  # Open Chrome non-blocking for linux
                agent.cli("chrome")  # Open Chrome blocking for linux
                agent.cli("echo Hello World")  # Prints "Hello World"
                agent.cli("python --version")  # Displays Python version

            ```
        """
        logger.debug("VisionAgent received instruction to execute '%s' on cli", command)
        self.tools.os.run_command(command)

    @telemetry.record_call()
    def close(self) -> None:
        self.tools.os.disconnect()
        self._reporter.generate()

    @telemetry.record_call()
    def open(self) -> None:
        self.tools.os.connect()

    @telemetry.record_call()
    def __enter__(self) -> "VisionAgent":
        self.open()
        return self

    @telemetry.record_call(exclude={"exc_value", "traceback"})
    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        self.close()
