from fastapi import FastAPI
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer

app = FastAPI()

@app.post("/predict_migration/")
def predict_migration():
    data = pd.read_csv('datos.csv')  # Update the URL
    argentina_data = data[data['country'] == 'Argentina']
    
    feature = 'Unemployment_Total_of_Total_Labor_Force'
    
    unemployment_2023 = 6.9
    
    input_data_2023 = [[unemployment_2023]]
    
    imputer = SimpleImputer(strategy='mean')
    
    X = argentina_data[[feature]]
    X_imputed = imputer.fit_transform(X)
    
    model = LinearRegression()
    
    y = argentina_data['Net_Migration']
    y = y.fillna(0)
    
    model.fit(X_imputed, y)
    
    predicted_migration_2023 = model.predict(input_data_2023)
    
    return {"predicted_migration": predicted_migration_2023[0]}
print(predict_migration())











