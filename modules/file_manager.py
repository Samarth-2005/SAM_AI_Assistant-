import os


def create_folder(folder_name):

    try:

        desktop = os.path.join(
            os.environ["USERPROFILE"],
            "OneDrive",
            "Desktop"
        )

        # If OneDrive Desktop doesn't exist,
        # use the normal Desktop location.
        if not os.path.exists(desktop):

            desktop = os.path.join(
                os.environ["USERPROFILE"],
                "Desktop"
            )

        folder_path = os.path.join(desktop, folder_name)

        if os.path.exists(folder_path):
            return f"The folder {folder_name} already exists."

        os.makedirs(folder_path)

        return f"Folder {folder_name} created successfully."

    except Exception as e:

        print("File Manager Error:", e)

        return "Sorry, I couldn't create the folder."


def create_text_file(file_name):

    try:

        desktop = os.path.join(
            os.environ["USERPROFILE"],
            "OneDrive",
            "Desktop"
        )

        if not os.path.exists(desktop):

            desktop = os.path.join(
                os.environ["USERPROFILE"],
                "Desktop"
            )

        if not file_name.lower().endswith(".txt"):
            file_name += ".txt"

        file_path = os.path.join(desktop, file_name)

        if os.path.exists(file_path):
            return f"The file {file_name} already exists."

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("")

        return f"Text file {file_name} created successfully."

    except Exception as e:

        print("File Manager Error:", e)

        return "Sorry, I couldn't create the text file."
def _desktop_locations():
    """Resolve Windows' configured Desktop plus existing local/OneDrive desktops."""
    from pathlib import Path
    candidates = []
    if os.name == 'nt':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                    r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders') as key:
                candidates.append(Path(os.path.expandvars(winreg.QueryValueEx(key, 'Desktop')[0])))
        except OSError:
            pass
    home = Path(os.environ.get('USERPROFILE', str(Path.home())))
    candidates.extend([home/'Desktop', home/'OneDrive'/'Desktop'])
    for key in ('OneDrive', 'OneDriveConsumer', 'OneDriveCommercial'):
        if os.environ.get(key): candidates.append(Path(os.environ[key])/'Desktop')
    if os.environ.get('PUBLIC'): candidates.append(Path(os.environ['PUBLIC'])/'Desktop')
    result, seen = [], set()
    for path in candidates:
        normalized = os.path.normcase(os.path.abspath(path))
        if normalized not in seen and path.is_dir():
            seen.add(normalized); result.append(path)
    return result


def _name_key(name):
    import re
    return ' '.join(re.sub(r'[_-]+', ' ', name.casefold()).split())


def _spoken_key(name):
    import re
    name = _name_key(name)
    name = re.sub(r'^(?:my|the)\s+', '', name)
    name = re.sub(r'\s+(?:folder|directory)$', '', name)
    # Explicit common variation, not fuzzy matching for arbitrary file names.
    return re.sub(r'\bprojects\b', 'project', name)


def _open_match(query, candidates):
    """Exact matches win. Never select silently between equal matches."""
    scores = []
    for path in candidates:
        names = [path.name] if path.is_dir() else [path.name, path.stem]
        score = 0
        if any(_name_key(query) == _name_key(n) for n in names): score = 2
        elif _spoken_key(query) and any(_spoken_key(query) == _spoken_key(n) for n in names): score = 1
        if score: scores.append((score, path))
    if not scores: return None
    best = max(score for score, _ in scores)
    paths = list(dict.fromkeys(path for score, path in scores if score == best))
    if len(paths) > 1:
        return 'I found several matches. Please use a more specific name: ' + '; '.join(str(p) for p in paths[:5])
    path = paths[0]
    if path.is_dir():
        from modules.desktop_control import open_folder_visible
        if open_folder_visible(path): return f'Opened {path.name}.'
        return f'Opened {path.name}, but Windows did not bring it forward. Click File Explorer on the taskbar.'
    os.startfile(str(path))
    return f'Opening {path.name}.'


def open_file_or_folder(name):
    import re
    from pathlib import Path
    try:
        query = re.sub(r'^open\s+', '', name.strip(), flags=re.IGNORECASE)
        query = re.sub(r'\s+(?:on|from)\s+(?:my|the)\s+desktop$', '', query, flags=re.IGNORECASE)
        if not query: return 'Please tell me the file or folder name.'
        desktops = _desktop_locations()
        print('Desktop search locations:', [str(p) for p in desktops])
        if not desktops: return 'I could not locate your Desktop folder.'
        top = []
        for desktop in desktops:
            try: top.extend(desktop.iterdir())
            except OSError: pass
        result = _open_match(query, top)
        if result: return result
        # Bounded nested search avoids crawling large environments and repositories.
        nested, seen = [], set()
        limit_reached = False
        for desktop in desktops:
            for root, dirs, files in os.walk(desktop, followlinks=False):
                depth = len(Path(root).relative_to(desktop).parts)
                dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', 'node_modules', '__pycache__'}]
                if depth >= 4: dirs[:] = []
                if depth > 0:
                    for entry in dirs + files:
                        path = Path(root)/entry
                        key = os.path.normcase(os.path.abspath(path))
                        if key not in seen:
                            seen.add(key);nested.append(path)
                        if len(nested) >= 15000:
                            limit_reached = True;break
                if limit_reached: break
            if limit_reached: break
        if limit_reached:
            return 'The Desktop search was too large. Move a shortcut to the top of your Desktop and ask me to open its exact name.'
        result = _open_match(query, nested)
        if result: return result
        return f"I couldn't find {query} on your Desktop or within four subfolder levels. Please check the exact folder name."
    except Exception as exc:
        print('File Manager Error:', exc)
        return f'I could not open that item: {exc}'


