# -*- coding: utf-8 -*-
"""Lab4-RFM.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1144R8dKEO0OFR51gcBHaImC0xSCFZJ5e

# Лабораторная работа 4
## RFM-кластеризация покупателей (CRISP-DM)

Баранов Д.А. ИВТ 2.1

Data Understanding

Загрузка данных и структура таблицы
"""

import pandas as pd

# Загрузка данных
data = pd.read_csv('customer_segmentation_project.csv', encoding = 'ISO-8859-1')

# Общая информация о таблице
print("Размер данных:", data.shape)
print("\nТипы данных и наличие non-null:")
data.info()

# Просмотр первых 5 строк
print("\nПервые 5 строк таблицы:")
data.head()

"""Первичный обзор данных"""

print("Диапазон дат:", data['InvoiceDate'].min(), "до", data['InvoiceDate'].max())
print("Уникальных CustomerID:", data['CustomerID'].nunique())
print("Уникальных StockCode:", data['StockCode'].nunique())
print("Уникальных стран:", data['Country'].nunique())
print("\nТоп-5 стран по числу транзакций:")
print(data['Country'].value_counts().head())
print("\nПример кол-ва позиций в одном заказе (InvoiceNo = 536365):")
print(data[data['InvoiceNo'] == '536365'].shape[0], "строк")
data[data['InvoiceNo'] == '536365'].head()

"""Поиск пропусков и дубликатов"""

# Количество пропусков в кажом столбце
print(data.isna().sum())

# Удаление записей без CustomerID или Description
print("Удаляем записи с пустым CustomerID или Description")
initial_rows = data.shape[0]
data = data.dropna(subset = ['CustomerID', 'Description'])
print(f"Удалено строк с пустым CustomerID/Description: {initial_rows - data.shape[0]}")

# Поиск и удаление полных дубликатов
print("Ищем полные дубликаты")
initial_rows = data.shape[0]
data = data.drop_duplicates()
print(f"Удалено полных дубликатов: {initial_rows - data.shape[0]}")

print("Размер данных после очистки:", data.shape)

"""Разведочный анализ: выбросы и аномалии"""

# Статистика Quantity и UnitPrice
print(data[['Quantity', 'UnitPrice']].describe(percentiles = [0.01, 0.05, 0.95, 0.99]))

# Сколько транзакций с отрицательным Quantity (Возвраты)?
print("\nКоличество строк с Quantity < 0 (возвраты):", (data['Quantity'] < 0).sum())

# Сколько тразакций с ценой 0?
print("\nКоличество строк с UnitPrice = 0 (бесплатно):", (data['UnitPrice'] == 0).sum())

# Пример очень больших Quantity
print("\nТоп-5 по Quantity:")
print(data.nlargest(5, 'Quantity')[['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'UnitPrice']])

"""Подготовка данных (Data Preparation)"""

# Удалим транзакции с Quantity = 0 или UnitPrice = 0, если есть
initial_rows = data.shape[0]
data = data[(data['Quantity'] != 0 ) & (data['UnitPrice'] != 0)]
print(f"Удалено строк с Quantity = 0 или UnitPrice = 0: {initial_rows - data.shape[0]}")

# Проверим, сколько отрицательных Quantity осталось
print("Отрицательных Quantity осталось:", (data['Quantity'] < 0).sum())

"""TotalPrice"""

# Добавляем столбец общей стоимости по строке (цена * количество)
data['TotalPrice'] = data['UnitPrice'] * data['Quantity']

# Контроль: средняя и суммарная выручка по данным после очистки
print("Средняя сумма по строке:", round(data['TotalPrice'].mean(), 2))
print("Общая сумма всех транзакций:", round(data['TotalPrice'].sum(), 2))

"""Формировние RFM-признаков"""

import numpy as np
import pandas as pd

# Преобразуем InvoiceDate в datetime
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])

# Определяем reference_date как день после последней даты в данных (чтобы последний день имел recency 0)
reference_date = data['InvoiceDate'].max() + pd.Timedelta(days = 1)

# Агрегирование
# Для Frequency используем только положительные транзакции, иначе возврат повысит Frequency, что неправильно)
sales_data = data[data['InvoiceNo'].str.startswith('C') == False]
rfm = sales_data.groupby('CustomerID').agg(
    Recency = ('InvoiceDate', lambda x: (reference_date - x.max()).days),
    Frequency = ('InvoiceNo', 'nunique')
).reset_index()

# Monetary считаем по ВСЕМ данным (с учетом возвратов)
monetary = data.groupby('CustomerID').agg(Monetary = ('TotalPrice', 'sum')).reset_index()

# Объединяем таблицы
rfm = pd.merge(rfm, monetary, on = 'CustomerID', how = 'left').fillna({'Recency': np.nan, 'Frequency': 0, 'Monetary': 0})

print("Пример RFM для первых 5 клиентов:")
rfm.head(5)
print("Всего клиентов в RFM таблице:", rfm.shape[0])
print("Есть ли клиенты с отрицательным Monetary?", (rfm['Monetary'] < 0).any())

"""Анализ распределений R, F, M и обработка выбросов"""

# Рассмотрим распределение R, F, M
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize = (12, 4))
plt.subplot(1, 3, 1)
sns.histplot(rfm['Recency'], bins = 30)
plt.title("Recency распределение")
plt.subplot(1, 3, 2)
sns.histplot(rfm['Frequency'], bins = 30)
plt.title("Frequency распределение")
plt.subplot(1, 3, 3)
sns.histplot(rfm['Monetary'], bins = 30)
plt.title("Monetary распределение")
plt.show()

