```python
sort(arr: List[Any], key: Callable[[Any], Any] = lambda x: x, reverse: bool = False)
```

内省排序`Introsort`，结合了多种排序算法的优点，以确保在各种情况下都能获得高效的性能，不返回列表。`arr`，待排序的列表。`key`，用于比较的键函数，自定义排序规则，而不必修改原始数据。`reverse`，是否降序排列，默认为升序。

Introsort, which combines the advantages of multiple sorting algorithms to ensure efficient performance in all cases. Does not return a list. `arr` is the list to be sorted. `key` is a function to extract a comparison key from each element, allowing custom sorting without modifying the original data. `reverse` specifies whether to sort in descending order (default is ascending).

```python
log(n, m, precision=50)
```

精确计算以`m`为底`n`的对数，参照`math.log()`参数顺序。默认保留50位小数，若计算结果非常接近整数，函数会返回四舍五入后的整数结果。`m`为对数的底数（`int/float/Decimal`类型），`n`为真数（`int/float/Decimal`类型），`precision`为可选的计算精度参数（整数类型，默认50位小数）。

Accurately calculate the logarithm of `n` with base `m`. Follow the parameter order of `math.log()`. The result retains 50 decimal places by default. If the calculation result is very close to an integer, the function will return the rounded integer value. `m` is the base of the logarithm (of type `int/float/Decimal`), `n` is the argument (of type `int/float/Decimal`), and `precision` is an optional calculation precision parameter (integer type, defaulting to 50 decimal places).

```python:
LaTeX(LaTeX_string: str)
```

> 目前支持功能 Currently supported functions
> 
> `i`, `j`, `\times`, `\div`, `\frac`, `\cfrac`, `\log`, `\sqrt`, `\cos`, `\sin`, `\tan`, `\cot`, `\sec`, `\csc`, `\arcsin`, `\arccos`, `\arctan`, `\ln`, `\exp`, `\pi`, `e`, `\lfloor ... \rfloor`, `\lceil ... \rceil`

使用`LaTeX()`包裹你的LaTeX字符串，即可获取LaTeX字符串的计算结果，内置许多详细报错。

Wrap your LaTeX string with `LaTeX()` to get the calculated result of the LaTeX string, with many detailed errors built in.
