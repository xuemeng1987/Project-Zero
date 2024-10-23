import math
import sympy as sp #new add
import numpy as np #new add

def perform_operation(operation, num1=None, num2=None, height=None, base=None, time=None, A=None, B=None, x=None, data=None):
    try:
        # 1. 基本運算符
        if operation == 'add':  # 加法
            return f"{num1} + {num2}\n結果：{num1 + num2}"
        elif operation == 'subtract':  # 減法
            return f"{num1} - {num2}\n結果：{num1 - num2}"
        elif operation == 'multiply':  # 乘法
            return f"{num1} * {num2}\n結果：{num1 * num2}"
        elif operation == 'divide':  # 除法
            if num2 == 0:
                return "無法除以0！"
            return f"{num1} ÷ {num2}\n結果：{num1 / num2}"
        elif operation == 'power':  # 指數運算
            return f"{num1}^{num2}\n結果：{math.pow(num1, num2)}"
        elif operation == 'sqrt':  # 平方根
            return f"√{num1}\n結果：{math.sqrt(num1)}"
        elif operation == 'log':  # 對數
            if num2 is None:
                return f"log({num1})\n結果：{math.log(num1)}"
            else:
                return f"log({num1}, {num2})\n結果：{math.log(num1, num2)}"
        elif operation == 'sin':  # 正弦
            return f"sin({num1})\n結果：{math.sin(math.radians(num1))}"
        elif operation == 'cos':  # 餘弦
            return f"cos({num1})\n結果：{math.cos(math.radians(num1))}"
        elif operation == 'tan':  # 正切
            return f"tan({num1})\n結果：{math.tan(math.radians(num1))}"

        # 2. 集合運算符
        elif operation == 'union':  # 聯集
            return f"{A} ∪ {B}\n結果：{A | B}"
        elif operation == 'intersection':  # 交集
            return f"{A} ∩ {B}\n結果：{A & B}"
        elif operation == 'subset':  # 子集
            return f"{A} ⊆ {B}\n結果：{A <= B}"
        elif operation == 'element_of':  # 元素屬於集合
            return f"{x} ∈ {A}\n結果：{x in A}"
        
        # 3. 幾何符號
        elif operation == 'circle_area':  # 圓的面積
            return f"π * {num1}^2\n結果：{math.pi * math.pow(num1, 2)}"
        elif operation == 'triangle_area':  # 三角形面積
            return f"0.5 * {base} * {height}\n結果：{0.5 * base * height}"
        elif operation == 'cylinder_volume':  # 圓柱體積
            return f"π * {num1}^2 * {height}\n結果：{math.pi * math.pow(num1, 2) * height}"

        # 4. 微積分符號
        elif operation == 'derivative':  # 導數
            x = sp.symbols('x')
            f = sp.Function('f')(x)
            return f"f'(x)\n結果：{sp.diff(f, x)}"
        elif operation == 'integral':  # 積分
            return f"∫f(x)dx\n結果：{sp.integrate(f, x)}"

        # 5. 邏輯與集合論符號
        elif operation == 'and':  # 邏輯與
            return f"{num1} ∧ {num2}\n結果：{num1 and num2}"
        elif operation == 'or':  # 邏輯或
            return f"{num1} ∨ {num2}\n結果：{num1 or num2}"
        elif operation == 'not':  # 否定
            return f"¬{num1}\n結果：{not num1}"

        # 6. 矩陣與向量符號
        elif operation == 'matrix_determinant':  # 行列式
            matrix = np.array([[num1, num2], [height, base]])  # 示例2x2矩陣
            return f"|A|\n結果：{np.linalg.det(matrix)}"
        elif operation == 'matrix_transpose':  # 矩陣轉置
            matrix = np.array([[num1, num2], [height, base]])
            return f"A^T\n結果：\n{matrix.T}"

        # 7. 統計與概率符號
        elif operation == 'mean':  # 平均值
            return f"μ\n結果：{sum(data) / len(data)}"
        elif operation == 'variance':  # 方差
            return f"Var(X)\n結果：{np.var(data)}"

        # 8. 特殊符號與其他運算
        elif operation == 'hypotenuse':  # 斜邊長度計算 (畢達哥拉斯定理)
            return f"√({num1}^2 + {num2}^2)\n結果：{math.sqrt(math.pow(num1, 2) + math.pow(num2, 2))}"
        elif operation == 'speed':  # 速度計算
            return f"距離 ÷ 時間\n結果：{num1 / time} 單位/時間"
        
        else:
            return "無效的運算！"

    except ValueError:
        return "輸入的數據無效！"
