# Copyright 2025 eelus1ve and the WaveTeam
#
# GitHub (author): https://github.com/eelus1ve
# GitHub (organization): https://github.com/WaveTeamDevs
# Repository: https://github.com/WaveTeamDevs/WaveSQL
# Website: https://waveteam.net
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
import re
from .constants import no_python_names
from typing import Literal

_query = "self._db_query"
_procedure = "self._db_call_procedure"


def substitute_template(text: str, values: dict) -> str:
    pattern = re.compile(r'\{\{\s*(\w+)\s*\}\}')

    def replacer(match):
        key = match.group(1)
        return str(values.get(key, match.group(0)))

    return pattern.sub(replacer, text)


class Sql:
    def __init__(self, code: str, create_python: bool = False, all_spacing_count: int = 4, spacing_after: int = 4):
        self.code = code
        try:
            self.name = " ".join(self.code.split(" ")[:3])
        except Exception:
            self.name = self.code
        self.count_spasing = spacing_after
        self.all_spacing_count = all_spacing_count
        self.spacing = " " * self.count_spasing
        self.all_spacing = " " * self.all_spacing_count


class SqlObject(Sql):
    def __init__(self, code: str, create_python: bool = False, all_spacing_count: int = 4, spacing_after: int = 4):
        super().__init__(code, create_python, all_spacing_count, spacing_after)
        self.can_python = False
        if create_python:
            if self.name != self.code:
                try:
                    self.action, self.type, self.python_name = self.name.split(" ")
                    self.sync_python_code = None
                    self.async_python_code = None
                    if self.action.lower() == "create":
                        if self.type.lower() == "procedure":
                            params = [i.strip().split(" ") for i in self.code.split("(")[1].split(")")[0].split(",")]
                            inputs = []
                            for i, el in enumerate(params):
                                if el[0].lower() == "in":
                                    inputs.append({"name": el[1], "type": self.get_type_from_sql(" ".join(el[2:]))})
                            self.sync_python_code = f"{self.all_spacing}def {self.python_name.lower()}(self, {f'*, ' if len(inputs) > 1 else ''}{', '.join([f"{i.get("name")}: {i.get("type")}" for i in inputs])}):\n{self.all_spacing}{self.spacing}{_procedure}('{self.python_name}', ({', '.join([i.get('name') for i in inputs])}))"
                            self.async_python_code = f"{self.all_spacing}async def {self.python_name.lower()}(self, {f'*, ' if len(inputs) > 1 else ''}{', '.join([f"{i.get("name")}: {i.get("type")}" for i in inputs])}):\n{self.all_spacing}{self.spacing}await {_procedure}('{self.python_name}', ({', '.join([i.get('name') for i in inputs])}))"
                    if self.async_python_code is not None:
                        self.can_python = True
                    else:
                        self.can_python = False
                except Exception:
                    self.can_python = False
        
    @staticmethod
    def get_type_from_sql(string: str):
        string = string.lower()
        lst = [
            {"sql": "int", "python": "int"},
            {"sql": "char", "python": "str"},
            {"sql": "text", "python": "str"},
            {"sql": "float", "python": "float"},
            {"sql": "double", "python": "float"},
            {"sql": "bool", "python": "bool"},
        ]
        for i in lst:
            if i.get("sql") in string:
                return i.get("python")


