# # Python code to emulate the given MATLAB logic with detailed output at each step
# a = 0xf5  # Initial value of a in hexadecimal
# b = 0x08  # Initial value of b in hexadecimal
# c = 0x04  # Initial value of c in hexadecimal
# d = 0x05  # Initial value of d in hexadecimal
# N = 16    # Number of iterations in decimal
#
# # Perform the loop for N iterations
# for i in range(N):
#     # First step: a + b
#     a_plus_b = a + b
#     print(f"Iteration {i+1}: a + b = {hex(a_plus_b)}")
#
#     # Second step: a + b - c
#     a_plus_b_minus_c = a_plus_b - c
#     print(f"Iteration {i+1}: a + b - c = {hex(a_plus_b_minus_c)}")
#
#     # Third step: (a + b - c) XOR d
#     result = a_plus_b_minus_c ^ d
#     print(f"Iteration {i+1}: (a + b - c) XOR d = {hex(result)}")
#
#     # Update a for the next iteration
#     a = result

# # Python code to emulate the given MATLAB logic with alternating sign 's' and detailed output
# a = 0xf5  # Initial value of a in hexadecimal
# b = 0x08  # Initial value of b in hexadecimal
# c = 0x04  # Initial value of c in hexadecimal
# d = 0x05  # Initial value of d in hexadecimal
# N = 16    # Number of iterations in decimal
# s = 1     # Initial value of s, which will alternate between 1 and -1
# 
# # Perform the loop for N iterations
# for i in range(N):
#     # First step: a + b
#     a_plus_b = a + b
#     print(f"Iteration {i+1}: a + b = {hex(a_plus_b)}")
#
#     # Second step: a + b + s*c
#     a_plus_b_plus_sc = a_plus_b + s * c
#     print(f"Iteration {i+1}: a + b + s*c = {hex(a_plus_b_plus_sc)}")
#
#     # Third step: (a + b + s*c) XOR d
#     result = a_plus_b_plus_sc ^ d
#     print(f"Iteration {i+1}: (a + b + s*c) XOR d = {hex(result)}")
#
#     # Update 'a' for the next iteration
#     a = result
#
#     # Alternate 's' between 1 and -1
#     s = -s
# import cmath
#
# # 定义虚数单位
# j = cmath.sqrt(-1)
#
# # 计算正切值
# tan_value = cmath.tan(0.329)
#
# # 计算分子和分母
# numerator = 60 + 40 * j + 50 * j * tan_value
# denominator = 50 + j * (60 + 40 * j) * tan_value
#
# # 计算整个表达式
# result = 50 * (numerator / denominator)
#
# # 输出结果
# print(result)



