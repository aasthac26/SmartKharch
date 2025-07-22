def check_budget_exceedance(df, budget_dict):
    alerts = []
    for category, budget in budget_dict.items():
        spent = df[df['Category'] == category]['Amount'].sum()
        if spent > budget:
            alerts.append(f"⚠️ Overspent in {category}: ₹{spent} (Budget: ₹{budget})")
    return alerts

def compare_monthly_spending(df, category_col='Category', amount_col='Amount', month_col='Month'):
    alerts = []
    categories = df[category_col].unique()
    
    for cat in categories:
        cat_data = df[df[category_col] == cat]
        monthly = cat_data.groupby(month_col)[amount_col].sum().sort_index()
        
        for i in range(1, len(monthly)):
            prev = monthly.iloc[i - 1]
            curr = monthly.iloc[i]
            if prev > 0 and (curr - prev) > 0.2 * prev:
                alerts.append(f"🔺 Spending on **{cat}** increased by more than 20% in {monthly.index[i]}")
    
    return alerts
