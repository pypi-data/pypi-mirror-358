r"""
cl /LD /EHsc /I "D:\Python\include" 
/I "D:\Python\Lib\site-packages\pybind11\include"   
C:\Users\36376\Desktop\pynativegui.cpp /link /LIBPATH:"D:\Python\libs"     
python311.lib user32.lib gdi32.lib comdlg32.lib
"""

import typing as t

def create_window(
    title: str = "Window",
    width: int = 400,
    height: int = 300,
    no_titlebar: bool = False,
    transparent: bool = False,
    resizable: bool = True,
    topmost: bool = False
) -> t.Any: 
    """
    Create a new window
    Creates a top-level application window
    
    Args:
        title: Window title bar text
        width: Initial window width in pixels
        height: Initial window height in pixels
        no_titlebar: Create borderless window without title bar
        transparent: Enable window transparency
        resizable: Allow user to resize window
        topmost: Keep window always on top of others
    
    Returns:
        Window capsule object reference
    
    创建新窗口
    创建顶层应用程序窗口
    
    参数:
        title: 窗口标题栏文本
        width: 初始窗口宽度（像素）
        height: 初始窗口高度（像素）
        no_titlebar: 创建无标题栏的无边框窗口
        transparent: 启用窗口透明效果
        resizable: 允许用户调整窗口大小
        topmost: 窗口始终保持在最上层
    """
    ...

def show_window(window: t.Any) -> None:
    """
    Display a created window
    Makes a previously created window visible on screen
    
    Args:
        window: Window capsule object reference
    
    显示已创建的窗口
    使先前创建的窗口在屏幕上可见
    
    参数:
        window: 窗口胶囊对象引用
    """
    ...

def set_window_title(window: t.Any, title: str) -> None:
    """
    Set window title text
    Updates the text displayed in window's title bar
    
    Args:
        window: Window capsule object reference
        title: New title text
    
    设置窗口标题文本
    更新窗口标题栏显示的文本
    
    参数:
        window: 窗口胶囊对象引用
        title: 新标题文本
    """
    ...

def set_window_size(window: t.Any, width: int, height: int) -> None:
    """
    Resize application window
    Changes dimensions of specified window
    
    Args:
        window: Window capsule object reference
        width: New window width in pixels
        height: New window height in pixels
    
    调整应用程序窗口大小
    更改指定窗口的尺寸
    
    参数:
        window: 窗口胶囊对象引用
        width: 新窗口宽度（像素）
        height: 新窗口高度（像素）
    """
    ...

def set_window_position(window: t.Any, x: int, y: int) -> None:
    """
    Reposition application window
    Moves window to new screen coordinates
    
    Args:
        window: Window capsule object reference
        x: New horizontal position (pixels from left)
        y: New vertical position (pixels from top)
    
    重新定位应用程序窗口
    将窗口移动到新的屏幕坐标
    
    参数:
        window: 窗口胶囊对象引用
        x: 新水平位置（距离左侧的像素数）
        y: 新垂直位置（距离顶部的像素数）
    """
    ...

def set_window_alpha(window: t.Any, alpha: int) -> None:
    """
    Set window transparency level
    Adjusts overall opacity of the window (0-255)
    
    Args:
        window: Window capsule object reference
        alpha: Transparency value (0=fully transparent, 255=opaque)
    
    设置窗口透明度级别
    调整窗口的整体不透明度（0-255）
    
    参数:
        window: 窗口胶囊对象引用
        alpha: 透明度值（0=完全透明，255=不透明）
    """
    ...

def create_label(
    parent: t.Any,
    text: str = "",
    x: int = 0,
    y: int = 0,
    width: int = 100,
    height: int = 20,
    anchor: str = "nw"
) -> t.Any:
    """
    Create text label control
    Displays static text in application window
    
    Args:
        parent: Parent window capsule object
        text: Label content text
        x: Horizontal position in parent
        y: Vertical position in parent
        width: Label width in pixels
        height: Label height in pixels
        anchor: Text anchoring position
    
    Returns:
        Label capsule object reference
    
    创建文本标签控件
    在应用程序窗口中显示静态文本
    
    参数:
        parent: 父窗口胶囊对象
        text: 标签内容文本
        x: 在父容器中的水平位置
        y: 在父容器中的垂直位置
        width: 标签宽度（像素）
        height: 标签高度（像素）
        anchor: 文本锚定位置
    """
    ...

