import os
import sqlite3
import sys
import termios
import time
import tty
import subprocess
import shutil
from pathlib import Path
from pypdf import PdfReader
from rich.console import Console
from rich.rule import Rule
from rich.panel import Panel
from rich.align import Align
from rich.columns import Columns
from rich.padding import Padding

CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"
ERROR_MSG = "Invalid option! Try it again"
AUTHOR = "tashi"
VERSION = "0.0.1"

def main():
  setup_app()

def add_book():
  clear_terminal()

  is_on_dir = check_option(
    "Point book's location",
    [
      "0) Is on book's directory",
      "1) It's not on book's directory",
      "2) Quit"
    ],
    ERROR_MSG,
    ["0", "1", "2"],
    True,
  )

  match is_on_dir:
    case "0":
      type_or_select = check_option(
        "Choose between selecting manually or typing the file name to add",
        [
          "0) Open select list",
          "1) Type file name",
          "2) Quit"
        ],
        ERROR_MSG,
        ["0", "1", "2"],
        True,
      )
      match type_or_select:
        case "0":
          select_file(push_book)
          return
        case "1":
          type_file(push_book)
          return
        case "2":
          clear_terminal()
          return 
    case "1":
      clear_terminal()

      while True:
        console.rule("Enter full path (including filename) or '0' to quit")
        file_path = tevah_input()
        file_path = file_path.strip()

        if file_path == "0":
          return

        file_path = Path(file_path)

        if file_path.exists() and file_path.is_file():
          break

        clear_terminal()
        print("\n   File doesn't exists, try it again!\n")
   
      cpmv_or_add = check_option(
        "Copy, move or just add to database",
        [
          "0) Copy to book's directory",
          "1) Move to book's directory",
        ],
        ERROR_MSG,
        ["0", "1"],
        True,
      )
      
      books_path = cursor.execute("SELECT books_path FROM library").fetchone()[0]
      destination = Path(books_path) / file_path.name

      match cpmv_or_add:
        case "0":
          try:
            shutil.copy(file_path, destination)
            print("copied!")
          except FileNotFoundError:
            print("file not found")
          except Exception as e:
            print(f"Error: {e}")
        case "1":
          try:
            shutil.move(file_path, destination)
          except FileNotFoundError:
            print("file not found")
          except Exception as e:
            print(f"Error: {e}")

      files = os.listdir(books_path)
      files = [f for f in files if f.endswith(".pdf")]

      for index, file in enumerate(files):
        if file == file_path.name:
          push_book(files, index)

    case "2":
      clear_terminal()
      return

def tevah_input(input_msg=""):
  console.print("\n=", style="blue", end="")
  console.print("תֵּבָה", style="red", end="")
  console.print("> ", style="blue", end="")
  return str(input(input_msg))


def check_option(title, avaliable_opts, error_msg, options, lower, menu=False, clear=True, execute=None):
  if clear:
    clear_terminal()
    
  
  while True:
    if execute:
      execute()

    if menu:
      console.print(f"\n{title}", style="red")
      console.print(f"version {VERSION} by {AUTHOR}\n", style="italic")
    else:
      if not title == "":
        console.print(Rule(f"{title}", align="center"))
    
    for option in avaliable_opts:
      print(f"\t{option}")

    res = tevah_input() 
    res = res.lower() if lower else res
    if res in options:
      break
    clear_terminal()
    console.print(f"[bold]{error_msg}[/bold]", style="red")

  return res


def clear_terminal():
  os.system(CLEAR_COMMAND)


def downarrow(items, item_index_track, books=False):
  if books:
    if item_index_track == len(items) - 1:
      item_index_track = 0
      for index, item in enumerate(items):
          if index == 0:
            print(f">  {item['title'].split(':')[0]}: {item['filename']}")
          else:
            print(f"   {item['title'].split(':')[0]}: {item['filename']}")
    else:
      item_index_track = item_index_track + 1
      for index, item in enumerate(items):
          if index == item_index_track:
            print(f">  {item['title'].split(':')[0]}: {item['filename']}")
          else:
            print(f"   {item['title'].split(':')[0]}: {item['filename']}")
  else:
    if item_index_track == len(items) - 1:
      item_index_track = 0
      for index, item in enumerate(items):
        if index == 0:
          print(f">  {item}")
        else:
          print(f"   {item}")
    else:
      item_index_track = item_index_track + 1
      for index, item in enumerate(items):
        if index == item_index_track:
          print(f">  {item}")
        else:
          print(f"   {item}")

  return item_index_track


