import os
import numpy as np
import pandas as pd

def make_dummy_data():
    np.random.seed(42)
    n_samples = 1000
    
    # Generate dummy features for hazard susceptibility
    data = {
        'habitation_id': [f'H_{i}' for i in range(n_samples)],
        'elevation': np.random.uniform(100, 3000, n_samples),
        'slope': np.random.uniform(0, 45, n_samples),
        'rainfall': np.random.uniform(500, 3000, n_samples),
        'soil_type_idx': np.random.randint(0, 5, n_samples),
        # Target for CQR (Hazard severity index, for example)
        'hazard_severity': np.random.uniform(0, 100, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Create target directory
    os.makedirs('data/raw', exist_ok=True)
    df.to_csv('data/raw/data.csv', index=False)
    print("Dummy dataset generated at data/raw/data.csv")

if __name__ == "__main__":
    # To run relative to services/ml
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    make_dummy_data()
