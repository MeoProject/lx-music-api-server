# ----------------------------------------
# - mode: python -
# - author: helloplhm-qwq -
# - name: log.py -
# - project: lx-music-api-server -
# - license: MIT -
# ----------------------------------------
# This file is part of the "lx-music-api-server" project.

import logging
import colorlog
import os
import sys
import re
import io
import traceback
import time
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from .utils import filterFileName, setGlobal
from .variable import debug_mode, log_length_limit, log_file, log_files
from colorama import Fore, Back, Style
from colorama import init as clinit

clinit()  # 初始化 colorama

if ((not os.path.exists("logs")) and log_file):
    try:
        os.mkdir("logs")
    except:
        pass

class Color:
    """
    彩色文字处理器
    """

    def __getattr__(self, k):
        return lambda x: f"{getattr(Fore, k.upper())}{x}{Style.RESET_ALL}"

color = Color()

def is_rubbish(input_string):
    return bool(re.match(r'^(\~|\^)*$', input_string))

def stack_error(exception):
    stack_trace = traceback.format_exception(type(exception), exception, exception.__traceback__)
    return ''.join(stack_trace)

def find_function(file_name, line_number):
    with open(file_name, 'r') as file:
        lines = file.readlines()
    target_line = lines[line_number - 1]  # 获取目标行内容
    for name, obj in inspect.getmembers(inspect.currentframe().f_back.f_globals):
        if (inspect.isfunction(obj)):#  and target_line.lstrip().startswith('def '+obj.__name__)):
            return obj.__name__, inspect.getsourcelines(obj)[1]

def python_highlight(code):
    return highlight(code, PythonLexer(), TerminalFormatter())

def read_code(file_path, target_line_number):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            start = max(0, target_line_number - 4)
            end = min(target_line_number + 4, len(lines))
            lineMap = {
                'current': lines[target_line_number - 1],
                'result': lines[start:end]
            }
            return lineMap
    except FileNotFoundError:
        sys.stderr.write("日志模块出错，本次日志可能无法记录，请报告给开发者: 处理错误语法高亮时找不到源文件")
    except Exception as e:
        sys.stderr.write(f"日志模块出错，本次日志可能无法记录，请报告给开发者: \n" + traceback.format_exc())

def stack_info(stack_trace_line):
    try:
        parts = stack_trace_line.split(', ')
        file_path = ' '.join(parts[0].split(' ')[1:])  # 提取文件路径
        line_number = int(parts[1].split(' ')[1])  # 提取行号
        function_name = parts[2].split(' ')[1]  # 提取函数名
        return file_path, line_number, function_name
    except Exception as e:
        sys.stderr.write(f"日志模块出错，本次日志可能无法记录，请报告给开发者: \n" + traceback.format_exc())

def highlight_error(e):
    try:
        if (isinstance(e, Exception)):
            error = stack_error(e)
        else:
            error = e
        lines = [i.strip() for i in error.split("\n") if i.strip()]
        final = []
        ign = False
        for i in lines:
            if (ign):
                ign = False
                continue

            if (i.startswith("Traceback (most recent call last):")):
                final.append(color.cyan(i))
            elif (i.startswith("During handling of the above exception, another exception occurred:")):
                final.append(color.cyan(i))
            elif (i.startswith("The above exception was the direct cause of the following exception:")):
                final.append(color.cyan(i))
            elif (i.startswith("File")):
                ign = True
                p, l, f = stack_info(i)
                p = p[1:-1]

                if (p.startswith('<') or not os.path.isfile(p)):
                    final.append(i)
                    final.append("    " if (lines[lines.index(l) + 1].startswith("File")) else ("        " + lines[lines.index(l) + 1]))
                    continue

                code = read_code(p, l)
                cc = []
                viewed = False
                for i in range(len(code['result'])):
                    c = code["result"][i]
                    if (c.startswith(code['current']) and (i <= 3)):
                        viewed = True
                        cc.append((' ' * (10 - len(str(l))) + f'{color.red(str(l))} >|' + python_highlight(c)))
                    else:
                        line_number = l + (code["result"].index(c) - 3)
                        cc.append((' ' * (10 - len(str(line_number))) + f'{color.blue(str(line_number))}  |' + python_highlight(c)))
                code = "\n".join(cc)
                p = '"' + p + '"'
                final.append(f"    File {color.yellow(f'{p}')} in {color.cyan(f)}()\n\n\n{code}\n")
            else:
                try:
                    if (is_rubbish(i)):
                        continue
                    if (issubclass(require(("builtins." if ("." not in i.split(":")[0]) else "") + i.split(":")[0]), Exception)):
                        exc = i.split(":")[0]
                        desc = "" if (len(i.split(":")) == 1) else ':'.join(i.split(":")[1:]).strip()
                        final.append(color.red(exc) + (": " + color.yellow(desc)) if (desc) else "")
                    else:
                        final.append(color.cyan(i))
                except:
                    # traceback.print_exc()
                    final.append(i)
        return "\n".join(final).replace('\n\n', '\n')
    except:
        sys.stderr.write('格式化错误失败，使用默认格式\n' + traceback.format_exc())
        if (isinstance(e, Exception)):
            return stack_error(e)
        else:
            return e

