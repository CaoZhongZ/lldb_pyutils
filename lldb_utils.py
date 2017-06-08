##
# Copyright (c) 2015-2017 Intel Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

import lldb

def Evaluate_PyObject_AsUTF8(fr, obj):
    return fr.EvaluateExpression('PyUnicode_AsUTF8('+obj+')')

def py3bt(debugger=None, command=None, result=None, dict=None, thread=None):
    """
    An lldb command that prints a Python call back trace for the specified
    thread or the currently selected thread.

    @param debugger: debugger to use
    @type debugger: L{lldb.SBDebugger}
    @param command: ignored
    @type command: ignored
    @param result: ignored
    @type result: ignored
    @param dict: ignored
    @type dict: ignored
    @param thread: the specific thread to target
    @type thread: L{lldb.SBThread}
    """

    if debugger is None:
        debugger = lldb.debugger
    target = debugger.GetSelectedTarget()
    if not isinstance(thread, lldb.SBThread):
        thread = target.GetProcess().GetSelectedThread()

    pystring_t = target.FindFirstType("PyUnicodeObject").GetPointerType()

    num_frames = thread.GetNumFrames()
    for i in range(num_frames - 1):
        fr = thread.GetFrameAtIndex(i)
        if fr.GetFunctionName() == "PyEval_EvalFrameEx":
            f = fr.GetValueForVariablePath("f")
            filename = Evaluate_PyObject_AsUTF8(fr, "f->f_code->co_filename")
            name = Evaluate_PyObject_AsUTF8(fr, "f->f_code->co_name")
            lineno = f.GetValueForExpressionPath("->f_lineno").GetValue()
            print("#{}: {} - {}:{}".format(
                fr.GetFrameID(),
                filename if filename else ".",
                name if name else ".",
                lineno if lineno else ".",
            ))

CMDS = ("py3bt",)


def __lldb_init_module(debugger, dict):
    """
    Register each command with lldb so they are available directly within lldb as
    well as within its Python script shell.

    @param debugger: debugger to use
    @type debugger: L{lldb.SBDebugger}
    @param dict: ignored
    @type dict: ignored
    """
    for cmd in CMDS:
        debugger.HandleCommand(
            "command script add -f lldb_utils.{cmd} {cmd}".format(cmd=cmd)
        )
