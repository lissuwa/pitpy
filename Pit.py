import math
import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def make_func(s):
    if s.strip() == "":
        raise ValueError("Пустое выражение")

    env = {}
    for name in dir(math):
        if not name.startswith("_"):
            env[name] = getattr(math, name)

    def f(t, u):
        env["t"] = t
        env["u"] = u
        return float(eval(s, {}, env))

    f(0, 0)     
    return f


def rk4(f, t, u, h):
    k1 = f(t, u)
    k2 = f(t + h/2, u + h*k1/2)
    k3 = f(t + h/2, u + h*k2/2)
    k4 = f(t + h, u + h*k3)
    return u + h*(k1 + 2*k2 + 2*k3 + k4)/6


def trapez(f, t, u, h):
    fu = f(t, u)
    v = u + h * fu         

    for i in range(50):
        fv = f(t + h, v)
        g = v - u - h*(fu + fv)/2
        if abs(g) < 1e-12:
            break
        df = (f(t + h, v + 1e-7) - f(t + h, v - 1e-7)) / 2e-7
        v = v - g / (1 - h*df/2)

    return v


def solve(f, t0, T, u0, n, method):
    h = (T - t0) / n
    ts = [t0]
    us = [u0]
    t = t0
    u = u0

    for i in range(n):
        if method == "rk4":
            u = rk4(f, t, u, h)
        else:
            u = trapez(f, t, u, h)
        t = t + h
        ts.append(t)
        us.append(u)

    return ts, us

def on_solve():
    try:
        t0 = float(entry_t0.get().replace(",", "."))
        T  = float(entry_T.get().replace(",", "."))
        u0 = float(entry_u0.get().replace(",", "."))
        n  = int(entry_n.get())
    except:
        messagebox.showerror("Ошибка", "Проверьте числа")
        return

    if T <= t0 or n <= 0:
        messagebox.showwarning("Ошибка", "T должно быть > t0, N > 0")
        return

    try:
        f = make_func(entry_f.get())
    except Exception as e:
        messagebox.showerror("Ошибка в f(t, u)", str(e))
        return

    ax.clear()
    ax.set_xlabel("t")
    ax.set_ylabel("u(t)")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_title("u' = " + entry_f.get() + ",  u(" + str(t0) + ") = " + str(u0))

    log.delete("1.0", "end")

    if var_rk4.get():
        ts, us = solve(f, t0, T, u0, n, "rk4")
        ax.plot(ts, us, color="blue", label="RK4")
        log.insert("end", "RK4: u(T) = " + str(us[-1]) + "\n")

    if var_trap.get():
        ts, us = solve(f, t0, T, u0, n, "trap")
        ax.plot(ts, us, color="red", linestyle="--", label="Трапеций")
        log.insert("end", "Трапеций: u(T) = " + str(us[-1]) + "\n")

    ax.legend()
    canvas.draw()


def on_reset():
    """Кнопка "Сброс"."""
    ax.clear()
    ax.set_xlabel("t")
    ax.set_ylabel("u(t)")
    ax.set_title("Решение задачи Коши")
    ax.grid(True, linestyle="--", alpha=0.4)
    canvas.draw()
    log.delete("1.0", "end")


def on_save():
    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG", "*.png")])
    if path:
        fig.savefig(path, dpi=150)
        log.insert("end", "Сохранено: " + path + "\n")

root = tk.Tk()
root.title("Задача Коши")
root.geometry("1100x640")

left = tk.Frame(root)
left.pack(side="left", fill="both", expand=True)

fig = plt.Figure(figsize=(7, 5))
ax = fig.add_subplot(111)
ax.set_xlabel("t")
ax.set_ylabel("u(t)")
ax.set_title("Решение задачи Коши")
ax.grid(True, linestyle="--", alpha=0.4)

canvas = FigureCanvasTkAgg(fig, master=left)
canvas.get_tk_widget().pack(fill="both", expand=True)

right = tk.Frame(root, width=320)
right.pack(side="right", fill="y", padx=8, pady=8)
right.pack_propagate(False)

tk.Label(right, text="u'(t) = f(t, u)",
         font=("Arial", 13, "bold")).pack(pady=5)

tk.Label(right, text="f(t, u) =").pack(anchor="w")
entry_f = tk.Entry(right)
entry_f.insert(0, "sin(t) - u")
entry_f.pack(fill="x", pady=2)

tk.Label(right, text="t0 =").pack(anchor="w")
entry_t0 = tk.Entry(right)
entry_t0.insert(0, "0")
entry_t0.pack(fill="x", pady=2)

tk.Label(right, text="T =").pack(anchor="w")
entry_T = tk.Entry(right)
entry_T.insert(0, "8")
entry_T.pack(fill="x", pady=2)

tk.Label(right, text="u0 =").pack(anchor="w")
entry_u0 = tk.Entry(right)
entry_u0.insert(0, "0")
entry_u0.pack(fill="x", pady=2)

tk.Label(right, text="N шагов =").pack(anchor="w")
entry_n = tk.Entry(right)
entry_n.insert(0, "300")
entry_n.pack(fill="x", pady=2)

var_rk4  = tk.BooleanVar(value=True)
var_trap = tk.BooleanVar(value=True)
tk.Checkbutton(right, text="RK4 (синий)",
               variable=var_rk4).pack(anchor="w")
tk.Checkbutton(right, text="Трапеций (красный)",
               variable=var_trap).pack(anchor="w")

tk.Button(right, text="Решить", command=on_solve,
          bg="blue", fg="white", height=2).pack(fill="x", pady=5)
tk.Button(right, text="Сброс", command=on_reset,
          height=2).pack(fill="x", pady=2)
tk.Button(right, text="Сохранить график",
          command=on_save).pack(fill="x", pady=2)

tk.Label(right, text="Журнал:").pack(anchor="w", pady=(10, 0))
log = tk.Text(right, height=8, font=("Consolas", 9))
log.pack(fill="both")

root.mainloop()