# src/sam2_annotator/main.py

import os
import sys
import torch
import traceback
import urllib.request
from appdirs import user_cache_dir
from importlib import resources
import tkinter as tk
from tkinter import ttk, filedialog, messagebox



# 关键函数1: 安全地获取包内资源（如配置文件）的路径
def get_config_path(config_filename="sam2_hiera_l.yaml"):
    """使用 importlib.resources 安全地获取包内配置文件的路径"""
    try:
        # For Python 3.9+
        # 这会返回一个可以像 pathlib.Path 一样使用的对象
        return resources.files('sam2_annotator').joinpath('configs').joinpath(config_filename)
    except (ImportError, AttributeError):
        # Fallback for Python 3.8
        with resources.path('sam2_annotator.configs', config_filename) as p:
            return p


# 关键函数2: 自动下载并缓存模型文件
def get_model_weights_path(model_name="sam2_hiera_large.pt"):
    """检查模型是否存在于用户缓存中，如果不存在则下载，并返回其路径。"""
    # 模型文件的直接下载链接
    MODEL_URL = "https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_large.pt"

    # 使用 appdirs 确定一个适合当前操作系统的用户缓存目录
    cache_directory = user_cache_dir("sam2_annotator", "EEBD")
    os.makedirs(cache_directory, exist_ok=True)
    model_path = os.path.join(cache_directory, model_name)

    if not os.path.exists(model_path):
        print(f"模型文件未找到。正在从以下链接下载 '{model_name}'...")
        print(f"URL: {MODEL_URL}")
        print(f"将保存到: {model_path}")
        try:
            # 创建一个临时的Tkinter窗口以显示下载进度
            progress_window = tk.Tk()
            progress_window.title("下载中")
            progress_window.geometry("400x100")

            progress_label = tk.Label(progress_window, text=f"正在下载 {model_name}...", pady=10)
            progress_label.pack()

            progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate")
            progress_bar.pack(pady=10)

            progress_text = tk.StringVar()
            progress_status_label = tk.Label(progress_window, textvariable=progress_text)
            progress_status_label.pack()

            progress_window.update()

            with urllib.request.urlopen(MODEL_URL) as response, open(model_path, 'wb') as out_file:
                total_length = response.getheader('content-length')
                if total_length:
                    total_length = int(total_length)
                    dl = 0
                    block_sz = 8192
                    while True:
                        buffer = response.read(block_sz)
                        if not buffer: break
                        dl += len(buffer)
                        out_file.write(buffer)

                        # 更新进度条
                        progress = int(100 * dl / total_length)
                        progress_bar['value'] = progress
                        mb_downloaded = dl / 1024 / 1024
                        mb_total = total_length / 1024 / 1024
                        progress_text.set(f"{mb_downloaded:.2f}MB / {mb_total:.2f}MB")
                        progress_window.update_idletasks()
                else:
                    out_file.write(response.read())

            progress_window.destroy()
            print("\n模型下载完成！")

        except Exception as e:
            print(f"\n下载模型失败: {e}")
            if 'progress_window' in locals() and progress_window.winfo_exists():
                progress_window.destroy()
            messagebox.showerror("下载失败", f"无法下载模型: {e}")
            if os.path.exists(model_path): os.remove(model_path)
            sys.exit(1)
    else:
        print(f"在缓存中找到模型: {model_path}")
    return model_path


# 程序的总入口点
def start():
    """此函数将作为命令行的入口点被调用"""
    print("--- EEBD-GESAM2 交互式标注工具 ---")

    # 确保使用CUDA（如果可用）
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"检测到设备: {device}")
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    try:
        # 从我们的包中相对导入主应用类
        from .app import InteractiveSAM2Annotator

        # 动态获取模型和配置的路径
        model_path = get_model_weights_path()
        config_path = str(get_config_path())  # 转换为字符串路径

        # 创建并运行应用实例
        # image_dir 默认为 None, 用户需要通过 "加载图像" 按钮选择目录
        annotator = InteractiveSAM2Annotator(
            model_path=model_path,
            config_path=config_path,
            device=device,
            output_dir="./annotations_sam2_tool",
            image_dir=None
        )
        print("UI界面已启动。请使用“加载图像”按钮开始。")
        annotator.mainloop()

    except Exception as e:
        # 创建一个临时的Tkinter root窗口来显示错误对话框
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("程序启动失败", f"发生致命错误: {e}\n\n详细信息请查看控制台输出。")
        root.destroy()

        print(f"程序启动失败: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    start()
