""" agent """
from enum import Enum
from typing import List, Any
from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import FunctionAgent, ReActAgent
from llama_index.core import Settings

class AgentType(Enum):
    """ enum """
    REACT_AGENT = 'ReactAgent'
    FUNCTION_AGENT = 'FunctionAgent'
    # 添加更多选项

class AgentFactory:
    """ factory """
    def __new__(cls, agent_type: AgentType | str,
                tools:List[FunctionTool] = None,
                tools_retriver = None,
                ) -> Any:
        if isinstance(agent_type,AgentType):
            assert agent_type.value in [i.value for i in AgentType]
            key_name = agent_type.value
        else:
            assert agent_type in [i.value for i in AgentType]
            key_name = agent_type
        instance = None

        # assert tools | tools_retriver
        assert (tools is not None) or (tools_retriver is not None)
        if key_name == 'ReactAgent':
            instance = ReActAgent(
                    tools = tools,
                    tools_retriver=tools_retriver,
                    llm=Settings.llm,
                    verbose=True,)

        elif key_name == 'FunctionAgent':
            instance = FunctionAgent(
                tools = tools,
                tools_retriver=tools_retriver,
                llm=Settings.llm,
                verbose=True,)

        else:
            raise TypeError('Unknown type')

        return instance