def create_button(
    parent: t.Any,
    text: str = "Button",
    x: int = 0,
    y: int = 0,
    width: int = 80,
    height: int = 24,
    command: t.Optional[t.Callable] = None
) -> t.Any:
    """
    Create clickable button control
    Executes callback function when clicked
    
    Args:
        parent: Parent window capsule object
        text: Button display text
        x: Horizontal position in parent
        y: Vertical position in parent
        width: Button width in pixels
        height: Button height in pixels
        command: Click event callback function
    
    Returns:
        Button capsule object reference
    
    创建可点击按钮控件
    点击时执行回调函数
    
    参数:
        parent: 父窗口胶囊对象
        text: 按钮显示文本
        x: 在父容器中的水平位置
        y: 在父容器中的垂直位置
        width: 按钮宽度（像素）
        height: 按钮高度（像素）
        command: 点击事件回调函数
    """
    ...

def create_entry(
    parent: t.Any,
    default_text: str = "",
    x: int = 0,
    y: int = 0,
    width: int = 120,
    height: int = 24
) -> t.Any:
    """
    Create text entry field
    Single-line user input control
    
    Args:
        parent: Parent window capsule object
        default_text: Initial field content
        x: Horizontal position in parent
        y: Vertical position in parent
        width: Field width in pixels
        height: Field height in pixels
    
    Returns:
        Entry capsule object reference
    
    创建文本输入框
    单行用户输入控件
    
    参数:
        parent: 父窗口胶囊对象
        default_text: 初始字段内容
        x: 在父容器中的水平位置
        y: 在父容器中的垂直位置
        width: 输入框宽度（像素）
        height: 输入框高度（像素）
    """
    ...

def get_entry_text(entry: t.Any) -> str:
    """
    Retrieve text from entry field
    Gets current content of text input control
    
    Args:
        entry: Entry capsule object reference
    
    Returns:
        Current text content
    
    从输入框获取文本
    获取文本输入控件的当前内容
    
    参数:
        entry: 输入框胶囊对象引用
    
    返回:
        当前文本内容
    """
    ...

def set_control_text(control: t.Any, text: str) -> None:
    """
    Update control display text
    Changes text content of various controls
    
    Args:
        control: Control capsule object reference
        text: New text content
    
    更新控件显示文本
    更改各种控件的文本内容
    
    参数:
        control: 控件胶囊对象引用
        text: 新文本内容
    """
    ...

def create_listbox(
    parent: t.Any,
    x: int = 0,
    y: int = 0,
    width: int = 200,
    height: int = 150
) -> t.Any:
    """
    Create selection list control
    Displays scrollable list of items
    
    Args:
        parent: Parent window capsule object
        x: Horizontal position in parent
        y: Vertical position in parent
        width: Listbox width in pixels
        height: Listbox height in pixels
    
    Returns:
        Listbox capsule object reference
    
    创建选择列表控件
    显示可滚动的项目列表
    
    参数:
        parent: 父窗口胶囊对象
        x: 在父容器中的水平位置
        y: 在父容器中的垂直位置
        width: 列表框宽度（像素）
        height: 列表框高度（像素）
    """
    ...

def listbox_insert(listbox: t.Any, index: int, text: str) -> None:
    """
    Add item to listbox
    Inserts text item at specified position
    
    Args:
        listbox: Listbox capsule object reference
        index: Insertion position (0-based)
        text: Item display text
    
    向列表框中添加项目
    在指定位置插入文本项目
    
    参数:
        listbox: 列表框胶囊对象引用
        index: 插入位置（从0开始）
        text: 项目显示文本
    """
    ...