def display_elapsed(elapsed):
  hours, remainder = divmod(elapsed, 3600)
  minutes, seconds = divmod(remainder, 60)

  if hours > 0:
    print(f"Elapsed time: {hours}h {minutes}m {seconds}s")
  elif minutes > 0:
    print(f"Elapsed time: {minutes}m {seconds}s")
  else:
    print(f"Elapsed time: {seconds}s")

def edit_book():
  options = ["0", "1", "2"]

  selected = check_option(
    "Choose between selecting manualy or typing the file name to edit",
    ["0) Select", "1) Type", "2) Quit"],
    ERROR_MSG,
    options,
    True
  )

  match selected:
    case "0":
      select_file(change_details)
    case "1":
      type_file(change_details)
    case "2":
      clear_terminal()
      return

def change_details(files, file_index_track):
  clear_terminal()

  books = cursor.execute("SELECT * FROM Books").fetchall()

  for book in books:
    if book["filename"] == files[file_index_track]["filename"]:
      book_to_edit = book["filename"]
      break
  
  options = ["0", "1", "2", "3"]
  option_to_edit = check_option(
    "Select an option to edit",
    ["0) Change title", "1) Change author", "2) Change readed", "3) Quit"],
    ERROR_MSG,
    options,
    True
  )

  clear_terminal()

  match option_to_edit:
    case "0":
      console.rule("Insert the new title")
      title = str(input("Title: "))
      cursor.execute("UPDATE books SET title = ? WHERE filename = ?", (title, book_to_edit))
      connection.commit()
    case "1":
      console.rule("Insert the new author name")
      author = str(input("Author: "))
      cursor.execute("UPDATE books SET author = ? WHERE filename = ?", (author, book_to_edit))
      connection.commit()
    case "2":
      console.rule("Mark as readed or not readed")
      current_state = cursor.execute("SELECT readed FROM books WHERE filename = ?", (book_to_edit,)).fetchone()[0]
      get_status    = "readed" if current_state else "not readed"

      print(f"\n   Current state: {get_status}\n")

      state_options = ["0", "1"]

      while True:
        print("0) Change State\n1) Quit\n")
        change_state  = str(input("   Change state: ")).lower()
        if change_state in state_options:
          break
        print(ERROR_MSG)

      match change_state:
        case "0":
          cursor.execute("UPDATE books SET readed = ? WHERE filename = ?", (not current_state, book_to_edit))
          connection.commit()
        case "1":
          clear_terminal()
          return
    case "3":
      clear_terminal()
      return

def change_path():
  clear_terminal()
  while True:
    
    console.rule("Provide a new path (that is currently created as directory) '0' to quit")
    new_path = tevah_input()
    new_path = new_path.strip()

    if new_path == "0":
      return

    new_path = Path(new_path)
    if new_path.exists() and new_path.is_dir:
      break

    clear_terminal()
    print("Invalid path, try it again!")

  books_path = cursor.execute("SELECT books_path FROM library LIMIT 1").fetchone()
  books_path = books_path[0] if books_path else None
  files = os.listdir(books_path)
  files = [f for f in files if f.endswith(".pdf") or f.endswith(".pdf:Zone.Identifier")]

  for file in files:
    current_file_path = Path(books_path) / file
    destination = Path(new_path) / file
    shutil.move(current_file_path, destination)

  set_library_path(str(new_path))

