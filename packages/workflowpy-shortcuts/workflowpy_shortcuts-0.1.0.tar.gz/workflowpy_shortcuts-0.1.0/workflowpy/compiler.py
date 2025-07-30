import ast as a
import uuid
from enum import IntEnum
from typing import Any, NoReturn, cast, overload

from pydantic import BaseModel, ConfigDict, Field

from workflowpy import value_type as T
from workflowpy.definitions.action import ActionHelper
from workflowpy.models.shortcuts import Action
from workflowpy.modules import modules
from workflowpy.synthesizer import Synthesizer
from workflowpy.utils import convert_property_to_name
from workflowpy.value import (
    ConstantValue,
    ItemValue,
    MagicVariableValue,
    PythonFunctionValue,
    PythonModuleValue,
    PythonTypeValue,
    ShortcutValue,
    TokenAttachmentValue,
    TokenStringValue,
    Value,
    VariableValue,
    token_attachment,
    token_string,
)


class ScopeType(IntEnum):
    GLOBAL = 1
    FUNCTION = 2
    FOREACH = 3
    FORCOUNTER = 4


class Scope(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str | None
    type: ScopeType
    actions: list[Action] = Field(default_factory=list)
    variables: dict[str, Value] = Field(default_factory=dict)
    wrappers: list[tuple[list[Action], list[Action]]] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)

    def add_action(self, identifier: str, parameters: dict[str, Any]):
        action = Action(
            WFWorkflowActionIdentifier=identifier,
            WFWorkflowActionParameters=parameters,
        )
        self.actions.append(action)


