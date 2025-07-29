# region Htyy

import inspect
import os
import warnings

class filedialog:
    def __init__(self, window, morphology='tkinter', icon=None):
        self.window = window
        self.morphology = morphology
        self._default_ext = None
        self.icon = icon

        if self.morphology == 'tkinter':
            self.impl = _TkinterFileDialogImpl(window)
        elif self.morphology == 'PyQt':
            self.impl = _PyQtFileDialogImpl(window)
        elif self.morphology == 'pyqt':
            self.impl = _PyQtFileDialogImpl(window)
        else:
            raise ValueError(f"Unsupported morphology: {morphology}")

    # region 公共接口
    def askopenfilename(self, icon=None, **kwargs):
        kwargs['icon'] = icon if icon is not None else self.icon
        return self.impl.askopenfilename(**self._prepare_kwargs(kwargs))

    def askopenfilenames(self, icon=None, **kwargs):
        kwargs['icon'] = icon if icon is not None else self.icon
        return self.impl.askopenfilenames(**self._prepare_kwargs(kwargs))

    def askopenfile(self, mode='r', icon=None, **kwargs):
        kwargs['icon'] = icon if icon is not None else self.icon
        return self.impl.askopenfile(mode=mode, **self._prepare_kwargs(kwargs))

    def askopenfiles(self, mode='r', icon=None, **kwargs):
        kwargs['icon'] = icon if icon is not None else self.icon
        return self.impl.askopenfiles(mode=mode, **self._prepare_kwargs(kwargs))

    def asksaveasfilename(self, icon=None, **kwargs):
        kwargs['icon'] = icon if icon is not None else self.icon
        return self.impl.asksaveasfilename(**self._prepare_kwargs(kwargs))

    def asksaveasfile(self, mode='w', icon=None, **kwargs):
        kwargs['icon'] = icon if icon is not None else self.icon
        return self.impl.asksaveasfile(mode=mode, **self._prepare_kwargs(kwargs))

    def askdirectory(self, icon=None, **kwargs):
        kwargs['icon'] = icon if icon is not None else self.icon
        return self.impl.askdirectory(**self._prepare_kwargs(kwargs))

    def set_default_extension(self, ext):
        self._default_ext = ext
        self.impl.set_default_extension(ext)
    # endregion

    def _prepare_kwargs(self, kwargs):
        """预处理公共参数"""
        if self._default_ext and 'defaultextension' not in kwargs:
            kwargs['defaultextension'] = self._default_ext
        return kwargs


class _TkinterFileDialogImpl:
    def __init__(self, window):
        import tkinter.filedialog as tkfiledialog
        self._window = window
        self._tk = tkfiledialog
        self._default_ext = None

    # region 实现方法
    def askopenfilename(self, **kwargs):
        return self._run_dialog(self._tk.askopenfilename, kwargs)

    def askopenfilenames(self, **kwargs):
        return self._run_dialog(self._tk.askopenfilenames, kwargs)

    def askopenfile(self, **kwargs):
        return self._run_dialog(self._tk.askopenfile, kwargs)

    def askopenfiles(self, **kwargs):
        return self._run_dialog(self._tk.askopenfiles, kwargs)

    def asksaveasfilename(self, **kwargs):
        return self._run_dialog(self._tk.asksaveasfilename, kwargs)

    def asksaveasfile(self, **kwargs):
        return self._run_dialog(self._tk.asksaveasfile, kwargs)

    def askdirectory(self, **kwargs):
        return self._run_dialog(self._tk.askdirectory, kwargs)

    def set_default_extension(self, ext):
        self._default_ext = ext
    # endregion

    def _run_dialog(self, dialog_func, kwargs):
        """统一执行Tkinter对话框"""
        # 处理图标参数
        icon = kwargs.pop('icon', None)
        if icon is not None:
            warnings.warn("Icon setting is not supported in Tkinter morphology", UserWarning)
        
        # 其余参数处理
        kwargs.setdefault('parent', self._window)
        if self._default_ext:
            kwargs.setdefault('defaultextension', self._default_ext)
        filtered = self._filter_kwargs(dialog_func, kwargs)
        return dialog_func(**filtered)

    @staticmethod
    def _filter_kwargs(func, kwargs):
        sig = inspect.signature(func)
        valid_params = [
            p.name for p in sig.parameters.values()
            if p.kind == p.POSITIONAL_OR_KEYWORD
        ]
        return {k: v for k, v in kwargs.items() if k in valid_params}


