class Table:
    def __init__(self, *columns, colnames=None):
        self.columns = columns
        if colnames is None:
            self.colnames = (f'col{i}' for i in range(len(columns)))
        else:
            self.colnames = colnames

        if not len(set(map(len, columns))) == 1:
            raise ValueError('Columns have different lengths.')

    def __rows(self):
        rows = []
        rows.append(','.join(self.colnames))
        for row in zip(*self.columns):
            rows.append(','.join(map(str, row)))
        return rows

    def __repr__(self):
        return '\n'.join(self.__rows())

    def __add_row_numbers(self):
        return Table(range(1, len(self.columns[0]) + 1),
                     *self.columns,
                     colnames=('№', *self.colnames))

    @staticmethod
    def csv(table, show_row_numbers=False):
        """Return given table as a multiline string in csv format."""
        if show_row_numbers:
            return table.__add_row_numbers().__repr__()
        else:
            return table.__repr__()

    @staticmethod
    def write_csv(table, filepath, show_row_numbers=False):
        """Write given table to file in csv format."""
        if not filepath.endswith('.csv'):
            raise ValueError('Filepath extension is not ".csv".')
        with open(filepath, 'x') as file:
            file.write(Table.csv(table, show_row_numbers=show_row_numbers))

    @staticmethod
    def latex(table, show_row_numbers=False):
        """Return given table as a LaTeX tabular."""
        table_copy = table.__add_row_numbers() if show_row_numbers else table
        line_ending = r' \\ \hline' + '\n'

        result = r'\begin{tabular}{|'
        for i in range(len(table_copy.columns)):
            result += 'c|'
        result += '}' + '\n' + r'\hline' + '\n'

        result += ' & '.join(map(str, table_copy.colnames)) + line_ending
        for row in zip(*table_copy.columns):
            result += ' & '.join(map(str, row)) + line_ending
        result += r'\end{tabular}'

        return result

    @staticmethod
    def write_latex(table, filepath, show_row_numbers=False):
        """Write given table to file in latex-tabular format"""
        if not filepath.endswith('.tex'):
            raise ValueError('Filepath extension is not ".tex".')
        with open(filepath, 'x') as file:
            file.write(Table.latex(table, show_row_numbers=show_row_numbers))

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
    table = Table(a, b, c, colnames=['a', 'b', 'c'])
    print(table)
    print(Table.csv(table))
    print(Table.csv(table, show_row_numbers=True))
    print(Table.latex(table))
    Table.write_csv(table, 'labtable-example-1.csv')
    Table.write_csv(table, 'labtable-example-2.csv', show_row_numbers=True)
    Table.write_latex(table, 'labtable-example-1.tex')
    Table.write_latex(table, 'labtable-example-2.tex', show_row_numbers=True)
    a, b, c = Table.read_csv('labtable-example-1.csv')
    print(f'a = {a}')
    print(f'b = {b}')
    print(f'c = {c}')
    print(a[1])
