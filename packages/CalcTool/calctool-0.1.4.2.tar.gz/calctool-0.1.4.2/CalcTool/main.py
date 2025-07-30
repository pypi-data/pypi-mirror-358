from typing import *
from decimal import *
from fractions import Fraction
import math, heapq, sys

def sort(arr: List[Any], key: Callable[[Any], Any] = lambda x: x, reverse: bool = False) -> None:
	"""使用内省排序对列表进行原地排序"""
	if len(arr) <= 1:
		return  # 已经有序或为空
	
	# 比较函数 - 使用 lambda 避免类型变量问题
	compare = lambda a, b: key(a) > key(b) if reverse else key(a) < key(b)
	
	# 计算最大递归深度
	max_depth = 2 * math.log2(len(arr)) if len(arr) > 0 else 0
	
	# 内省排序主循环
	def introsort(start: int, end: int, depth: float) -> None:
		while start < end:
			# 小规模数据使用插入排序
			if end - start <= 16:
				for i in range(start + 1, end + 1):
					current = arr[i]
					j = i - 1
					while j >= start and compare(current, arr[j]):
						arr[j + 1] = arr[j]
						j -= 1
					arr[j + 1] = current
				return
			
			# 递归深度过大时使用堆排序
			if depth <= 0:
				heap_size = end - start + 1
				
				# 构建堆
				for i in range(heap_size // 2 - 1, -1, -1):
					heapify(start, heap_size, i)
				
				# 一个个交换元素
				for i in range(heap_size - 1, 0, -1):
					arr[start], arr[start + i] = arr[start + i], arr[start]
					heapify(start, i, 0)
				return
			
			# 否则使用快速排序
			mid = (start + end) // 2
			a, b, c = start, mid, end
			
			# 三数取中法
			if compare(arr[b], arr[a]):
				arr[a], arr[b] = arr[b], arr[a]
			if compare(arr[c], arr[b]):
				arr[b], arr[c] = arr[c], arr[b]
			if compare(arr[b], arr[a]):
				arr[a], arr[b] = arr[b], arr[a]
			
			# 将基准值放到开头
			arr[start], arr[mid] = arr[mid], arr[start]
			pivot = arr[start]
			
			# 分区过程
			left = start + 1
			right = end
			
			while True:
				while left <= right and compare(arr[left], pivot):
					left += 1
				while left <= right and compare(pivot, arr[right]):
					right -= 1
				if left > right:
					break
				arr[left], arr[right] = arr[right], arr[left]
				left += 1
				right -= 1
			
			# 将基准值放到正确位置
			arr[start], arr[right] = arr[right], arr[start]
			pivot_index = right
			
			# 尾递归优化
			if pivot_index - start < end - pivot_index:
				introsort(start, pivot_index - 1, depth - 1)
				start = pivot_index + 1
			else:
				introsort(pivot_index + 1, end, depth - 1)
				end = pivot_index - 1
	
	# 堆排序辅助函数
	def heapify(start: int, heap_size: int, i: int) -> None:
		largest = i
		left = 2 * i + 1
		right = 2 * i + 2
		
		if left < heap_size and compare(arr[start + largest], arr[start + left]):
			largest = left
		
		if right < heap_size and compare(arr[start + largest], arr[start + right]):
			largest = right
		
		if largest != i:
			arr[start + i], arr[start + largest] = arr[start + largest], arr[start + i]
			heapify(start, heap_size, largest)
	
	# 启动内省排序
	introsort(0, len(arr) - 1, max_depth)

def log(n, m, precision=50):
    """
    精确计算以 m 为底 n 的对数 logₘ(n)
    
    参数:
    m (int/float/Decimal): 对数的底数 (必须大于 0 且不等于 1)
    n (int/float/Decimal): 真数 (必须大于 0)
    precision (int): 计算精度 (默认为 50 位小数)
    
    返回:
    Decimal: 高精度对数结果
    """
    # 检查输入是否有效
    if m <= 0 or m == 1:
        raise ValueError("The base must be greater than 0 and not equal to 1")
    if n <= 0:
        raise ValueError("The argument must be greater than 0")
    
    # 设置计算精度
    getcontext().prec = precision
    
    # 转换为 Decimal 类型进行高精度计算
    m_dec = Decimal(str(m))
    n_dec = Decimal(str(n))
    
    # 使用换底公式计算对数: logₘ(n) = ln(n) / ln(m)
    result = n_dec.ln() / m_dec.ln()
    
    # 检查结果是否非常接近整数
    int_result = result.to_integral_value(rounding=ROUND_HALF_UP)
    if abs(result - int_result) < Decimal('1e-10'):
        return int_result
    
    return result

def LaTeX(LaTeX_string: str):
    
    # 初始检查
    if "**" in LaTeX_string:
        raise NameError("'**' is not defined. Did you mean: '^'?")
    if "//" in LaTeX_string:
        raise NameError("'//' is not defined")
    if "！" in LaTeX_string:
        raise NameError("'！' is not defined. Did you mean: '!'?")
        
    # 初步分解LaTeX
    def Separate(LaTeX_string):
        global storage_pos, already_update_tag
        tag = []             # 存储解析后的LaTeX
        storage_pos = -1     # 在tag中应保存的位置
        current_tag = "None" # 现在的标签
        last_tag = "None"    # 上一个标签
        bracket_level = 0    # 目前括号嵌套层数
        # 对用户传入的字符串进行初步替换
        LaTeX_string = LaTeX_string\
        .replace(r'\left', '').replace(r'\right', '')\
        .replace('(', '{').replace(')', '}')\
        .replace("[]", "").replace("{}", "")\
        .replace(r"^\circ", r"*0.017453292519943295")

        # 存储新标签
        def storage_tag():
            global storage_pos
            tag.append([char, current_tag])
            storage_pos += 1 # 新标签的位置
        
        # 更新字符串
        def update_tag():
            global already_update_tag, storage_pos
            # 如果还未更新过字符串
            if already_update_tag == False:
                tag[storage_pos][0] += char # 在最新的字符串中增加现在的字符
                already_update_tag = True   # 标记已更新过字符串

        for i in range(len(LaTeX_string)):
            char = LaTeX_string[i]     # 本次循环的 字符
            already_update_tag = False # 每次循环重新设置未更新字符串
            
            # 如果是数字
            if char in "0123456789":
                # 如果在大括号中
                if bracket_level > 0:
                    update_tag()
                else:
                    current_tag = "number" # 标记标签为数字
                    storage_tag()
                    
            # 如果是小数点
            elif char == ".":
                # 如果在大括号中
                if bracket_level > 0:
                    update_tag()
                else:
                    current_tag = "decimal_point"
                    storage_tag()
            
            # 如果是字母
            elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
                # 如果在大括号中
                if bracket_level > 0:
                    update_tag()
                else:
                    # 如果上一个标签是"function"
                    if last_tag == "function":
                        update_tag()
                    else:
                        current_tag = "alphabet" # 标记标签为字母
                        storage_tag()
                        
            # 如果是反斜杠
            elif char == "\\":
                # 如果在大括号中
                if bracket_level > 0:
                    update_tag()
                else:
                    current_tag = "function" # 标记标签为功能
                    storage_tag()
            
            # 如果是运算符号
            elif char in "+-*×/÷":
                # 如果在大括号中
                if bracket_level > 0:
                    update_tag()
                else:
                    current_tag = "operator" # 标记标签为运算符
                    storage_tag()

            # 如果是上角标符号
            elif char == "^":
                try:
                    LaTeX_string[i+1]
                except IndexError:
                    raise SyntaxError("missing superscript argument") from None
                if i-1 == -1:
                    raise SyntaxError("missing superscript argument") from None

                # 如果在大括号中
                if bracket_level > 0:
                    update_tag()
                else:
                    current_tag = "superscript" # 标记标签为上角标
                    storage_tag()

            # 如果是下角标符号
            elif char == "_":
                try:
                    LaTeX_string[i+1]
                except IndexError:
                    raise SyntaxError("missing subscript argument") from None
                if i-1 == -1:
                    raise SyntaxError("missing subscript argument") from None
                    
                # 如果在大括号中
                if bracket_level > 0:
                    update_tag()
                else:
                    current_tag = "subscript" # 标记标签为下角标
                    storage_tag()

            # 如果是左中括号
            elif char == "[":
                current_tag = "in_parameter" # 标记标签为括号
                if bracket_level > 0:
                    update_tag()
                else:
                    storage_tag()
                bracket_level += 1 # 增加一层括号嵌套

            # 如果是右中括号
            elif char == "]":
                current_tag = "in_parameter"
                update_tag()
                bracket_level -= 1 # 减少一层括号嵌套
            
            # 如果是左大括号
            elif char == "{":
                current_tag = "in_bracket" # 标记标签为括号
                if bracket_level > 0:
                    update_tag()
                else:
                    storage_tag()
                bracket_level += 1 # 增加一层括号嵌套

            # 如果是右大括号
            elif char == "}":
                # 前面没有左括号直接报错
                if bracket_level == 0:
                    raise SyntaxError("extra close brace or missing open brace")
                current_tag = "in_bracket"
                update_tag()
                bracket_level -= 1 # 减少一层括号嵌套
            
            # 如果是空格
            elif char == " ":
                current_tag = "None" # 清空标签
            
            # 其他字符
            else:
                # 如果在大括号中
                if bracket_level > 0:
                    update_tag()
                else:
                    current_tag = "other" # 标记标签为其他
                    storage_tag()

            last_tag = current_tag # 记录现在的标签，即下个循环的上一个标签

        # 检测多出的左括号
        if bracket_level > 0:
            raise SyntaxError("extra open brace or missing close brace")

        return tag

    # 继续解析内层括号
    def Parse(tag):
        # 检查floor嵌套
        if tag.count([r"\lfloor", "function"]) > tag.count([r"\rfloor", "function"]):
            raise SyntaxError(r"extra \lfloor pr missing \rfloor")
        elif tag.count([r"\lfloor", "function"]) < tag.count([r"\rfloor", "function"]):
            raise SyntaxError(r"extra \rfloor or missing \lfloor")

        # 检查ceil嵌套
        if tag.count([r"\lceil", "function"]) > tag.count([r"\rceil", "function"]):
            raise SyntaxError(r"extra \lceil pr missing \rceil")
        elif tag.count([r"\lceil", "function"]) < tag.count([r"\rceil", "function"]):
            raise SyntaxError(r"extra \rceil or missing \lceil")

        checked_tag = tag
        # 转换运算符
        for para in checked_tag:
            # 转换乘号
            if para[0] in [r"\times", "×"]:
                para[0] = "*"        # 替换为"*"
                para[1] = "operator" # 标记标签为运算符
            # 转换除号
            elif para[0] in [r"\div", "÷"]:
                para[0] = "/"        # 替换为"/"
                para[1] = "operator" # 标记标签为运算符

        have_bracket = False
        
        # 先处理阶乘，防止括号内容被提前解析导致阶乘解析错误
        for i in range(len(checked_tag)*10):
            try:
                checked_tag[i]
            except IndexError:
                break

            if checked_tag[i][0] == "!":
                # 检查上一项是否是正整数
                if type(LaTeX(checked_tag[i-1][0])) != int:
                    raise SyntaxError("factorial is only supported for 'int' object")
                else:
                    if LaTeX(checked_tag[i-1][0]) < 0:
                        raise SyntaxError("factorial not defined for negative values")

                checked_tag = checked_tag[:i-1] + [
                    ["math.factorial", "string"],
                    ["{", "bracket"],
                    checked_tag[i-1],
                    ["}", "bracket"]
                ] + checked_tag[i+1:]
                
        # 处理其他
        for i in range(len(checked_tag)*10):
            try:
                checked_tag[i]
            except IndexError:
                break

            item = checked_tag[i][0]
            attribute = checked_tag[i][1]

            # 如果是分数
            if item in [r"\frac", r"\cfrac"]:
                try:
                    checked_tag[i+1]
                    checked_tag[i+2]
                except IndexError:
                    raise SyntaxError(r"missing argument for \frac" if item == r"\frac"
                        else r"missing argument for \cfrac") from None
                if checked_tag[i+1][0] + checked_tag[i+2][0] in "{}":
                    raise SyntaxError(r"missing argument for \frac" if item == r"\frac"
                        else r"missing argument for \cfrac")

                # 检查分母是否为0
                if LaTeX(checked_tag[i+2][0]) == 0:
                    raise ZeroDivisionError("denominator cannot be 0")

                checked_tag = checked_tag[:i] + [
                    ["{", "bracket"],
                    checked_tag[i+1],
                    ["/", "operator"],
                    checked_tag[i+2],
                    ["}", "bracket"]
                ] + checked_tag[i+3:]

            # 如果是根号
            elif item == r"\sqrt":
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \sqrt") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \sqrt")

                # 如果有中括号参数
                # \sqrt  [m]   {n}
                #  (i)  (i+1) (i+2)
                # -------------------
                #  {n}  ^{1/  {m}  }
                # (i+2)      (i+1)
                if checked_tag[i+1][1] == "in_parameter":
                    checked_tag = checked_tag[:i] + [
                        checked_tag[i+2],
                        ["^", "superscript"],
                        ["{", "bracket"],
                        ["1", "number"],
                        ["/", "operator"],
                        checked_tag[i+1],
                        ["}", "bracket"]
                    ] + checked_tag[i+3:]

                # 没有中括号参数
                # \sqrt  {n}
                #  (i)  (i+1)
                # -------------
                #  {n}   ^{1/2}
                # (i+1)
                else:
                    checked_tag = checked_tag[:i] + [
                        checked_tag[i+1],
                        ["^", "superscript"],
                        ["{", "bracket"],
                        ["1", "number"],
                        ["/", "operator"],
                        ["2", "number"],
                        ["}", "bracket"]
                    ] + checked_tag[i+2:]

            elif item == r"\log":
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \log") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \log")
                    
                # 定义底数
                # \log   _    {m}   {n}
                #  (i) (i+1) (i+2) (i+3)
                # -----------------------
                # math.log{  {n}  ,  {m}  }
                #           (i+3)   (i+2)
                if checked_tag[i+1][1] == "subscript":
                    try:
                        checked_tag[i+3]
                    except IndexError:
                        raise SyntaxError(r"missing argument for \log") from None
                    if checked_tag[i+1][0] in "{}":
                        raise SyntaxError(r"missing argument for \log")
                    if LaTeX(checked_tag[i+2][0]) < 0:
                        raise SyntaxError("log base must be a positive value")
                    if LaTeX(checked_tag[i+2][0]) == 1:
                        raise SyntaxError("log base cannot be 1")
                    if LaTeX(checked_tag[i+3][0]) < 0:
                        raise SyntaxError("log argument must be a positive value")
                    
                    checked_tag = checked_tag[:i] + [
                        ["math.log", "string"],
                        ["{", "bracket"],
                        checked_tag[i+3],
                        [",", "string"],
                        checked_tag[i+2],
                        ["}", "bracket"]
                    ] + checked_tag[i+4:]
                # 未定义底数
                # \log  {n}
                #  (i) (i+1)
                # ----------------
                # math.log10{  {n}  }
                #             (i+1)
                else:
                    checked_tag = checked_tag[:i] + [
                        ["math.log10", "string"],
                        ["{", "bracket"],
                        checked_tag[i+1],
                        ["}", "bracket"]
                    ] + checked_tag[i+2:]

            elif item == r"\cos":
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \cos") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \cos")

                checked_tag = checked_tag[:i] + [
                    ["math.cos", "string"],
                    ["{", "bracket"],
                    checked_tag[i+1],
                    ["}", "bracket"]
                ] + checked_tag[i+2:]

            elif item == r"\sin":
                error = False
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \sin") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \sin")

                checked_tag = checked_tag[:i] + [
                    ["math.sin", "string"],
                    ["{", "bracket"],
                    checked_tag[i+1],
                    ["}", "bracket"]
                ] + checked_tag[i+2:]

            elif item == r"\tan":
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \tan") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \tan")
                    
                checked_tag = checked_tag[:i] + [
                    ["math.tan", "string"],
                    ["{", "bracket"],
                    checked_tag[i+1],
                    ["}", "bracket"]
                ] + checked_tag[i+2:]

            elif item == r"\cot":
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \cot") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \cot")
                    
                checked_tag = checked_tag[:i] + [
                    ["1", "number"],
                    ["/", "operator"],
                    ["math.tan", "string"],
                    ["{", "bracket"],
                    checked_tag[i+1],
                    ["}", "bracket"]
                ] + checked_tag[i+2:]

            elif item == r"\sec":
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \sec") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \sec")
                    
                checked_tag = checked_tag[:i] + [
                    ["1", "number"],
                    ["/", "operator"],
                    ["math.cos", "string"],
                    ["{", "bracket"],
                    checked_tag[i+1],
                    ["}", "bracket"]
                ] + checked_tag[i+2:]

            elif item == r"\csc":
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \csc") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \csc")
                    
                checked_tag = checked_tag[:i] + [
                    ["1", "number"],
                    ["/", "operator"],
                    ["math.sin", "string"],
                    ["{", "bracket"],
                    checked_tag[i+1],
                    ["}", "bracket"]
                ] + checked_tag[i+2:]

            elif item == r"\arcsin":
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \arcsin") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \arcsin")
                    
                checked_tag = checked_tag[:i] + [
                    ["math.asin", "string"],
                    ["{", "bracket"],
                    checked_tag[i+1],
                    ["}", "bracket"]
                ] + checked_tag[i+2:]

            elif item == r"\arccos":
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \arccos") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \arccos")
                    
                checked_tag = checked_tag[:i] + [
                    ["math.acos", "string"],
                    ["{", "bracket"],
                    checked_tag[i+1],
                    ["}", "bracket"]
                ] + checked_tag[i+2:]

            elif item == r"\arctan":
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \arctan") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \arctan")
                    
                checked_tag = checked_tag[:i] + [
                    ["math.atan", "string"],
                    ["{", "bracket"],
                    checked_tag[i+1],
                    ["}", "bracket"]
                ] + checked_tag[i+2:]

            elif item == r"\ln":
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \ln") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \ln")
                    
                checked_tag = checked_tag[:i] + [
                    ["math.log", "string"],
                    ["{", "bracket"],
                    checked_tag[i+1],
                    ["}", "bracket"]
                ] + checked_tag[i+2:]

            elif item == r"\exp":
                try:
                    checked_tag[i+1]
                except IndexError:
                    raise SyntaxError(r"missing argument for \exp") from None
                if checked_tag[i+1][0] in "{}":
                    raise SyntaxError(r"missing argument for \exp")
                    
                checked_tag = checked_tag[:i] + [
                    ["math.exp", "string"],
                    ["{", "bracket"],
                    checked_tag[i+1],
                    ["}", "bracket"]
                ] + checked_tag[i+2:]

            # 解析当前层括号
            if checked_tag[i][1] in ["in_bracket", "in_parameter"]:
                # 插入解析内容
                checked_tag = checked_tag[:i] + [
                    ["{", "bracket"],                   # 插入前面的括号
                    *Separate(checked_tag[i][0][1:-1]), # 解析括号中内容
                    ["}", "bracket"]                    # 插入后面的括号
                ] + checked_tag[i+1:]                   # 无需第i项，直接使用i+1后的内容
                have_bracket = True                     # 标记找到括号
                break                                   # 解析完一个括号结束循环，先进行阶乘判断

        if have_bracket == False:
            # 没有括号可以解析，直接返回
            return checked_tag

        else:
            # 使用递归继续解析下一层括号
            return Parse(checked_tag)
    
    # 正式计算
    def Calculate(tag):
        calculate_string = []
        for i in range(len(tag)):
            item = tag[i][0]      # 获取第一项：字符串
            attribute = tag[i][1] # 获取第二项：标签(类型)

            # 检查小数点
            if attribute == "decimal_point":
                # 前面是否是数字
                if i-1 == -1 or tag[i-1][1] != "number":
                    raise SyntaxError("no numbers before the decimal point") 
                # 后面是否是数字
                if i+1 == len(tag) or tag[i+1][1] != "number":
                    raise SyntaxError("no numbers after the decimal point")
 
            # 无需替换
            if attribute in ["operator", "number", "string", "decimal_point"]:
                calculate_string.append(item) # 直接加入计算列表

            # 需要替换
            elif item == r"\lfloor":
                calculate_string.append("math.floor(")

            elif item == r"\rfloor":
                calculate_string.append(")")

            elif item == r"\lceil":
                calculate_string.append("math.ceil(")

            elif item == r"\rceil":
                calculate_string.append(")")

            elif item == "{":
                if tag[i-1][1] == "number":
                    calculate_string.append("*")
                calculate_string.append("(")

            elif item == "}":
                calculate_string.append(")")

            elif item == r"\pi":
                # 自动添加乘号防止报错
                if i-1 != -1 and (
                tag[i-1][1] == "number" or tag[i-1][0] in ["}", r"\pi", "e", "i", "j"]):
                    calculate_string.append("*")
                calculate_string.append("math.pi")

            elif item == "e":
                if i-1 != -1 and (
                tag[i-1][1] == "number" or tag[i-1][0] in ["}", r"\pi", "e", "i", "j"]):
                    calculate_string.append("*")
                calculate_string.append("math.e")
                
            elif item == "i" or item == "i":
                if i-1 != -1 and (
                tag[i-1][1] == "number" or tag[i-1][0] in ["}", r"\pi", "e", "i", "j"]):
                    calculate_string.append("*")
                calculate_string.append("(-1)**(1/2)")

            elif item == "^":
                calculate_string.append("**")

            # 未定义
            else:
                raise NameError(f"'{item}' is not defined")

        # 将计算列表中的字符串合并
        res = ''.join(calculate_string)

        # 最后检查
        if "/0" in res:
            raise ZeroDivisionError("division by zero")

        try:
            res = eval(res)

        except SyntaxError as e:
            if res == "":
                raise SyntaxError("empty LaTeX") from None
            raise SyntaxError(f"wrong character '{res[e.offset-1]}'") from None
        
        if res == ():
            raise SyntaxError("empty LaTeX")
            
        # 检测位数是否超过上限
        int_max_str_digits = 4300
        while True:
            try:
                str(res)
                break
            except ValueError:
                int_max_str_digits += 100
                sys.set_int_max_str_digits(int_max_str_digits)
            
        return res

    # 返回最终结果
    return Calculate(Parse(Separate(LaTeX_string)))