class Compiler(a.NodeVisitor):
    """
    This class is responsible for compiling Python code to actions.
    """

    def _push_scope(self, name: str | None, type: ScopeType):
        self.scopes.append(Scope(name=name, type=type))

    def _pop_scope(self):
        scope = self.scopes.pop()
        assert scope.type != ScopeType.GLOBAL
        if scope.type == ScopeType.FUNCTION:
            assert scope.name
            self.functions[scope.name] = scope
        else:
            pre = []
            post = []
            for a, b in scope.wrappers:
                pre.extend(a)
                post.extend(b)
            post = post[::-1]
            self.actions.extend(pre + scope.actions + post)

    def _count_scopes(self, *types: ScopeType):
        count = 0
        for scope in self.scopes:
            if scope.type in types:
                count += 1
        return count

    def _add_scope_wrapper(self, pre: list[Action], post: list[Action]):
        self.scopes[-1].wrappers.append((pre, post))

    @property
    def variables(self):
        return self.scopes[-1].variables

    @property
    def actions(self):
        return self.scopes[-1].actions

    def compile(self, module: a.Module | str):
        self.scopes: list[Scope] = [
            Scope(name=None, type=ScopeType.GLOBAL, variables={})
        ]
        mod = PythonModuleValue(**modules[''])
        for key in mod.children:
            self.variables[key] = mod.getattr(key)
        self.functions: dict[str, Scope] = {}
        if isinstance(module, str):
            module = a.parse(module)

        self.visit(module)

        synthesizer = Synthesizer()
        if self.functions:
            raise NotImplementedError("Functions are not implemented yet!")
        synthesizer.actions.extend(self.scopes[0].actions)
        synthesizer.functions.update({k: v.actions for k, v in self.functions.items()})
        return synthesizer.synthesize()

    visit_Module = visit_Expr = a.NodeVisitor.generic_visit

    def visit_ImportFrom(self, node: a.ImportFrom) -> Any:
        assert node.level == 0, "Relative imports are not supported"
        parts = cast(str, node.module).split('.')
        mod = PythonModuleValue(**modules)
        for part in parts:
            try:
                mod = mod.getattr(part)
            except KeyError:
                raise NotImplementedError(
                    f"Module {node.module!r} is not supported"
                ) from None
        assert isinstance(mod, PythonModuleValue), "{node.module} is not a module"
        for name in node.names:
            if name.name == '*':
                for key in mod.children:
                    self.variables[key] = mod.getattr(key)
            else:
                self.variables[name.asname or name.name] = mod.getattr(name.name)

    def _assign(
        self, var: a.expr, value: a.expr, override_type: T.ValueType | None = None
    ):
        if isinstance(var, a.Name):
            name = var.id
            val = self.visit(value)
            if override_type is not None and hasattr(val, '_type'):
                val._type = override_type
                val = val.aggrandized(
                    'WFCoercionVariableAggrandizement',
                    {'CoercionItemClass': override_type.content_item_class},
                )
            self.variables[name] = val
        else:
            raise NotImplementedError(f"Assign with target {var} is not supported")

    def visit_AnnAssign(self, node: a.AnnAssign) -> Any:
        assert node.value is not None, "Plain annotations are not supported"
        override_type_map = {
            'int': T.number,
            'float': T.number,
            'dict': T.dictionary,
            'str': T.text,
            'bool': T.boolean,
        }
        override_type = None
        annot = None
        if isinstance(node.annotation, a.Name):
            annot = node.annotation.id
            assert annot != 'list', 'List annotation must have a single type argument'
            if annot not in override_type_map:
                annot_val = self.visit(node.annotation)
                if isinstance(annot_val, PythonTypeValue):
                    override_type = annot_val.value_type
                    annot = None
                else:
                    raise ValueError(f'Unknown type annotation {annot}')
        elif isinstance(node.annotation, a.Subscript) and isinstance(
            node.annotation.value, a.Name
        ):
            annot = node.annotation.value.id
            if annot == 'list':
                assert isinstance(
                    node.annotation.slice, a.Name
                ), 'List annotation must have a single type argument'
                annot = node.annotation.slice.id
        else:
            annot_val = self.visit(node.annotation)
            if isinstance(annot_val, PythonTypeValue):
                override_type = annot_val.value_type
                annot = None
            else:
                raise ValueError(f'Unknown type annotation {node.annotation}')
        if annot is not None:
            override_type = override_type_map.get(annot)
        self._assign(node.target, node.value, override_type=override_type)

    def visit_Assign(self, node: a.Assign) -> Any:
        # TODO multiple targets
        if len(node.targets) > 1:
            raise NotImplementedError(
                "Assign with more than one targets is not supported"
            )
        self._assign(node.targets[0], node.value)

    def visit_Call(self, node: a.Call) -> Any:
        func = self.visit(node.func)
        raw_params = set()
        if isinstance(func, PythonFunctionValue):
            raw_params.update(func.raw_params)
        args = [
            self.visit(a) if i not in raw_params else a for i, a in enumerate(node.args)
        ]
        kws = {
            kw.arg: self.visit(kw.value) if kw.arg not in raw_params else kw.value
            for kw in node.keywords
        }
        if None in kws:
            raise NotImplementedError("**kwargs in Call is not supported")
        kws = cast(dict[str, Any], kws)
        if isinstance(func, PythonFunctionValue):
            result = func(ActionHelper(self), *args, **kws)
            return result
        else:
            raise NotImplementedError(f"Call with func {func} is not supported")

    def visit_For(self, node: a.For) -> Any:
        if node.orelse:
            raise NotImplementedError("else: is not supported in For statements")
        count_of_for = self._count_scopes(ScopeType.FORCOUNTER, ScopeType.FOREACH)
        suffix = '' if count_of_for == 0 else f' {count_of_for+1}'
        grouping_uuid = str(uuid.uuid4()).upper()
        if (
            isinstance(node.iter, a.Call)
            and isinstance(node.iter.func, a.Name)
            and node.iter.func.id == 'range'
        ):
            assert isinstance(
                node.target, a.Name
            ), "Only simple loop variables are supported"
            assert (
                not node.iter.keywords
            ), "for...range constructs cannot have keyword arguments"
            range_args = node.iter.args
            if len(range_args) == 1:
                range_start = ConstantValue(0)
                range_end = self.visit(range_args[0])
            elif len(range_args) == 2:
                range_start = self.visit(range_args[0])
                range_end = self.visit(range_args[1])
            elif len(range_args) == 3:
                raise NotImplementedError("for...range with step is not supported")
            else:
                raise ValueError("for...range has incorrect arguments")
            count_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.calculateexpression',
                WFWorkflowActionParameters={
                    'Input': TokenStringValue(range_end, ' - ', range_start).synthesize(
                        self.actions
                    )
                },
            ).with_output('Calculation Result', T.number)
            self.actions.append(count_action)
            count_value = count_action.output
            assert count_value
            start_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.repeat.count',
                WFWorkflowActionParameters={
                    'GroupingIdentifier': grouping_uuid,
                    'WFControlFlowMode': 0,
                    'WFRepeatCount': TokenAttachmentValue(count_value).synthesize(
                        self.actions
                    ),
                },
            )
            end_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.repeat.count',
                WFWorkflowActionParameters={
                    'GroupingIdentifier': grouping_uuid,
                    'WFControlFlowMode': 2,
                },
            )
            self._push_scope(None, ScopeType.FORCOUNTER)
            self.variables[node.target.id] = VariableValue(
                f'Repeat Index{suffix}', T.number
            )
        elif (
            isinstance(node.iter, a.Call)
            and isinstance(node.iter.func, a.Name)
            and node.iter.func.id == 'enumerate'
        ):
            assert (
                not node.iter.keywords and len(node.iter.args) == 1
            ), "for...enumerate has incorrect arguments"
            assert (
                isinstance(node.target, a.Tuple)
                and len(node.target.elts) == 2
                and isinstance(node.target.elts[0], a.Name)
                and isinstance(node.target.elts[1], a.Name)
            ), "Only two loop variables in a tuple is supported"
            iterable = self.visit(node.iter.args[0])
            start_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.repeat.each',
                WFWorkflowActionParameters={
                    'GroupingIdentifier': grouping_uuid,
                    'WFControlFlowMode': 0,
                    'WFInput': TokenAttachmentValue(iterable).synthesize(self.actions),
                },
            )
            end_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.repeat.each',
                WFWorkflowActionParameters={
                    'GroupingIdentifier': grouping_uuid,
                    'WFControlFlowMode': 2,
                },
            )
            self._push_scope(None, ScopeType.FOREACH)
            self.variables[node.target.elts[0].id] = VariableValue(
                f'Repeat Index{suffix}', T.number
            )
            self.variables[node.target.elts[1].id] = VariableValue(
                f'Repeat Item{suffix}', iterable.type
            )
        else:
            assert isinstance(
                node.target, a.Name
            ), "Only simple loop variables are supported"
            iterable = self.visit(node.iter)
            if iterable.type == T.dictionary:
                iterable = iterable.aggrandized(
                    'WFPropertyVariableAggrandizement', {'PropertyName': 'Keys'}
                )
            start_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.repeat.each',
                WFWorkflowActionParameters={
                    'GroupingIdentifier': grouping_uuid,
                    'WFControlFlowMode': 0,
                    'WFInput': TokenAttachmentValue(iterable).synthesize(self.actions),
                },
            )
            end_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.repeat.each',
                WFWorkflowActionParameters={
                    'GroupingIdentifier': grouping_uuid,
                    'WFControlFlowMode': 2,
                },
            )
            self._push_scope(None, ScopeType.FOREACH)
            self.variables[node.target.id] = VariableValue(
                f'Repeat Item{suffix}', iterable.type
            )

        self._add_scope_wrapper([start_action], [end_action])

        for stmt in node.body:
            self.visit(stmt)

        self._pop_scope()

    def _parse_if_values(self, node: a.If):
        if isinstance(node.test, a.Compare):
            assert (
                len(node.test.ops) == 1
            ), "Only a single compare operator are supported"
            op = node.test.ops[0]

            lhs: ShortcutValue = self.visit(node.test.left)

            bp = {
                'WFInput': {
                    'Type': 'Variable',
                    'Variable': token_attachment(self.actions, lhs),
                }
            }

            rhs_raw = node.test.comparators[0]
            rhs_is_none = isinstance(rhs_raw, a.Constant) and rhs_raw.value is None
            if rhs_is_none:
                # special: need to un-cast LHS for certain types to compare correctly
                lhs = lhs.copy()
                lhs.aggrandizements = [
                    a
                    for a in lhs.aggrandizements
                    if a['Type'] != 'WFCoercionVariableAggrandizement'
                ]
                bp['WFInput']['Variable'] = token_attachment(self.actions, lhs)
            if rhs_is_none and isinstance(op, a.Is):
                return 101, bp
            elif rhs_is_none and isinstance(op, a.IsNot):
                return 100, bp

            rhs: ShortcutValue = self.visit(rhs_raw)
            if lhs.type == T.number and isinstance(op, a.Eq):
                return 4, bp | {'WFNumberValue': token_attachment(self.actions, rhs)}
            elif lhs.type == T.number and isinstance(op, a.NotEq):
                return 5, bp | {'WFNumberValue': token_attachment(self.actions, rhs)}
            elif lhs.type == T.number and isinstance(op, a.Gt):
                return 2, bp | {'WFNumberValue': token_attachment(self.actions, rhs)}
            elif lhs.type == T.number and isinstance(op, a.Lt):
                return 0, bp | {'WFNumberValue': token_attachment(self.actions, rhs)}
            elif lhs.type == T.number and isinstance(op, a.LtE):
                return 1, bp | {'WFNumberValue': token_attachment(self.actions, rhs)}
            elif lhs.type == T.number and isinstance(op, a.GtE):
                return 3, bp | {'WFNumberValue': token_attachment(self.actions, rhs)}

            elif lhs.type == T.text and isinstance(op, a.Eq):
                return 4, bp | {
                    'WFConditionalActionString': token_string(self.actions, rhs)
                }
            elif lhs.type == T.text and isinstance(op, a.NotEq):
                return 5, bp | {
                    'WFConditionalActionString': token_string(self.actions, rhs)
                }

            elif rhs.type == T.dictionary and isinstance(op, a.In):
                sep = str(uuid.uuid4())
                combine_action = Action(
                    WFWorkflowActionIdentifier='is.workflow.actions.text.combine',
                    WFWorkflowActionParameters={
                        'WFTextCustomSeparator': sep,
                        'WFTextSeparator': 'Custom',
                        'text': token_attachment(
                            self.actions,
                            rhs.aggrandized(
                                'WFPropertyVariableAggrandizement',
                                {'PropertyName': 'Keys'},
                            ),
                        ),
                    },
                ).with_output('Combined Text', T.text)
                self.actions.append(combine_action)
                combine_output = combine_action.output
                assert combine_output
                text_action = Action(
                    WFWorkflowActionIdentifier='is.workflow.actions.gettext',
                    WFWorkflowActionParameters={
                        'WFTextActionText': token_string(
                            self.actions, sep, combine_output, sep
                        )
                    },
                ).with_output('Text', T.text)
                self.actions.append(text_action)
                text_output = text_action.output
                assert text_output
                return 99, bp | {
                    'WFInput': {
                        'Type': 'Variable',
                        'Variable': token_attachment(self.actions, text_output),
                    },
                    'WFConditionalActionString': token_string(
                        self.actions, sep, lhs, sep
                    ),
                }

            else:
                raise NotImplementedError(
                    f"If operator {op.__class__.__name__} is not supported"
                )
        else:
            raise NotImplementedError(
                f"If expression {node.test.__class__.__name__} is not supported"
            )

    def visit_If(self, node: a.If) -> Any:
        group_uuid = str(uuid.uuid4()).upper()

        condition, params = self._parse_if_values(node)

        base_params = {'GroupingIdentifier': group_uuid}
        start_params = (
            base_params | {'WFCondition': condition, 'WFControlFlowMode': 0} | params
        )
        end_params = base_params | {'WFControlFlowMode': 2}
        start_action = Action(
            WFWorkflowActionIdentifier='is.workflow.actions.conditional',
            WFWorkflowActionParameters=start_params,
        )
        self.actions.append(start_action)

        for stmt in node.body:
            self.visit(stmt)

        if node.orelse:
            otherwise_params = base_params | {'WFControlFlowMode': 1}
            otherwise_action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.conditional',
                WFWorkflowActionParameters=otherwise_params,
            )
            self.actions.append(otherwise_action)

            for stmt in node.orelse:
                self.visit(stmt)

        end_action = Action(
            WFWorkflowActionIdentifier='is.workflow.actions.conditional',
            WFWorkflowActionParameters=end_params,
        )
        self.actions.append(end_action)

    def visit_Break(self, node: a.Break) -> Any:
        # find the innermost FOREACH/FORCOUNTER scope
        for scope in self.scopes[::-1]:
            if scope.type in [ScopeType.FORCOUNTER, ScopeType.FOREACH]:
                break
        else:
            raise ValueError("Cannot break outside a for loop")
        if 'break' not in scope.meta:
            self._add_break_wrapper(scope)
        action = Action(
            WFWorkflowActionIdentifier='is.workflow.actions.setvariable',
            WFWorkflowActionParameters={
                'WFInput': TokenAttachmentValue(ConstantValue(1)).synthesize(
                    self.actions
                ),
                'WFVariableName': scope.meta['break'],
            },
        )
        self.actions.append(action)

    def _add_break_wrapper(self, scope: Scope):
        break_var_name = f'__break_{uuid.uuid4()}__'
        pre = []
        set_var_0 = Action(
            WFWorkflowActionIdentifier='is.workflow.actions.setvariable',
            WFWorkflowActionParameters={
                'WFInput': TokenAttachmentValue(ConstantValue(0)).synthesize(pre),
                'WFVariableName': break_var_name,
            },
        )
        pre.append(set_var_0)
        scope.wrappers.insert(0, (pre, []))
        pre = []
        group_uuid = str(uuid.uuid4()).upper()
        if_start = Action(
            WFWorkflowActionIdentifier='is.workflow.actions.conditional',
            WFWorkflowActionParameters={
                'GroupingIdentifier': group_uuid,
                'WFCondition': 4,
                'WFControlFlowMode': 0,
                'WFInput': {
                    'Type': 'Variable',
                    'Variable': TokenAttachmentValue(
                        VariableValue(break_var_name, T.number)
                    ).synthesize(pre),
                },
                'WFNumberValue': 0,
            },
        )
        pre.append(if_start)
        if_end = Action(
            WFWorkflowActionIdentifier='is.workflow.actions.conditional',
            WFWorkflowActionParameters={
                'GroupingIdentifier': group_uuid,
                'WFControlFlowMode': 2,
            },
        )
        scope.wrappers.append((pre, [if_end]))
        scope.meta['break'] = break_var_name

    def visit_Pass(self, node: a.Pass) -> Any:
        pass  # lol

    # expressions; all should return a Value

    def visit_Name(self, node: a.Name) -> Any:
        for scope in self.scopes[::-1]:
            if node.id in scope.variables:
                return scope.variables[node.id]
        raise NameError(f"Name {node.id!r} is not found")

    def visit_Constant(self, node: a.Constant) -> Any:
        if isinstance(node.value, (str, int, float)):
            return ConstantValue(node.value)
        raise TypeError(
            f'Constants of type {node.value.__class__.__name__} are not supported'
        )

    def visit_JoinedStr(self, node: a.JoinedStr) -> Any:
        parts = [self.visit(x) for x in node.values]
        return TokenStringValue(*parts)

    def visit_FormattedValue(self, node: a.FormattedValue) -> Any:
        if node.format_spec or node.conversion != -1:
            raise NotImplementedError("Conversions in F-strings are not supported")
        return self.visit(node.value)

    def visit_List(self, node: a.List) -> Any:
        values = [
            ItemValue(0, TokenStringValue(self.visit(x))).synthesize(self.actions)
            for x in node.elts
        ]
        action = Action(
            WFWorkflowActionIdentifier='is.workflow.actions.list',
            WFWorkflowActionParameters={'WFItems': values},
        ).with_output('List', T.any)
        self.actions.append(action)
        return action.output

    def visit_Subscript(self, node: a.Subscript) -> Any:
        value = self.visit(node.value)
        slice = self.visit(node.slice)
        if value.type == T.dictionary:
            action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.getvalueforkey',
                WFWorkflowActionParameters={
                    'WFDictionaryKey': token_string(self.actions, slice),
                    'WFInput': token_attachment(self.actions, value),
                },
            ).with_output('Dictionary Value', T.any)
        else:
            action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.getitemfromlist',
                WFWorkflowActionParameters={
                    'WFInput': TokenAttachmentValue(value).synthesize(self.actions),
                    'WFItemIndex': TokenAttachmentValue(slice).synthesize(self.actions),
                    'WFItemSpecifier': 'Item At Index',
                },
            ).with_output('Item from List', value.type)
        self.actions.append(action)
        return action.output

    def visit_BinOp(self, node: a.BinOp) -> Any:
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        if (
            isinstance(node.op, (a.Add, a.Sub, a.Mult, a.Div))
            and lhs.type == T.number
            and rhs.type == T.number
        ):
            operation_map = {'Add': '+', 'Sub': '-', 'Mult': '*', 'Div': '/'}
            action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.math',
                WFWorkflowActionParameters={
                    'WFInput': token_attachment(self.actions, lhs),
                    'WFMathOperand': token_attachment(self.actions, rhs),
                    'WFMathOperation': operation_map[node.op.__class__.__name__],
                },
            ).with_output('Calculation Result', T.number)
            self.actions.append(action)
            return action.output
        raise NotImplementedError(
            f"BinOp does not support {node.op.__class__.__name__} for the operand types"
        )

    def visit_UnaryOp(self, node: a.UnaryOp) -> Any:
        lhs = self.visit(node.operand)
        if isinstance(node.op, (a.USub)) and lhs.type == T.number:
            action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.math',
                WFWorkflowActionParameters={
                    'WFInput': '0',
                    'WFMathOperand': token_attachment(self.actions, lhs),
                    'WFMathOperation': '-',
                },
            ).with_output('Calculation Result', T.number)
            self.actions.append(action)
            return action.output
        raise NotImplementedError(
            f"UnaryOp does not support {node.op.__class__.__name__} or the operand type"
        )

    def visit_Dict(self, node: a.Dict) -> Any:
        action = Action(
            WFWorkflowActionIdentifier='is.workflow.actions.dictionary',
            WFWorkflowActionParameters={},
        ).with_output('Dictionary', T.dictionary)
        self.actions.append(action)
        last_variable = action.output
        assert last_variable
        for key, val in zip(node.keys, node.values):
            assert key is not None, "{**dict} expression is not supported"
            key = self.visit(key)
            val = self.visit(val)
            action = Action(
                WFWorkflowActionIdentifier='is.workflow.actions.setvalueforkey',
                WFWorkflowActionParameters={
                    'WFDictionary': token_attachment(self.actions, last_variable),
                    'WFDictionaryKey': token_string(self.actions, key),
                    'WFDictionaryValue': token_string(self.actions, val),
                },
            ).with_output('Dictionary', T.dictionary)
            self.actions.append(action)
            last_variable = action.output
            assert last_variable
        return last_variable

    def visit_Attribute(self, node: a.Attribute) -> Any:
        value = self.visit(node.value)
        attr = node.attr
        try:
            return value.getattr(attr)
        except TypeError as exc:
            if not value.can_get_property:
                raise ValueError(f'Cannot get property for value {value}') from None
            try:
                type: T.ValueType = value.type
                for prop in type.properties:
                    if convert_property_to_name(prop) == attr:
                        return value.aggrandized(
                            'WFPropertyVariableAggrandizement', {'PropertyName': prop}
                        )
            except TypeError:
                raise exc

    def generic_visit(self, node: a.AST) -> NoReturn:
        name = node.__class__.__name__
        raise NotImplementedError(f"{name} nodes are not implemented yet!")
