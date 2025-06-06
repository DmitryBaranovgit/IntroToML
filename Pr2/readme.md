# Практическая работа 2: Кластеризация студентов на основе опроса с использованием методов машинного обучения

## Цель работы
Сегментация студентов по их цифровым образовательным предпочтениям на основе результатов анкеты. Кластеризация позволяет выявить типичные профили студентов и использовать это для персонализации онлайн-курсов.

## Методология
Работа выполнена по этам процесса CRISP-DM:

1. **Понимание задачи**

Определена цель кластеризации - помощь университету в адаптации цифровых платформ под реальные потребности студентов.

3. **Понимание данных**
- Использован Excel-файл с анкетами студентов.
- Большинство признаков - бинарные (да/нет).
- Проведен первичный осмотр, визуализация распределений, проверка пропусков.

3. **Подготовка данных**
- Пропуски обработаны.
- Все бинарные признаки закодированы (0/1).
- Применено снижение размерности с помощью UMAP (`n_neighbors=15`, `min_dist=0.1, `metric='jaccard'`).

4. **Моделирование**
- Опробованы алгоритмы: KMeans, Agglomerative Clustering, GMM, DBSCAN, Fuzzy C-Means.
- Наилучший результат показал KMeans на 2D-пространстве UMAP (Silhouette = 0.86).

5. **Оценка**
- Рассчитаны метрики: Silhouette Score, Davies-Bouldin Index.
- Кластеры интерпретированы и названы: <Традиционалисты>, <Умеренные>, <Цифровые энтузиасты>.

6. **Визуализация**
- Построены радарные диаграммы профилей кластеров.
- Построено распределение студентов по кластерам внутри каждого факультета.

## Инструменты
- Python, Jupiter Notebook
- Pandas, scikit-learn, UMAP, matplotlib, seaborn

## Результат
Получена устойчивая кластеризация студентов, позволяющая:
- Выделить цифрово-активные и пассивные группы.
- Учитывать различия между факультетами.
- Сделать выводы для улучшения цифровых курсов.

## Структура проекта
- [Основной код и пояснения](student_survey_clustering_umap_kmeans.ipynb)
- [Описание проекта](readme.md)