class SqlQuery(Sql):
    def __init__(self, code: str, create_python: bool = False, all_spacing_count: int = 4, spacing_after: int = 4, dictionary_default: bool = True):
        super().__init__(code, create_python, all_spacing_count, spacing_after)
        self.dictionary_default = dictionary_default
        if create_python:
            if self.name != self.code:
                try:
                    self.action, self.python_name = self.name.split(" ")[:2]
                    execute_query = " ".join(self.code.split(" ")[4:])
                    query_type = execute_query.split(" ")[0]
                    self.sync_python_code = None
                    self.async_python_code = None
                    if self.action.lower() == "create" and self.python_name:
                        if query_type.lower() == "select":
                            self.sync_python_code, self.async_python_code = self.parse_select_query_to_method(query=execute_query)
                        elif query_type.lower() == "insert":
                            self.sync_python_code, self.async_python_code = self.parse_insert_query_to_method(query=execute_query)
                        elif query_type.lower() == "delete":
                            self.sync_python_code, self.async_python_code = self.parse_delete_query_to_method(query=execute_query)
                        elif query_type.lower() == "update":
                            self.sync_python_code, self.async_python_code = self.parse_update_query_to_method(query=execute_query)
                            
                    if not (self.async_python_code is None or self.sync_python_code is None):
                        self.can_python = True
                    else:
                        self.can_python = False
                except Exception:
                    self.can_python = False

    def clean_commas_inside_parentheses(self, s: str) -> str:
        def clean(match):
            inside = match.group(1)
            tokens = [token.strip() for token in inside.split(",") if token.strip()]
            return f"({', '.join(tokens)})"
        
        last = None
        while s != last:
            last = s
            s = re.sub(r"\(([^()]+)\)", clean, s)
        return s

    def clean_outer_commas(self, sql: str) -> str:
        sql = re.sub(r",\s*,+", ",", sql)
        sql = re.sub(r"\)\s*,\s*,+", ")", sql)
        sql = re.sub(r",\s*\)", ")", sql)
        sql = re.sub(r"\(\s*,", "(", sql)
        return sql

    def get_matches_query(self, query: str) -> tuple[list, str]:
        matches = re.findall(r"\{\%\s*extend\s+(\w+)\s*:\s*(\w+)\s*\%\}", query)
        sql_query = re.sub(r"\{\%\s*extend\s+\w+\s*:\s*\w+\s*\%\}", "%s", query).strip()
        return matches, sql_query

    def parse_select_query_to_method(self, query: str) -> str:
        matches, sql_query = self.get_matches_query(query=query)

        sql_query = self.clean_commas_inside_parentheses(sql_query)

        select_match = re.search(r"(SELECT\s+)(.*?)(\s+FROM)", sql_query, re.IGNORECASE | re.DOTALL)
        if not select_match:
            raise ValueError("Failed to parse SELECT ... FROM")

        select_prefix, raw_fields, select_suffix = select_match.groups()

        cleaned_fields = ", ".join(filter(None, [f.strip() for f in raw_fields.split(",")]))

        sql_query = sql_query[:select_match.start()] + select_prefix + cleaned_fields + select_suffix + sql_query[select_match.end():]

        has_limit_1 = bool(re.search(r"LIMIT\s+1\s*;?$", sql_query.strip(), re.IGNORECASE))
        fetch_value = "1" if has_limit_1 else "2"

        param_signature = ", ".join(f"{name}: {typ}" for name, typ in matches)
        param_values = ", ".join(name for name, _ in matches)
        param_tuple = f" ({param_values}, )," if param_values else ""
        
        return (
            self.parse_select_query_to_sync_method(
                cleaned_fields=cleaned_fields, has_limit_1=has_limit_1,
                param_signature=param_signature, fetch_value=fetch_value,
                sql_query=sql_query, param_tuple=param_tuple
            ),
            self.parse_select_query_to_async_method(
                cleaned_fields=cleaned_fields, has_limit_1=has_limit_1,
                param_signature=param_signature, fetch_value=fetch_value,
                sql_query=sql_query, param_tuple=param_tuple
            )
        )

    def parse_select_query_to_sync_method(
        self, cleaned_fields: str, has_limit_1: bool, param_signature: str,
        fetch_value: Literal["1", "2"], sql_query: str, param_tuple: str
    ) -> str:
        if cleaned_fields != "*" and len(cleaned_fields.split(",")) == 1:
            if has_limit_1:
                fetch_suffix = ", dictionary=False)[0]"
                start_suffix = ""
            else:
                fetch_suffix = ", dictionary=False)))"
                start_suffix = "list(map(lambda x: x[0], "
        else:
            fetch_suffix = ")"
            start_suffix = ""
            
        result_type = ("dict" if self.dictionary_default else "tuple")
        full_result = ""
        len_cleaned_fields = len(cleaned_fields.split(" "))
        if len_cleaned_fields == 1 and cleaned_fields != "*" and has_limit_1:
            full_result = ' -> int | float | str | bool | datetime | None'
        elif len_cleaned_fields == 1 and cleaned_fields != "*" and not has_limit_1:
            full_result = ' -> list'
        elif fetch_value != "1":
            full_result = f' -> list[{result_type}]'
        else:
            full_result = f' -> {result_type}'

        return f"{self.all_spacing}def {self.python_name}(self, {param_signature}){full_result}:\n{self.all_spacing}{self.spacing}return {start_suffix}{_query}(\"{sql_query}\",{param_tuple} fetch={fetch_value}{fetch_suffix}"

    def parse_select_query_to_async_method(
        self, cleaned_fields: str, has_limit_1: bool, param_signature: str,
        fetch_value: Literal["1", "2"], sql_query: str, param_tuple: str
    ) -> str:
        if cleaned_fields != "*" and len(cleaned_fields.split(",")) == 1:
            if has_limit_1:
                fetch_suffix = ", dictionary=False))[0]"
                start_suffix = "(await "
            else:
                fetch_suffix = ", dictionary=False))))"
                start_suffix = "list(map(lambda x: x[0], (await "
        else:
            fetch_suffix = ")"
            start_suffix = "await "
            
        result_type = ("dict" if self.dictionary_default else "tuple")
        full_result = ""
        len_cleaned_fields = len(cleaned_fields.split(" "))
        if len_cleaned_fields == 1 and cleaned_fields != "*" and has_limit_1:
            full_result = ' -> int | float | str | bool | datetime | None'
        elif len_cleaned_fields == 1 and cleaned_fields != "*" and not has_limit_1:
            full_result = ' -> list'
        elif fetch_value != "1":
            full_result = f' -> list[{result_type}]'
        else:
            full_result = f' -> {result_type}'
            
        return f"{self.all_spacing}async def {self.python_name}(self, {param_signature}){full_result}:\n{self.all_spacing}{self.spacing}return {start_suffix}{_query}(\"{sql_query}\",{param_tuple} fetch={fetch_value}{fetch_suffix}"
    
    def parse_insert_query_to_method(self, query: str) -> str:
        matches, sql_query = self.get_matches_query(query=query)

        sql_query = self.clean_commas_inside_parentheses(sql_query)
        sql_query = self.clean_outer_commas(sql_query)

        param_signature = ", ".join(f"{name}: {typ}" for name, typ in matches)
        param_values = ", ".join(name for name, _ in matches)
        values_part = f"({param_values}, )" if param_values else ""

        return (
            self.parse_insert_query_to_sync_method(param_signature=param_signature, sql_query=sql_query, values_part=values_part),
            self.parse_insert_query_to_async_method(param_signature=param_signature, sql_query=sql_query, values_part=values_part)
        )
    
    def parse_insert_query_to_sync_method(self, param_signature: str, sql_query: str, values_part: str) -> str:
        return f"{self.all_spacing}def {self.python_name}(self, {param_signature}) -> None:\n{self.all_spacing}{self.spacing}{_query}(\"{sql_query}\", {values_part})"
    
    def parse_insert_query_to_async_method(self, param_signature: str, sql_query: str, values_part: str) -> str:
        return f"{self.all_spacing}async def {self.python_name}(self, {param_signature}) -> None:\n{self.all_spacing}{self.spacing}await {_query}(\"{sql_query}\", {values_part})"

    def parse_delete_query_to_method(self, query: str) -> str:
        matches, sql_query = self.get_matches_query(query=query)
        
        sql_query = self.clean_commas_inside_parentheses(sql_query)

        param_signature = ", ".join(f"{name}: {typ}" for name, typ in matches)
        param_values = ", ".join(name for name, _ in matches)
        values_part = f"({param_values}, )" if param_values else ""

        return (
            self.parse_delete_query_to_sync_method(param_signature=param_signature, sql_query=sql_query, values_part=values_part),
            self.parse_delete_query_to_async_method(param_signature=param_signature, sql_query=sql_query, values_part=values_part)
        )
    
    def parse_delete_query_to_sync_method(self, param_signature: str, sql_query: str, values_part: str) -> str:
        return f"{self.all_spacing}def {self.python_name}(self, {param_signature}) -> None:\n{self.all_spacing}{self.spacing}{_query}(\"{sql_query}\", {values_part})"

    def parse_delete_query_to_async_method(self, param_signature: str, sql_query: str, values_part: str) -> str:
        return f"{self.all_spacing}async def {self.python_name}(self, {param_signature}) -> None:\n{self.all_spacing}{self.spacing}await {_query}(\"{sql_query}\", {values_part})"

    def parse_update_query_to_method(self, query: str) -> str:
        matches, sql_query = self.get_matches_query(query=query)

        sql_query = self.clean_commas_inside_parentheses(sql_query)
        sql_query = self.clean_outer_commas(sql_query)

        set_match = re.search(r"(SET\s+)(.*?)(\s+WHERE)", sql_query, re.IGNORECASE | re.DOTALL)
        if not set_match:
            raise ValueError("Failed to parse SET ... WHERE")

        set_prefix, raw_set_fields, set_suffix = set_match.groups()
        cleaned_set_fields = ", ".join(filter(None, [f.strip() for f in raw_set_fields.split(",")]))

        sql_query = sql_query[:set_match.start()] + set_prefix + cleaned_set_fields + set_suffix + sql_query[set_match.end():]

        param_signature = ", ".join(f"{name}: {typ}" for name, typ in matches)
        param_values = ", ".join(name for name, _ in matches)
        param_tuple = f" ({param_values}, )" if param_values else ""

        return (
            self.parse_update_query_to_sync_method(param_signature=param_signature, sql_query=sql_query, param_tuple=param_tuple),
            self.parse_update_query_to_async_method(param_signature=param_signature, sql_query=sql_query, param_tuple=param_tuple)
        )
    
    def parse_update_query_to_sync_method(self, param_signature: str, sql_query: str, param_tuple: str) -> str:
        return f"{self.all_spacing}def {self.python_name}(self, {param_signature}) -> None:\n{self.all_spacing}{self.spacing}{_query}(\"{sql_query}\",{param_tuple})"

    def parse_update_query_to_async_method(self, param_signature: str, sql_query: str, param_tuple: str) -> str:
        return f"{self.all_spacing}async def {self.python_name}(self, {param_signature}) -> None:\n{self.all_spacing}{self.spacing}await {_query}(\"{sql_query}\",{param_tuple})"