def create_combobox(
    parent: t.Any,
    x: int = 0,
    y: int = 0,
    width: int = 120,
    height: int = 100
) -> t.Any:
    """
    Create dropdown selection control
    Combines text field with drop-down list
    
    Args:
        parent: Parent window capsule object
        x: Horizontal position in parent
        y: Vertical position in parent
        width: Combobox width in pixels
        height: Combobox height in pixels
    
    Returns:
        Combobox capsule object reference
    
    创建下拉选择控件
    组合文本框和下拉列表
    
    参数:
        parent: 父窗口胶囊对象
        x: 在父容器中的水平位置
        y: 在父容器中的垂直位置
        width: 组合框宽度（像素）
        height: 组合框高度（像素）
    """
    ...

def combobox_add(combobox: t.Any, text: str) -> None:
    """
    Add option to combobox
    Appends item to dropdown list
    
    Args:
        combobox: Combobox capsule object reference
        text: Option display text
    
    向组合框添加选项
    将项目追加到下拉列表
    
    参数:
        combobox: 组合框胶囊对象引用
        text: 选项显示文本
    """
    ...

def create_progressbar(
    parent: t.Any,
    x: int = 0,
    y: int = 0,
    width: int = 200,
    height: int = 20,
    orient: int = 0
) -> t.Any:
    """
    Create progress indicator
    Visual representation of task completion
    
    Args:
        parent: Parent window capsule object
        x: Horizontal position in parent
        y: Vertical position in parent
        width: Progressbar width in pixels
        height: Progressbar height in pixels
        orient: Orientation (0=horizontal, 1=vertical)
    
    Returns:
        Progressbar capsule object reference
    
    创建进度指示器
    任务完成进度的可视化表示
    
    参数:
        parent: 父窗口胶囊对象
        x: 在父容器中的水平位置
        y: 在父容器中的垂直位置
        width: 进度条宽度（像素）
        height: 进度条高度（像素）
        orient: 方向（0=水平，1=垂直）
    """
    ...

def progress_set(progressbar: t.Any, value: int) -> None:
    """
    Update progress indicator
    Sets current progress percentage (0-100)
    
    Args:
        progressbar: Progressbar capsule object reference
        value: Completion percentage
    
    更新进度指示器
    设置当前进度百分比（0-100）
    
    参数:
        progressbar: 进度条胶囊对象引用
        value: 完成百分比
    """
    ...

def create_canvas(
    parent: t.Any,
    x: int = 0,
    y: int = 0,
    width: int = 300,
    height: int = 200,
    bg: str = "white"
) -> t.Any:
    """
    Create drawing surface
    Provides area for custom graphics rendering
    
    Args:
        parent: Parent window capsule object
        x: Horizontal position in parent
        y: Vertical position in parent
        width: Canvas width in pixels
        height: Canvas height in pixels
        bg: Background color name
    
    Returns:
        Canvas capsule object reference
    
    创建绘图表面
    提供自定义图形渲染区域
    
    参数:
        parent: 父窗口胶囊对象
        x: 在父容器中的水平位置
        y: 在父容器中的垂直位置
        width: 画布宽度（像素）
        height: 画布高度（像素）
        bg: 背景颜色名称
    """
    ...

def canvas_line(
    canvas: t.Any,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: str = "black",
    width: int = 1
) -> None:
    """
    Draw line on canvas
    Renders straight line between two points
    
    Args:
        canvas: Canvas capsule object reference
        x1: Starting X coordinate
        y1: Starting Y coordinate
        x2: Ending X coordinate
        y2: Ending Y coordinate
        color: Line color name
        width: Line thickness in pixels
    
    在画布上绘制直线
    在两点之间渲染直线
    
    参数:
        canvas: 画布胶囊对象引用
        x1: 起始X坐标
        y1: 起始Y坐标
        x2: 结束X坐标
        y2: 结束Y坐标
        color: 线条颜色名称
        width: 线条粗细（像素）
    """
    ...

