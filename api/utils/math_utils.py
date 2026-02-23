def calculate_pipeline_metrics(opps):
    valid_opps = [o for o in opps if o.get('estimatedvalue')]
    all_values = sorted([o['estimatedvalue'] for o in valid_opps])
    median_deal_size = all_values[len(all_values) // 2] if all_values else 0
    top_25_deal_size = all_values[int(len(all_values) * 0.75)] if all_values else 0
    total_open_pipeline = sum(o['estimatedvalue'] for o in valid_opps)
    weighted_forecast = sum(o['estimatedvalue'] * (o.get('closeprobability') or 0) / 100 for o in valid_opps)
    
    return {
        "median_deal_size": median_deal_size,
        "top_25_deal_size": top_25_deal_size,
        "total_open_pipeline": total_open_pipeline,
        "weighted_forecast": weighted_forecast
    }
