
from functools import wraps
import inspect
import logging
import sys
import os
import importlib
from typing import Union

from knowledgenet.rule import Rule
from knowledgenet.ruleset import Ruleset
from knowledgenet.repository import Repository
from knowledgenet.util import to_tuple

registry={}

def lookup(repositories:str|list|tuple, id:str=None)->Repository:
    if not isinstance(repositories, str) and not id:
        raise Exception("When multiple repositories are specified, a repository id must be provided")
    
    repositories = to_tuple(repositories)
    if not id:
        id = repositories[0]
    #print(registry)
    
    ruleset=[]
    for repository in repositories:
        if repository not in registry:
            raise Exception(f'repository: repository not found')
        
        for ruleset_id,rules in registry[repository].items():
            ruleset.append(Ruleset(ruleset_id, rules))
        
    # Sort by id. The assumption is that the ids are defined in alphabetical order. For example: 001-validation-rules, 002-business-rules, etc.
    ruleset.sort(key=lambda r: r.id)
    return Repository(id, ruleset)

def ruledef(*decorator_args, **decorator_kwargs):
    def ruledef_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'enabled' in decorator_kwargs and not decorator_kwargs['enabled']:
                return None

            rule = func(*args, **kwargs)
        
            # Override the rule ruleset and repository ids
            rule.id = decorator_kwargs.get('id', func.__name__)
            rule_path = os.path.dirname(inspect.getfile(func)).replace("/", os.sep).replace("\\", os.sep)
            splits = rule_path.split(os.sep)
            rule.ruleset = decorator_kwargs.get('ruleset', splits[-1])
            rule.repository = decorator_kwargs.get('repository', splits[-2])
            #logging.info(f"Rule: {rule_path}, {rule.id}, {rule.repository}, {rule.ruleset}")
            
            if rule.repository not in registry:
                registry[rule.repository] = {}
            if rule.ruleset not in registry[rule.repository]:
                registry[rule.repository][rule.ruleset] = []
            if any(existing_rule.id == rule.id for existing_rule in registry[rule.repository][rule.ruleset]):
                raise Exception(f"Rule with id {rule.id} already exists")
            registry[rule.repository][rule.ruleset].append(rule)
            return rule
        return wrapper
    if decorator_args and callable(decorator_args[0]):
        # Decorator called without arguments
        #print('without', decorator_args, decorator_kwargs)
        return ruledef_wrapper(decorator_args[0])
    else:
        # Decorator called with arguments
        #print('with', decorator_args, decorator_kwargs)
        return ruledef_wrapper

def _load_rules_from_module(module):
    for name,obj in inspect.getmembers(module):
        #print(f"{name}:{obj}")
        if inspect.isfunction(obj) and name != 'ruledef':
            if getattr(obj, '__wrapped__', False):
                # Perform the following action only for functions that have been decorated with @ruledef
                rule = obj()
                if rule and type(rule) is not Rule:
                    raise Exception(f"Function {name} must return a Rule object")
                
def _find_modules(path):
    modules = []
    for file in os.listdir(path):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]  # Remove .py extension
            # print(f"Loading module: {module_name}")
            modules.append(importlib.import_module(module_name))
    return modules

def load_rules_from_filepaths(*paths:str|list|tuple):
    if len(paths) == 1:
        paths = to_tuple(*paths)

    for path in paths:
        #logging.info(f"Loading path: {path}")
        sys.path.append(path)
        modules = _find_modules(path)
        for module in modules:
            _load_rules_from_module(module)

'''
import my_module
# Get the absolute path of the module
module_path = my_module.__file__ 
# Get the directory containing the module
module_dir = os.path.dirname(module_path)
'''
def load_rules_from_packages(packages:Union[str,list,tuple]):
    packages = to_tuple(packages)
    for package in packages:
        init_module = importlib.__import__(package)
        path = os.path.dirname(init_module.__file__)
        modules = _find_modules(path)
        for module in modules:
            _load_rules_from_module(module)
