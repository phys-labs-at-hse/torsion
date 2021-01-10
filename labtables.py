class Table:
    def __init__(self, *columns, colnames=None):
        self.columns = columns
        if colnames is None:
            self.colnames = [f'col{i}' for i in range(len(columns))]
        else:
            self.colnames = colnames

        if not len(set(map(len, columns))) == 1:
            raise ValueError('Columns have different lengths.')

    def __repr__(self):
        rows = ','.join(self.colnames) + '\n'
        for row in zip(*self.columns):
            rows += ','.join(map(str, row)) + '\n'
        return rows

    @staticmethod
    def csv(table):
        """Return given table as a multiline string in csv format."""
        return table.__repr__()

    @staticmethod
    def write_csv(table, filepath):
        """Write given table to file in csv format."""
        if not filepath.endswith('.csv'):
            raise ValueError('Filepath extension is not ".csv".')
        with open(filepath, 'x') as file:
            file.write(Table.csv(table))

    @staticmethod
    def latex(table):
        """Return given table as a LaTeX tabular."""
        rows = r'\begin{tabular}{|'
        for i in range(len(table.columns)):
            rows += 'c|'

        line_ending = r' \\ \hline' + '\n'
        rows += '}' + '\n' + r'\hline' + '\n'
        rows += ' & '.join(table.colnames) + line_ending

        for row in zip(*table.columns):
            rows += ' & '.join(map(str, row)) + line_ending
        rows += r'\end{tabular}'

        return rows

    @staticmethod
    def write_latex(table, filepath):
        """Write given table to file in latex-tabular format"""
        if not filepath.endswith('.tex'):
            raise ValueError('Filepath extension is not ".tex".')
        with open(filepath, 'x') as file:
            file.write(Table.latex(table))

    @staticmethod
    def read_csv(filepath):
        """Read csv file and return an iterable of it's columns

        If the first line in the csv file contains letters, it is
        assumed to be a header row and skipped.
        To assign the result, use unpacking:

            col1, col2, col3 = labtable.read_csv(filepath)
        """
        with open(filepath) as file:
            rows = []

            first_line = next(file).strip()
            if not any(char.isalpha() for char in first_line):
                rows.append(list(map(float, first_line.split(','))))

            for line in file:
                rows.append(list(map(float, line.strip().split(','))))

            return zip(*rows)


if __name__ == '__main__':
    # This is a simple test.
    a, b, c = [(i, i + 1, i + 2) for i in [1, 5, 10]]
    print(f'a = {a}')
    print(f'b = {b}')
    print(f'c = {c}')
    table = Table(a, b, c, colnames = ['a', 'b', 'c'])
    print(table)
    print(Table.csv(table))
    print(Table.latex(table))
    Table.write_csv(table, 'labtable-example.csv')
    Table.write_latex(table, 'labtable-example.tex')
    a, b, c = Table.read_csv('labtable-example.csv')
    print(f'a = {a}')
    print(f'b = {b}')
    print(f'c = {c}')
    print(a[1])
