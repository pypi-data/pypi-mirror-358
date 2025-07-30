import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from typing import Any, Callable, Literal, TypeVar, Union
from uuid import uuid4

RADIO_NOTHING = uuid4().hex
TkVar = TypeVar('TkVar', bound=Union[tk.StringVar, tk.IntVar, tk.DoubleVar, tk.BooleanVar])


class TkForm(tk.Tk):

    _rowIndex = -1
    _initList: list[Callable[..., None]] = []
    _varList: list[tk.Variable] = []  # 用来存储 var 变量，避免传出去，外面没有接收导致界面异常

    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        self.bind("<Map>", self._onInit)

    def _onInit(self, evt: tk.Event):
        if evt.widget == self:
            for callback in self._initList:
                callback()
            self._initList.clear()

    def addInitHandler(self, handler: Callable[..., None]):
        self._initList.append(handler)

    def _initVar(self, var: TkVar) -> TkVar:
        self._varList.append(var)
        return var

    def run(self):
        self.center()
        self.mainloop()

    def center(self):
        self.withdraw()  # 先隐藏窗口，避免闪动
        self.update_idletasks()  # 确保获取正确的窗口尺寸
        width = self.winfo_width()  # 获取窗口宽度
        height = self.winfo_height()  # 获取窗口高度
        screen_width = self.winfo_screenwidth()  # 屏幕宽度
        screen_height = self.winfo_screenheight()  # 屏幕高度
        x = (screen_width - width) // 2  # 水平居中
        y = (screen_height - height) // 2  # 垂直居中
        self.geometry(f"+{x}+{y}")  # 设置窗口位置
        self.deiconify()  # 恢复显示窗口

    def addRow(self, desc: str, widget: tk.Widget):
        self._rowIndex += 1
        tk.Label(text=desc).grid(row=self._rowIndex, column=0, padx=10, pady=5, sticky='e')
        widget.grid(row=self._rowIndex, column=1, padx=10, pady=5, sticky='w')

    def addRowFrame(self):
        self._rowIndex += 1
        frame = tk.Frame(self)
        frame.grid(row=self._rowIndex, column=0, columnspan=2, padx=10, pady=5)
        return frame

    def addRowFrameWithDesc(self, desc: str):
        self._rowIndex += 1
        tk.Label(text=desc).grid(row=self._rowIndex, column=0, padx=10, pady=5, sticky='e')
        frame = tk.Frame(self)
        frame.grid(row=self._rowIndex, column=1, padx=10, pady=5, sticky='w')
        return frame

    def addLabel(
        self,
        desc: str,
        text: str
    ):
        self.addRow(desc, tk.Label(text=text))

    def addBtn(
        self,
        label: str,
        command: Callable[..., None],
        *,
        width: int = 20,
        focus: bool = False
    ):
        frame = self.addRowFrame()
        btn = tk.Button(frame, text=label, width=width, command=command)
        btn.pack(side="left", expand=True, padx=15)
        if focus:
            self._initFocus(btn)

    def addRadioBtnList(
        self,
        desc: str,
        selectionList: list[str],
        *,
        selectedIndex: int | None = None,
        focusIndex: int | None = None,
        onChanged: Callable[[str], None] | None = None,
    ):
        frame = tk.Frame()
        self.addRow(desc, frame)
        var = tk.StringVar(value=selectionList[selectedIndex] if selectedIndex is not None else RADIO_NOTHING)
        radioBtnList: list[tk.Radiobutton] = []
        for version in selectionList:
            radioBtn = tk.Radiobutton(frame, text=version, variable=var, value=version)
            radioBtn.pack(side="left", padx=(0, 15))
            setWidgetClickFocus(radioBtn)
            radioBtnList.append(radioBtn)
        if focusIndex is not None:
            self._initFocus(radioBtnList[focusIndex])
        if onChanged:
            var.trace_add('write', lambda *args: onChanged(var.get()))  # type: ignore
            self.addInitHandler(
                lambda: onChanged(var.get())
            )
        return var

    def addEntry(
        self,
        desc: str,
        var: tk.StringVar,
        *,
        width: int = 60,
        focus: bool = False,
        justify: Literal['left', 'right', 'center'] = tk.LEFT,
        password: bool = False,
        command: Callable[..., Any] | None = None,
    ):
        self._initVar(var)
        entry = tk.Entry(self, width=width, justify=justify, textvariable=var)
        entry.icursor(tk.END)
        self.addRow(desc, entry)
        if password:
            entry.config(show='*')
        if focus:
            self._initFocus(entry)
        if command:
            entry.bind('<Return>', lambda event: command())
        return entry

    def addChoisePath(
        self,
        desc: str,
        var: tk.StringVar,
        *,
        width: int = 47,
        focus: bool = False,
        isDir: bool = False,
    ):
        self._initVar(var)
        frame = self.addRowFrameWithDesc(desc)
        entry = tk.Entry(frame, width=width, textvariable=var)
        entry.icursor(tk.END)
        entry.pack(side="left")
        btn = tk.Button(frame, text=f'选择{'目录' if isDir else '文件'} ...', width=10, command=lambda: onBtn())
        btn.pack(side="left", padx=(10, 0))
        if focus:
            self._initFocus(btn)

        def onBtn():
            if isDir:
                var.set(filedialog.askdirectory())
            else:
                var.set(filedialog.askopenfilename())

    def addScrolledText(
        self,
        desc: str,
        var: tk.StringVar,
        *,
        width: int = 60,
        height: int = 3,
        focus: bool = False,
    ):
        self._initVar(var)
        scrolledText = ScrolledText(self, width=width, height=height)
        scrolledText.insert(tk.END, var.get())
        self.addRow(desc, scrolledText)

        def on_text_change(*args: Any):
            new_value = scrolledText.get("1.0", tk.END)
            if new_value != var.get():
                var.set(new_value)

        scrolledText.bind("<KeyRelease>", on_text_change)

        def on_tab(event: tk.Event):
            widget = event.widget.tk_focusNext()
            assert widget
            widget.focus_set()
            return "break"

        scrolledText.bind("<Tab>", on_tab)

        if focus:
            self._initFocus(scrolledText)
        return scrolledText

    def addCheckBox(
        self,
        desc: str,
        text: str,
        value: bool = False,
    ):
        var = tk.BooleanVar(value=value)
        self._initVar(var)
        check_btn = tk.Checkbutton(text=text, variable=var)
        self.addRow(desc, check_btn)
        self.addInitHandler(
            lambda: var.set(var.get())
        )
        setWidgetClickFocus(check_btn)
        return var

    def addCheckBoxList(
        self,
        desc: str,
        dataList: list[tuple[str, bool]],
    ):
        varDict: dict[str, tk.BooleanVar] = {}
        frame = tk.Frame(self)
        self.addRow(desc, frame)
        for label, value in dataList:
            varDict[label] = tk.BooleanVar(value=value)
            checkbox = tk.Checkbutton(frame, text=label, variable=varDict[label])
            checkbox.pack(side="left", expand=True, padx=(0, 15))
            setWidgetClickFocus(checkbox)
            self.addInitHandler(
                lambda: varDict[label].set(varDict[label].get())
            )
        return varDict

    def _initFocus(self, widget: tk.Widget):
        self.addInitHandler(
            lambda: widget.focus_set()
        )


def setWidgetEnabled(widget: tk.Widget, value: bool):
    widget['state'] = tk.NORMAL if value else tk.DISABLED


def setWidgetClickFocus(widget: tk.Widget):
    widget.bind("<Button-1>", lambda args: args.widget.focus_set())
