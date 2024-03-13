import locale
import os
import pathlib
import pprint
import shlex
import subprocess
import sys
import tempfile

import click
import yaml
from pyparsing import *

locale.setlocale(locale.LC_ALL, "")
encoding = locale.getpreferredencoding()


def error(msg):
    click.echo(click.style(msg, fg="red"))


def sucess(msg):
    click.echo(click.style(msg, fg="green"))


def info(msg):
    click.echo(msg)


class parsers:
    compiler_command_modeline = (
        Literal("snippet-compiler.compiler-command")
        + Literal(":")
        + restOfLine("compiler-command")
    )
    exec_name_modeline = (
        Literal("snippet-compiler.exec-name") + Literal(":") + restOfLine("exec-name")
    )
    true_value = Literal("yes") | Literal("true")
    false_value = Literal("no") | Literal("false")
    run_modeline = (
        Literal("snippet-compiler.run")
        + Literal(":")
        + (true_value("true") | false_value("false"))
    )
    snippet_template_tag = Literal("{snippet}")
    template = snippet_template_tag
    template_modeline = (
        Literal("snippet-compiler.template") + Literal(":") + restOfLine("template")
    )

    class markdown_render:
        html_comment = QuotedString(
            quote_char="<!---", end_quote_char="-->", multiline=True, unquote_results=False
        )
        code_fence = QuotedString(
            quote_char="```", multiline=True, unquote_results=False
        )
        code_fense_with_control_block = html_comment("config") + code_fence("code")

        snippet_control_block = html_comment
        snippet_code_block = code_fence
        snippet = code_fense_with_control_block


class WorkingDirectory(object):
    def __init__(self, directory):
        self._dir = directory
        self._cwd = os.getcwd()
        self._pwd = self._cwd
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

    def __enter__(self):
        # print("ENTER: ",self._dir)
        self._pwd = self._cwd
        os.chdir(self._dir)
        self._cwd = os.getcwd()
        return self

    def __exit__(self, *args):
        # print("EXIT: ",self._dir)
        os.chdir(self._pwd)
        self._cwd = self._pwd


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Print verbose messages.")
@click.option(
    "--compiler-command",
    default="g++ {file}",
    help="Compiler command line to run. This is a string.template, use {file} to reference the filename.",
)
@click.option("--run/--no-run", help="Run execuable after compiling.")
@click.option(
    "--exec-name",
    default="./a.out",
    help="The execuable name that will be run if --run is given.",
)
@click.option(
    "--template",
    help="Specify a template file to use for the snippet. The contents of the file should include the string '{snippet}' where the snippet should be inserted.",
)
@click.pass_context
def main(ctx, verbose, compiler_command, run, exec_name, template):
    """
    Read code snippet from standard input and compile it.
    """

    sourcecode = "".join(sys.stdin)

    # check source code for modelines
    compiler_command_modelines = parsers.compiler_command_modeline.searchString(
        sourcecode
    )
    for line in compiler_command_modelines:
        if "compiler-command" in line:
            compiler_command = line["compiler-command"]
    exec_name_modelines = parsers.exec_name_modeline.searchString(sourcecode)
    for line in exec_name_modelines:
        if "exec-name" in line:
            exec_name = line["exec-name"]
    run_modelines = parsers.run_modeline.searchString(sourcecode)
    for line in run_modelines:
        if "true" in line:
            run = True
    template_modelines = parsers.template_modeline.searchString(sourcecode)
    for line in template_modelines:
        if "template" in line:
            template = line["template"]

    if template:
        template_text = pathlib.Path(template).read_text()
    else:
        template_text = "{snippet}"

    def insert_source_code(toks):
        toks[0] = sourcecode
        return toks

    parsers.template.setParseAction(insert_source_code)
    rendered_text = parsers.template.transformString(template_text)

    cwd = pathlib.Path(os.getcwd()).absolute()
    with tempfile.TemporaryDirectory() as dir:
        os.chdir(dir)
        sourcefile = pathlib.Path("main.cpp")

        sourcefile.write_text(rendered_text)
        cmd = compiler_command.format(file=str(sourcefile), cwd=str(cwd))
        res = subprocess.run(shlex.split(cmd))
        if run and res.returncode == 0:
            subprocess.run(exec_name)


def run_snippet(config, snippet):
    cmd = ["snippet-compiler"]
    for item in config.get("snippet-compiler", {}).get("options", {}).items():
        cmd.append("--" + item[0])
        cmd.append(item[1])
    for item in config.get("snippet-compiler", {}).get("flags", {}):
        cmd.append("--" + item)
    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    output = proc.communicate(input=snippet.encode(encoding))[0].decode(encoding)
    return output


