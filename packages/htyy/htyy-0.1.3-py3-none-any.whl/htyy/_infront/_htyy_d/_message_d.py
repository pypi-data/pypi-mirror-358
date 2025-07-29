"""
Message
~~~~~~~~
The module provides a series of functions for displaying different types of message boxes,
It includes information prompts, warning boxes, error boxes, and various problem prompts with buttons such as confirmation and cancel.
"""
#Copyright (c) 2025, <363766687@qq.com>
#Author: Huang Yiyi

import ctypes

user32 = ctypes.windll.user32

MB_OK = 0x00000000
MB_OKCANCEL = 0x00000001
MB_YESNO = 0x00000004
MB_RETRYCANCEL = 0x00000005

MB_ICONINFORMATION = 0x00000040
MB_ICONWARNING = 0x00000030
MB_ICONERROR = 0x00000010
MB_ICONQUESTION = 0x00000020

IDI_APPLICATION = 32512
IDI_HAND = 32513
IDI_QUESTION = 32514
IDI_EXCLAMATION = 32515
IDI_ASTERISK = 32516

IMAGE_ICON = 1
LR_LOADFROMFILE = 0x00000010


class __Message__:
    """
    有关消息的(消息弹窗)类，封装了各种显示消息框的方法。
    """
    def __init__(self):
        """
        初始化 _Message 类的实例。
        将各种消息框样式和图标常量绑定到实例属性，并加载 user32.dll 库，
        同时设置 MessageBoxA 函数的参数类型和返回值类型。
        """
        # 将常量绑定到实例属性
        self.MB_OK = MB_OK
        self.MB_ICONWARNING = MB_ICONWARNING
        self.MB_ICONINFORMATION = MB_ICONINFORMATION
        self.MB_ICONERROR = MB_ICONERROR
        self.MB_ICONQUESTION = MB_ICONQUESTION
        self.IDI_APPLICATION = IDI_APPLICATION
        self.IDI_HAND = IDI_HAND
        self.IDI_QUESTION = IDI_QUESTION
        self.IDI_EXCLAMATION = IDI_EXCLAMATION
        self.IDI_ASTERISK = IDI_ASTERISK
        self.MB_OKCANCEL = MB_OKCANCEL
        self.MB_YESNO = MB_YESNO
        self.MB_RETRYCANCEL = MB_RETRYCANCEL
        self.IMAGE_ICON = IMAGE_ICON
        self.LR_LOADFROMFILE = LR_LOADFROMFILE
        # 加载 user32.dll
        user32 = ctypes.windll.user32
        # 设置 MessageBoxA 函数的参数类型和返回值类型
        user32.MessageBoxA.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        user32.MessageBoxA.restype = ctypes.c_int

    def show_message_box(self, message, title, style=MB_OK | MB_ICONINFORMATION):
        """
        一切的根源,不推荐用,因为要自己输入常量。
        显示消息框并处理可能的错误。

        :param message: 消息框显示的消息内容
        :param title: 消息框的标题
        :param style: 消息框的样式，默认为 OK 按钮和信息图标
        :return: 消息框的返回值，如果出现错误则返回 None
        """
        try:
            # 编码消息和标题
            encoded_message = message.encode('gbk')
            encoded_title = title.encode('gbk')
            # 调用 MessageBoxA 显示消息框
            result = user32.MessageBoxA(0, encoded_message, encoded_title, style)
            return result
        except UnicodeEncodeError:
            print("编码消息或标题时出现错误，请检查字符是否支持 GBK 编码。")
            return None
        except Exception as e:
            print(f"显示消息框时出现未知错误: {e}")
            return None

    def showinfo(self, title, message):
        """
        显示一个带有信息图标的消息框，包含 OK 按钮。

        :param title: 消息框的标题
        :param message: 消息框显示的消息内容
        :return: 消息框的返回值，如果出现错误则返回 None
        """
        return self.show_message_box(title=title, message=message, style=self.MB_OK | self.MB_ICONINFORMATION)

    def showwarning(self, title, message):
        """
        显示一个带有警告图标的消息框，包含 OK 按钮。

        :param title: 消息框的标题
        :param message: 消息框显示的消息内容
        :return: 消息框的返回值，如果出现错误则返回 None
        """
        return self.show_message_box(title=title, message=message, style=self.MB_OK | self.MB_ICONWARNING)

    def showerror(self, title, message):
        """
        显示一个带有错误图标的消息框，包含 OK 按钮。

        :param title: 消息框的标题
        :param message: 消息框显示的消息内容
        :return: 消息框的返回值，如果出现错误则返回 None
        """
        return self.show_message_box(title=title, message=message, style=self.MB_OK | self.MB_ICONERROR)

    def showyescancel(self, title, message):
        """
        显示一个带有问号图标的消息框，包含 OK 和 Cancel 按钮。

        :param title: 消息框的标题
        :param message: 消息框显示的消息内容
        :return: 如果用户点击 OK 按钮返回 'ok'，点击 Cancel 按钮返回 'cancel'，出现错误则返回 None
        """
        ok_cancel_result = self.show_message_box(title=title, message=message,
                                                 style=self.MB_OKCANCEL | self.MB_ICONQUESTION)
        if ok_cancel_result is not None:
            if ok_cancel_result == 1:  # OK 按钮被点击
                return 'ok'
            elif ok_cancel_result == 2:  # Cancel 按钮被点击
                return 'cancel'

    def showyesno(self, title, message):
        """
        显示一个带有问号图标的消息框，包含 Yes 和 No 按钮。

        :param title: 消息框的标题
        :param message: 消息框显示的消息内容
        :return: 如果用户点击 Yes 按钮返回 'yes'，点击 No 按钮返回 'no'，出现错误则返回 None
        """
        yes_no_result = self.show_message_box(message, title, self.MB_YESNO | self.MB_ICONQUESTION)
        if yes_no_result is not None:
            if yes_no_result == 6:  # Yes 按钮被点击
                return 'yes'
            elif yes_no_result == 7:  # No 按钮被点击
                return 'no'

    def showRetry(self, title, message):
        """
        显示一个带有错误图标的消息框，包含 Retry 和 Cancel 按钮。

        :param title: 消息框的标题
        :param message: 消息框显示的消息内容
        :return: 如果用户点击 Retry 按钮返回 'retry'，点击 Cancel 按钮返回 'cancel'，出现错误则返回 None
        """
        retry_cancel_error_result = self.show_message_box(message, title,
                                                          style=self.MB_RETRYCANCEL | self.MB_ICONERROR)
        if retry_cancel_error_result is not None:
            if retry_cancel_error_result == 4:
                return 'retry'
            elif retry_cancel_error_result == 2:
                return 'cancel'

    def show_custom_message_box(self, title, message, message_type='info', icon_path=None, button_style=MB_OK):
        """
        显示一个自定义消息框，可指定消息类型、自定义图标和按钮样式。
        此功能处于实验阶段，可能无法正常加载图标。

        :param title: 消息框的标题
        :param message: 消息框显示的消息内容
        :param message_type: 消息类型，可选值为 'warning'、'info'、'error' 等，默认为 'info'
        :param icon_path: 自定义图标的路径，默认为 None
        :param button_style: 按钮样式，默认为 OK 按钮
        :return: 消息框的返回值
        """
        icon_handle = None
        # 根据消息类型设置图标和标题前缀
        if message_type == 'warning':
            icon = MB_ICONWARNING
            title_prefix = "[警告] "
        elif message_type == 'info':
            icon = MB_ICONINFORMATION
            title_prefix = "[提醒] "
        elif message_type == 'error':
            icon = MB_ICONERROR
            title_prefix = "[错误] "
        else:
            icon = 0
            title_prefix = ""

        # 拼接最终标题
        final_title = title_prefix + title

        if icon_path:
            # 加载自定义图标
            try:
                icon_handle = user32.LoadImageW(None, icon_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE)
                if icon_handle == 0:
                    print("加载图标失败")
                    icon_handle = None
            except Exception as e:
                print(f"加载图标时出现错误: {e}")
        else:
            # 使用系统预定义图标
            button_style |= icon

        # 显示消息框
        result = user32.MessageBoxW(0, message, final_title, button_style)
        return result

    def askquestion(self, title, message):
        """
        显示一个带有问号图标的是/否问题提示框。

        :param title: 消息框的标题
        :param message: 消息框显示的消息内容
        :return: 如果用户点击 Yes 按钮返回 'yes'，点击 No 按钮返回 'no'，出现错误则返回 None
        """
        yes_no_result = self.show_message_box(message, title, self.MB_YESNO | self.MB_ICONQUESTION)
        if yes_no_result is not None:
            if yes_no_result == 6:  # Yes 按钮被点击
                return 'yes'
            elif yes_no_result == 7:  # No 按钮被点击
                return 'no'


