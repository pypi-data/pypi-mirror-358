



import random
import string
from datetime import datetime, timedelta

import matplotlib
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

import df2tables as df2dtb


def random_data(num_rows=100):

    def get_rdylgn_colors(num_colors=100):
        cmap = matplotlib.colormaps["YlGnBu"]
        color_indices = np.linspace(0, 1, num_colors)
        colors = []
        for i in color_indices:
            rgba_color = cmap(i)
            hex_color = mcolors.rgb2hex(rgba_color[:3])
            colors.append(
                f"<div style='font-family: monospace;background-color:{hex_color}'>{hex_color}</div>"
            )
        return colors

    unicode_ranges = [
        (0x0020, 0x007E),  # Basic Latin (printable ASCII)
        (0x00A0, 0x00FF),  # Latin-1 Supplement (e.g., accented characters)
        (0x0100, 0x017F),  # Latin Extended-A (more European characters)
    ]

    def gen_datetime(min_year=1990, max_year=datetime.now().year):
        # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
        start = datetime(min_year, 1, 1, 00, 00, 00)
        years = max_year - min_year + 1
        end = start + timedelta(days=365 * years)
        return start + (end - start) * random.random()

    def get_random_unicode_char():
        """Get a random Unicode character from various language ranges."""
        range_start, range_end = random.choice(unicode_ranges)
        code_point = random.randint(range_start, range_end)
        try:
            return chr(code_point)
        except ValueError:
            return chr(random.randint(0x00C0, 0x00FF))

    result = []
    # colors = list(reversed(get_rdylgn_colors(num_rows)))
    colors = get_rdylgn_colors(num_rows)
    for i in range(num_rows):
        row = [
            random.choice(string.ascii_letters),
            random.randint(100, 100000),
            random.uniform(-1, 1),
            get_random_unicode_char(),
            random.choice([True, False]),
            str(gen_datetime()),
            colors[i],
        ]
        result.append(row)
    columns= [f'col{i}' for i in range(len(result[0]))]
    df = pd.DataFrame(result,  columns=columns)
   
    outfile = "rnd_table2.html"
    df2dtb.to_html(df, outfile=outfile, title="Example Diverse Random Data", html_cols=["col1", "col2"])
    return result

def pkg_test():

    def get_packages():
        try:
            import pkg_resources

            dists = [repr(d).split(" ") for d in sorted(pkg_resources.working_set)]
            dists = sorted(dists, key=lambda x: x[0].lower())
        except ModuleNotFoundError:
            print("Error loading module pkg_resources - using random data")
            dists = generate_random_data(num_rows=100)
            # dists.insert(0, ["name1", "name2", "name3", "name4", "name5", "name6"])
        return dists

    header_list = ["name        ", "ver  ", "full package path"]
    df = pd.DataFrame(get_packages(), columns=header_list)
    
    outfile = "pkg_table.html"
    df2dtb.to_html(df, outfile=outfile)

def test_yfinance(ticker='AAPL'):
    import yfinance as yf
    per = "2y"
    df = yf.download(ticker, period=per)
    df['Date'] = df.index.map(lambda x: pd.to_datetime(x).date()) 
    
    outfile = "yfinance.html"
    df2dtb.to_html(
        df,
        outfile=outfile,
        title=f"{ticker}, last {per}",
    )



if __name__ == "__main__":
    # random_data()
    test_yfinance()
    # pkg_test()
