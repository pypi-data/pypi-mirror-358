import json
import functools
from novatrace.database.model import Session, Project, Trace, Base, engine as default_engine, sessionmaker, TraceTypes
from sqlalchemy import create_engine
from datetime import datetime
from novatrace.connect import hora
from typing import Dict, Union
import pytz
import inspect

class NovaTrace:
    def __init__(self, session_name: str, engine_url: str = None, time_zone: pytz.tzinfo = pytz.utc):
        """
        Init a new NovaTrace instance.
        Args:
            session_name (str): Name of the session to be created or connected to.
            engine_url (str, optional): SQLAlchemy engine URL. If not provided, defaults to the default engine.
            time_zone (pytz.tzinfo, optional): Time zone for timestamps. Defaults to UTC.
        Raises:
            ValueError: If metadata is not provided or incomplete.
        Returns:
            None
        """
        self.time_zone = time_zone
        if engine_url:
            self.engine = create_engine(engine_url)
        else:
            self.engine = default_engine
        Base.metadata.create_all(self.engine)
        session = sessionmaker(bind=self.engine)

        self.session = session() # Sesion de SQLAlchemy

        for name in ["LLM", "Agent", "Tool"]:
            if not self.session.query(TraceTypes).filter_by(name=name).first():
                new_type = TraceTypes(name=name)
                self.session.add(new_type) 
        self.session.commit() # BDD Build

        self.active_session = self.session.query(Session).filter_by(name=session_name).first()

        if not self.active_session:
            self.active_session = Session(name=session_name, created_at=datetime.now(self.time_zone))
            self.session.add(self.active_session)
            self.session.commit()
        self.project = None
        self.provider: str = None
        self.model: str = None
        self.input_cost_per_million_tokens: float = 0.0
        self.output_cost_per_million_tokens: float = 0.0
        
    def close(self):
        """
        Close the current session and connection to the database.
        Returns:
            None
        """
        self.session.close()

    def list_projects(self):
        """
        List all projects in the current session.
        """
        return self.session.query(Project).filter_by(session_id=self.active_session.id).all()
    
    def tokenizer(self, response) -> Dict[str, Union[int, float]]:
        """
        Tokenizer to calculate the number of tokens used in a response and their cost.
        Args:
            response: The response object from the LLM or agent.
        Returns:
            Dict[str, Union[int, float]]: A dictionary containing the number of input tokens,
                                          output tokens, total tokens
        """
        if hasattr(response, "usage"):
            prompt_tokens = response.usage.input_tokens
            completion_tokens = response.usage.output_tokens
            total_tokens = prompt_tokens + completion_tokens

            tokens = {
                "input_tokens": prompt_tokens,
                "output_tokens": completion_tokens,
                "total_tokens": total_tokens,
            }
        else:
            tokens = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }
        return tokens
    
    def metadata(self, metadata: Dict[str, Union[str, float]]):
        """
        Set metadata for the current session.
        Args:
            metadata (Dict[str, Union[str, float]]): A dictionary containing metadata about the model
               - provider (str) | The provider of the model (e.g., "OpenAI", "Anthropic")
               - model (str) | The name of the model (e.g., "gpt-3.5-turbo", "claude-3-haiku-20240307")
               - input_cost_per_million_tokens (float) | Cost per million tokens for input
               - output_cost_per_million_tokens (float) | Cost per million tokens for output
        Raises:
            ValueError: If metadata is not a dictionary or does not contain the required keys.
        Returns:
            None
        """
        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")
        
        self.provider = metadata.get('provider', None)
        self.model = metadata.get('model', None)
        self.input_cost_per_million_tokens = metadata.get('input_cost_per_million_tokens', 0.0)
        self.output_cost_per_million_tokens = metadata.get('output_cost_per_million_tokens', 0.0)

        if not all([self.provider, self.model, self.input_cost_per_million_tokens, self.output_cost_per_million_tokens]):
            raise ValueError("Metadata must contain 'provider', 'model', 'input_cost_per_million_tokens', and 'output_cost_per_million_tokens'")

    def create_project(self, project_name: str):
        """
        Create a new project in the current session.
        Args:
            project_name (str): Name of the project to be created.
        Raises:
            ValueError: If a project with the same name already exists in the current session.
        Returns:
            None
        """
        existing_project = self.session.query(Project).filter_by(name=project_name, session_id=self.active_session.id).first()
        if existing_project:
            raise ValueError(f"Project '{project_name}' already exists in session '{self.active_session.name}'")
        self.project = Project(name=project_name, session_id=self.active_session.id, created_at=datetime.now(self.time_zone))

        self.session.add(self.project)
        self.session.commit()

    def connect_to_project(self, project_name: str):
        """
        Connect to an existing project in the current session.
        Args:
            project_name (str): Name of the project to connect to.
        Raises:
            ValueError: If the project with the specified name does not exist in the current session.
        Returns:
            Project: The project object if found.
        """
        self.project = self.session.query(Project).filter_by(name=project_name, session_id=self.active_session.id).first()
        if not self.project:
            raise ValueError(f"Project '{project_name}' not found in session '{self.active_session.name}'")
        return self.project

    def _get_named_args(self, func, *args, **kwargs):
        """
        Get named arguments from a function call.
        """
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        named_args = {}
        for name, value in bound_args.arguments.items():
            named_args[name] = {
                "type": type(value).__name__,
                "value": value
            }
        return named_args

    def _log_trace(self, type_id: int, input_data, output_data, request_time, response_time,
                    input_tokens=0, output_tokens=0, model_name=None, model_provider=None):
        """
        Log a trace for the current request.
        Args:
            type_id (int): Type of trace (1 for LLM, 2 for Agent, 3 for Tool).
            input_data: Input data for the trace.
            output_data: Output data for the trace.
            request_time (datetime): Time when the request was made.
            response_time (datetime): Time when the response was received.
            input_tokens (int, optional): Number of input tokens used. Defaults to 0.
            output_tokens (int, optional): Number of output tokens used. Defaults to 0.
        Returns:
            None
        Raises:
            None
        """
        duration = (response_time - request_time).total_seconds() * 1000  # ms
        trace = Trace(
            type_id=type_id,
            input_data=json.dumps(input_data, default=str),
            output_data=json.dumps(output_data, default=str),
            project_id=self.project.id,
            created_at=response_time,
            request_time=request_time,
            response_time=response_time,
            duration_ms=duration,
            input_tokens=input_tokens,
            output_tokens=output_tokens,

            model_provider=model_provider if model_provider else self.provider,
            model_name=model_name if model_name else self.model,
            model_input_cost=self.input_cost_per_million_tokens,
            model_output_cost=self.output_cost_per_million_tokens,
            call_cost = ((input_tokens * self.input_cost_per_million_tokens) + (output_tokens * self.output_cost_per_million_tokens))
        )
        self.session.add(trace)
        self.session.commit()

    def llm(self, func):
        """
        Decorator to trace LLM calls.
        Args:
            func: The function to be traced.
        Returns:
            function: The wrapped function that logs the trace.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_time = datetime.now(self.time_zone)
            result = func(*args, **kwargs)
            response_time = datetime.now(self.time_zone)
            try:
                _args = self._get_named_args(func, *args, **kwargs)
            except Exception as e:
                _args = {"args": args}
            self._log_trace(2, {"args": _args},
                            result, request_time, response_time,
                            model_name=kwargs.get("model_name", self.model),
                            model_provider=kwargs.get("model_provider", self.provider),
                            input_tokens=kwargs.get("input_tokens", 0),
                            output_tokens=kwargs.get("output_tokens", 0),
                            )
            return result
        return wrapper

    def agent(self, func):
        """
        Decorator to trace agent calls.
        Args:
            func: The function to be traced.
        Returns:
            function: The wrapped function that logs the trace. 
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_time = datetime.now(self.time_zone)
            result = func(*args, **kwargs)
            tokens = self.tokenizer(result)
            response_time = datetime.now(self.time_zone)
            try:
                _args = self._get_named_args(func, *args, **kwargs)
            except Exception as e:
                _args = {"args": args}
            self._log_trace(2, {"args": _args}, 
                            result, request_time, response_time,
                            tokens.get("input_tokens", 0),
                            tokens.get("output_tokens", 0),
                            model_name=kwargs.get("model_name", self.model),
                            model_provider=kwargs.get("model_provider", self.provider),
                            )
            return result
        return wrapper

    def tool(self, func):
        """ 
        Decorator to trace tool calls.
        Args:
            func: The function to be traced.
        Returns:
            function: The wrapped function that logs the trace.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_time = datetime.now(self.time_zone)
            result = func(*args, **kwargs)
            try:
                result_raw = result[-1]['result']
                result_text = result_raw[0].text if isinstance(result_raw, list) and result_raw else ""

            except Exception as e:
                result_text = result

            response_time = datetime.now(self.time_zone)
            try:
                _args = self._get_named_args(func, *args, **kwargs)
            except Exception as e:
                _args = {"args": args}
            self._log_trace(2, {"args": _args}, 
                            str(result_text), request_time, response_time, # ---
                            )
            return result
        return wrapper