class SqlFileQueries:
    def __init__(
        self, path: Path | str, create_python: bool = False, all_spacing_count: int = 4,
        spacing_after: int = 4, is_dictionary_default: bool = True, dict_of_values: dict = {}
    ) -> None:
        self.file_path = path
        self.create_python = create_python
        self.all_spacing_count = all_spacing_count
        self.spacing_after = spacing_after
        self.dictionary_default = is_dictionary_default
        self.dict_of_values = dict_of_values
        self.sql_queries: tuple[SqlQuery] = self.file_to_sql_scripts()
    
    def parse_sql(self, code: str) -> tuple[SqlQuery]:
        sql_obj_lst = []
        sql_commands = code.split(";")
        for command in sql_commands:
            stripped_command = command.strip()
            if stripped_command:
                sql_obj_lst.append(SqlQuery(code=stripped_command, create_python=self.create_python, all_spacing_count=self.all_spacing_count, spacing_after=self.spacing_after, dictionary_default=self.dictionary_default))
                    
        return tuple(sql_obj_lst)
    
    def file_to_sql_scripts(self, ) -> tuple[SqlQuery]:
        with open(self.file_path, "r", encoding="utf-8") as sql_file:
            code = sql_file.read()
        code = substitute_template(text=code, values=self.dict_of_values)
        return self.parse_sql(code=code)


