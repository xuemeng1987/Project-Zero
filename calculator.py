import math

def perform_operation(operation, num1=None, num2=None, height=None, base=None, time=None):
    try:
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
        elif operation == 'cylinder_volume':  # 圓柱體積
            if num1 is None or height is None:
                return "需要提供半徑和高度來計算圓柱體積！"
            volume = math.pi * math.pow(num1, 2) * height
            return f"π * {num1}^2 * {height}\n結果：{volume}"
        elif operation == 'circle_area':  # 圓的面積
            if num1 is None:
                return "需要提供半徑來計算圓的面積！"
            area = math.pi * math.pow(num1, 2)
            return f"π * {num1}^2\n結果：{area}"
        elif operation == 'triangle_area':  # 三角形面積
            if base is None or height is None:
                return "需要提供底和高度來計算三角形面積！"
            area = 0.5 * base * height
            return f"0.5 * {base} * {height}\n結果：{area}"
        elif operation == 'sphere_volume':  # 球的體積
            if num1 is None:
                return "需要提供半徑來計算球的體積！"
            volume = (4 / 3) * math.pi * math.pow(num1, 3)
            return f"(4/3) * π * {num1}^3\n結果：{volume}"

        elif operation == 'hypotenuse':  # 斜邊長度計算 (畢達哥拉斯定理)
            if num1 is None or num2 is None:
                return "需要提供兩條直角邊的長度來計算斜邊！"
            hypotenuse = math.sqrt(math.pow(num1, 2) + math.pow(num2, 2))
            return f"√({num1}^2 + {num2}^2)\n結果：{hypotenuse}"

        elif operation == 'speed':  # 速度計算 (速度 = 距離 / 時間)
            if num1 is None or time is None:
                return "需要提供距離和時間來計算速度！"
            speed = num1 / time
            return f"距離 ÷ 時間\n結果：{speed} 單位/時間"

        else:
            return "無效的運算！"
    
    except ValueError:
        return "輸入的數據無效！"
