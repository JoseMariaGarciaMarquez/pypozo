import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from welly import Well
from welly import project
from welly import Synthetic
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


ruta1 = "data/PALO BLANCO 791_PROCESADO.las"
well = Well.from_las(ruta1)


gr = well.data['GR'].values
m1r6 = well.data['M1R6'].values
phie = well.data['PHIE'].values
zden = well.data['ZDEN'].values
dts = well.data['DTS'].values


print(f"Longitud de GR: {len(gr)}")
print(f"Longitud de M1R6: {len(m1r6)}")
print(f"Longitud de PHIE: {len(phie)}")
print(f"Longitud de ZDEN: {len(zden)}")
print(f"Longitud de DTS: {len(dts)}")


min_length = min(len(gr), len(m1r6), len(phie), len(zden), len(dts))


gr = gr[:min_length]
m1r6 = m1r6[:min_length]
phie = phie[:min_length]
zden = zden[:min_length]
dts = dts[:min_length]

df = pd.DataFrame({
    'GR': gr,
    'M1R6': m1r6,
    'PHIE': phie,
    'ZDEN': zden,
    'DTS': dts
})


df.dropna(inplace=True)


df['LITHOLOGY'] = np.where(df['ZDEN'] > 2.5, 'Limestone', 'Sandstone')


X = df[['GR', 'M1R6', 'PHIE', 'ZDEN', 'DTS']]
y = df['LITHOLOGY']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)


y_pred = clf.predict(X_test)


accuracy = accuracy_score(y_test, y_pred)
classification_rep = classification_report(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

print("Accuracy:", accuracy)
print("Classification Report:\n", classification_rep)


plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", xticklabels=clf.classes_, yticklabels=clf.classes_)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()