# Статистики и 95-99 перцентили
print(rfm[['Recency', 'Frequency', 'Monetary']].describe(percentiles = [0.95, 0.99]))

# Фильтр от выбросов
rfm_filtered = rfm[(rfm['Frequency'] <= 30) & (rfm['Monetary'] <= 20000)].copy()
print("Удалено клиентов-выбросов:", rfm.shape[0] - rfm_filtered.shape[0])

# Проверим размеры и описательные статистики после фильтрации
print("Оставшихся клиентов:", rfm_filtered.shape[0])
print(rfm_filtered[['Recency', 'Frequency', 'Monetary']].describe())

from sklearn.preprocessing import StandardScaler

# Стандартизация признаков RFM
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_filtered[['Recency', 'Frequency', 'Monetary']])

# Корреляционная матрица RFM
corr_matrix = rfm_filtered[['Recency', 'Frequency', 'Monetary']].corr()
sns.heatmap(corr_matrix, annot = True, cmap = "coolwarm")
plt.title("Корреляция между R, F, M")
plt.show()

"""Modeling

Выбор числа кластеров (K) для K-Means: метод "локтя" и коэффициент силуэта
"""

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

Ks = range(2, 11)
inertias = []
sil_scores = []

for k in Ks:
  kmeans = KMeans(n_clusters = k, init = 'k-means++', random_state = 42)
  kmeans.fit(rfm_scaled) # Обучение модели на стандаризированных данных
  inertias.append(kmeans.inertia_)
  # Оценка качества кластеризации силуэтом
  labels = kmeans.labels_
  sil_scores.append(silhouette_score(rfm_scaled, labels))

# Визуализация метрики локтя и силуэта
import matplotlib.pyplot as plt
plt.figure(figsize = (12, 5))
plt.subplot(1, 2, 1)
plt.plot(list(Ks), inertias, marker = 'o')
plt.title("Elbow Method")
plt.xlabel("K (число кластеров)")
plt.ylabel("Sum of squared distances (Inertia)")

plt.subplot(1, 2, 2)
plt.plot(list(Ks), sil_scores, marker = 'o', color = 'green')
plt.title("Silhouette Score")
plt.xlabel("K (число кластеров)")
plt.ylabel("Средний силуэт")
plt.show()

# Найдем максимальный силуэт и соответствующий K
best_k = Ks[sil_scores.index(max(sil_scores))]
print("Лучший K по силуэту:", best_k, "с оценкой", round(max(sil_scores), 3))

"""Применение K-Means с оптимальным K"""

optimal_k = best_k
kmeans_model = KMeans(n_clusters = optimal_k, init = 'k-means++', random_state = 42)
cluster_labels = kmeans_model.fit_predict(rfm_scaled)

# Метки кластеров в таблицу rfm_filtered
rfm_filtered['Cluster'] = cluster_labels

# Сколько клиентов в каждом кластере
print("Распределение количества клиентов по кластерам:")
print(rfm_filtered['Cluster'].value_counts())

"""Альтернативные алгоритмы кластеризации (DBSCAN, Hierarchical, GMM, Spectral)

DBSCAN (Density-Based Spatial Clustering of Applications with Noise):
"""

from sklearn.cluster import DBSCAN

# Настройка DBSCAN
# eps - радиус для соседей, min_samples - мин. точек для формирования кластера
dbscan = DBSCAN(eps = 0.5, min_samples = 5)
dbscan_labels = dbscan.fit_predict(rfm_scaled)
n_clusters_dbscan = len(set(dbscan_labels) - {-1})
print("DBSCAN нашел кластеров (не считая шум):", n_clusters_dbscan)
print("Шумовых точек (отмечено -1):", list(dbscan_labels).count(-1))

"""Иерархическая кластеризация (AgglomerativeClustering)"""

from sklearn.cluster import AgglomerativeClustering

