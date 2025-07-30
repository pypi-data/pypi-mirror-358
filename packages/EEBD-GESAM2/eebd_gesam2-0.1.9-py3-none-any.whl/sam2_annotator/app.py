# src/sam2_annotator/app.py
import sys
import os
import json
import glob
import torch
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import time
import traceback
import colorsys

# --- 核心的 SAM2 依赖 ---
try:
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor

    print("成功导入SAM2组件")
except ImportError as e:
    print(f"导入SAM2组件失败: {e}", file=sys.stderr)
    print("错误：无法导入 'sam2' 库。请确保您已按照README.md中的指示安装了它，例如：", file=sys.stderr)
    print("pip install git+https://github.com/facebookresearch/segment-anything-2.git", file=sys.stderr)
    sys.exit(1)

# 默认标注标签
DEFAULT_LABELS = ["_background_", "Cropland", "Forest", "Grass", "Shrub", "Wetland", "Water", "Solar panel",
                  "Impervious surface", "Bareland", "Ice/snow", "desert"]


class InteractiveSAM2Annotator(tk.Tk):
    def __init__(self, model_path, config_path=None, device=None, output_dir="./annotations", image_dir=None):
        """
        初始化交互式 SAM2 标注器应用。

        Args:
            model_path (str): SAM2 模型检查点的路径。
            config_path (str, optional): SAM2 模型配置文件的路径。如果为 None，将根据 model_path 使用默认配置。
            device (torch.device, optional): 运行模型的设备（例如 'cuda', 'cpu'）。默认为 'cuda'（如果可用），否则为 'cpu'。
            output_dir (str, optional): 保存标注的目录。默认为 "./annotations"。
            image_dir (str, optional): 从中加载图像的初始目录。默认为 None。
        """
        super().__init__()
        # 确定模型推理的设备
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu") if device is None else device
        print(f"使用设备: {self.device}")

        # 设置标注的输出目录
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.last_session_file = os.path.join(self.output_dir, "last_session_state.json")

        self.dataset_dir = os.path.join(output_dir, "datasets")
        self.jpgs_path = os.path.join(self.dataset_dir, "JPEGImages")
        self.jsons_path = os.path.join(self.dataset_dir, "before")  # JSON 标注
        self.pngs_path = os.path.join(self.dataset_dir, "SegmentationClass")  # 分割掩码
        os.makedirs(self.jpgs_path, exist_ok=True)
        os.makedirs(self.jsons_path, exist_ok=True)
        os.makedirs(self.pngs_path, exist_ok=True)

        # 加载 SAM2 模型 (模型本身保持不变)
        self.model = None  # 预声明为 None
        self.load_model(model_path, config_path)  # 将模型加载到 self.model

        # SAM 预测器实例 (关键修改：此处不再初始化 SAM2ImagePredictor)
        self.predictor = None  # 将 SAM 预测器实例初始化为 None，将在 load_current_image 中动态创建

        # --- 状态变量 ---
        # 图像相关状态
        self.image_paths = []
        self.current_image_index = -1
        self.image_np = None  # 当前图像的 NumPy 数组
        self.image_name = ""
        self.image_list_loaded = False
        self.display_img = None  # 准备用于显示（带叠加层）的图像
        self.current_loaded_image_dir = None  # 上次加载图像的目录

        # SAM/预测相关状态
        self.points = []  # SAM 的交互点 (y, x) 格式
        self.labels = []  # 交互点的标签 (1=正向, 0=负向)
        self.masks = None  # SAM 预测的掩码
        self.scores = None  # 预测掩码的分数
        self.current_mask_idx = 0  # 当前显示的预测掩码的索引
        self.selected_mask = None  # 用户选择的掩码 (来自 SAM 或多边形)
        self.current_label = DEFAULT_LABELS[0]  # 当前用于标注的标签
        self.available_labels = DEFAULT_LABELS.copy()  # 所有可用标签

        # 多边形模式相关状态
        self.is_polygon_mode = False
        self.polygon_points = []  # 自定义多边形标注的点 (x, y) 格式
        self.temp_polygon_line = None  # 用于多边形绘制的临时线
        self.polygon_lines = []  # 构成闭合多边形的线
        self.closed_polygon = False  # 如果多边形已闭合则为 True

        # 标注管理状态
        self.annotation_complete = False  # 当前图像标注完成的标志
        self.is_modified = False  # 如果当前图像的标注被修改则为 True
        self.annotation_masks = {}  # 存储已确认掩码的字典: {label: [mask1, mask2, ...]}
        self.history = []  # 存储状态用于撤销功能
        self.previous_annotations = {}  # 缓存之前访问过的图像的标注

        # 掩码颜色生成
        self.colors = self.generate_colors(len(DEFAULT_LABELS))

        # 缩放和平移状态
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.pan_step = 100

        # 编辑模式相关状态
        self.editable_regions = []  # 存储可编辑区域的信息: {'mask', 'label', 'bbox'}
        self.hovered_region_index = None  # 当前悬停区域的索引
        self.selected_region_index = None  # 当前选中区域的索引

        # 初始化用户界面
        self.init_ui()

        # 如果提供了目录，则加载初始图像
        if image_dir and os.path.exists(image_dir):
            self._initial_image_load(image_dir)
        else:
            self.status_var.set("请加载图像或提供有效的初始图像目录")

        # 处理窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _initial_image_load(self, folder_path):
        """如果提供了目录，则在启动时加载图像。"""
        self.current_loaded_image_dir = os.path.abspath(folder_path)  # 存储绝对路径
        start_idx = self._get_start_index_for_dir(self.current_loaded_image_dir)
        self._execute_load_procedure(self.current_loaded_image_dir, start_idx)

    def handle_load_button_press_ui(self):
        """处理来自UI的“加载图像”按钮点击。"""
        folder = filedialog.askdirectory(title="选择图像文件夹")
        if folder:
            abs_folder = os.path.abspath(folder)
            self.current_loaded_image_dir = abs_folder  # 更新上下文
            start_idx = self._get_start_index_for_dir(abs_folder)  # 检查此新/选定文件夹的会话
            self._execute_load_procedure(abs_folder, start_idx)
        elif not self.image_list_loaded:  # 仅在未加载任何内容时更新状态
            self.status_var.set("请加载图像")

    def _execute_load_procedure(self, folder_path, requested_start_index):
        """
        从给定文件夹加载图像并跳转到特定索引的核心逻辑。

        Args:
            folder_path (str): 包含图像的目录。
            requested_start_index (int): 开始的图像索引。
        """
        supported_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff']
        self.image_paths = []
        for ext in supported_extensions:
            self.image_paths.extend(glob.glob(os.path.join(folder_path, ext)))
            self.image_paths.extend(glob.glob(os.path.join(folder_path, ext.upper())))
        self.image_paths.sort()  # 确保一致的顺序

        if not self.image_paths:
            messagebox.showwarning("警告", f"在目录 '{folder_path}' 中未找到支持的图像文件")
            self.image_list_loaded = False
            self.current_image_index = -1
            self.image_name = ""
            self.image_canvas.delete("all")
            self.status_var.set(f"在 '{folder_path}' 中未找到图像。请加载其他图像目录。")
            self.title("SAM2 交互式图像标注工具 - 无图像")
            self.image_selector['values'] = []
            self.image_selection_var.set("")
            return False

        # 填充图像选择器组合框
        image_basenames = [os.path.basename(p) for p in self.image_paths]
        self.image_selector['values'] = image_basenames

        self.image_list_loaded = True
        self.current_loaded_image_dir = folder_path  # 确认成功加载

        # 设置当前图像索引
        if 0 <= requested_start_index < len(self.image_paths):
            self.current_image_index = requested_start_index
        else:
            self.current_image_index = -1  # 没有有效的起始索引，将转到下一张图像

        # 加载图像 (请求的图像或第一个可用的图像)
        if self.current_image_index == -1:
            self.next_image()
        else:
            self.load_current_image()
            self._save_last_session_info()

        return True

    def _get_start_index_for_dir(self, target_dir):
        """
        检查会话文件中是否有匹配的目录，并返回其最后一个图像索引。

        Args:
            target_dir (str): 要在会话数据中检查的目录路径。

        Returns:
            int: 目标目录的最后一个保存的图像索引，如果未找到则为 -1。
        """
        target_dir_abs = os.path.abspath(target_dir)
        if os.path.exists(self.last_session_file):
            try:
                with open(self.last_session_file, 'r') as f:
                    data = json.load(f)
                saved_dir_abs = os.path.abspath(data.get("last_image_dir", ""))
                if saved_dir_abs == target_dir_abs:
                    last_idx = data.get('last_image_index', -1)
                    print(f"加载上次会话信息: 目录 '{target_dir_abs}', 索引 {last_idx}")
                    return last_idx
            except Exception as e:
                print(f"加载上次会话文件 '{self.last_session_file}' 失败: {e}")
        print(f"未找到目录 '{target_dir_abs}' 的上次会话信息。")
        return -1

    def _save_last_session_info(self):
        """保存当前图像索引和目录以供将来会话使用。"""
        if self.image_list_loaded and self.current_image_index >= 0 and self.current_loaded_image_dir:
            data = {
                "last_image_dir": os.path.abspath(self.current_loaded_image_dir),
                "last_image_index": self.current_image_index
            }
            try:
                with open(self.last_session_file, 'w') as f:
                    json.dump(data, f, indent=4)
            except Exception as e:
                print(f"保存会话文件 '{self.last_session_file}' 失败: {e}")

    def on_closing(self):
        """处理应用程序关闭事件，如果存在待定更改，则提示保存。"""
        if self.is_modified and self.image_list_loaded:
            if messagebox.askyesno("退出", "有未保存的更改，确定要退出吗？"):
                self._save_last_session_info()
                self.destroy()
            else:
                return  # 如果用户取消，则阻止关闭
        else:
            self._save_last_session_info()
            self.destroy()

    def generate_colors(self, n):
        """生成一个不同RGB颜色的列表。"""
        colors = []
        for i in range(n):
            hue = i / n
            saturation = 0.9
            value = 0.9
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            rgb = tuple(int(255 * x) for x in rgb)
            colors.append(rgb)
        return colors

    def init_ui(self):
        """初始化主图形用户界面元素。"""
        self.title("SAM2 交互式图像标注工具")
        self.geometry("1200x800")

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 图像显示区域
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.image_canvas = tk.Canvas(image_frame, bg="gray")
        self.image_canvas.pack(fill=tk.BOTH, expand=True)

        # 控制面板
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # 加载图像按钮
        self.load_button = ttk.Button(control_frame, text="加载图像", command=self.handle_load_button_press_ui)
        self.load_button.pack(fill=tk.X, pady=2)

        # 图像选择组合框
        image_selection_frame = ttk.LabelFrame(control_frame, text="快速跳转到图像")
        image_selection_frame.pack(fill=tk.X, pady=5)
        self.image_selection_var = tk.StringVar()
        self.image_selector = ttk.Combobox(image_selection_frame, textvariable=self.image_selection_var,
                                           state="readonly")
        self.image_selector.pack(fill=tk.X, expand=True, padx=5, pady=2)
        self.image_selector.bind("<<ComboboxSelected>>", self.on_image_select)

        # 缩放控件
        zoom_frame = ttk.Frame(control_frame)
        zoom_frame.pack(fill=tk.X, pady=2)
        ttk.Button(zoom_frame, text="放大", command=lambda: self.zoom(1.2)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(zoom_frame, text="缩小", command=lambda: self.zoom(0.8333)).pack(side=tk.LEFT, fill=tk.X,
                                                                                    expand=True)

        # 平移控件
        pan_frame = ttk.Frame(control_frame)
        pan_frame.pack(fill=tk.X, pady=2)
        pan_frame.columnconfigure((0, 1), weight=1)
        ttk.Button(pan_frame, text="向左移动", command=self.pan_left).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(pan_frame, text="向右移动", command=self.pan_right).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(pan_frame, text="向上移动", command=self.pan_up).grid(row=1, column=0, sticky="ew", padx=2)
        ttk.Button(pan_frame, text="向下移动", command=self.pan_down).grid(row=1, column=1, sticky="ew", padx=2)

        # 模式选择 (SAM, 多边形, 编辑)
        self.mode_frame = ttk.LabelFrame(control_frame, text="选择操作模式")
        self.mode_frame.pack(fill=tk.X, pady=2)
        self.mode_var = tk.StringVar(value="SAM标注")
        self.sam_mode_radio = ttk.Radiobutton(self.mode_frame, text="SAM标注", variable=self.mode_var, value="SAM标注",
                                              command=self.change_to_sam_mode)
        self.sam_mode_radio.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.polygon_mode_radio = ttk.Radiobutton(self.mode_frame, text="多边形", variable=self.mode_var,
                                                  value="多边形", command=self.change_to_polygon_mode)
        self.polygon_mode_radio.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.edit_mode_radio = ttk.Radiobutton(self.mode_frame, text="编辑标签", variable=self.mode_var,
                                               value="编辑标签", command=self.change_to_edit_mode)
        self.edit_mode_radio.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # SAM 标注工具框架
        self.sam_frame = ttk.LabelFrame(control_frame, text="SAM标注工具")
        self.sam_frame.pack(fill=tk.X, pady=2)
        self.predict_button = ttk.Button(self.sam_frame, text="预测掩码", command=self.predict_masks)
        self.predict_button.pack(fill=tk.X, pady=2)
        self.select_button = ttk.Button(self.sam_frame, text="选择掩码", command=self.select_mask)
        self.select_button.pack(fill=tk.X, pady=2)
        self.next_mask_button = ttk.Button(self.sam_frame, text="下一个掩码", command=self.next_mask)
        self.next_mask_button.pack(fill=tk.X, pady=2)

        # 多边形标注工具框架
        self.polygon_frame = ttk.LabelFrame(control_frame, text="多边形标注工具")
        self.close_polygon_button = ttk.Button(self.polygon_frame, text="闭合多边形", command=self.close_polygon)
        self.close_polygon_button.pack(fill=tk.X, pady=2)
        self.clear_polygon_button = ttk.Button(self.polygon_frame, text="清除多边形", command=self.clear_polygon)
        self.clear_polygon_button.pack(fill=tk.X, pady=2)

        # 编辑标签工具框架
        self.edit_frame = ttk.LabelFrame(control_frame, text="编辑工具")
        self.update_label_button = ttk.Button(self.edit_frame, text="更新标签", command=self.update_selected_label,
                                              state=tk.DISABLED)  # 在选择区域之前禁用
        self.update_label_button.pack(fill=tk.X, pady=2)

        # 撤销和重置按钮
        self.undo_button = ttk.Button(control_frame, text="撤销", command=self.undo)
        self.undo_button.pack(fill=tk.X, pady=2)
        self.reset_button = ttk.Button(control_frame, text="重置", command=self.reset_annotation)
        self.reset_button.pack(fill=tk.X, pady=2)

        # 当前标注的标签选择
        label_frame = ttk.Frame(control_frame)
        label_frame.pack(fill=tk.X, pady=2)
        ttk.Label(label_frame, text="标签:").pack(side=tk.LEFT)
        self.label_var = tk.StringVar(value=self.current_label)
        self.label_combo = ttk.Combobox(label_frame, textvariable=self.label_var, values=self.available_labels)
        self.label_combo.bind("<<ComboboxSelected>>", self.on_label_change)
        self.label_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 确认和保存按钮
        self.confirm_button = ttk.Button(control_frame, text="确认并锁定此区域", command=self.confirm_label)
        self.confirm_button.pack(fill=tk.X, pady=2)
        self.complete_button = ttk.Button(control_frame, text="完成并保存", command=self.complete_annotation)
        self.complete_button.pack(fill=tk.X, pady=2)

        # 导航按钮 (上一张/下一张图像)
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(fill=tk.X, pady=2)
        self.prev_button = ttk.Button(nav_frame, text="上一张", command=self.prev_image)
        self.prev_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.next_button = ttk.Button(nav_frame, text="下一张", command=self.next_image)
        self.next_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 不同模式的帮助文本
        self.sam_help_text = "SAM模式: 左键正向点, 右键负向点, 中键擦除。"
        self.polygon_help_text = "多边形模式: 左键添加顶点, 右键删除顶点。"
        self.edit_help_text = "编辑模式: 单击已标注区域可选中, 然后在上方选择新标签并点击'更新标签'按钮进行修改。"
        self.help_var = tk.StringVar(value=self.sam_help_text)
        self.help_label = ttk.Label(control_frame, textvariable=self.help_var, wraplength=280, justify=tk.LEFT)
        self.help_label.pack(fill=tk.X, pady=10, padx=5)

        # 状态栏
        self.status_var = tk.StringVar(value="请加载图像")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 设置默认模式为 SAM
        self.change_to_sam_mode()

    def on_image_select(self, event=None):
        """
        处理来自组合框的图像选择。
        如果当前图像有未保存的更改，则提示保存。
        """
        selected_image_name = self.image_selection_var.get()
        if not selected_image_name or not self.image_list_loaded or selected_image_name == self.image_name:
            return  # 如果没有选择、没有图像或已经在所选图像上，则不执行任何操作

        try:
            # 查找所选图像的索引
            target_index = [os.path.basename(p) for p in self.image_paths].index(selected_image_name)
        except ValueError:
            messagebox.showerror("错误", f"在图像列表中未找到 '{selected_image_name}'")
            self.image_selection_var.set(self.image_name)  # 将组合框恢复到当前图像
            return

        if self.is_modified:
            # 如果有未保存的更改，则提示保存
            if not messagebox.askyesno("提示", "当前图像已修改但未保存，是否继续？"):
                self.image_selection_var.set(self.image_name)  # 将组合框恢复到当前图像
                return

        # 在加载新图像之前缓存当前标注
        if self.annotation_masks and self.image_name:
            self.previous_annotations[self.image_name] = self.annotation_masks.copy()

        # 重置缩放/平移并加载新图像
        self.current_image_index = target_index
        self.zoom_factor = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.load_current_image()
        self._save_last_session_info()  # 加载后保存会话信息

    def bind_sam_events(self):
        """绑定与 SAM 标注模式相关的画布事件。"""
        self.image_canvas.unbind("<Button-1>")  # 左键单击
        self.image_canvas.unbind("<Button-3>")  # 右键单击
        self.image_canvas.unbind("<Button-2>")  # 中键单击
        self.image_canvas.unbind("<Motion>")  # 鼠标移动
        self.image_canvas.bind("<Button-1>", self.on_left_click)
        self.image_canvas.bind("<Button-3>", self.on_right_click)
        self.image_canvas.bind("<Button-2>", self.on_middle_click)
        self.image_canvas.bind("<Configure>", self.on_canvas_resize)

    def bind_polygon_events(self):
        """绑定与多边形标注模式相关的画布事件。"""
        self.image_canvas.unbind("<Button-1>")
        self.image_canvas.unbind("<Button-3>")
        self.image_canvas.unbind("<Button-2>")
        self.image_canvas.unbind("<Motion>")
        self.image_canvas.bind("<Button-1>", self.on_polygon_left_click)
        self.image_canvas.bind("<Button-3>", self.on_polygon_right_click)
        self.image_canvas.bind("<Motion>", self.on_polygon_mouse_move)
        self.image_canvas.bind("<Configure>", self.on_canvas_resize)

    def bind_edit_events(self):
        """绑定与编辑标签模式相关的画布事件。"""
        self.image_canvas.unbind("<Button-1>")
        self.image_canvas.unbind("<Button-3>")
        self.image_canvas.unbind("<Button-2>")
        self.image_canvas.unbind("<Motion>")
        self.image_canvas.bind("<Motion>", self.on_edit_mode_motion)
        self.image_canvas.bind("<Button-1>", self.on_edit_mode_click)
        self.image_canvas.bind("<Configure>", self.on_canvas_resize)

    def zoom(self, scale):
        """放大或缩小显示的图像。"""
        new_zoom = self.zoom_factor * scale
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
        self.zoom_factor = new_zoom
        self.status_var.set(
            f"当前图像: {self.image_name} | 缩放: {self.zoom_factor:.2f}x | 平移: ({self.pan_offset_x}, {self.pan_offset_y})")
        if self.image_np is not None:
            self.display_image(self.image_np)

    def pan_left(self):
        """向左平移图像。"""
        if self.image_np is None: return
        self.pan_offset_x -= self.pan_step
        self.status_var.set(
            f"当前图像: {self.image_name} | 缩放: {self.zoom_factor:.2f}x | 平移: ({self.pan_offset_x}, {self.pan_offset_y})")
        self.display_image(self.image_np)

    def pan_right(self):
        """向右平移图像。"""
        if self.image_np is None: return
        self.pan_offset_x += self.pan_step
        self.status_var.set(
            f"当前图像: {self.image_name} | 缩放: {self.zoom_factor:.2f}x | 平移: ({self.pan_offset_x}, {self.pan_offset_y})")
        self.display_image(self.image_np)

    def pan_up(self):
        """向上平移图像。"""
        if self.image_np is None: return
        self.pan_offset_y -= self.pan_step
        self.status_var.set(
            f"当前图像: {self.image_name} | 缩放: {self.zoom_factor:.2f}x | 平移: ({self.pan_offset_x}, {self.pan_offset_y})")
        self.display_image(self.image_np)

    def pan_down(self):
        """向下平移图像。"""
        if self.image_np is None: return
        self.pan_offset_y += self.pan_step
        self.status_var.set(
            f"当前图像: {self.image_name} | 缩放: {self.zoom_factor:.2f}x | 平移: ({self.pan_offset_x}, {self.pan_offset_y})")
        self.display_image(self.image_np)

    def change_to_sam_mode(self):
        """将应用程序切换到 SAM 标注模式。"""
        self.sam_frame.pack(fill=tk.X, pady=2, after=self.mode_frame)
        self.polygon_frame.pack_forget()  # 隐藏多边形控件
        self.edit_frame.pack_forget()  # 隐藏编辑控件
        self.confirm_button.config(state=tk.NORMAL)  # 为新标注启用确认按钮

        self.help_var.set(self.sam_help_text)
        self.bind_sam_events()
        self.clear_polygon()  # 清除任何待定的多边形绘制
        self._clear_selection_state()  # 如果之前在编辑模式，则清除选择
        if self.image_np is not None:
            self.display_image(self.image_np)

    def change_to_polygon_mode(self):
        """将应用程序切换到多边形标注模式。"""
        self.is_polygon_mode = True
        self.sam_frame.pack_forget()
        self.polygon_frame.pack(fill=tk.X, pady=2, after=self.mode_frame)
        self.edit_frame.pack_forget()
        self.confirm_button.config(state=tk.NORMAL)

        self.help_var.set(self.polygon_help_text)
        self.bind_polygon_events()
        self._clear_selection_state()
        if self.image_np is not None:
            self.display_image(self.image_np)

    def change_to_edit_mode(self):
        """将应用程序切换到编辑标签模式。"""
        self.sam_frame.pack_forget()
        self.polygon_frame.pack_forget()
        self.edit_frame.pack(fill=tk.X, pady=2, after=self.mode_frame)
        self.confirm_button.config(state=tk.DISABLED)  # 禁用确认按钮，因为此处不创建新标注

        self.help_var.set(self.edit_help_text)
        self.bind_edit_events()
        self.clear_polygon()  # 清除任何待定的多边形绘制
        self._prepare_for_editing()  # 为编辑现有标注准备数据
        if self.image_np is not None:
            self.display_image(self.image_np)

    def on_polygon_left_click(self, event):
        """在多边形模式下处理左键单击事件以添加点。"""
        if self.image_np is None or self.closed_polygon:
            return

        x, y = self._convert_canvas_to_image_coords(event.x, event.y)
        canvas_x = event.x
        canvas_y = event.y

        # 检查单击是否靠近第一个点以闭合多边形
        if len(self.polygon_points) > 2:
            first_x, first_y = self.polygon_points[0]
            canvas_first_x, canvas_first_y = self._convert_image_to_canvas_coords(first_x, first_y)
            if ((canvas_x - canvas_first_x) ** 2 + (canvas_y - canvas_first_y) ** 2) ** 0.5 < 10:
                self.close_polygon()
                return

        self.polygon_points.append((x, y))
        self.image_canvas.create_oval(
            canvas_x - 5, canvas_y - 5, canvas_x + 5, canvas_y + 5,
            fill="red", outline="white", tags="polygon_point"
        )

        if len(self.polygon_points) > 1:
            prev_x, prev_y = self._convert_image_to_canvas_coords(
                self.polygon_points[-2][0], self.polygon_points[-2][1]
            )
            line_id = self.image_canvas.create_line(
                prev_x, prev_y, canvas_x, canvas_y,
                fill="yellow", width=2, tags="polygon_line"
            )
            self.polygon_lines.append(line_id)

        self.status_var.set(f"多边形顶点 #{len(self.polygon_points)} 添加在 ({x}, {y})")

    def on_polygon_right_click(self, event):
        """在多边形模式下处理右键单击事件以移除最后一个点。"""
        if not self.polygon_points or self.closed_polygon:
            return

        self.polygon_points.pop()  # 移除最后一个点
        # 移除相应的画布元素
        points = self.image_canvas.find_withtag("polygon_point")
        if points:
            self.image_canvas.delete(points[-1])

        if self.polygon_lines:
            self.image_canvas.delete(self.polygon_lines.pop())

        # 如果还有点，则更新临时线
        if self.polygon_points and self.temp_polygon_line:
            prev_x, prev_y = self._convert_image_to_canvas_coords(
                self.polygon_points[-1][0], self.polygon_points[-1][1]
            )
            self.image_canvas.coords(
                self.temp_polygon_line,
                prev_x, prev_y, event.x, event.y
            )

        self.status_var.set(f"已删除多边形最后一个顶点，剩余 {len(self.polygon_points)} 个顶点")

    def on_polygon_mouse_move(self, event):
        """在多边形模式下处理鼠标移动以绘制到当前光标位置的临时线。"""
        if not self.polygon_points or self.closed_polygon:
            return

        last_x, last_y = self._convert_image_to_canvas_coords(
            self.polygon_points[-1][0], self.polygon_points[-1][1]
        )

        if self.temp_polygon_line:
            self.image_canvas.coords(
                self.temp_polygon_line,
                last_x, last_y, event.x, event.y
            )
        else:
            self.temp_polygon_line = self.image_canvas.create_line(
                last_x, last_y, event.x, event.y,
                fill="gray", dash=(4, 4), tags="temp_line"
            )

    def clear_polygon(self):
        """清除当前多边形绘制的所有点和线。"""
        self.polygon_points = []
        self.closed_polygon = False
        self.image_canvas.delete("polygon_point")
        self.image_canvas.delete("polygon_line")
        self.image_canvas.delete("temp_line")
        self.temp_polygon_line = None
        self.polygon_lines = []
        self.selected_mask = None  # 清除可能来自多边形模式的任何选定掩码
        self.status_var.set("已清除多边形")
        if self.image_np is not None:
            self.display_image(self.image_np)

    def close_polygon(self):
        """
        闭合多边形，将其转换为掩码，并强制不与现有标注重叠。
        """
        if len(self.polygon_points) < 3:
            messagebox.showwarning("警告", "多边形至少需要3个顶点")
            return

        self.save_to_history()  # 在闭合多边形之前保存当前状态
        self.closed_polygon = True

        # 在画布上绘制闭合线
        first_x, first_y = self._convert_image_to_canvas_coords(
            self.polygon_points[0][0], self.polygon_points[0][1]
        )
        last_x, last_y = self._convert_image_to_canvas_coords(
            self.polygon_points[-1][0], self.polygon_points[-1][1]
        )
        line_id = self.image_canvas.create_line(
            last_x, last_y, first_x, first_y,
            fill="yellow", width=2, tags="polygon_line"
        )
        self.polygon_lines.append(line_id)

        # 从多边形点创建掩码
        mask = np.zeros(self.image_np.shape[:2], dtype=np.uint8)
        pts = np.array(self.polygon_points, dtype=np.int32)
        cv2.fillPoly(mask, [pts], 1)
        mask_bool = mask.astype(bool)

        # --- 重要：强制不与现有标注重叠 ---
        locked_mask = self._get_locked_mask()  # 获取所有已确认标注的合并掩码
        if locked_mask is not None:
            original_area = np.sum(mask_bool)  # 排除前多边形区域的面积
            mask_bool = np.logical_and(mask_bool, ~locked_mask)  # 排除已锁定区域
            new_area = np.sum(mask_bool)  # 排除后多边形区域的面积

            # 如果多边形在排除后变为空，则警告用户
            if original_area > 0 and new_area == 0:
                messagebox.showwarning("警告", "您绘制的多边形完全位于已标注区域内，无有效新区域。请重新绘制。")
                self.clear_polygon()  # 清除无效多边形
                self.display_image(self.image_np)
                return

        self.selected_mask = mask_bool  # 清理后的掩码现在被选中
        self.is_modified = True

        # 清理画布上的多边形绘制元素
        self.image_canvas.delete("polygon_point")
        self.image_canvas.delete("polygon_line")
        self.image_canvas.delete("temp_line")
        self.temp_polygon_line = None
        self.polygon_lines = []

        self.display_image(self.image_np)
        self.status_var.set("多边形已闭合，请分配标签")

    def on_canvas_resize(self, event):
        """在画布调整大小时重绘图像。"""
        if self.image_np is not None:
            self.display_image(self.image_np)

    def load_model(self, model_path, config_path=None):
        """加载 SAM2 模型。"""
        try:
            print(f"正在加载SAM2模型: {model_path}")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"模型文件不存在: {model_path}")
            if config_path is None:
                # 如果未提供，则根据模型名称推断配置路径
                config_path = "configs/sam2/sam2_hiera_l.yaml" if "large" in model_path.lower() else "configs/sam2/sam2_hiera_b.yaml"
                print(f"未提供配置路径，使用: {config_path}")
            self.model = build_sam2(config_path, model_path, device=self.device)
            print("模型加载成功")
        except Exception as e:
            print(f"加载模型失败: {e}")
            traceback.print_exc()
            messagebox.showerror("模型加载失败", f"无法加载SAM2模型: {e}\n请检查模型和配置文件路径是否正确。")
            self.destroy()  # 如果模型加载失败，直接关闭应用

    def next_image(self):
        """加载列表中的下一张图像。"""
        if not self.image_list_loaded or not self.image_paths:
            messagebox.showwarning("警告", "未加载图像列表")
            return
        if self.is_modified:
            if not messagebox.askyesno("提示", "当前图像已修改但未保存，是否继续？"):
                return
        if self.current_image_index < len(self.image_paths) - 1:
            # 移动到下一张图像前缓存当前标注
            if self.annotation_masks and self.image_name:
                self.previous_annotations[self.image_name] = self.annotation_masks.copy()
            self.current_image_index += 1
            self.zoom_factor = 1.0
            self.pan_offset_x = 0
            self.pan_offset_y = 0
            self.load_current_image()
            self._save_last_session_info()
        else:
            messagebox.showinfo("提示", "已经是最后一张图像")

    def prev_image(self):
        """加载列表中的上一张图像。"""
        if not self.image_list_loaded or not self.image_paths:
            messagebox.showwarning("警告", "未加载图像列表")
            return
        if self.is_modified:
            if not messagebox.askyesno("提示", "当前图像已修改但未保存，是否继续？"):
                return
        if self.current_image_index > 0:
            # 移动到上一张图像前缓存当前标注
            if self.annotation_masks and self.image_name:
                self.previous_annotations[self.image_name] = self.annotation_masks.copy()
            self.current_image_index -= 1
            self.zoom_factor = 1.0
            self.pan_offset_x = 0
            self.pan_offset_y = 0
            self.load_current_image()
            self._save_last_session_info()
        else:
            messagebox.showinfo("提示", "已经是第一张图像")

    def load_current_image(self):
        """加载 current_image_index 处的图像。"""
        if not (0 <= self.current_image_index < len(self.image_paths)):
            print(f"错误: current_image_index ({self.current_image_index}) 超出范围 (0-{len(self.image_paths) - 1})")
            self.status_var.set("错误：图像索引超出范围")
            self.title("SAM2 交互式图像标注工具 - 索引错误")
            if self.image_np is not None:
                self.image_np = None
                self.image_canvas.delete("all")
            return

        image_path = self.image_paths[self.current_image_index]
        try:
            image = Image.open(image_path)
            self.image_np = np.array(image.convert("RGB"))  # 为保持一致性转换为 RGB
            self.image_name = os.path.basename(image_path)

            self.title(f"SAM2 交互式图像标注工具 - {self.image_name}")

            if self.image_list_loaded:
                self.image_selection_var.set(self.image_name)

            # 每次加载新图像时，重新初始化 SAM 预测器
            # 这确保了 SAM 总是从“干净”的状态开始处理新图像
            self.predictor = SAM2ImagePredictor(self.model)  # 重新创建 SAM2ImagePredictor 实例

            self.reset_annotation()  # 为新图像重置标注状态

            # 注意：这里不再调用 self.predictor.set_image()
            # 我们希望 SAM 在 predict_masks 中始终使用被扣除的图像

            self.annotation_masks = {}  # 为当前图像初始化标注掩码
            json_file = os.path.join(self.jsons_path, self.image_name.rsplit('.', 1)[0] + '.json')

            # 如果缓存或从 JSON 文件加载，则加载以前的标注
            if self.image_name in self.previous_annotations:
                self.annotation_masks = self.previous_annotations[self.image_name].copy()
            elif os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for shape in data.get('shapes', []):
                    label = shape['label']
                    points = np.array(shape['points'], dtype=np.int32)
                    if points.ndim == 2 and points.shape[0] >= 3 and points.shape[1] == 2:
                        mask = np.zeros(self.image_np.shape[:2], dtype=np.uint8)
                        cv2.fillPoly(mask, [points], 1)
                        mask_bool = mask.astype(bool)
                        if label not in self.annotation_masks:
                            self.annotation_masks[label] = []
                        self.annotation_masks[label].append(mask_bool)
                    else:
                        print(f"警告: 在JSON文件 '{json_file}' 中找到标签 '{label}' 的无效点集。")

            self.status_var.set(
                f"当前图像: {self.image_name} | 进度: {self.current_image_index + 1}/{len(self.image_paths)} | 缩放: {self.zoom_factor:.2f}x | 平移: ({self.pan_offset_x}, {self.pan_offset_y})")

            # 根据当前活动模式刷新UI
            current_mode = self.mode_var.get()
            if current_mode == "SAM标注":
                self.change_to_sam_mode()
            elif current_mode == "多边形":
                self.change_to_polygon_mode()
            elif current_mode == "编辑标签":
                self.change_to_edit_mode()

            self.display_image(self.image_np)  # 显示带有现有标注的加载图像

        except FileNotFoundError:
            print(f"错误: 图像文件未找到 '{image_path}'")
            messagebox.showerror("错误", f"图像文件未找到: {os.path.basename(image_path)}")
            self.status_var.set(f"错误: 图像文件 '{os.path.basename(image_path)}' 未找到。")
            self.title(f"SAM2 交互式图像标注工具 - 文件未找到")
            if len(self.image_paths) > 1:
                self.image_paths.pop(self.current_image_index)  # 移除损坏的路径
                image_basenames = [os.path.basename(p) for p in self.image_paths]
                self.image_selector['values'] = image_basenames
                # 必要时调整索引
                if self.current_image_index >= len(self.image_paths) and len(self.image_paths) > 0:
                    self.current_image_index = len(self.image_paths) - 1
                elif len(self.image_paths) == 0:
                    self.current_image_index = -1
                    self.image_list_loaded = False
                    self.title("SAM2 交互式图像标注工具 - 无图像")
                    self.image_canvas.delete("all")
                    self.status_var.set("所有图像加载失败或列表为空。")
                    return
                self.load_current_image()  # 尝试加载下一个有效图像
            else:
                # 没有更多图像可加载
                self.image_np = None
                self.image_name = ""
                self.image_list_loaded = False
                self.current_image_index = -1
                self.image_canvas.delete("all")
                self.status_var.set(f"图像 '{os.path.basename(image_path)}' 未找到。列表为空。")
                self.image_selector['values'] = []
                self.image_selection_var.set("")
        except Exception as e:
            print(f"加载图像 '{image_path}' 失败: {e}")
            traceback.print_exc()
            messagebox.showerror("错误", f"加载图像 '{os.path.basename(image_path)}' 失败: {str(e)}")
            self.status_var.set(f"加载图像 '{os.path.basename(image_path)}' 失败。")
            self.title(f"SAM2 交互式图像标注工具 - 加载失败")

    def display_image(self, image):
        """
        在画布上显示图像，应用已确认的掩码、
        预测的掩码和交互点。
        """
        self.display_img = image.copy()

        # 帮助函数，用叠加层绘制掩码轮廓
        def draw_mask_contours(mask_to_draw, color=(0, 165, 255), alpha=0.5):
            if mask_to_draw is None or not np.any(mask_to_draw):
                return
            self.apply_mask(self.display_img, mask_to_draw, color, alpha)  # 应用半透明颜色叠加层
            # 绘制白色轮廓以获得更好的可见性
            contours, _ = cv2.findContours(
                mask_to_draw.astype(np.uint8),
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            cv2.drawContours(self.display_img, contours, -1, (255, 255, 255), 1)

        # 绘制所有已确认的标注掩码
        for label, masks_list in self.annotation_masks.items():
            if label in self.available_labels:
                label_idx = self.available_labels.index(label)
            else:  # 动态地将新标签添加到可用列表中
                self.available_labels.append(label)
                self.label_combo['values'] = self.available_labels
                label_idx = len(self.available_labels) - 1
                if label_idx >= len(self.colors):  # 如果需要，生成更多颜色
                    self.colors = self.generate_colors(len(self.available_labels))

            color = self.colors[label_idx % len(self.colors)]  # 如果有很多标签，则使用模数循环颜色
            combined_mask = np.zeros_like(masks_list[0], dtype=bool) if masks_list else None

            # 应用此标签的每个掩码并组合用于质心计算
            for mask in masks_list:
                alpha = 0.4  # 已确认掩码的不透明度
                self.apply_mask(self.display_img, mask, color, alpha=alpha)
                if combined_mask is not None:
                    combined_mask = np.logical_or(combined_mask, mask)

            # 在组合掩码的质心上绘制标签文本
            if combined_mask is not None and np.any(combined_mask):
                y_indices, x_indices = np.where(combined_mask)
                if len(y_indices) > 0 and len(x_indices) > 0:
                    center_y = int(np.mean(y_indices))
                    center_x = int(np.mean(x_indices))
                    # 确保文本在图像边界内
                    text_x = max(0, min(center_x, self.display_img.shape[1] - 10))
                    text_y = max(15, min(center_y, self.display_img.shape[0] - 5))
                    cv2.putText(self.display_img, label, (text_x, text_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # 绘制当前预测的 SAM 掩码 (如果有)
        if self.masks is not None and len(self.masks) > 0 and self.current_mask_idx < len(self.masks):
            mask = self.masks[self.current_mask_idx]
            draw_mask_contours(mask, color=(0, 165, 255))  # 橙蓝色用于预测掩码

        # 绘制当前选定的掩码 (来自 SAM 或多边形)
        if self.selected_mask is not None:
            draw_mask_contours(self.selected_mask, color=(0, 255, 255))  # 青色用于选定掩码

        # 在 SAM 模式下绘制交互点
        if self.mode_var.get() == "SAM标注":
            self.draw_points(self.display_img)

        # 在编辑模式下为可编辑区域绘制边界框
        if self.mode_var.get() == "编辑标签":
            for i, region in enumerate(self.editable_regions):
                x, y, w, h = region['bbox']
                color = (255, 255, 255)  # 默认白色
                if i == self.selected_region_index:
                    color = (0, 255, 0)  # 选中时为绿色
                elif i == self.hovered_region_index:
                    color = (255, 255, 0)  # 悬停时为黄色
                cv2.rectangle(self.display_img, (x, y), (x + w, y + h), color, 2)  # 绘制矩形

        # 准备图像用于 Tkinter 画布显示 (缩放和平移)
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        img_height, img_width = self.display_img.shape[:2]

        # 在画布正确配置前的初始大小回退
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = max(1, self.image_canvas.winfo_reqwidth())
            canvas_height = max(1, self.image_canvas.winfo_reqheight())
            if canvas_width <= 1: canvas_width = 800
            if canvas_height <= 1: canvas_height = 600

        # 计算缩放后的尺寸
        zoomed_width = int(img_width * self.zoom_factor)
        zoomed_height = int(img_height * self.zoom_factor)

        # 确保尺寸至少为 1 像素
        if zoomed_width < 1 or zoomed_height < 1:
            zoomed_width = max(1, zoomed_width)
            zoomed_height = max(1, zoomed_height)

        # 调整图像大小以供显示
        image_at_zoom_level = cv2.resize(self.display_img, (zoomed_width, zoomed_height), interpolation=cv2.INTER_AREA)

        # 转换为 PhotoImage 用于 Tkinter
        image_pil = Image.fromarray(image_at_zoom_level)
        self.photo = ImageTk.PhotoImage(image_pil)
        self.image_canvas.delete("all")  # 清除画布上以前的绘图

        # 计算绘制图像的位置，带平移偏移
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        draw_x = center_x - zoomed_width // 2 + self.pan_offset_x
        draw_y = center_y - zoomed_height // 2 + self.pan_offset_y

        self.image_canvas.create_image(
            draw_x, draw_y,
            image=self.photo,
            anchor="nw"  # 锚定到左上角
        )

        # 存储当前显示比例和偏移以进行坐标转换
        self.current_display_scale = self.zoom_factor
        self.canvas_offset_x = draw_x
        self.canvas_offset_y = draw_y

        # 如果在多边形模式下，则重绘多边形点/线
        if self.mode_var.get() == "多边形" and self.polygon_points:
            self.redraw_polygon()

    def redraw_polygon(self):
        """在缩放/平移后在画布上重绘多边形点和线。"""
        self.image_canvas.delete("polygon_point")
        self.image_canvas.delete("polygon_line")
        self.image_canvas.delete("temp_line")  # 确保临时线也被清除/重绘
        self.polygon_lines = []
        self.temp_polygon_line = None

        for i, (x, y) in enumerate(self.polygon_points):
            canvas_x, canvas_y = self._convert_image_to_canvas_coords(x, y)
            self.image_canvas.create_oval(
                canvas_x - 5, canvas_y - 5, canvas_x + 5, canvas_y + 5,
                fill="red", outline="white", tags="polygon_point"
            )
            if i > 0:
                prev_x_img, prev_y_img = self.polygon_points[i - 1]
                prev_x_canvas, prev_y_canvas = self._convert_image_to_canvas_coords(prev_x_img, prev_y_img)
                line_id = self.image_canvas.create_line(
                    prev_x_canvas, prev_y_canvas, canvas_x, canvas_y,
                    fill="yellow", width=2, tags="polygon_line"
                )
                self.polygon_lines.append(line_id)

        # 如果多边形已闭合，则绘制闭合线
        if self.closed_polygon and len(self.polygon_points) > 2:
            first_x_img, first_y_img = self.polygon_points[0]
            last_x_img, last_y_img = self.polygon_points[-1]
            first_x_canvas, first_y_canvas = self._convert_image_to_canvas_coords(first_x_img, first_y_img)
            last_x_canvas, last_y_canvas = self._convert_image_to_canvas_coords(last_x_img, last_y_img)

            line_id = self.image_canvas.create_line(
                last_x_canvas, last_y_canvas, first_x_canvas, first_y_canvas,
                fill="yellow", width=2, tags="polygon_line"
            )
            self.polygon_lines.append(line_id)

    def apply_mask(self, image, mask, color, alpha=0.5):
        """将半透明的彩色掩码叠加层应用于图像。"""
        mask = mask.astype(bool)  # 确保掩码是布尔值
        colored_mask = np.zeros_like(image)
        colored_mask[mask] = color  # 将颜色应用于掩码区域
        cv2.addWeighted(colored_mask, alpha, image, 1.0, 0, image)  # 与原始图像混合
        return image

    def draw_points(self, image_to_draw_on):
        """在图像上绘制 SAM 交互点。"""
        if self.image_np is None: return

        for i, (point_orig_coords, label) in enumerate(zip(self.points, self.labels)):
            y_orig, x_orig = point_orig_coords
            color = (0, 255, 0) if label == 1 else (0, 0, 255)  # 正向为绿色，负向为红色
            star_base_size = 10
            star_points = []
            # 生成星形点
            for j in range(10):
                angle = np.pi / 5 * j - np.pi / 2
                radius = star_base_size if j % 2 == 0 else star_base_size * 0.4
                point_x = int(x_orig + radius * np.cos(angle))
                point_y = int(y_orig + radius * np.sin(angle))
                star_points.append([point_x, point_y])

            star_points_np = np.array(star_points, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(image_to_draw_on, [star_points_np], True, (255, 255, 255), 2)  # 白色轮廓
            cv2.fillPoly(image_to_draw_on, [star_points_np], color)  # 填充颜色

    def _convert_canvas_to_image_coords(self, canvas_x, canvas_y):
        """将画布坐标转换为原始图像坐标。"""
        if self.image_np is None or self.current_display_scale == 0:
            return canvas_x, canvas_y

        # 调整画布平移并计算缩放图像上的位置
        x_on_zoomed_image = canvas_x - self.canvas_offset_x
        y_on_zoomed_image = canvas_y - self.canvas_offset_y

        # 缩放回原始图像尺寸
        original_x = x_on_zoomed_image / self.current_display_scale
        original_y = y_on_zoomed_image / self.current_display_scale

        # 将坐标限制在图像边界内
        img_height, img_width = self.image_np.shape[:2]
        original_x = max(0, min(original_x, img_width - 1))
        original_y = max(0, min(original_y, img_height - 1))

        return int(original_x), int(original_y)

    def _convert_image_to_canvas_coords(self, image_x, image_y):
        """将原始图像坐标转换为画布坐标。"""
        if self.image_np is None:
            return image_x, image_y

        # 缩放到缩放图像尺寸
        x_on_zoomed_image = image_x * self.current_display_scale
        y_on_zoomed_image = image_y * self.current_display_scale

        # 调整画布平移
        canvas_x = x_on_zoomed_image + self.canvas_offset_x
        canvas_y = y_on_zoomed_image + self.canvas_offset_y

        return int(canvas_x), int(canvas_y)

    def on_left_click(self, event):
        """处理 SAM 模式下的左键单击 (正向点)。"""
        if self.image_np is None: return
        x, y = self._convert_canvas_to_image_coords(event.x, event.y)
        self.add_point(x, y, is_positive=True)
        self.display_image(self.image_np)

    def on_right_click(self, event):
        """处理 SAM 模式下的右键单击 (负向点)。"""
        if self.image_np is None: return
        x, y = self._convert_canvas_to_image_coords(event.x, event.y)
        self.add_point(x, y, is_positive=False)
        self.display_image(self.image_np)

    def on_middle_click(self, event):
        """处理 SAM 模式下的中键单击 (擦除区域)。"""
        if self.image_np is None: return
        x, y = self._convert_canvas_to_image_coords(event.x, event.y)
        self.remove_mask_region(x, y)  # 尝试从任何可见掩码中移除区域
        self.display_image(self.image_np)

    def on_edit_mode_motion(self, event):
        """处理编辑模式下的鼠标移动以高亮区域。"""
        if self.image_np is None: return
        x, y = self._convert_canvas_to_image_coords(event.x, event.y)

        current_hover = None
        for i, region in enumerate(self.editable_regions):
            rx, ry, rw, rh = region['bbox']  # 原始图像坐标中的边界框
            if rx <= x < rx + rw and ry <= y < ry + rh:
                # 检查光标下的像素是否实际是掩码的一部分
                if region['mask'][y, x]:
                    current_hover = i
                    break

        # 仅当悬停状态更改时才重绘以避免不必要的更新
        if current_hover != self.hovered_region_index:
            self.hovered_region_index = current_hover
            self.display_image(self.image_np)

    def on_edit_mode_click(self, event):
        """处理编辑模式下的单击以选择要更新标签的区域。"""
        # 必须悬停在区域上才能选择
        if self.hovered_region_index is not None:
            self.selected_region_index = self.hovered_region_index
            selected_label = self.editable_regions[self.selected_region_index]['label']
            self.label_var.set(selected_label)  # 将标签组合框设置为所选区域的标签
            self.update_label_button.config(state=tk.NORMAL)  # 启用更新按钮
            self.status_var.set(f"已选中区域，标签为 '{selected_label}'。可选择新标签并点击'更新标签'。")
        else:
            self._clear_selection_state()  # 单击空白处，取消选择
            self.status_var.set("已取消选择。")

        self.display_image(self.image_np)  # 刷新显示以显示选择高亮

    def remove_mask_region(self, x, y, radius=20):
        """
        从当前预测的掩码、选定的掩码或任何已确认的标注掩码中移除一个圆形区域。
        """
        modified = False
        if self.image_np is None: return False

        # 创建一个圆形擦除掩码
        erase_mask = np.zeros(self.image_np.shape[:2], dtype=np.uint8)
        cv2.circle(erase_mask, (x, y), radius, 1, -1)  # 用 1 填充圆形
        erase_mask_bool = erase_mask.astype(bool)

        # 1. 尝试从当前预测的掩码中移除 (如果可见)
        if self.masks is not None and self.current_mask_idx < len(self.masks) and \
                self.masks[self.current_mask_idx] is not None:
            current_pred_mask = self.masks[self.current_mask_idx]
            if np.any(current_pred_mask[erase_mask_bool]):  # 在修改前检查重叠
                self.save_to_history()
                self.masks[self.current_mask_idx] = np.logical_and(current_pred_mask, ~erase_mask_bool)
                self.is_modified = True
                modified = True
                self.status_var.set(f"已从预测掩码中移除区域")

        # 2. 如果未修改，则尝试从当前选定的掩码中移除
        if not modified and self.selected_mask is not None:
            if np.any(self.selected_mask[erase_mask_bool]):
                self.save_to_history()
                self.selected_mask = np.logical_and(self.selected_mask, ~erase_mask_bool)
                self.is_modified = True
                modified = True
                self.status_var.set(f"已从选中掩码中移除区域")

        # 3. 如果仍未修改，则尝试从任何已确认的标注掩码中移除
        if not modified:
            for label, masks_list in self.annotation_masks.items():
                for i, mask in enumerate(masks_list):
                    if np.any(mask[erase_mask_bool]):
                        self.save_to_history()
                        self.annotation_masks[label][i] = np.logical_and(mask, ~erase_mask_bool)
                        self.is_modified = True
                        modified = True
                        self.status_var.set(f"已从标签 '{label}' 的掩码中移除区域")
                        break  # 每次单击只修改每个标签列表中的一个掩码
                if modified:
                    break  # 如果修改了掩码，则停止迭代标签

        if not modified:
            self.status_var.set("点击位置没有可擦除的掩码")
        else:
            self.display_image(self.image_np)  # 如果发生更改，则刷新显示
        return modified

    def reset_annotation(self):
        """重置当前图像的所有临时和当前标注状态。"""
        self.points = []
        self.labels = []
        self.masks = None
        self.scores = None
        self.current_mask_idx = 0
        self.selected_mask = None
        self.annotation_complete = False
        self.is_modified = False
        self.history = []  # 清除撤销历史记录

        self.clear_polygon()  # 清除任何多边形绘制
        self._clear_selection_state()  # 清除编辑模式选择

        # 如果当前在编辑模式，则重新准备编辑模式状态
        if self.image_np is not None:
            current_mode = self.mode_var.get()
            if current_mode == "编辑标签":
                self._prepare_for_editing()  # 重新计算现有标注的边界框
            self.display_image(self.image_np)

    def save_to_history(self):
        """将当前标注状态保存到历史记录以供撤销功能使用。"""
        state = {
            'points': self.points.copy(),
            'labels': self.labels.copy(),
            'masks': self.masks.copy() if self.masks is not None else None,
            'scores': self.scores.copy() if self.scores is not None else None,
            'current_mask_idx': self.current_mask_idx,
            'selected_mask': self.selected_mask.copy() if self.selected_mask is not None else None,
            # 深拷贝 annotation_masks 以避免共享引用
            'annotation_masks': {k: [m.copy() for m in v] for k, v in self.annotation_masks.items()},
            'is_modified': self.is_modified,
            'polygon_points': self.polygon_points.copy(),
            'closed_polygon': self.closed_polygon,
        }
        self.history.append(state)

    def undo(self):
        """将应用程序恢复到历史记录中的上一个状态。"""
        if not self.history:
            messagebox.showinfo("提示", "没有可撤销的操作")
            return
        state = self.history.pop()  # 获取最后一个保存的状态
        # 恢复所有状态变量
        self.points = state['points']
        self.labels = state['labels']
        self.masks = state['masks']
        self.scores = state['scores']
        self.current_mask_idx = state['current_mask_idx']
        self.selected_mask = state['selected_mask']
        self.annotation_masks = state['annotation_masks']
        self.is_modified = state['is_modified']
        self.polygon_points = state['polygon_points']
        self.closed_polygon = state['closed_polygon']

        if self.image_np is not None:
            # 撤销后更新编辑模式状态
            if self.mode_var.get() == "编辑标签":
                self._prepare_for_editing()  # 重新计算可编辑区域
                self._clear_selection_state()  # 清除任何活动选择
            self.display_image(self.image_np)
            if self.is_polygon_mode:
                self.redraw_polygon()  # 确保正确重绘多边形绘制
        messagebox.showinfo("提示", "已撤销上一步操作")

    def add_point(self, x, y, is_positive=True):
        """
        为 SAM 预测添加交互点。
        现在包含一个检查，防止在已锁定（已标注）区域内添加点。
        """
        if self.image_np is None: return False

        # 获取所有已确认标注区域的合并掩码
        locked_mask = self._get_locked_mask()
        if locked_mask is not None and locked_mask[y, x]:  # 检查点击点 (y,x) 是否在已锁定区域内
            messagebox.showwarning("警告", "该点位于已标注区域内，请在未标注区域点击。")
            self.status_var.set(f"无法在已标注区域添加点: ({x}, {y})")
            return False  # 阻止添加点

        self.save_to_history()  # 在添加点之前保存当前状态到历史记录
        label = 1 if is_positive else 0
        self.points.append([y, x])  # SAM 期望点的格式为 (y, x)
        self.labels.append(label)
        self.is_modified = True
        point_type = "正向" if is_positive else "负向"
        self.status_var.set(f"添加{point_type}点: ({x}, {y}), 总点数: {len(self.points)}")
        return True  # 点添加成功

    def _get_locked_mask(self):
        """
        创建一个布尔掩码，它合并了所有当前已确认的标注区域。
        这个掩码代表了“已锁定”区域，新的标注不应与这些区域重叠。

        Returns:
            np.ndarray (dtype=bool): 一个布尔掩码，其中 True 表示一个已标注像素，
                                      如果没有标注则返回 None。
        """
        if not self.annotation_masks or self.image_np is None:
            return None

        h, w = self.image_np.shape[:2]
        locked_mask = np.zeros((h, w), dtype=bool)

        for _, masks_list in self.annotation_masks.items():
            for mask in masks_list:
                # 使用逻辑或操作将所有掩码合并到一个单一的锁定区域掩码中
                # 确保掩码在进行或操作前是布尔类型
                locked_mask = np.logical_or(locked_mask, mask.astype(bool))

        return locked_mask

    def predict_masks(self):
        """
        根据当前点触发 SAM 预测掩码。
        关键是，通过向 SAM 提供掩蔽图像，并对预测结果进行后处理，确保预测的掩码不与已确认区域重叠。
        """
        if self.image_np is None:
            messagebox.showwarning("警告", "未加载图像")
            return
        if len(self.points) == 0:
            messagebox.showwarning("警告", "请先添加至少一个点")
            return
        if self.predictor is None:  # 确保 predictor 已初始化
            messagebox.showerror("错误", "SAM 预测器未初始化。请重新加载图像。")
            return

        self.status_var.set("正在预测掩码...")
        self.update_idletasks()  # 强制更新 UI

        # 为 SAM 预测创建一个掩蔽图像
        # 已标注区域将被黑色填充，这样 SAM 就“看不见”它们了。
        # 这一步在每次预测前都会执行，确保使用了最新的 locked_mask
        masked_image_for_sam = self.image_np.copy()
        locked_mask = self._get_locked_mask()
        if locked_mask is not None:
            masked_image_for_sam[locked_mask] = 0  # 将锁定区域像素置为黑色

        # 将掩蔽图像设置给预测器。这会强制 SAM 重新计算图像嵌入。
        self.predictor.set_image(masked_image_for_sam)

        points_for_sam = np.array([[p[1], p[0]] for p in self.points])
        labels_array = np.array(self.labels)

        start_time = time.time()
        try:
            masks, scores, logits = self.predictor.predict(
                point_coords=points_for_sam,
                point_labels=labels_array,
                multimask_output=True
            )
        except Exception as e:
            print(f"掩码预测失败: {e}")
            traceback.print_exc()
            messagebox.showerror("错误", f"掩码预测失败: {str(e)}")
            return
        end_time = time.time()

        # 预测后，我们仍然需要进行最终检查，以确保 SAM 没有在黑色区域上进行预测（尽管使用掩蔽输入应该会最小化这种情况）。
        # 此处的后处理是双重保障
        if locked_mask is not None:
            unlocked_area = ~locked_mask  # 未锁定区域是锁定区域的补集
            masks = [np.logical_and(m, unlocked_area) for m in masks]  # 将每个预测掩码与未锁定区域进行逻辑与操作

        valid_masks = []
        valid_scores = []
        for mask, score in zip(masks, scores):
            if np.any(mask):  # 检查掩码是否还有任何非零像素（即是否不为空）
                valid_masks.append(mask)
                valid_scores.append(score)

        if not valid_masks:
            messagebox.showwarning("警告", "预测的掩码均为空或完全位于已标注区域内，请尝试在未标注区域调整点击位置。")
            self.masks = None
            self.scores = None
            self.current_mask_idx = 0
            self.display_image(self.image_np)
            return

        sorted_ind = np.argsort(valid_scores)[::-1]
        self.masks = np.array(valid_masks)[sorted_ind][:3]  # 获取分数最高的前3个掩码
        self.scores = np.array(valid_scores)[sorted_ind][:3]
        self.current_mask_idx = 0
        self.is_modified = True
        self.save_to_history()
        messagebox.showinfo("提示", f"预测完成，用时 {end_time - start_time:.2f}秒，找到 {len(self.masks)} 个有效新掩码")
        self.display_image(self.image_np)

    def next_mask(self):
        """显示 SAM 输出中的下一个预测掩码。"""
        if self.masks is None or len(self.masks) <= 1:
            messagebox.showinfo("提示", "没有更多掩码可用")
            return
        self.current_mask_idx = (self.current_mask_idx + 1) % len(self.masks)  # 循环浏览掩码
        self.status_var.set(
            f"当前掩码: {self.current_mask_idx + 1}/{len(self.masks)}, 分数: {self.scores[self.current_mask_idx]:.3f}")
        if self.image_np is not None: self.display_image(self.image_np)

    def select_mask(self):
        """选择当前显示的预测掩码进行确认。"""
        if self.masks is None or len(self.masks) == 0 or self.current_mask_idx >= len(self.masks):
            messagebox.showwarning("警告", "没有可选择的掩码")
            return
        self.save_to_history()  # 在选择前保存状态
        self.selected_mask = self.masks[self.current_mask_idx].copy()  # 深拷贝以避免修改问题
        self.is_modified = True
        messagebox.showinfo("提示", f"已选择掩码 {self.current_mask_idx + 1}/{len(self.masks)}，请分配标签")
        if self.image_np is not None: self.display_image(self.image_np)

    def on_label_change(self, event=None):
        """处理标签组合框中的更改，如果输入则添加新标签。"""
        new_label = self.label_var.get()
        if new_label and new_label not in self.available_labels:
            self.available_labels.append(new_label)
            self.label_combo['values'] = self.available_labels  # 更新组合框选项
            if len(self.available_labels) > len(self.colors):
                self.colors = self.generate_colors(len(self.available_labels))  # 生成更多颜色
        self.current_label = new_label

    def confirm_label(self):
        """
        使用 `current_label` 确认 `selected_mask` 并将其添加到 `annotation_masks`。
        此方法假定 `selected_mask` 已经过处理以排除重叠。
        """
        if self.selected_mask is None:
            messagebox.showwarning("警告", "请先选择一个掩码 (通过SAM预测或多边形绘制)")
            return
        label = self.current_label
        if not label or label == "" or label == DEFAULT_LABELS[0]:
            messagebox.showwarning("警告", "请选择一个有效的标签 (非背景)")
            return
        if not np.any(self.selected_mask):
            messagebox.showwarning("警告", "选择的区域为空，无法确认。")
            self.selected_mask = None  # 清除无效选择
            self.display_image(self.image_np)
            return

        self.save_to_history()  # 在确认前保存状态

        if label not in self.annotation_masks:
            self.annotation_masks[label] = []
        self.annotation_masks[label].append(self.selected_mask.copy())  # 添加掩码的副本
        action = "添加" if len(self.annotation_masks[label]) == 1 else "叠加"  # 简化消息

        self.is_modified = True
        self.selected_mask = None  # 确认后清除选定的掩码

        # 为下一个标注任务重置状态
        self.points = []
        self.labels = []
        self.masks = None
        self.scores = None
        self.current_mask_idx = 0
        self.clear_polygon()  # 清除任何剩余的多边形元素

        messagebox.showinfo("提示", f"已{action}并锁定标签为 '{label}' 的区域")

        # 将标签选择重置为背景，以提示为下一个区域选择新标签
        self.label_var.set(DEFAULT_LABELS[0])
        self.current_label = DEFAULT_LABELS[0]

        if self.image_np is not None: self.display_image(self.image_np)

    def _prepare_for_editing(self):
        """
        通过为每个已确认的标注掩码计算边界框，为编辑模式准备数据。
        """
        self.editable_regions = []
        if self.image_np is None:
            return

        # 遍历所有已确认的掩码并计算其边界框
        for label, masks_list in self.annotation_masks.items():
            for mask in masks_list:
                if not np.any(mask):  # 跳过空掩码
                    continue
                # 查找轮廓以获取边界框。
                # 使用 RETR_EXTERNAL 仅获取外部轮廓，如果掩码有孔。
                contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if not contours:
                    continue
                # 合并给定掩码的所有轮廓以获得单个整体边界框
                all_points = np.concatenate(contours)
                x, y, w, h = cv2.boundingRect(all_points)
                # 存储原始掩码引用及其标签/边界框以供编辑
                self.editable_regions.append({'mask': mask, 'label': label, 'bbox': (x, y, w, h)})

    def _clear_selection_state(self):
        """清除编辑模式下的所有选择和悬停状态。"""
        self.selected_region_index = None
        self.hovered_region_index = None
        self.update_label_button.config(state=tk.DISABLED)  # 禁用更新按钮
        self.label_var.set(DEFAULT_LABELS[0])  # 重置标签组合框
        self.current_label = DEFAULT_LABELS[0]
        # self.editable_regions = [] # 状态可能已更改，因此清除准备好的区域 - 在 prepare_for_editing 中处理

    def update_selected_label(self):
        """更新当前选定标注区域的标签。"""
        if self.selected_region_index is None:
            messagebox.showwarning("警告", "没有选中的区域可更新。")
            return

        new_label = self.label_var.get()
        if not new_label or new_label == DEFAULT_LABELS[0]:
            messagebox.showwarning("警告", "请选择一个有效的新标签。")
            return

        region_to_update = self.editable_regions[self.selected_region_index]
        old_label = region_to_update['label']
        mask_to_move = region_to_update['mask']  # 获取对实际掩码对象的引用

        if new_label == old_label:
            messagebox.showinfo("提示", "新旧标签相同，未做更改。")
            return

        self.save_to_history()  # 在修改前保存状态

        # 从其旧标签的列表中移除掩码
        # 使用 'is' 比较对象身份，确保移除确切的掩码对象
        if old_label in self.annotation_masks:
            self.annotation_masks[old_label] = [m for m in self.annotation_masks[old_label] if m is not mask_to_move]
            if not self.annotation_masks[old_label]:  # 如果旧标签的列表变空，则移除该键
                del self.annotation_masks[old_label]

        # 将掩码添加到其新标签的列表中
        if new_label not in self.annotation_masks:
            self.annotation_masks[new_label] = []
        self.annotation_masks[new_label].append(mask_to_move)  # 添加相同的掩码对象

        self.is_modified = True
        messagebox.showinfo("成功", f"区域标签已从 '{old_label}' 更新为 '{new_label}'。")

        # 重置选择状态并重新准备编辑以反映更改
        self._clear_selection_state()
        self._prepare_for_editing()
        self.display_image(self.image_np)

    def complete_annotation(self):
        """
        将图像的所有当前标注保存到 JSON 文件 (LabelMe 格式)
        并保存图像的副本。
        然后，移动到下一张图像。
        """
        if not self.annotation_masks:
            if not messagebox.askyesno("提示", "当前图像没有任何标注，确定要完成并跳到下一张吗？"):
                return
        if self.image_name == "" or self.image_np is None:
            messagebox.showerror("错误", "没有加载图像，无法保存。")
            return

        try:
            base_name = self.image_name.rsplit('.', 1)[0]
            json_file = os.path.join(self.jsons_path, base_name + '.json')

            # 保存原始图像的副本
            jpg_file_name = base_name + '.jpg'
            jpg_file_path = os.path.join(self.jpgs_path, jpg_file_name)

            img_pil = Image.fromarray(self.image_np)
            img_pil.save(jpg_file_path, "JPEG")

            height, width = self.image_np.shape[:2]
            # 初始化 LabelMe JSON 结构
            data = {
                "version": "5.0.1",
                "flags": {},
                "shapes": [],
                "imagePath": jpg_file_name,
                "imageData": None,
                "imageHeight": height,
                "imageWidth": width
            }

            # 将所有已确认的掩码转换为 JSON 的多边形形状
            for label, masks_list in self.annotation_masks.items():
                for mask_item in masks_list:
                    if not np.any(mask_item):  # 跳过空掩码
                        continue
                    contours, _ = cv2.findContours(
                        mask_item.astype(np.uint8),
                        cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE
                    )
                    for contour in contours:
                        if contour.shape[0] < 3:  # 多边形至少需要3个点
                            continue
                        points = contour.reshape(-1, 2).tolist()  # 重塑为 [[x,y], [x,y], ...]
                        shape = {
                            "label": label,
                            "points": points,
                            "group_id": None,
                            "shape_type": "polygon",
                            "flags": {}
                        }
                        data["shapes"].append(shape)

            # 即使没有标注，也保存一个空的 JSON 文件以标记为“已处理”
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 更新缓存并重置标志
            self.previous_annotations[self.image_name] = self.annotation_masks.copy()
            self.is_modified = False
            self.annotation_complete = True

            if data["shapes"]:
                messagebox.showinfo("提示", f"标注已保存到 {json_file}\n图像副本已保存到 {jpg_file_path}")
            else:
                messagebox.showinfo("提示", f"已将空标注保存到 {json_file}，表示此图像无需标注。")

            self._save_last_session_info()  # 保存会话状态
            self.next_image()  # 自动移动到下一张图像

        except Exception as e:
            print(f"保存标注失败: {e}")
            traceback.print_exc()
            messagebox.showerror("错误", f"保存标注失败: {str(e)}")


def main():
    """运行 SAM2 标注器应用的主函数。"""
    # 确定是否从 PyInstaller 包运行
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        try:
            application_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            application_path = os.getcwd()  # 交互式环境的回退

    default_model_path = os.path.join(application_path, "weights", "sam2_hiera_large.pt")
    default_config_path = os.path.join(application_path, "configs", "sam2", "sam2_hiera_l.yaml")
    default_output_dir = os.path.join(application_path, "annotations_output")

    # --- 用户: 请确认这些路径 ---
    # !! 请务必将下面的路径修改为您自己电脑上的正确路径 !!
    # 用户定义的模型、配置、输出和图像路径。
    # 重要提示：请将这些路径更新为您的实际文件位置。
    model_path_to_use = r"D:\python-deeplearning\CVlearn\SAM2\sam2-main\weights\sam2_hiera_large.pt"
    config_path_to_use = r"D:\python-deeplearning\CVlearn\SAM2\sam2-main\configs\sam2\sam2_hiera_l.yaml"
    output_dir_to_use = r"./annotations_sam2_tool"  # 生成的标注的输出目录
    image_dir_to_use = r"D:\python-deeplearning\CVlearn\SAM2\sam2-main\VOCdevkit\VOC2007\JPEGImages_test_small"  # 包含要标注的图像的目录

    # 如果用户提供的路径未找到，则回退到默认路径
    if not os.path.exists(model_path_to_use) and os.path.exists(default_model_path):
        print(f"警告: 提供的模型路径未找到。使用默认路径: {default_model_path}")
        model_path_to_use = default_model_path
    if config_path_to_use and not os.path.exists(config_path_to_use) and os.path.exists(default_config_path):
        print(f"警告: 提供的配置文件路径未找到。使用默认路径: {default_config_path}")
        config_path_to_use = default_config_path

    # 关键检查：确保模型路径存在
    if not os.path.exists(model_path_to_use):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("启动错误",
                             f"SAM2模型文件未找到: {model_path_to_use}\n请在main()函数中设置正确的'model_path_to_use'。")
        sys.exit(1)
    # 对缺失配置的警告，因为它可能仍然可以使用默认值工作
    if config_path_to_use and not os.path.exists(config_path_to_use):
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("启动警告",
                               f"SAM2配置文件未找到: {config_path_to_use}\n将尝试使用模型内部或SAM2库的默认配置。")

    # 创建并运行应用
    app = InteractiveSAM2Annotator(
        model_path=model_path_to_use,
        config_path=config_path_to_use,
        output_dir=output_dir_to_use,
        image_dir=image_dir_to_use
    )
    app.mainloop()


if __name__ == "__main__":
    main()
