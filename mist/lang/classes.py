from string import Formatter
import json
from dataclasses import dataclass, field
from typing import List

from mist.sdk import db, get_id, get_key, get_param, watchers, functions, config, watchedInsert, MistAbortException, command_runner, function_runner, execution
from mist.sdk.exceptions import MistException
from mist.sdk.stack import stack

@dataclass
class DataCommand:
    parent: object
    name: str
    params: list = field(default_factory=list)

    def run(self):

        table_params = [
            f"{param} text"
            for param in self.params
        ]

        db.create_table(self.name, table_params)

@dataclass
class SaveCommand:
    parent: object
    sources: list
    target: str
    params: list

    def run(self):
        if config.debug:
            print(f"-> Put to {self.target}")
        fields = None
        if self.params:
            fields = [p for p in self.params]
        values = [
            json.dumps(get_id(i)) if i.customList or type(get_id(i)) is list else str(get_id(i))
            for i in self.sources
        ]
        watchedInsert(self.target, values, fields=fields)

@dataclass
class SaveListCommand:
    parent: object
    list: str
    selectors: list
    sources: list
    target: str
    params: list

    def run(self):
        if config.debug:
            print(f"->Put list to {self.target}")

        cols = [c for c in self.params] if self.params else None
        sels = [s for s in self.selectors] if self.selectors else None

        elements = get_id(self.list)
        if type(elements) is not list:
            raise MistException(f"{self.list} is not a list")

        commons = [ str(get_id(it)) for it in self.sources ] if self.sources else None

        for el in elements:
            if type(el) is dict:
                values = [ v for v in el.values() ] if sels is None else [ el[sel] for sel in sels ]
            else:
                values = list(str(el))

            if commons is not None:
                values.extend(commons)

            watchedInsert(self.target, values, fields=cols)

@dataclass
class CheckCommand:
    parent: object
    var: str
    operator: str
    result: list
    commands: list
    elseCommands: list

    def run(self):
        if config.debug:
            print(f"-> Check that {self.var} is {self.result}")

        # If condition is not met we substitute the check command list with the else command list.
        if (self.operator == 'is') and (get_id(self.var) != get_id(self.result)):
            self.commands = self.elseCommands
        elif (self.operator == 'is not') and (get_id(self.var) == get_id(self.result)):
            self.commands = self.elseCommands
        return True

@dataclass
class PrintCommand:
    parent: object
    texts: list

    def run(self):
        if config.debug:
            print(f"-> BuiltPrint")

        print(*([get_id(s) for s in self.texts]))

@dataclass
class AbortCommand:
    parent: object
    reason: str

    def run(self):
        if self.reason:
            reason = self.reason
        else:
            reason = "Abort reached"

        raise MistAbortException(reason)

@dataclass
class IterateCommand:
    parent: object
    var: str
    name: str
    commands: list

    def run(self):
        if config.debug:
            print(f"-> Iterate {self.var}")

        res = []

        for index, item in enumerate(get_id(self.var)):
            res.append({self.name: item, "index": index})

        return res

@dataclass
class WatchCommand:
    parent: object
    var: str
    name: str
    commands: list

    def run(self):
        if config.debug:
            print(f"-> Watch {self.var}")
        watchers.append({"var": self.var, "name": self.name, "commands": self.commands})

@dataclass
class AppendCommand:
    parent: object
    target: str
    value: str

    def run(self):
        if config.debug:
            print(f"-> AppendCommand {self.target}")
        for s in reversed(stack):
            if "MistBaseNamespace" in s:
                s[self.target].append(get_id(self.value))

@dataclass
class SetCommand:
    parent: object
    key: str
    value: str

    def run(self):
        if config.debug:
            print(f"-> SetCommand {self.key}")
        for s in reversed(stack):
            if "MistBaseNamespace" in s:
                s[self.key] = get_id(self.value)

@dataclass
class ExposeCommand:
    parent: object
    value: str

    def run(self):
        if config.debug:
            print(f"-> ExposeCommand {self.value}")
        for i in range(len(stack)-1,0,-1):
            if "MistBaseNamespace" in stack[i]:
                stack[i-1][self.value] = get_key(self.value)

@dataclass
class FunctionCall:
    parent: object
    name: str
    args: list
    namedArgs: list
    result: str
    commands: list
    targets: list

    def run(self):
        if config.debug:
            print(f"-> FunctionCall {self.name}")
        result = function_runner(self.name, self.args, self.namedArgs)
        if self.commands:
            stack.append({self.result: result} if self.result else {})
            command_runner(self.commands)
            stack.pop()
        #TODO: handle stream targets

@dataclass
class FunctionDefinition:
    parent: object
    name: str
    args: list
    result: str
    commands: list

    def run(self):
        if config.debug:
            print(f"-> Function Definition {self.name}")
        functions[self.name] = {"native": False, "commands": self.commands, "args": self.args, "result": self.result}

exports = [DataCommand, SaveCommand, SaveListCommand, CheckCommand,
           PrintCommand, IterateCommand, WatchCommand, AbortCommand,
           SetCommand, ExposeCommand, AppendCommand, FunctionCall,
           FunctionDefinition]
