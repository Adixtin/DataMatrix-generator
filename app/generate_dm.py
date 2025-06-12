from Datamatrix import DataMatrix

if __name__ == "__main__":
    msg = input("Enter a message: ")
    datamatrix_name = input("Enter a file name: ")

    if not datamatrix_name:
        datamatrix_name = "DataMatrix"

    dm = DataMatrix(msg)

    svg_code = dm.svg()

    with open(f'generated_datamatrixes/{datamatrix_name}.svg', "w", encoding="utf-8") as f:
        f.write(svg_code)

    print(f'SVG saved as {datamatrix_name}.svg')