def write_to_file(file_name, text):

    try:

        desktop = os.path.join(
            os.environ["USERPROFILE"],
            "OneDrive",
            "Desktop"
        )

        if not os.path.exists(desktop):

            desktop = os.path.join(
                os.environ["USERPROFILE"],
                "Desktop"
            )

        file_name = file_name.strip()

        # Add .txt if necessary
        if not file_name.lower().endswith(".txt"):
            file_name += ".txt"

        file_path = os.path.join(desktop, file_name)

        # Write the text
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)

        return f"Text written successfully to {file_name}."

    except Exception as e:

        print("File Manager Error:", e)

        return "Sorry, I couldn't write to the file."
def add_to_file(file_name, text):

    try:

        desktop = os.path.join(
            os.environ["USERPROFILE"],
            "OneDrive",
            "Desktop"
        )

        if not os.path.exists(desktop):

            desktop = os.path.join(
                os.environ["USERPROFILE"],
                "Desktop"
            )

        file_name = file_name.strip()

        if not file_name.lower().endswith(".txt"):
            file_name += ".txt"

        file_path = os.path.join(desktop, file_name)

        # Add text to the existing file
        with open(file_path, "a", encoding="utf-8") as file:

            if os.path.getsize(file_path) > 0:
                file.write("\n")

            file.write(text)

        return f"Text added successfully to {file_name}."

    except Exception as e:

        print("File Manager Error:", e)

        return "Sorry, I couldn't add the text to the file."
def read_file(file_name):

    try:

        desktop = os.path.join(
            os.environ["USERPROFILE"],
            "OneDrive",
            "Desktop"
        )

        if not os.path.exists(desktop):

            desktop = os.path.join(
                os.environ["USERPROFILE"],
                "Desktop"
            )

        # Clean the name
        name = file_name.strip()

        # Remove "read" if it accidentally comes through
        if name.lower().startswith("read "):
            name = name[5:].strip()

        print(f"Searching for file: {name}")

        # ------------------------------------------------
        # Search Desktop and all subfolders
        # ------------------------------------------------

        for root, folders, files in os.walk(desktop):

            for file in files:

                file_without_extension = os.path.splitext(file)[0]

                # Exact match
                if file_without_extension.lower() == name.lower():

                    file_path = os.path.join(root, file)

                    with open(
                        file_path,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        content = f.read().strip()

                    if not content:

                        return f"{file} is empty."

                    return content

                # Match underscores and spaces
                if (
                    file_without_extension
                    .lower()
                    .replace("_", " ")
                    ==
                    name.lower()
                    .replace("_", " ")
                ):

                    file_path = os.path.join(root, file)

                    with open(
                        file_path,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        content = f.read().strip()

                    if not content:

                        return f"{file} is empty."

                    return content

        return f"I couldn't find {name} on your Desktop."

    except Exception as e:

        print("File Manager Error:", e)

        return "Sorry, I couldn't read the file."
def delete_file_or_folder(name):

    try:

        desktop = os.path.join(
            os.environ["USERPROFILE"],
            "OneDrive",
            "Desktop"
        )

        if not os.path.exists(desktop):

            desktop = os.path.join(
                os.environ["USERPROFILE"],
                "Desktop"
            )

        name = name.strip()

        print(f"Searching for: {name}")

        # Search Desktop and subfolders
        for root, folders, files in os.walk(desktop):

            # -----------------------------
            # Check folders
            # -----------------------------
            for folder in folders:

                if folder.lower() == name.lower():

                    full_path = os.path.join(root, folder)

                    # Safety: don't delete the main Desktop
                    if os.path.abspath(full_path) == os.path.abspath(desktop):
                        return "I cannot delete the Desktop folder."

                    import shutil

                    shutil.rmtree(full_path)

                    return f"Folder {folder} deleted successfully."

            # -----------------------------
            # Check files
            # -----------------------------
            for file in files:

                file_without_extension = os.path.splitext(file)[0]

                if (
                    file_without_extension.lower() == name.lower()
                    or
                    file_without_extension.lower().replace("_", " ")
                    == name.lower().replace("_", " ")
                ):

                    full_path = os.path.join(root, file)

                    os.remove(full_path)

                    return f"File {file} deleted successfully."

        return f"I couldn't find {name} on your Desktop."

    except Exception as e:

        print("Delete Error:", e)

        return "Sorry, I couldn't delete that item."
def search_files(search_term):

    try:

        desktop = os.path.join(
            os.environ["USERPROFILE"],
            "OneDrive",
            "Desktop"
        )

        if not os.path.exists(desktop):

            desktop = os.path.join(
                os.environ["USERPROFILE"],
                "Desktop"
            )

        search_term = search_term.strip().lower()

        # Remove common voice-command words
        words_to_remove = [
            "the",
            "my",
            "a",
            "an"
        ]

        for word in words_to_remove:

            if search_term.startswith(word + " "):

                search_term = search_term[
                    len(word) + 1:
                ].strip()

        if not search_term:
            return []

        results = []

        # Search Desktop and all subfolders
        for root, folders, files in os.walk(desktop):

            # Search folders
            for folder in folders:

                if search_term in folder.lower():

                    full_path = os.path.join(
                        root,
                        folder
                    )

                    results.append(full_path)

            # Search files
            for file in files:

                if search_term in file.lower():

                    full_path = os.path.join(
                        root,
                        file
                    )

                    results.append(full_path)

        return results

    except Exception as e:

        print("File Search Error:", e)

        return []