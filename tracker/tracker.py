import subprocess


def search(query):
    """ Searches the specified query in Tracker """
    out = subprocess.run([
        "tracker3", "search", "--folders", "--disable-color", "-l", "20", query
    ],
                         capture_output=True,
                         timeout=20,
                         text=True,
                         check=True)

    lines = out.stdout.splitlines()[1:]
    results = []
    for line in lines:
        formatted_line = line.strip().replace("file://", "")

        if formatted_line == "" or formatted_line == "...":
            continue

        results.append(formatted_line)

    return results
