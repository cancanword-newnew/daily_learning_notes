import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
import os
import hashlib

class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 合并工具")
        self.root.geometry("600x500")
        
        self.file_list = []

        # --- 顶部按钮栏 ---
        top_frame = tk.Frame(root, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10)
        
        btn_add = tk.Button(top_frame, text="➕ 添加文件", command=self.add_files, bg="#e1e1e1", width=15)
        btn_add.pack(side=tk.LEFT, padx=5)
        
        btn_clear = tk.Button(top_frame, text="🗑️ 清空列表", command=self.clear_list, bg="#ffcccc", width=10)
        btn_clear.pack(side=tk.LEFT, padx=5)

        # --- 中间列表区域 ---
        list_frame = tk.Frame(root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED, font=("微软雅黑", 10), bg="#f9f9f9")
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- 侧边排序按钮 ---
        # 为了布局方便，其实可以放在列表右侧或者底部，这里放在底部控制栏上方
        control_frame = tk.Frame(root, pady=5)
        control_frame.pack(fill=tk.X, padx=10)
        
        btn_up = tk.Button(control_frame, text="⬆️ 上移", command=self.move_up, width=10)
        btn_up.pack(side=tk.LEFT, padx=5)
        
        btn_down = tk.Button(control_frame, text="⬇️ 下移", command=self.move_down, width=10)
        btn_down.pack(side=tk.LEFT, padx=5)
        
        btn_remove = tk.Button(control_frame, text="❌ 移除选中", command=self.remove_selected, width=10)
        btn_remove.pack(side=tk.LEFT, padx=20)

        # --- 底部保存按钮 ---
        bottom_frame = tk.Frame(root, pady=15)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
        
        btn_merge = tk.Button(bottom_frame, text="🚀 开始合并并保存", command=self.merge_pdfs, 
                              bg="#4CAF50", fg="white", font=("微软雅黑", 12, "bold"), height=2)
        btn_merge.pack(fill=tk.X)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if files:
            for f in files:
                if f not in self.file_list:
                    self.file_list.append(f)
                    self.listbox.insert(tk.END, os.path.basename(f))

    def clear_list(self):
        self.file_list = []
        self.listbox.delete(0, tk.END)

    def remove_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        
        # 从后往前删，防止索引错位
        for index in reversed(selection):
            self.file_list.pop(index)
            self.listbox.delete(index)

    def move_up(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        
        for index in selection:
            if index == 0: continue # 已经在最上面
            
            # 交换数据
            self.file_list[index], self.file_list[index-1] = self.file_list[index-1], self.file_list[index]
            
            # 交换列表显示
            text = self.listbox.get(index)
            self.listbox.delete(index)
            self.listbox.insert(index-1, text)
            self.listbox.selection_set(index-1)

    def move_down(self):
        selection = self.listbox.curselection()
        if not selection:
            return
            
        # 从后往前处理，防止索引影响
        for index in reversed(selection):
            if index == len(self.file_list) - 1: continue # 已经在最下面
            
            # 交换数据
            self.file_list[index], self.file_list[index+1] = self.file_list[index+1], self.file_list[index]
            
            # 交换列表显示
            text = self.listbox.get(index)
            self.listbox.delete(index)
            self.listbox.insert(index+1, text)
            self.listbox.selection_set(index+1)

    def merge_pdfs(self):
        if len(self.file_list) < 2:
            messagebox.showwarning("提示", "请至少添加两个 PDF 文件进行合并")
            return
            
        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile="合并后的文件.pdf"
        )
        
        if not output_path:
            return
            
        try:
            merged_doc = fitz.open()
            seen_hashes = set()
            
            for file_path in self.file_list:
                doc = fitz.open(file_path)
                # 逐页检查重复
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    # 获取页面图像数据的哈希值用于去重
                    # 使用默认分辨率即可，如果速度太慢可以降低分辨率 matrix=fitz.Matrix(0.5, 0.5)
                    pix = page.get_pixmap()
                    page_hash = hashlib.md5(pix.tobytes()).hexdigest()
                    
                    if page_hash not in seen_hashes:
                        seen_hashes.add(page_hash)
                        merged_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                
                doc.close()
            
            # 使用 garbage=4 和 deflate=True 确保文件尽可能小
            merged_doc.save(output_path, garbage=4, deflate=True)
            merged_doc.close()
            
            messagebox.showinfo("成功", f"文件已合并保存至:\n{output_path}")
            
        except Exception as e:
            messagebox.showerror("合并失败", f"发生错误:\n{str(e)}")

if __name__ == "__main__":
    try:
        import fitz
    except ImportError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("缺少依赖", "请先安装 PyMuPDF:\n\npip install pymupdf")
        exit()

    root = tk.Tk()
    app = PDFMergerApp(root)
    root.mainloop()