def get_last_page(pdf_path):
  history_file   = os.path.expanduser("~/.local/share/zathura/history")
  history_dir    = os.path.dirname(history_file)
  last_book_page = None

  os.makedirs(history_dir, exist_ok=True)

  open(history_file, "a", encoding="utf-8").close()

  pdf_path       = os.path.abspath(pdf_path)

  with open(history_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

  for i, line in enumerate(lines):
    line = line.strip()
    if line == f"[{pdf_path}]":
      if i + 1 < len(lines) and lines[i + 1].startswith("page="):
        last_book_page = int(lines[i + 1].split("=")[1])
      break

  return last_book_page

def list_books():
  clear_terminal()
  option = check_option(
    "",
    [
      "0) Open",
      "1) Quit"
    ],
    ERROR_MSG,
    ["0", "1"],
    True,
    execute=show_books
  )  

  match option:
    case "0":
      open_book()
    case "1":
      clear_terminal()
      return

def show_books():
  cursor.execute("SELECT * FROM books")
  books = cursor.fetchall()
  options = ["0", "1"]

  console.rule("List of books")
  panels = []
  for book in books:
    bar = progress_bar(book['last_page'], book['pages'])

    content = f"[bold]{book['title'].split(':')[0]}[/bold]\nby {book['author']}\nfilename: {book['filename']}\npages: {book['pages']}\nreaded: {book['last_page']}\n{bar}"
    panels.append(Padding(Panel(content, expand=True), (0, 0, 0, 2)))

  console.print(Columns(panels, equal=True))
  print("")


def open_book():
  type_or_select = check_option(
    "Choose between selecting manually or typing the file name to open",
    [
      "0) Select",
      "1) Type",
      "2) Quit"
    ],
    ERROR_MSG,
    ["0", "1", "2"],
    True,
  )
  match type_or_select:
    case "0":
      select_file(open_in_zathura)
    case "1":
      type_file(open_in_zathura)
    case "2":
      clear_terminal()
      return


def open_in_zathura(files, file_index_track):
  clear_terminal()
  books = cursor.execute("SELECT * FROM books").fetchall()
  books_path = cursor.execute("SELECT books_path FROM library LIMIT 1").fetchone()[0]

  for book in books:
    if book["filename"] == files[file_index_track]["filename"]:
      pdf_filename = book["filename"]
      file_path = os.path.join(books_path, pdf_filename)
      break

  if os.path.exists(file_path):
    start = time.time()
    subprocess.run(["zathura", file_path])
    end = time.time()
    elapsed = int(end - start)
    display_elapsed(elapsed)
    last_page = get_last_page(file_path)
    cursor.execute(
      "UPDATE books SET last_page = ? WHERE filename = ?",
      (last_page, pdf_filename)
    )
    connection.commit()

def progress_bar(readed_pages, total_pages):
  bar_length = 20
  
  if readed_pages == total_pages:
    return f"{'▮' * bar_length} 100%"

  filled = int((readed_pages / total_pages) * bar_length)
  bar = "▮" * filled + " " * (bar_length - filled)
  percentage_readed = (readed_pages / total_pages) * 100
  
  return f"{bar}] {percentage_readed:.2f}%"



def push_book(files, file_index_track):
  clear_terminal()
  filename = files[file_index_track]
  books_path = cursor.execute("SELECT books_path FROM library LIMIT 1").fetchone()
  books_path = books_path[0] if books_path else None
  books = cursor.execute("SELECT * FROM books").fetchall()

  for book in books:
    if book["filename"] == filename:
      print("Error: Book was already added into library!")
      return

  path = os.path.join(books_path, filename)
  book_reader = PdfReader(path)
  book_metadata = book_reader.metadata

  total_pages = len(book_reader.pages)
  book_title = book_metadata.title
  book_author = book_metadata.author
  last_page = get_last_page(path)
  if not last_page:
    last_page = 0

  if not book_title:
      book_title = str(input("Provide book title: "))
  if not book_author:
      book_author = str(input("Provide book author: "))

  print(book_title)
  print(book_author)
  print(filename)
  print(total_pages)

  cursor.execute(
      """
  INSERT INTO books (title, author, filename, pages, added_on, last_page)
  VALUES (?, ?, ?, ?, datetime('now'), ?)
  """,
      (book_title, book_author, filename, total_pages, last_page),
  )

  connection.commit()

  print(f"{filename} was added succesfully!")


def quit_library():
  clear_terminal()
  print("Until the next time :)")
  sys.exit()

def remove_book():
  options  = ["0", "1", "2"]
  selected = check_option(
    "Choose between selecting manually or typing the file name to remove",
    ["0) Open select list", "1) Type file name", "2) Quit"],
    ERROR_MSG,
    options,
    True
  )

  match selected:
    case "0":
      select_file(delete_book)
    case "1":
      type_file(delete_book)
    case "2":
      clear_terminal()
      return


def delete_book(files, file_index_track):
  clear_terminal()
  print(files)
  print(file_index_track)
  print(files[file_index_track])

  books = cursor.execute("SELECT * FROM books").fetchall()

  for book in books:
    if book["filename"] == files[file_index_track]["filename"]:
      book_to_delete = book["filename"]
      break
  
  cursor.execute("""
    DELETE FROM books WHERE filename = ?
    """, (book_to_delete,)
  )

  connection.commit()


def select_file(execute):
  clear_terminal()
  books_path = cursor.execute("SELECT books_path FROM library LIMIT 1").fetchone()
  books_path = books_path[0] if books_path else None

  if execute == open_in_zathura or execute == delete_book or execute == change_details:
    books = cursor.execute("SELECT * FROM books").fetchall()

    files = os.listdir(books_path)
    files = [f for f in files if f.endswith(".pdf")]

    if not books:
      print("No books were added!")
      return

    book_index_track = 0

    while True:
      console.rule("Use arrow Up/Down to select book then hit ENTER or Press hit q to quit")
      print("")

      for index, book in enumerate(books):
        if index == book_index_track:
          print(f">  {book['title'].split(':')[0]}: {book['filename']}")
        else:
          print(f"   {book['title'].split(':')[0]}: {book['filename']}")

      fd = sys.stdin.fileno()
      old_settings = termios.tcgetattr(fd)

      try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        if key == "\x1b":
          key += sys.stdin.read(2)
      finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
     
      match key:
        case "\x1b[A":
          book_index_track = uparrow(books, book_index_track, True)
        case "\x1b[B":
          book_index_track = downarrow(books, book_index_track, True)
        case "\r":
          execute(books, book_index_track)
          return
        case "q":
          print("Exiting...")
          return
      clear_terminal()
  else:
    files = os.listdir(books_path)
    files = [f for f in files if f.endswith(".pdf")]

    file_index_track = 0

    while True:
      console.rule("Use arrow Up/Down to select file hit ENTER or Press hit q to quit")
      print("")
      for index, file in enumerate(files):
        if index == file_index_track:
          print(f">  {file}")
        else:
          print(f"   {file}")

      fd = sys.stdin.fileno()
      old_settings = termios.tcgetattr(fd)

      try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        if key == "\x1b":
          key += sys.stdin.read(2)
      finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

      match key:
        case "\x1b[A":
          file_index_track = uparrow(files, file_index_track)
        case "\x1b[B":
          file_index_track = downarrow(files, file_index_track)
        case "\r":
          execute(files, file_index_track)
          return
        case "q":
          print("exiting...")
          return

      clear_terminal()


def set_library_path(full_path):
  # Check if the library table has a row
  cursor.execute("SELECT COUNT(*) FROM library")
  count = cursor.fetchone()[0]

  if count == 0:
      # No row exists, insert a new one
      cursor.execute(
          "INSERT INTO library (books_path, books_id) VALUES (?, ?)", (full_path, 0)
      )
  else:
      # Row exists, update it
      cursor.execute("UPDATE library SET books_path = ?", (full_path,))

  connection.commit()


def setup_app():
  while True:
    books_path = cursor.execute("SELECT books_path FROM library LIMIT 1").fetchone()
    books_path = books_path[0] if books_path else None

    if not books_path:
        ask_path = check_option(
            "You still don't have a path to save your books, choose one!",
            [
                "0) Use default path, the app root",
                "1) Create or select a path",
                "2) Quit",
            ],
            ERROR_MSG,
            ["0", "1", "2"],
            True,
        )

        match ask_path:
            case "0":
                clear_terminal()
                full_path = os.path.join(os.getcwd(), "books")
                set_library_path(full_path)
                clear_terminal()
            case "1":
                exist_or_create = check_option(
                    "Want to provide an existing path or create a new one?",
                    [
                      "0) Create a new path",
                      "1) Provide an existing path",
                      "2) Quit"
                    ],
                    ERROR_MSG,
                    ["0", "1", "2"],
                    True,
                )

                match exist_or_create:
                    case "0":
                        clear_terminal()
                        while True:
                            books_path = Path(input("Path: "))

                            if not books_path.exists():
                                books_path.mkdir(parents=True, exist_ok=True)
                                set_library_path(str(books_path))
                                clear_terminal()
                                break

                            clear_terminal()
                    case "1":
                        clear_terminal()
                        while True:
                            books_path = Path(input("Path: "))

                            if books_path.exists():
                                set_library_path(str(books_path))
                                print("Path was selected succesfully")
                                break

                            clear_terminal()
                    case "2":
                        clear_terminal()
                        print("Quitting...")
                        return
            case "1":
                return

    with open("tevah.txt", "r", encoding="utf-8") as f:
        banner = f.read()
    
    choice = check_option(
      banner,
      [
        "0) Add book          ",
        "1) Change books path ",
        "2) Edit book         ",
        "3) Open book         ",
        "4) List books        ",
        "5) Remove book       ",
        "6) Quit library      ",
      ],
      ERROR_MSG,
      ["0", "1", "2", "3", "4", "5", "6"],
      True,
      menu=True
    )
  

    match choice:
      case "0":
        add_book()
      case "1":
        change_path()
      case "2":
        edit_book()
      case "3":
        open_book()
      case "4":
        list_books()
      case "5":
        remove_book()
      case "6":
        connection.close()
        quit_library()

def type_file(execute):
  books_path = cursor.execute("SELECT books_path FROM library LIMIT 1").fetchone()
  books_path = books_path[0] if books_path else None

  if execute == open_in_zathura or execute == delete_book or execute == change_details:

    books = cursor.execute("SELECT * FROM books").fetchall()

    if not books:
      print("No books were added!")
      return

    book_index_track = 0

    while True:
      clear_terminal()
      console.rule("Book's list")
      print("")

      for book in books:
        print(f"{book['filename']}")

      print("\nType book name or ENTER '0' to exit")
      console.print("\n=", style="blue", end="")
      console.print("תֵּבָה", style="red", end="")
      console.print("> ", style="blue", end="")
      filename = str(input("")).lower()

      if filename == "0":
        return

      for book_index_track, book in enumerate(books):
        if books[book_index_track]['filename'] == filename:
          execute(books, book_index_track)
          return

      print("not found")
  else:
    files = os.listdir(books_path)
    files = [f for f in files if f.endswith(".pdf")]

    file_index_track = 0
    
    while True:
      clear_terminal()

      for file in files:
        print(f"{file}")

      print("\nType book name or ENTER '0' to exit")
      console.print("\n=", style="blue", end="")
      console.print("תֵּבָה", style="red", end="")
      console.print("> ", style="blue", end="")
      filename = str(input("")).lower()

      if filename == "0":
        return
    
      for file_index_track, file in enumerate(files):
        if file == filename:
          execute(files, file_index_track)
          return

      print("not found")

    

def uparrow(items, item_index_track, books=False):
  if books:
    if item_index_track == 0:
      item_index_track = len(items) - 1

      for index, item in enumerate(items):
        if index == len(items) - 1:
          print(f">  {item['title'].split(':')[0]}: {item['filename']}")
        else:
          print(f"   {item['title'].split(':')[0]}: {item['filename']}")
    else:
      item_index_track = item_index_track - 1
      for index, item in enumerate(items):
        if index == item_index_track:
          print(f">  {item['title'].split(':')[0]}: {item['filename']}")
        else:
          print(f"   {item['title'].split(':')[0]}: {item['filename']}")
  else:
    if item_index_track == 0:
      item_index_track = len(items) - 1
      for index, item in enumerate(items):
        if index == len(items) - 1:
          print(f">  {item}")
        else:
          print(f"   {item}")
    else:
      item_index_track = item_index_track - 1
      for index, item in enumerate(items):
        if index == item_index_track:
          print(f">  {item}")
        else:
          print(f"   {item}")

  return item_index_track


if __name__ == "__main__":
  clear_terminal()
  console = Console()

  connection = sqlite3.connect("bookshelf.db")
  connection.row_factory = sqlite3.Row

  cursor = connection.cursor()

  cursor.execute("""
  CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cover TEXT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    filename TEXT NOT NULL,
    pages INTEGER NOT NULL,
    readed INTEGER NOT NULL DEFAULT 0,
    added_on TEXT NOT NULL DEFAULT (datetime('now')),
    last_page INTEGER NOT NULL DEFAULT 0,
    started_on TEXT DEFAULT NULL,
    finished_on TEXT DEFAULT NULL
  )
  """)

  cursor.execute("""
  CREATE TABLE IF NOT EXISTS library (
    books_id INTEGER NOT NULL,
    books_path TEXT NOT NULL,
    FOREIGN KEY (books_id) REFERENCES books(id)
  )
  """)

  main()

