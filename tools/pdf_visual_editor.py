import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import os

class PDFEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 可视化页面删除工具")
        self.root.geometry("1000x700")
        
        self.filepath = None
        self.doc = None
        self.page_vars = []
        self.page_images = [] # 保持引用防止被垃圾回收
        self.page_frames = []
        
        # --- 顶部控制栏 ---
        top_frame = tk.Frame(root, height=50)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        btn_open = tk.Button(top_frame, text="📂 打开 PDF 文件", command=self.open_pdf, bg="#e1e1e1", font=("微软雅黑", 10))
        btn_open.pack(side=tk.LEFT, padx=10)
        
        self.lbl_info = tk.Label(top_frame, text="请先打开一个 PDF 文件", font=("微软雅黑", 10))
        self.lbl_info.pack(side=tk.LEFT, padx=10)
        
        btn_save = tk.Button(top_frame, text="💾 保存新 PDF (移除选中页)", command=self.save_pdf, bg="#4CAF50", fg="white", font=("微软雅黑", 10, "bold"))
        btn_save.pack(side=tk.RIGHT, padx=10)

        # --- 主内容区域 (带滚动条) ---
        container = tk.Frame(root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(container, bg="#f0f0f0")
        self.scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # 绑定窗口大小改变，调整内部frame宽度
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return
            
        try:
            self.filepath = file_path
            self.doc = fitz.open(self.filepath)
            self.lbl_info.config(text=f"当前文件: {os.path.basename(self.filepath)} | 总页数: {len(self.doc)}")
            self.refresh_ui()
        except Exception as e:
            messagebox.showerror("错误", f"无法打开 PDF 文件:\n{str(e)}")
        
    def refresh_ui(self):
        # 清除旧控件
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.page_vars = []
        self.page_images = []
        self.page_frames = []
        
        # 网格布局参数
        columns = 4
        thumbnail_width = 200
        
        for i, page in enumerate(self.doc):
            # 渲染页面为图片
            # 计算缩放比例以适应缩略图宽度
            zoom = thumbnail_width / page.rect.width
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # 转换为 tkinter 可用的图片
            img_data = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            tk_img = ImageTk.PhotoImage(img_data)
            self.page_images.append(tk_img)
            
            # 每个页面的容器 Frame
            frame = tk.Frame(self.scrollable_frame, borderwidth=1, relief="groove", bg="white")
            row = i // columns
            col = i % columns
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="n")
            self.page_frames.append(frame)
            
            # 图片标签 (点击图片也可以切换选中状态)
            lbl_img = tk.Label(frame, image=tk_img, bg="white", cursor="hand2")
            lbl_img.pack(padx=5, pady=5)
            
            # 复选框
            var = tk.BooleanVar()
            chk = tk.Checkbutton(frame, text=f"第 {i+1} 页 - 删除", variable=var, bg="white", font=("微软雅黑", 9), fg="red")
            chk.pack(pady=2)
            self.page_vars.append(var)
            
            # 绑定点击事件
            lbl_img.bind("<Button-1>", lambda e, v=var, f=frame: self.toggle_selection(v, f))
            frame.bind("<Button-1>", lambda e, v=var, f=frame: self.toggle_selection(v, f))

    def toggle_selection(self, var, frame):
        # 切换布尔值
        var.set(not var.get())
        # 更新视觉反馈
        if var.get():
            frame.config(bg="#ffcccc") # 选中删除时变红
        else:
            frame.config(bg="white")

    def save_pdf(self):
        if not self.doc:
            return
            
        # 检查是否有选中的页面
        pages_to_delete = [i for i, var in enumerate(self.page_vars) if var.get()]
        if not pages_to_delete:
            if not messagebox.askyesno("提示", "您没有选择任何要删除的页面。\n是否直接另存为新文件？"):
                return
        
        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=f"已处理_{os.path.basename(self.filepath)}"
        )
        
        if not output_path:
            return
            
        try:
            new_doc = fitz.open()
            # 只插入未被标记删除的页面
            for i in range(len(self.doc)):
                if not self.page_vars[i].get():
                    new_doc.insert_pdf(self.doc, from_page=i, to_page=i)
            
            new_doc.save(output_path, garbage=4, deflate=True)
            new_doc.close()
            messagebox.showinfo("成功", f"文件已保存！\n共删除了 {len(pages_to_delete)} 页。")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

if __name__ == "__main__":
    # 检查依赖
    try:
        import fitz
        from PIL import Image, ImageTk
    except ImportError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("缺少依赖", f"请先安装必要的库:\n\npip install pymupdf pillow\n\n错误信息: {e}")
        exit()

    root = tk.Tk()
    app = PDFEditorApp(root)
    root.mainloop()
