#!/bin/bash
# Bash скрипт для очистки старых данных Elasticsearch (для Linux/Mac/WSL)
# Использование: ./cleanup-elastic.sh [days]
# По умолчанию удаляет индексы старше 30 дней

DAYS_OLD=${1:-30}

echo "Очистка Elasticsearch индексов старше $DAYS_OLD дней..."

# Получаем дату для удаления
CUTOFF_DATE=$(date -d "$DAYS_OLD days ago" +%Y.%m.%d 2>/dev/null || date -v-${DAYS_OLD}d +%Y.%m.%d)

echo "Будут удалены индексы старше: $CUTOFF_DATE"

# Получение списка всех индексов
INDICES=$(curl -s "http://localhost:9200/_cat/indices?format=json")

if [ $? -ne 0 ]; then
    echo "Ошибка подключения к Elasticsearch"
    echo "Убедитесь, что ClearML Server запущен (make clearml-server-up)"
    exit 1
fi

DELETED_COUNT=0

# Обработка каждого индекса
echo "$INDICES" | jq -r '.[].index' | while read -r index_name; do
    # Пропускаем системные индексы
    if [[ "$index_name" == .* ]]; then
        continue
    fi

    # Извлекаем дату из имени индекса (формат: *-YYYY.MM.DD)
    if [[ "$index_name" =~ ([0-9]{4}\.[0-9]{2}\.[0-9]{2}) ]]; then
        INDEX_DATE="${BASH_REMATCH[1]}"

        # Сравниваем даты
        if [[ "$INDEX_DATE" < "$CUTOFF_DATE" ]]; then
            echo "Удаление индекса: $index_name (дата: $INDEX_DATE)"
            curl -s -X DELETE "http://localhost:9200/$index_name" >/dev/null
            ((DELETED_COUNT++))
        fi
    fi
done

echo ""
echo "Удалено индексов: $DELETED_COUNT"

# Оптимизация: принудительное слияние сегментов
echo ""
echo "Запуск оптимизации Elasticsearch..."
docker exec clearml-elastic curl -s -X POST "http://localhost:9200/_forcemerge?only_expunge_deletes=true&max_num_segments=1" >/dev/null 2>&1

echo ""
echo "Очистка завершена успешно!"

# Показываем текущее использование места
echo ""
echo "Текущее использование дискового пространства:"
STATS=$(curl -s "http://localhost:9200/_cluster/stats")
STORE_SIZE=$(echo "$STATS" | jq -r '.indices.store.size_in_bytes')
STORE_GB=$(awk "BEGIN {printf \"%.2f\", $STORE_SIZE/1024/1024/1024}")
echo "Elasticsearch занимает: $STORE_GB GB"
