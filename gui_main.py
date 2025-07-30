import tkinter as tk
import sys, os, subprocess, threading, queue, runpy

# ------------------------------------------------------------------
# 全局变量
# ------------------------------------------------------------------
# 保存当前 QtStyleConsole 实例，供 patched_run 访问
console_instance = None

# ------------------------------------------------------------------
# 补丁：拦截 subprocess.run 以实现「cls」清屏
# ------------------------------------------------------------------
# 备份原始函数
orig_run = subprocess.run


def patched_run(*args, **kwargs):
    """
    拦截对 subprocess.run 的调用。
    当检测到 cls / clear 命令时，直接调用本地清屏方法，
    否则保持原有行为。
    """
    # 将命令列表/元组转为统一字符串
    cmd = " ".join(map(str, args[0])) if isinstance(args[0], (list, tuple)) else str(args[0])

    # 若命令包含 cls，则本地清屏并返回空结果
    if "cls" in cmd.lower():
        console_instance.clear_screen()
        return orig_run("echo off", shell=True, capture_output=True)

    # 其余情况走原始调用
    return orig_run(*args, **kwargs)


# 全局打补丁
subprocess.run = patched_run


# ------------------------------------------------------------------
# 主窗口：Qt 风格终端
# ------------------------------------------------------------------
class QtStyleConsole(tk.Tk):
    """
    一个极简的「终端」窗口：
      - 接管 sys.stdin / stdout / stderr
      - 通过 Text 显示输出，Entry 收集输入
      - 支持内部脚本 main.py 的运行
    """

    def __init__(self):
        super().__init__()

        # 窗口外观
        self.title("QX Console")
        self.geometry("700x500")
        # 设置窗口图标
        try:
            self.iconbitmap("icon.ico")
        except tk.TclError:
            pass  # 使用默认Tk图标
        self.configure(bg="#111111")

        # 输出区域
        self.text = tk.Text(
            self,
            wrap="word",
            state="disabled",
            bg="#111111",
            fg="#d4d4d4",
            insertbackground="#ffffff",
            font=("Consolas", 11),
            bd=0,
            highlightthickness=0
        )
        # 配置ANSI颜色支持
        self._setup_ansi_colors()
        self.text.pack(fill="both", expand=True, padx=10, pady=10)

        # 输入单行
        self.entry = tk.Entry(
            self,
            font=('Consolas', 11),
            bg='#1a1a1a',
            fg='#d4d4d4',
            insertbackground='#ffffff',
            relief='flat',
            highlightthickness=0
        )
        # 添加占位符功能
        self.placeholder_text = 'Enter...'
        self.entry.insert(0, self.placeholder_text)
        self.entry.config(fg='#888888')
        self.entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.entry.bind('<FocusOut>', self.on_entry_focus_out)
        self.entry.pack(fill='x', padx=10, pady=(0, 10))
        self.entry.bind('<Return>', lambda e: self.send_input())

        # 输入队列与标志位
        self._input_q = queue.Queue()
        self._waiting = False

        # 重定向标准流
        for s in ("stdin", "stdout", "stderr"):
            setattr(self, f"_bak_{s}", getattr(sys, s))
            setattr(sys, s, self)

        # 后台线程：运行 main.py
        threading.Thread(target=self.run_main, daemon=True).start()

    # ------------------------------
    # 标准流接口
    # ------------------------------
    def write(self, txt):
        """处理带ANSI颜色代码的输出"""
        if not txt:
            return
        
        self.text.configure(state="normal")
        
        # 处理ANSI转义序列
        ansi_parts = self._process_ansi_escape(txt)
        
        # 插入带标签的文本
        for text, tags in ansi_parts:
            self.text.insert("end", text, tags)
        
        self.text.configure(state="disabled")
        self.text.see("end")

    def readline(self):
        """stdin 读取回调（阻塞）"""
        self._waiting = True
        line = self._input_q.get()
        self._waiting = False
        return line + "\n"

    # ------------------------------
    # 交互逻辑
    # ------------------------------
    def clear_screen(self):
        """清空输出区域"""
        self.text.configure(state="normal")
        self.text.delete(1.0, "end")
        self.text.configure(state="disabled")

    def send_input(self):
        """处理用户回车输入"""
        line = self.entry.get()
        if line == self.placeholder_text:
            return
        if not line:
            line = "\n"
        self.entry.delete(0, "end")
        self.write(line)  # 将输入回显到窗口

        # 若后台脚本正在等待输入
        if self._waiting:
            self._input_q.put(line)
            return

        # 否则视为 shell 命令
        cmd = line.rstrip()
        if cmd.lower() in {"cls", "clear"}:
            self.clear_screen()
        else:
            # 新开线程执行系统命令
            threading.Thread(
                target=lambda: subprocess.run(
                    cmd if cmd.lower() != "cls" else "powershell -Command Clear-Host",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                ).stdout and None,  # 丢弃返回值，仅触发输出
                daemon=True
            ).start()

    # ------------------------------
    # 脚本入口
    # ------------------------------
    def run_main(self):
        """在后台线程里运行 main.py"""
        try:
            runpy.run_path("main.py", run_name="__main__")
        except Exception as e:
            print("main.py 运行错误:", e)

    # ------------------------------
    # 退出恢复
    # ------------------------------
    def destroy(self):
        """恢复标准流并关闭窗口"""
        for s in ("stdin", "stdout", "stderr"):
            setattr(sys, s, getattr(self, f"_bak_{s}"))
        super().destroy()

    def _setup_ansi_colors(self):
        """初始化ANSI颜色标签"""
        # ANSI颜色代码到Tkinter颜色的映射
        self.ansi_color_map = {
            30: "#000000",  # 黑色
            31: "#ff0000",  # 红色
            32: "#00ff00",  # 绿色
            33: "#ffff00",  # 黄色
            34: "#0000ff",  # 蓝色
            35: "#ff00ff",  # 紫色
            36: "#00ffff",  # 青色
            37: "#d4d4d4",  # 白色
            90: "#808080",  # 亮黑
            91: "#ff8080",  # 亮红
            92: "#80ff80",  # 亮绿
            93: "#ffff80",  # 亮黄
            94: "#8080ff",  # 亮蓝
            95: "#ff80ff",  # 亮紫
            96: "#80ffff",  # 亮青
            97: "#ffffff"   # 亮白
        }
        
        # 创建默认标签
        self.text.tag_configure("default", foreground="#d4d4d4")
        
        # 为每种颜色创建标签
        for code, color in self.ansi_color_map.items():
            self.text.tag_configure(f"ansi_{code}", foreground=color)

    def _process_ansi_escape(self, text):
        """处理ANSI转义序列并返回(文本, 标签)元组列表"""
        import re
        ansi_escape = re.compile(r'\033\[([0-9;]+)m')
        parts = []
        current_tags = ["default"]
        last_pos = 0
        
        for match in ansi_escape.finditer(text):
            # 添加匹配前的文本
            if match.start() > last_pos:
                parts.append((text[last_pos:match.start()], current_tags.copy()))
            
            # 处理转义码
            codes = match.group(1).split(';')
            for code in codes:
                try:
                    code_int = int(code)
                    if code_int == 0:  # 重置所有属性
                        current_tags = ["default"]
                    elif 30 <= code_int <= 37 or 90 <= code_int <= 97:  # 前景色
                        current_tags = [f"ansi_{code_int}"]
                except ValueError:
                    pass
            
            last_pos = match.end()
        
        # 添加剩余文本
        if last_pos < len(text):
            parts.append((text[last_pos:], current_tags.copy()))
        
        return parts

    def on_entry_focus_in(self, event):
        if self.entry.get() == self.placeholder_text:
            self.entry.delete(0, tk.END)
            self.entry.config(fg='#d4d4d4')

    def on_entry_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder_text)
            self.entry.config(fg='#888888')


# ------------------------------------------------------------------
# 程序入口
# ------------------------------------------------------------------
if __name__ == "__main__":
    console_instance = QtStyleConsole()
    console_instance.mainloop()