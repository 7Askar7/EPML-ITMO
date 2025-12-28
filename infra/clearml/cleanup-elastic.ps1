# PowerShell скрипт для очистки старых данных Elasticsearch
# Использование: .\cleanup-elastic.ps1 [days]
# По умолчанию удаляет индексы старше 30 дней

param(
    [int]$DaysOld = 30
)

Write-Host "Очистка Elasticsearch индексов старше $DaysOld дней..." -ForegroundColor Yellow

# Получаем дату для удаления
$cutoffDate = (Get-Date).AddDays(-$DaysOld)
$datePattern = $cutoffDate.ToString("yyyy.MM.dd")

Write-Host "Будут удалены индексы старше: $datePattern" -ForegroundColor Cyan

# Получение списка всех индексов
try {
    $indices = Invoke-RestMethod -Uri "http://localhost:9200/_cat/indices?format=json" -Method Get -ErrorAction Stop

    $deletedCount = 0
    foreach ($index in $indices) {
        $indexName = $index.index

        # Пропускаем системные индексы
        if ($indexName -match "^\.") {
            continue
        }

        # Проверяем дату в имени индекса (формат: *-YYYY.MM.DD)
        if ($indexName -match "(\d{4}\.\d{2}\.\d{2})") {
            $indexDate = [DateTime]::ParseExact($matches[1], "yyyy.MM.dd", $null)

            if ($indexDate -lt $cutoffDate) {
                Write-Host "Удаление индекса: $indexName (дата: $($matches[1]))" -ForegroundColor Red
                try {
                    Invoke-RestMethod -Uri "http://localhost:9200/$indexName" -Method Delete -ErrorAction Stop | Out-Null
                    $deletedCount++
                } catch {
                    Write-Host "Ошибка при удалении $indexName : $_" -ForegroundColor Red
                }
            }
        }
    }

    Write-Host "`nУдалено индексов: $deletedCount" -ForegroundColor Green

    # Оптимизация: принудительное слияние сегментов
    Write-Host "`nЗапуск оптимизации Elasticsearch..." -ForegroundColor Yellow
    docker exec clearml-elastic curl -X POST "http://localhost:9200/_forcemerge?only_expunge_deletes=true&max_num_segments=1" 2>$null

    Write-Host "`nОчистка завершена успешно!" -ForegroundColor Green

    # Показываем текущее использование места
    Write-Host "`nТекущее использование дискового пространства:" -ForegroundColor Cyan
    $stats = Invoke-RestMethod -Uri "http://localhost:9200/_cluster/stats" -Method Get
    $storeSize = [math]::Round($stats.indices.store.size_in_bytes / 1GB, 2)
    Write-Host "Elasticsearch занимает: $storeSize GB" -ForegroundColor White

} catch {
    Write-Host "Ошибка подключения к Elasticsearch: $_" -ForegroundColor Red
    Write-Host "Убедитесь, что ClearML Server запущен (make clearml-server-up)" -ForegroundColor Yellow
    exit 1
}
