"""
Message
~~~~~~~~
The module provides a series of functions for displaying different types of message boxes,
It includes information prompts, warning boxes, error boxes, and various problem prompts with buttons such as confirmation and cancel.
"""
#Copyright (c) 2025, <363766687@qq.com>
#Author: Huang Yiyi

from htyy._infront._htyy_d._message_d import (
    showerror, showinfo, showwarning, askcancelretry,
    askyescancel, askquestion, askyesno
)

if __name__ == "__main__":
    print(askquestion("Test","Just a test message."))
    print(askcancelretry("Test","Just a test message."))
    print(askyescancel("Test","Just a test message."))
    print(askyesno("Test","Just a test message."))
    print(showerror("Test","Just a test message."))
    print(showinfo("Test","Just a test message."))
    print(showwarning("Test","Just a test message."))