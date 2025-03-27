from decimal import Decimal, ROUND_HALF_UP
import json

# --- 基础数据与专项扣除计算 ---
# 自2024年7月1日起，采用新的三倍社平数据
BASE = 36921.05  # 新社平基数
# 根据 BASE 计算的专项扣除（养老、医疗、失业、住房公积金）
deductions = [
    round(BASE * 0.08, 2),  # 养老保险
    round(BASE * 0.02, 2),  # 医疗保险
    round(BASE * 0.005, 2), # 失业保险
    round(BASE * 0.07)      # 公积金（保留整数）
]
DEDUCTIONS = sum(deductions)
print(f"special deduction is: {DEDUCTIONS}")

# 自2024年7月1日前，旧的三倍社平数据
BASE2 = 36549
# 根据 BASE2 计算的专项扣除（对应旧数据）
DEDUCTIONS2 = sum([
    round(BASE2 * 0.08, 2),  # 养老保险
    round(BASE2 * 0.02, 2),  # 医疗保险
    round(BASE2 * 0.005, 2), # 失业保险
    round(BASE2 * 0.07)      # 公积金（保留整数）
])
print(f"special deduction 2 is: {DEDUCTIONS2}")

# 起征点：每月 5000 元
TAXABLE_THRESHOLD = 5000

# --- 一次性奖金税额计算函数 ---
def calculate_bonus_tax(bonus):
    """
    计算一次性奖金的个人所得税。
    采用“单独计税”方式：将一次性奖金除以12，根据按月换算后的税率表确定税率及速算扣除数，
    然后计算总税额。

    参数:
        bonus -- 一次性奖金金额
    返回:
        字符串格式的奖金应缴税额（保留两位小数，严格四舍五入）
    """
    monthly_bonus = bonus / 12
    # 根据月均奖金确定适用的税率和速算扣除数（单位：元）
    if monthly_bonus <= 3000:
        tax_rate, quick_deduction = 0.03, 0
    elif monthly_bonus <= 12000:
        tax_rate, quick_deduction = 0.10, 210
    elif monthly_bonus <= 25000:
        tax_rate, quick_deduction = 0.20, 1410
    elif monthly_bonus <= 35000:
        tax_rate, quick_deduction = 0.25, 2660
    elif monthly_bonus <= 55000:
        tax_rate, quick_deduction = 0.30, 4410
    elif monthly_bonus <= 80000:
        tax_rate, quick_deduction = 0.35, 7160
    else:
        tax_rate, quick_deduction = 0.45, 15160

    bonus_tax = bonus * tax_rate - quick_deduction
    # 返回严格四舍五入的结果（字符串格式，两位小数）
    return f"{Decimal(bonus_tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"


# --- 累进税率表计算函数 ---
def compute_personal_income_tax(taxable_income):
    """
    根据超额累进税率表计算累计应缴个人所得税。
    税率表如下：
        - 不超过 36,000：3%
        - 36,000 至 144,000：10%，速算扣除数 2520
        - 144,000 至 300,000：20%，速算扣除数 16920
        - 300,000 至 420,000：25%，速算扣除数 31920
        - 420,000 至 660,000：30%，速算扣除数 52920
        - 660,000 至 960,000：35%，速算扣除数 85920
        - 超过 960,000：45%，速算扣除数 181920

    参数:
        taxable_income -- 累计应纳税所得额
    返回:
        字符串格式的累计应缴税额（保留两位小数，采用严格四舍五入）
    """
    tax_brackets = [
        (36000, 0.03, 0),
        (144000, 0.10, 2520),
        (300000, 0.20, 16920),
        (420000, 0.25, 31920),
        (660000, 0.30, 52920),
        (960000, 0.35, 85920),
        (float("inf"), 0.45, 181920),
    ]

    for limit, rate, deduction in tax_brackets:
        if taxable_income <= limit:
            tax = taxable_income * rate - deduction
            # 使用严格四舍五入（ROUND_HALF_UP）保留两位小数
            return f"{Decimal(tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"
    return "0.00"


