# Copyright (c) Alibaba, Inc. and its affiliates.
import os.path
from abc import abstractmethod
from typing import Dict, Optional, Type

from ms_agent.agent import Agent
from ms_agent.config import Config
from ms_agent.utils import get_logger
from omegaconf import DictConfig

from .base import Workflow

logger = get_logger()


class ChainWorkflow(Workflow):

    def __init__(self,
                 config_dir_or_id: Optional[str] = None,
                 config: Optional[DictConfig] = None,
                 env: Optional[Dict[str, str]] = None,
                 trust_remote_code: Optional[bool] = False,
                 **kwargs):
        if config_dir_or_id is None:
            self.config = config
        else:
            self.config = Config.from_task(config_dir_or_id, env)
        self.trust_remote_code = trust_remote_code or False
        self.load_cache = kwargs.get('load_cache', True)
        self.mcp_server_file = kwargs.get('mcp_server_file', None)
        self.workflow_chains = []
        self.build_workflow()

    def build_workflow(self):
        if not self.config:
            return []

        has_next = set()
        start_task = None
        for task_name, task_config in self.config.items():
            if 'next' in task_config:
                next_tasks = task_config['next']
                if isinstance(next_tasks, str):
                    has_next.add(next_tasks)
                else:
                    assert len(
                        next_tasks
                    ) == 1, 'ChainWorkflow only supports one next task'
                    has_next.update(next_tasks)

        for task_name in self.config.keys():
            if task_name not in has_next:
                start_task = task_name
                break

        if start_task is None:
            raise ValueError('No start task found')

        result = []
        current_task = start_task

        while current_task:
            result.append(current_task)
            next_task = None
            task_config = self.config[current_task]
            if 'next' in task_config:
                next_tasks = task_config['next']
                if isinstance(next_tasks, str):
                    next_task = next_tasks
                else:
                    next_task = next_tasks[0]

            current_task = next_task
        self.workflow_chains = result

    @abstractmethod
    async def run(self, inputs, **kwargs):
        config = None
        for task in self.workflow_chains:
            task_info = getattr(self.config, task)
            agent_cls: Type[Agent] = self.find_agent(task_info.agent.name)
            _cfg = getattr(task_info, 'config', config)
            init_args = getattr(task_info.agent, 'kwargs', {})
            init_args.pop('trust_remote_code', None)
            init_args['trust_remote_code'] = self.trust_remote_code
            init_args['mcp_server_file'] = self.mcp_server_file
            init_args['task'] = task
            init_args['load_cache'] = self.load_cache
            if isinstance(_cfg, str):
                if config is not None:
                    logger.info(
                        f'Task {task} has its own config: {_cfg}, '
                        f'the config from the previous task will be ignored.')
                agent = agent_cls(
                    config_dir_or_id=os.path.join(self.config.local_dir, _cfg),
                    **init_args)
            else:
                agent = agent_cls(config=_cfg, **init_args)
            inputs = await agent.run(inputs, **kwargs)
            config = agent.prepare_config_for_next_step()
        return inputs
