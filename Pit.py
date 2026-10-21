import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QCheckBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

def create_function(expr):
    """Превращает строку в функцию f(t, u)"""
    if expr.strip() == "":
        raise ValueError("Пустое выражение")

    math_funcs = {}
    for name in dir(math):
        if not name.startswith("_"):
            math_funcs[name] = getattr(math, name)

    def f(t, u):
        result = eval(expr, {"__builtins__": {}}, {**math_funcs, "t": t, "u": u})
        return float(result)

    f(0, 0)
    return f


def rk4_step(f, t, u, h):
    """Один шаг метода Рунге-Кутты 4-го порядка"""
    k1 = f(t, u)
    k2 = f(t + h/2, u + h*k1/2)
    k3 = f(t + h/2, u + h*k2/2)
    k4 = f(t + h, u + h*k3)
    return u + h * (k1 + 2*k2 + 2*k3 + k4) / 6


def trap_step(f, t, u, h):
    """Один шаг неявного метода Трапеций (метод Ньютона)"""
    f_curr = f(t, u)
    v = u + h * f_curr 
    
    for i in range(50):
        f_next = f(t + h, v)
        g = v - u - (h/2) * (f_curr + f_next)
        if abs(g) < 1e-12:
            break
      
        df = (f(t + h, v + 1e-7) - f(t + h, v - 1e-7)) / 2e-7
        v = v - g / (1 - h*df/2)
        
    return v

def solve_ode(f, t0, T, u0, n, method):
    """Считает решение на всем отрезке"""
    h = (T - t0) / n
    ts = [t0]
    us = [u0]
    
    t = t0
    u = u0
    for i in range(n):
        if method == "rk4":
            u = rk4_step(f, t, u, h)
        else:
            u = trap_step(f, t, u, h)
        t += h
        ts.append(t)
        us.append(u)
        
    return ts, us

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Курсовая работа: Задача Коши")
        self.resize(1050, 650)
       
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        self.figure = Figure(figsize=(6, 5))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.grid(True, linestyle="--", alpha=0.5)
        self.ax.set_xlabel("t")
        self.ax.set_ylabel("u(t)")
        main_layout.addWidget(self.canvas, stretch=2)
        
        panel = QWidget()
        layout = QVBoxLayout(panel)
        main_layout.addWidget(panel, stretch=1)
        
        # Поля ввода
        layout.addWidget(QLabel("Уравнение f(t, u):"))
        self.eq_input = QLineEdit("-u") 
        layout.addWidget(self.eq_input)
        
        layout.addWidget(QLabel("Начальное время t0:"))
        self.t0_input = QLineEdit("0")
        layout.addWidget(self.t0_input)
        
        layout.addWidget(QLabel("Конечное время T:"))
        self.T_input = QLineEdit("5")
        layout.addWidget(self.T_input)
        
        layout.addWidget(QLabel("Начальное значение u0:"))
        self.u0_input = QLineEdit("1")
        layout.addWidget(self.u0_input)
        
        layout.addWidget(QLabel("Шагов N:"))
        self.n_input = QLineEdit("100")
        layout.addWidget(self.n_input)
    
        self.cb_rk4 = QCheckBox("Метод Рунге-Кутты (RK4)")
        self.cb_rk4.setChecked(True)
        layout.addWidget(self.cb_rk4)
        
        self.cb_trap = QCheckBox("Метод Трапеций")
        self.cb_trap.setChecked(True)
        layout.addWidget(self.cb_trap)
      
        self.btn = QPushButton("Решить")
        self.btn.setMinimumHeight(40)
        self.btn.clicked.connect(self.on_solve)
        layout.addWidget(self.btn)
        
        layout.addStretch() 

    def on_solve(self):
        """Обработка нажатия кнопки 'Решить'"""
        try:
            t0 = float(self.t0_input.text())
            T = float(self.T_input.text())
            u0 = float(self.u0_input.text())
            n = int(self.n_input.text())
           
            if T <= t0:
                QMessageBox.warning(self, "Ошибка", "T должно быть больше t0")
                return
            if n <= 0:
                QMessageBox.warning(self, "Ошибка", "N должно быть больше нуля")
                return
                
            f = create_function(self.eq_input.text())
            
            self.ax.clear()
            self.ax.grid(True, linestyle="--", alpha=0.5)
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("u(t)")
            self.ax.set_title(f"u' = {self.eq_input.text()}")
            
            if self.cb_rk4.isChecked():
                ts_rk4, us_rk4 = solve_ode(f, t0, T, u0, n, "rk4")
                self.ax.plot(ts_rk4, us_rk4, color="blue", label="RK4")
                
            if self.cb_trap.isChecked():
                ts_trap, us_trap = solve_ode(f, t0, T, u0, n, "trap")
                self.ax.plot(ts_trap, us_trap, color="red", linestyle="--", label="Трапеций")
                
            self.ax.legend()
            self.canvas.draw() 
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Что-то пошло не так:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