class FensedBlock:
    def __init__(self, file_loc_line_col, control_block, code_block):
        self.file_loc_line_col = file_loc_line_col
        self.control_block = control_block
        self.code_block = code_block

        beg = 0
        end = len(self.control_block)
        # remove quotes (if any) from control block and parse it as yaml.
        if self.control_block.startswith(
            parsers.markdown_render.snippet_control_block.quote_char
        ):
            beg = parsers.markdown_render.snippet_control_block.quote_char_len
        if self.control_block.endswith(
            parsers.markdown_render.snippet_control_block.end_quote_char
        ):
            end = -parsers.markdown_render.snippet_control_block.end_quote_char_len
        try:
            self.config = yaml.safe_load(self.control_block[beg:end])
        except:
            raise RuntimeError(
                f"Could not parse the config block on line {self.lineno}. Block must be valid YAML."
            )

        if "file" in self.config:
            self.config["tag"] = self.config["file"]
            self.config["type"] = "file"
        if "cmd" in self.config:
            self.config["tag"] = self.config["cmd"]
            self.config["type"] = "cmd"
            if "wd" not in self.config:
                self.config["wd"] = self.markdown_file.parent
            else:
                wd = pathlib.Path(self.config["wd"])
                if wd.is_absolute():
                    self.config["wd"] = wd
                else:
                    self.config["wd"] = self.markdown_file.parent / wd

        if "tag" not in self.config:
            raise KeyError(
                f"No 'tag' element found in snippet control block on line {self.lineno}. A 'tag' element is required to match snippet input and output blocks."
            )

        if "type" not in self.config:
            if "io" in self.config:
                self.config["type"] = self.config["io"]
            else:
                self.config["type"] = None

    @property
    def tag(self):
        return self.config["tag"]

    @property
    def markdown_file(self):
        return pathlib.Path(self.file_loc_line_col[0])

    @property
    def loc(self):
        return self.file_loc_line_col[1]

    @property
    def lineno(self):
        return self.file_loc_line_col[2]

    @property
    def col(self):
        return self.file_loc_line_col[3]

    @property
    def type(self):
        return self.config["type"]

    def set_type(self, type):
        self.config["type"] = type

    @property
    def code_block_text(self):
        return self.code_block


class CodeBlockCollection:
    def __init__(self):
        self.code_blocks = {}

    def add_code_block(self, code_block):
        if code_block.type is None:
            # need to figure out if this is an input block our output block.
            # if the block is not marked, we will assume the first occurrence is
            # an input, and any later occurances are output.
            if code_block.tag in self.code_blocks:
                code_block.set_type("out")
            else:
                code_block.set_type("in")

        if code_block.tag not in self.code_blocks:
            self.code_blocks[code_block.tag] = []

        self.code_blocks[code_block.tag].append(code_block)

    def compile_snippets(self):
        for blocks in self.code_blocks.values():
            input_block = None
            for block in blocks:
                if block.type == "in":
                    if input_block is not None:
                        raise RuntimeError(
                            f"Found multiple code blocks marked as 'input' with tag '{block.tag}'. Only output blocks may appear multiple times. Note: if an output block appears before its input block, it must be explicitly marked."
                        )
                    input_block = block

            for block in blocks:
                if block.type == "out":
                    input_lines = input_block.code_block.split("\n")
                    output_lines = block.code_block.split("\n")
                    block.code_block = (
                        output_lines[0]
                        + "\n"
                        + run_snippet(input_block.config, "\n".join(input_lines[1:-1]))
                        + output_lines[-1]
                    )
                if block.type == "file":
                    file = block.markdown_file.parent / block.config["file"]
                    output_lines = block.code_block.split("\n")
                    block.code_block = output_lines[0] + "\n"
                    block.code_block += file.read_text()
                    block.code_block += output_lines[-1]
                if block.type == "cmd":
                    with WorkingDirectory(block.config["wd"]) as f:
                        cmd_output = subprocess.check_output(
                            shlex.split(block.config["cmd"])
                        ).decode("utf-8")
                        output_lines = block.code_block.split("\n")
                        block.code_block = output_lines[0] + "\n"
                        block.code_block += cmd_output
                        block.code_block += output_lines[-1]

    def get_code_block_by_tag(self, tag):
        return self.code_blocks[tag]

    def get_code_block_by_loc(self, loc):
        for blocks in self.code_blocks.values():
            for block in blocks:
                if block.loc == loc:
                    return block
        raise KeyError("Could not find code block at location {loc}.")


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Print verbose messages.")
@click.argument("markdown-file", default="-")
@click.pass_context
def markdown_render(ctx, verbose, markdown_file):
    try:
        if markdown_file == "-":
            markdown_text = "".join(sys.stdin)
        else:
            markdown_file = pathlib.Path(markdown_file).absolute()
            markdown_text = markdown_file.read_text()

        out = sys.stdout

        # we will have to render in two passes (like latex)
        # once to extract all of the snippets
        # and again to replace the outputs
        code_blocks = CodeBlockCollection()

        def CollectInputs(text, loc, toks):
            linenumber = lineno(loc, markdown_text)
            colnumber = col(loc, markdown_text)
            code_block = FensedBlock(
                (markdown_file, loc, linenumber, colnumber),
                toks["config"],
                toks["code"],
            )
            code_blocks.add_code_block(code_block)

        parsers.markdown_render.code_fense_with_control_block.setParseAction(
            CollectInputs
        )
        parsers.markdown_render.code_fense_with_control_block.searchString(
            markdown_text
        )

        code_blocks.compile_snippets()

        def ReplaceOutputs(text, loc, toks):
            code_block = code_blocks.get_code_block_by_loc(loc)
            toks[1] = "\n" + code_block.code_block_text
            return toks

        parsers.markdown_render.code_fense_with_control_block.setParseAction(
            ReplaceOutputs
        )
        rendered_markdown_text = (
            parsers.markdown_render.code_fense_with_control_block.transformString(
                markdown_text
            )
        )

        out.write(rendered_markdown_text)
        sys.exit(0)
    except Exception as e:
        print("There was an error.")
        print(e)
        sys.exit(1)