class _PyQtFileDialogImpl:
    def __init__(self, window):
        try:
            from PyQt5.QtWidgets import QFileDialog, QApplication
            from PyQt5.QtGui import QIcon
        except ImportError:
            try:
                from PyQt6.QtWidgets import QFileDialog, QApplication
                from PyQt6.QtGui import QIcon
            except ImportError as e:
                raise ImportError("PyQt5 package is required") from e

        self._window = window
        self._QFileDialog = QFileDialog
        self._QIcon = QIcon
        self._app = QApplication.instance() or QApplication([])
        self._default_ext = None

    # region 实现方法
    def askopenfilename(self, **kwargs):
        return self._file_dialog('getOpenFileName', **kwargs)

    def askopenfilenames(self, **kwargs):
        return self._file_dialog('getOpenFileNames', **kwargs)

    def askopenfile(self, **kwargs):
        filename = self._file_dialog('getOpenFileName', **kwargs)
        return self._open_file(filename, kwargs.get('mode', 'r'))

    def askopenfiles(self, **kwargs):
        filenames = self._file_dialog('getOpenFileNames', **kwargs)
        return [self._open_file(f, kwargs.get('mode', 'r')) for f in filenames]

    def asksaveasfilename(self, **kwargs):
        return self._file_dialog('getSaveFileName', **kwargs)

    def asksaveasfile(self, **kwargs):
        filename = self._file_dialog('getSaveFileName', **kwargs)
        return self._open_file(filename, kwargs.get('mode', 'w'))

    def askdirectory(self, **kwargs):
        return self._file_dialog('getExistingDirectory', **kwargs)

    def set_default_extension(self, ext):
        self._default_ext = ext
    # endregion

    def _file_dialog(self, method, **kwargs):
        """统一处理Qt对话框"""
        dialog = self._QFileDialog(self._window)
        
        # 设置基础属性
        dialog.setWindowTitle(kwargs.get('title', ''))
        dialog.setDirectory(kwargs.get('initialdir', ''))
        
        # 设置文件类型过滤器
        file_types = self._parse_filetypes(kwargs.get('filetypes', []))
        if file_types:
            dialog.setNameFilters(file_types)
        
        # 设置默认扩展名
        defaultextension = kwargs.get('defaultextension', self._default_ext)
        if defaultextension:
            dialog.setDefaultSuffix(defaultextension.lstrip('.'))
        
        # 设置窗口图标
        if 'icon' in kwargs and kwargs['icon'] is not None:
            dialog.setWindowIcon(self._QIcon(kwargs['icon']))
        
        # 配置对话框模式
        method_mapping = {
            'getOpenFileName': (self._QFileDialog.AcceptOpen, self._QFileDialog.ExistingFile),
            'getOpenFileNames': (self._QFileDialog.AcceptOpen, self._QFileDialog.ExistingFiles),
            'getSaveFileName': (self._QFileDialog.AcceptSave, self._QFileDialog.AnyFile),
            'getExistingDirectory': (self._QFileDialog.AcceptOpen, self._QFileDialog.Directory)
        }
        
        if method in method_mapping:
            accept_mode, file_mode = method_mapping[method]
            dialog.setAcceptMode(accept_mode)
            dialog.setFileMode(file_mode)
            if method == 'getExistingDirectory':
                dialog.setOption(self._QFileDialog.ShowDirsOnly, True)
        else:
            raise ValueError(f"Unsupported dialog method: {method}")

        # 执行对话框
        if dialog.exec_() == self._QFileDialog.Accepted:
            if method == 'getExistingDirectory':
                return dialog.selectedFiles()[0]
            elif method == 'getOpenFileNames':
                return dialog.selectedFiles()
            else:
                return dialog.selectedFiles()[0] if dialog.selectedFiles() else ''
        else:
            return '' if method != 'getOpenFileNames' else []

    def _open_file(self, filename, mode):
        """打开文件并返回文件对象"""
        if not filename:
            return None
        return open(filename, mode)

    @staticmethod
    def _parse_filetypes(filetypes):
        """转换文件类型格式"""
        return [
            f"{desc} ({patterns})"
            for desc, patterns in filetypes
        ]
    
letter = {
    "A":"a",
    "B":"b",
    "C":"c",
    "D":"d",
    "E":"e",
    "F":"f",
    "G":"g",
    "H":"h",
    "I":"i",
    "J":"j",
    "K":"k",
    "L":"l",
    "M":"m",
    "N":"n",
    "O":"o",
    "P":"p",
    "Q":"q",
    "R":"r",
    "S":"s",
    "T":"t",
    "U":"u",
    "V":"v",
    "W":"w",
    "X":"x",
    "Y":"y",
    "Z":"z"
}

def _test():
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()

    dialog = filedialog(root, 'tkinter')
    print("Open file:", dialog.askopenfilename(title="选择数据文件", filetypes=[("CSV File", "*.csv")]))
    root.destroy()

if __name__== "__main__":
    _test()

# region Htyy