class SqlFileObject:
    def __init__(self, path: Path | str, dict_of_values: dict = {}, is_create_python: bool = False) -> None:
        self.file_path = path
        self.dict_of_values = dict_of_values
        self.is_create_python = is_create_python
        self.sql_objects: tuple[SqlObject] = self.file_to_sql_scripts()
    
    def parse_sql(self, code: str, is_create_python: bool | None = None) -> tuple[SqlObject]:
        if is_create_python is None:
            is_create_python = self.is_create_python
        sql_obj_lst = []
        sql_commands_and_procedures_list = code.replace("$$", ";").replace(" ;", ";").split("DELIMITER;")
        for i, el in enumerate(sql_commands_and_procedures_list):
            if not i % 2:
                sql_commands = el.split(";")
                for command in sql_commands:
                    stripped_command = command.strip()
                    if stripped_command:
                        sql_obj_lst.append(SqlObject(code=stripped_command, create_python=is_create_python))
            else:
                stripped_el = el.strip()
                if stripped_el:
                    sql_obj_lst.append(SqlObject(code=stripped_el, create_python=is_create_python))
                    
        return tuple(sql_obj_lst)
    
    def file_to_sql_scripts(self, ) -> tuple[SqlObject]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as sql_file:
                code = sql_file.read()
        except Exception:
            code = self.file_path
        code = substitute_template(text=code, values=self.dict_of_values)
        return self.parse_sql(code=code, is_create_python=((not self.file_path.name.startswith("-")) and self.is_create_python))