def canvas_rectangle(
    canvas: t.Any,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    outline: str = "black",
    fill: str = "",
    width: int = 1
) -> None:
    """
    Draw rectangle on canvas
    Renders rectangular shape with optional fill
    
    Args:
        canvas: Canvas capsule object reference
        x1: Top-left X coordinate
        y1: Top-left Y coordinate
        x2: Bottom-right X coordinate
        y2: Bottom-right Y coordinate
        outline: Border color name
        fill: Fill color name (empty for transparent)
        width: Border thickness in pixels
    
    在画布上绘制矩形
    渲染矩形形状（可选填充）
    
    参数:
        canvas: 画布胶囊对象引用
        x1: 左上角X坐标
        y1: 左上角Y坐标
        x2: 右下角X坐标
        y2: 右下角Y坐标
        outline: 边框颜色名称
        fill: 填充颜色名称（空表示透明）
        width: 边框粗细（像素）
    """
    ...

def canvas_text(
    canvas: t.Any,
    x: int,
    y: int,
    text: str,
    color: str = "black",
    font: str = "Arial",
    size: int = 12
) -> None:
    """
    Draw text on canvas
    Renders specified text at given position
    
    Args:
        canvas: Canvas capsule object reference
        x: Text baseline X coordinate
        y: Text baseline Y coordinate
        text: String content to render
        color: Text color name
        font: Font family name
        size: Font size in points
    
    在画布上绘制文本
    在指定位置渲染文本
    
    参数:
        canvas: 画布胶囊对象引用
        x: 文本基线X坐标
        y: 文本基线Y坐标
        text: 要渲染的字符串内容
        color: 文本颜色名称
        font: 字体名称
        size: 字体大小（磅值）
    """
    ...

def create_menu(window: t.Any) -> t.Any:
    """
    Create menu container
    Prepares menu structure for window
    
    Args:
        window: Window capsule object reference
    
    Returns:
        Menu capsule object reference
    
    创建菜单容器
    为窗口准备菜单结构
    
    参数:
        window: 窗口胶囊对象引用
    """
    ...

def menu_add_item(
    menu: t.Any,
    label: str,
    callback: t.Callable,
    accelerator: str = ""
) -> None:
    """
    Add command to menu
    Appends clickable item to menu container
    
    Args:
        menu: Menu capsule object reference
        label: Menu item display text
        callback: Click event handler
        accelerator: Keyboard shortcut hint
    
    向菜单添加命令项
    将可点击项目添加到菜单容器
    
    参数:
        menu: 菜单胶囊对象引用
        label: 菜单项显示文本
        callback: 点击事件处理函数
        accelerator: 键盘快捷键提示
    """
    ...

def add_menu(window: t.Any, menu: t.Any, label: str) -> None:
    """
    Attach menu to window
    Adds menu container to window's menu bar
    
    Args:
        window: Window capsule object reference
        menu: Menu capsule object reference
        label: Menu display text
    
    将菜单附加到窗口
    将菜单容器添加到窗口的菜单栏
    
    参数:
        window: 窗口胶囊对象引用
        menu: 菜单胶囊对象引用
        label: 菜单显示文本
    """
    ...

def create_statusbar(window: t.Any) -> None:
    """
    Create status bar
    Adds information panel to window bottom
    
    Args:
        window: Window capsule object reference
    
    创建状态栏
    在窗口底部添加信息面板
    
    参数:
        window: 窗口胶囊对象引用
    """
    ...

def statusbar_set(
    window: t.Any,
    part: int,
    text: str
) -> None:
    """
    Update status bar text
    Sets content for specified status bar section
    
    Args:
        window: Window capsule object reference
        part: Status bar segment index
        text: Text content to display
    
    更新状态栏文本
    设置指定状态栏部分的内容
    
    参数:
        window: 窗口胶囊对象引用
        part: 状态栏分段索引
        text: 要显示的文本内容
    """
    ...

