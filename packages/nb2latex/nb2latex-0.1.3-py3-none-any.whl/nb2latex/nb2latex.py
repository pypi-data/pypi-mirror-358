import subprocess
import argparse
import sys
import os
import shutil

if shutil.which("pandoc") is None:
    print("Error: pandoc is not installed. Please install it from https://pandoc.org")
    exit(1)


# subprocess shell run to latex, and executes the .ipynb to ensure cell outputs on code
def nbconvert(nb):
    print(f"Converting {nb}.ipynb to LaTeX...")
    subprocess.run(
        ["jupyter", "nbconvert", f"{nb}.ipynb", "--to", "latex", "--execute"],
        check=True,
    )


# extract lines between \begin{document} and \end{document} also remove \begin{doucment}, \maketitle, and \end{document} to leave body
def extractTexBody(texFile, bodyFile):
    with open(texFile, "r") as f:
        lines = f.readlines()  # reads .tex file and stores for processing
    start = None
    end = None
    for i, line in enumerate(lines):
        if r"\begin{document}" in line:
            start = i  # saves line no. for \begin{document}
        elif r"\end{document}" in line:
            end = i  # saves line no. for \end{document}
            break
    if start is None or end is None:
        print(f"Can't find Tex document environment in {texFile}")
        sys.exit(1)
    # extract lines via line numbers
    bodyLines = lines[
        start + 1 : end
    ]  # from begin{document} to end{document}, including neither
    # remove \maketitle
    bodyLines = [l for l in bodyLines if r"\maketitle" not in l]
    # make body.tex file (ie no preamble or begin\end{document})
    with open(bodyFile, "w") as f:
        f.writelines(bodyLines)


def extractPreamble(texFile, preambleFile):
    with open(texFile, "r") as f:
        lines = f.readlines()
    start = 0
    end = None
    for i, line in enumerate(lines):
        if r"\begin{document}" in line:
            end = i  # saves \begin{document} line no.
            break
    if end is None:
        print(r"Can't find \begin{document}")
        sys.exit(1)
    # save only up to (not including) \begin{document}
    preamble = lines[start:end]
    with open(preambleFile, "w") as f:
        f.writelines(preamble)


def compilePDF(texFile):
    print("Compiling PDF")
    # run pdflatex two times to generate table of contents correctly in pdf
    subprocess.run(
        ["pdflatex", texFile],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    subprocess.run(
        ["pdflatex", texFile],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def runBuild(title, notebooks):
    pdfTitle = title
    notebooks = [
        os.path.splitext(nb)[0] for nb in notebooks if nb.endswith(".ipynb")
    ]  # splits into filename and .ipynb extension and then leaves the extention behind
    outputDir = f"{pdfTitle} output files"
    os.makedirs(
        outputDir, exist_ok=True
    )  # creates directory for extra files from pdf creation with LaTeX

    if not notebooks:
        print("No notebooks provided.")
        sys.exit(1)

    # convert notebook to .tex and extract body only of each
    for nb in notebooks:
        nbconvert(nb)
        extractTexBody(f"{nb}.tex", f"{nb}Body.tex")

    # take preamble from first notebook arg
    extractPreamble(f"{notebooks[0]}.tex", f"{pdfTitle}.tex")

    ###### creating master .tex document ######
    with open(f"{pdfTitle}.tex", "a") as f:
        f.write(f"\\title{{{pdfTitle}}}\n")
        f.write("\\begin{document}\n")
        f.write("\\maketitle\n")
        f.write("\\tableofcontents\n")

        # add input body tex files
        for nb in notebooks:
            f.write("\\clearpage\n")
            f.write(f"\\input{{{nb}Body.tex}}\n")

        f.write("\\end{document}\n")

    compilePDF(f"{pdfTitle}.tex")

    # remove excess files post-compiling
    for nb in notebooks:
        texFile = f"{nb}.tex"
        bodyFile = f"{nb}Body.tex"
        if os.path.exists(texFile):
            os.remove(texFile)
        if os.path.exists(bodyFile):
            os.remove(bodyFile)

    # move excess files to outputDir
    for ext in ["aux", "log", "out", "toc", "tex", "pdf"]:
        fileName = f"{pdfTitle}.{ext}"
        if os.path.exists(fileName):
            shutil.move(fileName, os.path.join(outputDir, fileName))

    print(
        f"Compiling complete! PDF output: {os.path.join(outputDir, f'{pdfTitle}.pdf')}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="nb2latex CLI tool - convert multiple notebooks to a single LaTeX output. \nMore info: https://github.com/archiebenn/nb2latex"
    )
    parser.add_argument("--title", default="My Document", help="Document title")
    parser.add_argument(
        "notebooks", nargs="*", help="List of notebooks (.ipynb) to include"
    )
    args = parser.parse_args()

    runBuild(args.title, args.notebooks)


if __name__ == "__main__":
    main()
