-- Reset lists_item sequence
-- Bu migration lists_item tablosunun sequence'ini resetler ve max ID'den başlatır

SELECT SETVAL('lists_item_list_item_id_seq', (SELECT MAX(list_item_id) FROM lists_item), true);