agg = AgglomerativeClustering(n_clusters = optimal_k, metric = 'euclidean', linkage = 'ward')
agg_labels = agg.fit_predict(rfm_scaled)
print("Agglomerative кластеры распределения:")
print(pd.Series(agg_labels).value_counts())

# Построение дендрограммы (для небольших подвыборок)
from scipy.cluster.hierarchy import linkage, dendrogram

sample_index = np.random.choice(rfm_filtered.index, size = 100, replace = False)
sample_data = rfm_scaled[sample_index]
linked = linkage(sample_data, method = 'ward')
plt.figure(figsize = (10, 7))
dendrogram(linked, orientation = 'top')
plt.title("Dendrogram (sample of 100 customers)")
plt.show()

"""Gaussian Mixture (EM)

GMM
"""

from sklearn.mixture import GaussianMixture

best_gmm_k = None
best_gmm_score = -1
for k in Ks:
  gmm = GaussianMixture(n_components = k, random_state = 42)
  labels = gmm.fit_predict(rfm_scaled)
  score = silhouette_score(rfm_scaled, labels)
  if score > best_gmm_score:
    best_gmm_score = score
    best_gmm_k = k

print("Лучшее число кластеров для GMM по силуэту:", best_gmm_k, "силуэт:", round(best_gmm_score, 3))

# Получим метки кластеров для этого лучшего K
gmm_model = GaussianMixture(n_components = best_gmm_k, random_state = 42)
gmm_labels = gmm_model.fit_predict(rfm_scaled)

"""Spectral Clustering"""

from sklearn.cluster import SpectralClustering

spectral = SpectralClustering(n_clusters = optimal_k, affinity = 'rbf', assign_labels = 'kmeans', random_state = 42)
spectral_labels = spectral.fit_predict(rfm_scaled)
print("Spectral Clustering метки кластеров (первые 20):", spectral_labels[:20])
print("Распределение по кластерам Spectral:")
print(pd.Series(spectral_labels).value_counts())

"""Визуализация кластеров"""

import seaborn as sns
sns.pairplot(rfm_filtered, vars = ['Recency', 'Frequency', 'Monetary'], hue = 'Cluster', palette = 'tab10')
plt.suptitle("Pairplot RFM by Cluster", y = 1.02)
plt.show()

"""2D PCA проекция"""

from sklearn.decomposition import PCA

pca = PCA(n_components = 2)
rfm_pca = pca.fit_transform(rfm_scaled)
pca_df = pd.DataFrame(rfm_pca, columns = ['PC1', 'PC2'], index = rfm_filtered.index)
pca_df['Cluster'] = rfm_filtered['Cluster']

sns.scatterplot(data = pca_df, x = 'PC1', y = 'PC2', hue = 'Cluster', palette = 'tab10')
plt.title("Кластеры в пространстве главных компонент")
plt.show()

"""UMAP проекция"""

!pip install umap-learn

import umap
# Обучение UMAP на стандартизированных данных
reducer = umap.UMAP(n_neighbors = 15, min_dist = 0.1, random_state = 42)
rfm_umap = reducer.fit_transform(rfm_scaled)
umap_df = pd.DataFrame(rfm_umap, columns = ['UMAP1', 'UMAP2'], index = rfm_filtered.index)
umap_df['Cluster'] = rfm_filtered['Cluster']

sns.scatterplot(data = umap_df, x = 'UMAP1', y = 'UMAP2', hue = 'Cluster', palette = 'tab10')
plt.title("Clusters via UMAP projection")
plt.show()

"""Визуализация профилей кластеров: радарные диаграммы (Radar Charts)"""

cluster_summary = rfm_filtered.groupby('Cluster').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': 'mean',
    'CustomerID': 'count'
}).rename(columns = {'CustomerID': 'NumCustomers'})
cluster_summary = cluster_summary.round(1)
cluster_summary

"""Радарный график"""

import numpy as np

# Список категорий
categories = ['Recency', 'Frequency', 'Monetary']
num_vars = len(categories)

# Угол для каждой категории в радианах
angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
angles += [angles[0]] # замыкаем круг

# Подготовка полотна
plt.figure(figsize = (6, 6))
ax = plt.subplot(111, polar = True)

# Чертим одну окружность для максимального значения
max_values = cluster_summary[categories].max().values
ax.set_ylim(0, max(max_values))

# Подписи осей по кругу
plt.xticks(angles[:-1], categories)

# Для каждого кластера строим линию
for cluster, row in cluster_summary.iterrows():
  values = row[categories].tolist()
  values += [values[0]] # повторяем первый показатель в конец для замыкания
  ax.plot(angles, values, label = f'Cluster {cluster}')
  ax.fill(angles, values, alpha = 0.1)

plt.title("Средние RFM по кластерам (Radar Chart)")
plt.legend(loc = 'upper right', bbox_to_anchor = (1.3, 1.1))
plt.show()