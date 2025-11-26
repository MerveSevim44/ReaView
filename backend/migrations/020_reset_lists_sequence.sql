-- Reset lists sequence to prevent duplicate key violations
-- Bu migration lists tablosunun list_id sequence'ini reset eder

-- Sequence'i kontrol et ve maksimum list_id'ye göre ayarla
SELECT SETVAL('lists_list_id_seq', (SELECT MAX(list_id) FROM lists), true);
