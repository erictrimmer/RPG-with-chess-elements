extends Node

# Singleton for managing opening books
var _loaded_books = {}

func load_book(book_name: String) -> Dictionary:
	if _loaded_books.has(book_name):
		return _loaded_books[book_name]
	
	var path = "res://Data/OpeningBooks/" + book_name
	var file = FileAccess.open(path, FileAccess.READ)
	
	if not file:
		printerr("Failed to load opening book: ", path)
		return {}
	
	var json_string = file.get_as_text()
	file.close()
	
	var json = JSON.new()
	var error = json.parse(json_string)
	
	if error != OK:
		printerr("Failed to parse opening book JSON: ", path)
		return {}
	
	var book_data = json.data
	_loaded_books[book_name] = book_data
	print("Loaded opening book: ", book_name, " (", book_data.size(), " positions)")
	
	return book_data

func get_book_move(book_name: String, fen: String) -> String:
	var book = load_book(book_name)
	
	print("  [OpeningBookManager] Looking up FEN: '", fen, "'")
	
	if book.has(fen):
		print("  [OpeningBookManager] FOUND in book!")
		return book[fen]
	
	print("  [OpeningBookManager] NOT FOUND in book")
	print("  [OpeningBookManager] Available keys:")
	var count = 0
	for key in book.keys():
		if count < 3:  # Show first 3 for comparison
			print("    '", key, "'")
		count += 1
	
	return "" # No book move found

func clear_cache():
	_loaded_books.clear()