__msg__ = __Message__()


def showinfo(title, message):
    """
    Displays a message box with an information icon, containing an OK button.

    :param title: The title of the message box
    :param message: The content of the message displayed in the message box
    :return: The return value of the message box, or None if there is an error
    """
    return __msg__.showinfo(title=title, message=message)


def showerror(title, message):
    """
    A message box with an error icon is displayed, containing an OK button.

    :param title: The title of the message box
    :param message: The content of the message displayed in the message box
    :return: The return value of the message box, or None if there is an error
    """
    return __msg__.showerror(title=title, message=message)


def showwarning(title, message):
    """
    Displays a message box with a warning icon, containing an OK button.

    :param title: The title of the message box
    :param message: The content of the message displayed in the message box
    :return: The return value of the message box, or None if there is an error
    """
    return __msg__.showwarning(title=title, message=message)


def askcancelretry(title, message):
    """
    Displays a message box with an error icon, containing the Retry and Cancel buttons.

    :param title: The title of the message box
    :param message: The content of the message displayed in the message box
    :return: If the user clicks the Retry button to return 'retry', clicks the Cancel button to return 'cancel', and returns None if there is an error
    """
    return __msg__.showRetry(title=title, message=message)


def askyescancel(title, message):
    """
    Displays a message box with a question mark icon with the OK and Cancel buttons.

    :param title: The title of the message box
    :param message: The content of the message displayed in the message box
    :return: If the user clicks the OK button to return 'ok', clicks the Cancel button to return 'cancel', and returns None if there is an error
    """
    return __msg__.showyescancel(title=title, message=message)


def askyesno(title, message):
    """
    Displays a message box with a question mark icon, including Yes and No buttons.

    :param title: The title of the message box
    :param message: The content of the message displayed in the message box
    :return: If the user clicks the Yes button to return 'yes', clicks the No button to return 'no', and returns None if there is an error
    """
    return __msg__.showyesno(title=title, message=message)


def askquestion(title, message):
    """
    Displays a yes/no question prompt with a question mark icon.

    :param title: The title of the message box
    :param message: The content of the message displayed in the message box
    :return: If the user clicks the Yes button to return 'yes', clicks the No button to return 'no', and returns None if there is an error
    """
    return __msg__.askquestion(title, message)

if __name__ == "__main__":
    print(askquestion("Test","Just a test message."),  )
    print(askcancelretry("Test","Just a test message."),  )
    print(askyescancel("Test","Just a test message."),  )
    print(askyesno("Test","Just a test message."),  )
    print(showerror("Test","Just a test message."),  )
    print(showinfo("Test","Just a test message."),  )
    print(showwarning("Test","Just a test message."),  )