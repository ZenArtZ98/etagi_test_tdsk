import pandas as pd
import matplotlib.pyplot as plt
import re
from pathlib import Path

INPUT_PATH = 'data/tdsk.csv'
OUTPUT_TABLE = 'output/active_objects_by_day.csv'
OUTPUT_GRAPH = 'output/active_by_room_month.png'

df = pd.read_csv(INPUT_PATH, sep='\t', encoding='utf-8')

df['actualized_at'] = pd.to_datetime(df['actualized_at'], utc=True, errors='coerce')

def extract_corpus_address(address):
    if pd.isna(address):
        return ''
    match = re.split(r'подъезд|кв\.|квартира', address, flags=re.IGNORECASE)[0]
    return match.strip().rstrip(',')

df['corpus_address'] = df['address'].apply(extract_corpus_address)

summary = (
    df.groupby([df['actualized_at'].dt.date, 'corpus_address'])
    .size()
    .reset_index(name='Кол-во активных квартир')
    .rename(columns={'actualized_at': 'Дата', 'corpus_address': 'Корпус'})
)

Path('output').mkdir(exist_ok=True)
summary.to_csv(OUTPUT_TABLE, index=False, encoding='utf-8-sig')

df['month'] = df['actualized_at'].dt.to_period('M').astype(str)
df = df[df['month'] != 'NaT']

monthly = df.groupby(['month', 'room_count']).size().unstack(fill_value=0)

monthly.plot(kind='bar', figsize=(12, 6))
plt.title('Количество активных квартир по месяцам в разрезе комнатности')
plt.xlabel('Месяц')
plt.ylabel('Количество активных квартир')
plt.grid(axis='y')
plt.legend(title='Комнатность')
plt.tight_layout()
plt.savefig(OUTPUT_GRAPH)

print("Готово: таблица и график сохранены.")