def bind(
    control: t.Any,
    event_name: str,
    callback: t.Callable
) -> None:
    """
    Bind event to control
    Attaches event handler to UI component
    
    Args:
        control: Control capsule object reference
        event_name: Event identifier string
        callback: Event handler function
    
    Supported events:
        "<Button-1>"      : Mouse button press
        "<ButtonRelease-1>": Mouse button release
        "<Motion>"        : Mouse movement
        "<Key>"           : Keyboard key press
        "<Configure>"     : Control resize
        "<FocusIn>"       : Control gains focus
        "<FocusOut>"      : Control loses focus
    
    将事件绑定到控件
    将事件处理函数附加到UI组件
    
    参数:
        control: 控件胶囊对象引用
        event_name: 事件标识字符串
        callback: 事件处理函数
    
    支持的事件:
        "<Button-1>"      : 鼠标按钮按下
        "<ButtonRelease-1>": 鼠标按钮释放
        "<Motion>"        : 鼠标移动
        "<Key>"           : 键盘按键
        "<Configure>"     : 控件调整大小
        "<FocusIn>"       : 控件获得焦点
        "<FocusOut>"      : 控件失去焦点
    """
    ...

def filedialog(
    title: str = "Open File",
    filetypes: str = "All Files\0*.*\0",
    initialdir: str = "",
    save: bool = False
) -> t.Optional[str]:
    """
    Show file selection dialog
    Opens system file chooser interface
    
    Args:
        title: Dialog window title
        filetypes: File filter patterns
        initialdir: Starting directory path
        save: True for save dialog, False for open
    
    Returns:
        Selected file path or None
    
    显示文件选择对话框
    打开系统文件选择器界面
    
    参数:
        title: 对话框窗口标题
        filetypes: 文件过滤模式
        initialdir: 起始目录路径
        save: True为保存对话框，False为打开对话框
    
    返回:
        选择的文件路径或None
    """
    ...

def colorchooser(
    initial_color: t.Optional[t.Tuple[int, int, int]] = None
) -> t.Optional[t.Tuple[int, int, int]]:
    """
    Show color selection dialog
    Opens system color picker interface
    
    Args:
        initial_color: Preselected RGB color tuple
    
    Returns:
        Selected RGB color tuple or None
    
    显示颜色选择对话框
    打开系统颜色选择器界面
    
    参数:
        initial_color: 预选的RGB颜色元组
    
    返回:
        选择的RGB颜色元组或None
    """
    ...

def messagebox(
    title: str,
    message: str,
    type: str = "info"
) -> t.Optional[bool]:
    """
    Display message dialog
    Shows system alert with buttons
    
    Args:
        title: Dialog window title
        message: Information text content
        type: Dialog type ("info", "warning", "error", "question")
    
    Returns:
        For question dialogs: True=Yes, False=No
        For other types: None
    
    显示消息对话框
    显示带按钮的系统警报
    
    参数:
        title: 对话框窗口标题
        message: 信息文本内容
        type: 对话框类型 ("info", "warning", "error", "question")
    
    返回:
        对于问题对话框: True=是, False=否
        其他类型: None
    """
    ...

def mainloop() -> None:
    """
    Start application event loop
    Begins processing user interface events
    
    启动应用程序事件循环
    开始处理用户界面事件
    """
    ...

def quit() -> None:
    """
    Terminate application
    Exits program and closes all windows
    
    终止应用程序
    退出程序并关闭所有窗口
    """
    ...

def set_window_icon(window: t.Any, icon_path: str) -> None:
    """
    Set window title bar icon
    Loads and displays custom icon in window title bar
    
    Args:
        window: Window capsule object reference
        icon_path: Path to .ico icon file
    
    Supported formats:
        .ico files (recommended)
        .exe files with icon resources
        .dll files with icon resources
    
    Note: For best results, provide icons in multiple sizes:
        - 16x16 (small/taskbar)
        - 32x32 (standard)
        - 48x48 (large)
        - 256x256 (high DPI)
    
    设置窗口标题栏图标
    加载并显示自定义图标在窗口标题栏
    
    参数:
        window: 窗口胶囊对象引用
        icon_path: .ico图标文件路径
    
    支持格式:
        .ico 文件 (推荐)
        包含图标资源的 .exe 文件
        包含图标资源的 .dll 文件
    
    注意: 为获得最佳效果，请提供多种尺寸的图标:
        - 16x16 (小尺寸/任务栏)
        - 32x32 (标准尺寸)
        - 48x48 (大尺寸)
        - 256x256 (高DPI)
    """
    ...