import json

def process_transactions(file_path, output_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    transactions = data.get('transactions', [])
    
    total_sides = len(transactions)
    sales_sides = 0
    lease_sides = 0
    sales_gci = 0
    lease_gci = 0
    
    agents_sales = {} # {license: [count, volume]}
    agents_leases = {} # {license: [count, volume]}
    
    for tx in transactions:
        p_type = tx.get('property_type', '')
        close_price = tx.get('close_price', 0)
        agent_license = tx.get('agent_license')
        
        if 'Lease' in p_type:
            lease_sides += 1
            gci = close_price * 0.50
            lease_gci += gci
            if agent_license not in agents_leases:
                agents_leases[agent_license] = [0, 0]
            agents_leases[agent_license][0] += 1
            agents_leases[agent_license][1] += close_price
        else:
            sales_sides += 1
            gci = close_price * 0.03
            sales_gci += gci
            if agent_license not in agents_sales:
                agents_sales[agent_license] = [0, 0]
            agents_sales[agent_license][0] += 1
            agents_sales[agent_license][1] += close_price
            
    # Sort agents
    top_sales = sorted(agents_sales.items(), key=lambda x: x[1][0], reverse=True)[:5]
    top_leases = sorted(agents_leases.items(), key=lambda x: x[1][0], reverse=True)[:5]
    
    result = {
        "total_sides": total_sides,
        "sales_sides": sales_sides,
        "lease_sides": lease_sides,
        "sales_gci": sales_gci,
        "lease_gci": lease_gci,
        "top_sales": top_sales,
        "top_leases": top_leases
    }
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    import sys
    process_transactions(sys.argv[1], sys.argv[2])
