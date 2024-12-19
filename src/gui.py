import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QRadioButton, QPushButton, 
                           QFileDialog, QLabel, QButtonGroup, QLineEdit,
                           QMessageBox, QDialog)
from PyQt5.QtCore import Qt
from converter import convert_to_jmx

class TestPlanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置TestPlan")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        # TestPlan名称输入
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入TestPlan名称")
        layout.addWidget(QLabel("TestPlan名称:"))
        layout.addWidget(self.name_input)
        
        # 确定取消按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Postman/ApiPost to JMeter Converter")
        self.setMinimumSize(800, 400)
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 添加说明标签
        intro_label = QLabel("请选择转换模式和相应的配置文件")
        intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(intro_label)
        
        # 选择转换模式
        mode_group = QButtonGroup(self)
        mode_layout = QHBoxLayout()
        self.postman_radio = QRadioButton("Postman")
        self.apipost_radio = QRadioButton("ApiPost")
        mode_group.addButton(self.postman_radio)
        mode_group.addButton(self.apipost_radio)
        mode_layout.addWidget(self.postman_radio)
        mode_layout.addWidget(self.apipost_radio)
        layout.addLayout(mode_layout)
        
        # 文件选择区域
        self.file_layout = QVBoxLayout()
        
        # Postman文件选择
        self.postman_widget = QWidget()
        postman_layout = QVBoxLayout(self.postman_widget)
        
        # Collection文件选择
        collection_layout = QHBoxLayout()
        self.collection_path = QLineEdit()
        self.collection_path.setPlaceholderText("请选择Postman Collection文件")
        collection_btn = QPushButton("选择Collection文件")
        collection_layout.addWidget(self.collection_path)
        collection_layout.addWidget(collection_btn)
        postman_layout.addLayout(collection_layout)
        
        # Environment文件选择
        env_layout = QHBoxLayout()
        self.env_path = QLineEdit()
        self.env_path.setPlaceholderText("请选择Postman Environment文件（可选）")
        env_btn = QPushButton("选择Environment文件")
        env_layout.addWidget(self.env_path)
        env_layout.addWidget(env_btn)
        postman_layout.addLayout(env_layout)
        
        # ApiPost文件选择
        self.apipost_widget = QWidget()
        apipost_layout = QHBoxLayout(self.apipost_widget)
        self.apipost_path = QLineEdit()
        self.apipost_path.setPlaceholderText("请选择ApiPost导出的JSON文件")
        apipost_btn = QPushButton("选择ApiPost文件")
        apipost_layout.addWidget(self.apipost_path)
        apipost_layout.addWidget(apipost_btn)
        
        # 输出路径显示和选择
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("输出路径（与输入文件同级目录）")
        output_btn = QPushButton("选择输出路径")
        output_layout.addWidget(QLabel("输出路径:"))
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_btn)
        
        self.file_layout.addWidget(self.postman_widget)
        self.file_layout.addWidget(self.apipost_widget)
        self.file_layout.addLayout(output_layout)
        layout.addLayout(self.file_layout)
        
        # 转换按钮
        convert_btn = QPushButton("转换")
        convert_btn.setFixedHeight(40)
        layout.addWidget(convert_btn)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 信号连接
        self.postman_radio.toggled.connect(self.toggle_mode)
        self.apipost_radio.toggled.connect(self.toggle_mode)
        collection_btn.clicked.connect(lambda: self.select_file(self.collection_path, "Postman Collection (*.json)"))
        env_btn.clicked.connect(lambda: self.select_file(self.env_path, "Postman Environment (*.json)"))
        apipost_btn.clicked.connect(lambda: self.select_file(self.apipost_path, "ApiPost Export (*.json)"))
        convert_btn.clicked.connect(self.convert)
        output_btn.clicked.connect(self.select_output_dir)
        
        # 初始化界面
        self.postman_radio.setChecked(True)
        self.toggle_mode()
        
    def toggle_mode(self):
        is_postman = self.postman_radio.isChecked()
        self.postman_widget.setVisible(is_postman)
        self.apipost_widget.setVisible(not is_postman)
        
    def select_file(self, line_edit, file_filter):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            file_filter
        )
        if file_name:
            line_edit.setText(file_name)
            # 只有当输出路径为空时才自动设置
            if not self.output_path.text():
                self.output_path.setText(os.path.dirname(file_name))
            
    def select_output_dir(self):
        dir_name = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            self.output_path.text() or ""  # 如果当前有路径则使用当前路径作为起始目录
        )
        if dir_name:
            self.output_path.setText(dir_name)
        
    def validate_inputs(self):
        if self.postman_radio.isChecked():
            if not self.collection_path.text():
                QMessageBox.warning(self, "警告", "请选择Postman Collection文件！")
                return False
        else:
            if not self.apipost_path.text():
                QMessageBox.warning(self, "警告", "请选择ApiPost导出文件！")
                return False
        return True
            
    def convert(self):
        if not self.validate_inputs():
            return
            
        # 获取TestPlan名称
        dialog = TestPlanDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
            
        test_plan_name = dialog.name_input.text()
        if not test_plan_name:
            QMessageBox.warning(self, "警告", "TestPlan名称不能为空！")
            return
            
        try:
            self.status_label.setText("正在转换...")
            self.status_label.repaint()
            
            # 使用输出路径
            output_dir = self.output_path.text()
            
            # 执行转换
            if self.postman_radio.isChecked():
                output_file = convert_to_jmx(
                    'postman',
                    self.collection_path.text(),
                    self.env_path.text() if self.env_path.text() else None,
                    test_plan_name,
                    output_dir
                )
            else:
                output_file = convert_to_jmx(
                    'apipost',
                    self.apipost_path.text(),
                    None,
                    test_plan_name,
                    output_dir
                )
                
            self.status_label.setText("转换完成！")
            QMessageBox.information(
                self, 
                "成功", 
                f"转换完成！\n文件已保存至：{output_file}"
            )
        except Exception as e:
            self.status_label.setText("转换失败！")
            QMessageBox.critical(self, "错误", f"转换失败：{str(e)}")
