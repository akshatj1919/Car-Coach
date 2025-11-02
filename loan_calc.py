def calculate_monthly_payment(principal: float, annual_rate_percent: float, years: int) -> float:
    r = (annual_rate_percent / 100.0) / 12.0  # monthly rate
    n = years * 12
    if n <= 0:
        raise ValueError("Years must be positive.")
    if principal < 0:
        raise ValueError("Deposit cannot exceed price.")
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


# recursive total calculation
def total_payment(monthly: float, months: int) -> float:
    if months == 0:
        return 0
    return monthly + total_payment(monthly, months - 1)


def money(x: float) -> str:
    return f"${x:,.2f}"  # Formating money with 2 decimal places