class LogHelper(logging.Handler):
    # 日志转接器
    def __init__(self, custom_logger):
        super().__init__()
        self.custom_logger = custom_logger

    def emit(self, record):
        # print(record)
        log_message = self.format(record)
        self.custom_logger.info(log_message)

class fileWriter(logging.Handler):
    def __init__(self, f: io.TextIOWrapper, f2: logging.Formatter):
        self.file = f
        self.formatter = f2

    def emit(self, record: logging.LogRecord):
        self.file.write(self.format(record) + '\n')
        self.file.flush()

class log:
    # 主类
    def __init__(self, module_name='Not named logger', output_level='INFO', filename=''):
        self.name = module_name
        self._logger = logging.getLogger(module_name)
        if not output_level.upper() in dir(logging):
            raise NameError('Unknown loglevel: '+output_level)
        if not debug_mode:
            self._logger.setLevel(getattr(logging, output_level.upper()))
        else:
            self._logger.setLevel(logging.DEBUG)
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s|[%(name)s/%(levelname)s]|%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            })
        if log_file:
            if filename:
                filename = filterFileName(filename)
            else:
                filename = './logs/' + module_name + '.log'
            self.file = open(filename, 'a+', encoding='utf-8')
            log_files.append(self.file)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.module_name = module_name
        self._logger.addHandler(console_handler)
        debug_handler = logging.StreamHandler()
        debug_handler.setFormatter(formatter)

    def debug(self, message, allow_hidden=True):
        if (log_file):
            self.file.write('{time}|[{name}/DEBUG]{msg}'.format(time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), name = self.module_name, msg = message) + '\n')

        if len(str(message)) > log_length_limit and allow_hidden:
            message = str(message)[:log_length_limit] + " ..."
        self._logger.debug(message)

    def log(self, message, allow_hidden=True):
        if (log_file):
            self.file.write('{time}|[{name}/INFO]{msg}'.format(time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), name = self.module_name, msg = message) + '\n')

        if len(str(message)) > log_length_limit and allow_hidden:
            message = str(message)[:log_length_limit] + " ..."
        self._logger.info(message)

    def info(self, message, allow_hidden=True):
        if (log_file):
            self.file.write('{time}|[{name}/INFO]{msg}'.format(time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), name = self.module_name, msg = message) + '\n')

        if len(str(message)) > log_length_limit and allow_hidden:
            message = str(message)[:log_length_limit] + "..."
        self._logger.info(message)

    def warning(self, message):
        if (log_file):
            self.file.write('{time}|[{name}/WARNING]{msg}'.format(time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), name = self.module_name, msg = message) + '\n')

        if (message.strip().startswith('Traceback')):
            self._logger.warning('\n' + highlight_error(message))
        else:
            self._logger.warning(message)

    def error(self, message):
        if (log_file):
            self.file.write('{time}|[{name}/ERROR]{msg}'.format(time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), name = self.module_name, msg = message) + '\n')

        if (message.startswith('Traceback')):
            self._logger.error('\n' + highlight_error(message))
        else:
            self._logger.error(message)

    def critical(self, message):
        if (log_file):
            self.file.write('{time}|[{name}/CRITICAL]{msg}'.format(time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), name = self.module_name, msg = message) + '\n')

        if (message.startswith('Traceback')):
            self._logger.critical('\n' + highlight_error(message))
        else:
            self._logger.critical(message)

    def set_level(self, loglevel):
        loglevel_upper = loglevel.upper()
        if not loglevel_upper in dir(logging):
            raise NameError('Unknown loglevel: ' + loglevel)
        self._logger.setLevel(getattr(logging, loglevel_upper))

    def getLogger(self):
        return self._logger

    def addHandler(self, handler):
        self._logger.addHandler(handler)


printlogger = log('print')


def logprint(*args, sep=' ', end='', file=None, flush=None):
    printlogger.info(sep.join(str(arg) for arg in args), allow_hidden=False)


setGlobal(logprint, 'print')
