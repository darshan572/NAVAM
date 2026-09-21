from copulas.multivariate import GaussianMultivariate
import pandas as pd
import numpy as np

def fit_copula(flood_probs, landslide_probs):
    data = pd.DataFrame({
        'flood': flood_probs,
        'landslide': landslide_probs
    })
    
    copula = GaussianMultivariate()
    copula.fit(data)
    return copula

def generate_joint_scenarios(copula_model, n_samples=1000):
    return copula_model.sample(n_samples)

if __name__ == "__main__":
    print("Testing copula fusion...")
    # Dummy test
    fp = np.random.uniform(0, 1, 100)
    lp = np.random.uniform(0, 1, 100)
    model = fit_copula(fp, lp)
    samples = generate_joint_scenarios(model, 5)
    print("Generated Scenarios:\n", samples)
