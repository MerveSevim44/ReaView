-- Reset items sequence to max item_id
-- Bu migration silinen item'lar nedeniyle oluşan boşlukları düzeltir
-- Sequence, tablodaki en yüksek item_id'den sonraya ayarlanır

SELECT setval('items_item_id_seq', (SELECT MAX(item_id) FROM items), true);
