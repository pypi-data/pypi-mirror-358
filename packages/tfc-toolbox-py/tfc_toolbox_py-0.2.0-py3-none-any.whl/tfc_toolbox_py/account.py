"""
Account

This module is some tools related to the account.

Such as input password, change password and so on.
"""

import sys
import hashlib
if sys.platform.startswith('linux'):
    import tty
    import termios
elif sys.platform.startswith('win'):
    import msvcrt


def _getch_linux():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def _getpass_linux(mask_char):
    password = ""
    while True:
        ch = _getch_linux()
        if ch == "\r" or ch == "\n":
            return password
        elif ch == "\b" or ord(ch) == 127:
            if len(password) > 0:
                sys.stdout.write("\b \b")
                password = password[:-1]
        else:
            if mask_char is not None:
                sys.stdout.write(mask_char)
            password += ch


def _pwd_input_win():
    chars = []
    while True:
        try:
            new_char = msvcrt.getch().decode(encoding="utf-8")
        except:
            # 很可能不是在cmd命令行下运行，密码输入将不能隐藏
            return input("你很可能不是在cmd命令行下运行，密码输入将不能隐藏:")
        if new_char in '\r\n':  # 如果是换行，则输入结束
            break
        elif new_char == '\b':  # 如果是退格，则删除密码末尾一位并且删除一个星号
            if chars:
                del chars[-1]
                msvcrt.putch('\b'.encode(encoding='utf-8'))  # 光标回退一格
                msvcrt.putch(' '.encode(encoding='utf-8'))  # 输出一个空格覆盖原来的星号
                msvcrt.putch('\b'.encode(encoding='utf-8'))  # 光标回退一格准备接受新的输入
        else:
            chars.append(new_char)
            msvcrt.putch('*'.encode(encoding='utf-8'))  # 显示为星号
    return ''.join(chars)


def _password_hash(password):
    md = hashlib.md5(password.encode())  # 创建md5对象
    md5pwd = md.hexdigest()  # md5加密
    return md5pwd



def input_password():
    """
    Input password function
    You can input a password.
    """
    password = ""
    if sys.platform.startswith('linux'):
        password = _getpass_linux("*")
    elif sys.platform.startswith('win'):
        password = _pwd_input_win()
    return password



def change_password(password_md5):
    """
    Change password function
    You can input a password and get a hash code.
    return -1: password input error
    return hash code: change password successfully
    return 0: password has not been changed
    """
    if password_md5:
        print("请输入原密码：", end="")
        old_password = input_password()
        # 获取旧密码md5值
        old_password_md5 = _password_hash(old_password)
        if old_password_md5 == password_md5:
            print("密码正确")
            while 1:
                print("请输入新密码（输入0退出）：", end="")
                new_password = input_password()
                if new_password != "0":
                    # 新密码加密
                    new_password_md5 = _password_hash(new_password)
                    if new_password_md5 == password_md5:
                        print("密码与原密码相同，请重新输入")
                    else:
                        return new_password_md5
                elif new_password == "0":
                    return 0
        else:
            print("密码输入错误")
            return -1
    else:
        print("未设置密码")
        print("请输入新密码：", end="")
        new_password = input_password()
        password_md5 = _password_hash(new_password)
        return password_md5