# --- 年度税额计算函数 ---
def calculate_yearly_tax(monthly_incomes, monthly_deductions_addition, one_time_bonus=0, year=2024):
    """
    计算每个月的纳税情况，并计算一次性奖金的税额。
    累计收入、专项扣除和税额均按月份累积计算。
    注意：专项扣除使用不同标准：前6个月使用 DEDUCTIONS2（旧数据），后续使用 DEDUCTIONS（新数据）。

    参数:
        monthly_incomes -- 列表，包含各月税前收入（可少于12个月）
        monthly_deductions_addition -- 列表，包含各月专项附加扣除
        one_time_bonus -- 一次性奖金金额（默认为0，单独计税）
        year -- 当前年份（默认2024，用于判断使用哪套专项扣除数据）
    返回:
        JSON字符串，包含每个月的纳税详情以及总收入和总税额的汇总信息。
    """
    if len(monthly_incomes) != len(monthly_deductions_addition):
        raise ValueError("收入列表和专项附加扣除列表长度必须相同。")

    cumulative_income = 0       # 累计收入（前 N 个月收入之和）
    cumulative_tax = 0          # 累计已缴税额
    cumulative_month = 0        # 处理的月份数
    cumulative_deductions = 0   # 累计专项扣除总额（需要累加每个月使用的专项扣除）
    tax_details = []            # 存储每个月的详细纳税信息

    # 遍历所有月份，逐月计算
    for month in range(len(monthly_incomes)):
        income = monthly_incomes[month]
        additional_deduction = monthly_deductions_addition[month]
        cumulative_month += 1
        # 按月累积收入：直接求前 cumulative_month 个月的和
        cumulative_income = sum(monthly_incomes[:cumulative_month])
        # 根据当前月份选择专项扣除标准：7月1号前使用旧数据 DEDUCTIONS2，否则使用 DEDUCTIONS
        current_deductions = DEDUCTIONS2 if cumulative_month <= 7 and year == 2024 else DEDUCTIONS
        # 累加当前月份使用的专项扣除到累计扣除中
        cumulative_deductions += current_deductions

        # 计算累计应纳税所得额：
        # = 累计收入 - 累计专项扣除 - (起征点 * 累计月份) - 当月专项附加扣除
        taxable_income = cumulative_income - cumulative_deductions - TAXABLE_THRESHOLD * cumulative_month - additional_deduction

        # 计算累计应缴税额，并得出当月应缴税额（差值）
        total_tax = compute_personal_income_tax(taxable_income)
        tax_due = float(total_tax) - cumulative_tax
        cumulative_tax += tax_due

        # 当月税后收入 = 当月收入 - 当月应缴税额 - 当前专项扣除
        net_income = income - tax_due - current_deductions

        # 将本月的纳税详情保存到列表中，所有金额均以两位小数格式显示
        tax_details.append({
            "月份": cumulative_month,
            "税前收入": f"{income:.2f}",
            "当月应纳税额": f"{tax_due:.2f}",
            "累计应纳税所得额": f"{taxable_income:.2f}",
            "税后收入": f"{net_income:.2f}",
            "专项扣除": f"{current_deductions:.2f}",
            "专项扣除附加": f"{additional_deduction:.2f}"
        })

    # 计算一次性奖金的税额（单独计税，不计入月收入）
    bonus_tax = 0
    if one_time_bonus > 0:
        bonus_tax = calculate_bonus_tax(one_time_bonus)
        cumulative_tax += float(bonus_tax)

    # 总收入 = 各月收入总和 + 一次性奖金
    total_income = sum(monthly_incomes) + one_time_bonus
    # 总税额 = 各月应纳税额合计 + 一次性奖金税额
    total_tax = sum(float(entry["当月应纳税额"]) for entry in tax_details) + float(bonus_tax)

    summary = {
        "收入合计": f"{total_income:.2f}",
        "已申报税额合计": f"{total_tax:.2f}",
        "一次性奖金": f"{one_time_bonus:.2f}",
        "一次性奖金税额": f"{float(bonus_tax):.2f}"
    }

    print("\n=== 收入与税额合计 ===\n")
    print(json.dumps(summary, ensure_ascii=False, indent=4))

    return json.dumps(tax_details, ensure_ascii=False, indent=4)


# --- 示例使用 ---
# 这里提供一个示例，包含12个月的收入、各月不同的专项附加扣除以及一次性奖金
monthly_incomes = [1,2,3,4
    
]

monthly_deductions_addition = [2500, 5000, 7500, 10000, 12500, 6000, 7000, 8000, 36000, 40000, 44000, 48000]

one_time_bonus = 1

# 调用计算函数，并输出全年每个月的纳税情况（JSON格式）
tax_report_json = calculate_yearly_tax(monthly_incomes, monthly_deductions_addition, one_time_bonus)
print("\n=== 全年每个月的纳税情况 ===\n")
print(tax_report_json)
