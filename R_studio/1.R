# 创建身高体重数据
heights <- c(1.75, 1.68, 1.82)
weights <- c(72, 55, 85)

# 计算BMI
bmi <- weights / (heights ^ 2)

# 查看结果
print(bmi)

# 简单分析
mean(bmi)    # 平均BMI
max(bmi)     # 最大BMI
min(bmi)     # 最小BMI

# 绘制柱状图
barplot(bmi, 
        names.arg = c("Person1", "Person2", "Person3"),
        main = "BMI Comparison",
        col = c("lightblue", "lightgreen", "lightcoral"),
        ylab = "BMI Value",
        ylim = c(0, 30))
